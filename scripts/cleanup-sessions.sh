#!/usr/bin/env bash
#
# cleanup-sessions.sh — Remove expired session files from Gateway
#
# Three cleanup phases:
#   Phase 1: MAS session keys in sessions.json (single-use, 24h TTL)
#   Phase 2: Non-MAS session keys in sessions.json (conversation, 72h TTL)
#   Phase 3: Orphan .jsonl files on disk (no sessions.json entry, 24h TTL)
#
# Usage: cleanup-sessions.sh [--dry-run]
# Cron:  0 4 * * * /home/mayacrew/.f1crew/scripts/mas/scripts/cleanup-sessions.sh >> /home/mayacrew/.f1crew/logs/session-cleanup.log 2>&1

set -euo pipefail

export SESSIONS_DIR="${HOME}/.f1crew/agents/main/sessions"
SESSIONS_JSON="${SESSIONS_DIR}/sessions.json"
export MAS_MAX_AGE_HOURS=24
export CONV_MAX_AGE_HOURS=72
export ORPHAN_MAX_AGE_HOURS=24
export DRY_RUN=false

[[ "${1:-}" == "--dry-run" ]] && export DRY_RUN=true

ts() { date -u "+%Y-%m-%dT%H:%M:%SZ"; }

if [[ ! -f "$SESSIONS_JSON" ]]; then
    echo "$(ts) sessions.json not found at $SESSIONS_JSON"
    exit 0
fi

BEFORE_SIZE=$(stat -c%s "$SESSIONS_JSON" 2>/dev/null || stat -f%z "$SESSIONS_JSON")
BEFORE_COUNT=$(ls "$SESSIONS_DIR"/*.jsonl 2>/dev/null | wc -l)

echo "$(ts) Starting session cleanup (mas=${MAS_MAX_AGE_HOURS}h, conv=${CONV_MAX_AGE_HOURS}h, orphan=${ORPHAN_MAX_AGE_HOURS}h, dry_run=${DRY_RUN})"

python3 << 'PYEOF'
import json, os, sys, time

sessions_dir = os.environ.get("SESSIONS_DIR", os.path.expanduser("~/.f1crew/agents/main/sessions"))
sessions_json = os.path.join(sessions_dir, "sessions.json")
mas_max_age = int(os.environ.get("MAS_MAX_AGE_HOURS", "24")) * 3600
conv_max_age = int(os.environ.get("CONV_MAX_AGE_HOURS", "72")) * 3600
orphan_max_age = int(os.environ.get("ORPHAN_MAX_AGE_HOURS", "24")) * 3600
dry_run = os.environ.get("DRY_RUN", "false") == "true"

now = time.time()

with open(sessions_json) as f:
    data = json.load(f)

original_count = len(data)
to_remove_keys = []
to_remove_files = []

# Collect all referenced session IDs for orphan detection
referenced_sids = set()
for val in data.values():
    if isinstance(val, dict):
        sid = val.get("sessionId", "")
        if sid:
            referenced_sids.add(sid)

# ── Phase 1: MAS sessions (24h TTL) ──
mas_removed = 0
for key, val in data.items():
    if "mas:" not in key:
        continue
    if not isinstance(val, dict):
        continue
    sid = val.get("sessionId", "")
    session_file = os.path.join(sessions_dir, f"{sid}.jsonl")
    if os.path.exists(session_file):
        if (now - os.path.getmtime(session_file)) > mas_max_age:
            to_remove_keys.append(key)
            to_remove_files.append(session_file)
            lock = f"{session_file}.lock"
            if os.path.exists(lock):
                to_remove_files.append(lock)
            mas_removed += 1
    else:
        to_remove_keys.append(key)
        mas_removed += 1

# ── Phase 2: Non-MAS conversation sessions (72h TTL) ──
conv_removed = 0
for key, val in data.items():
    if "mas:" in key:
        continue
    if not isinstance(val, dict):
        continue
    sid = val.get("sessionId", "")
    session_file = os.path.join(sessions_dir, f"{sid}.jsonl")
    if os.path.exists(session_file):
        if (now - os.path.getmtime(session_file)) > conv_max_age:
            to_remove_keys.append(key)
            to_remove_files.append(session_file)
            lock = f"{session_file}.lock"
            if os.path.exists(lock):
                to_remove_files.append(lock)
            conv_removed += 1
    else:
        to_remove_keys.append(key)
        conv_removed += 1

# ── Phase 3: Orphan .jsonl files (no sessions.json entry, 24h TTL) ──
orphan_removed = 0
orphan_size = 0
for fname in os.listdir(sessions_dir):
    if not fname.endswith(".jsonl"):
        continue
    sid = fname[:-6]  # strip .jsonl
    if sid in referenced_sids:
        continue
    fpath = os.path.join(sessions_dir, fname)
    file_age = now - os.path.getmtime(fpath)
    if file_age > orphan_max_age:
        orphan_size += os.path.getsize(fpath)
        to_remove_files.append(fpath)
        lock = f"{fpath}.lock"
        if os.path.exists(lock):
            to_remove_files.append(lock)
        orphan_removed += 1

print(f"Phase 1 (MAS keys): {mas_removed} expired")
print(f"Phase 2 (conv keys): {conv_removed} expired")
print(f"Phase 3 (orphan files): {orphan_removed} files ({orphan_size/1024:.0f}KB)")

if not to_remove_keys and not orphan_removed:
    print("Nothing to clean up")
    sys.exit(0)

if dry_run:
    for k in to_remove_keys:
        print(f"  [dry-run] Remove key: {k[:40]}...")
    print(f"  [dry-run] Would delete {len(to_remove_files)} files")
    sys.exit(0)

# Remove entries from sessions.json
for key in to_remove_keys:
    del data[key]

tmp_path = sessions_json + ".tmp"
with open(tmp_path, "w") as f:
    json.dump(data, f)
os.replace(tmp_path, sessions_json)

# Remove files
removed_files = 0
for fpath in to_remove_files:
    try:
        os.remove(fpath)
        removed_files += 1
    except OSError:
        pass

print(f"Removed {len(to_remove_keys)} keys from sessions.json, {removed_files} files deleted")
print(f"sessions.json: {original_count} → {len(data)} keys")
PYEOF

AFTER_SIZE=$(stat -c%s "$SESSIONS_JSON" 2>/dev/null || stat -f%z "$SESSIONS_JSON")
AFTER_COUNT=$(ls "$SESSIONS_DIR"/*.jsonl 2>/dev/null | wc -l)

echo "$(ts) Done. sessions.json: ${BEFORE_SIZE}→${AFTER_SIZE} bytes, files: ${BEFORE_COUNT}→${AFTER_COUNT}"
