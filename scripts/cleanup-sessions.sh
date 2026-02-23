#!/usr/bin/env bash
#
# cleanup-sessions.sh — Remove expired MAS session files from Gateway
#
# MAS sessions are single-use (one per request, never revisited).
# This script cleans up session files older than MAX_AGE_HOURS
# and removes corresponding entries from sessions.json.
#
# Usage: cleanup-sessions.sh [--dry-run]
# Cron:  0 4 * * * /home/mayacrew/.f1crew/scripts/mas/scripts/cleanup-sessions.sh >> /home/mayacrew/.f1crew/logs/session-cleanup.log 2>&1

set -euo pipefail

export SESSIONS_DIR="${HOME}/.f1crew/agents/main/sessions"
SESSIONS_JSON="${SESSIONS_DIR}/sessions.json"
export MAX_AGE_HOURS=24
export DRY_RUN=false

[[ "${1:-}" == "--dry-run" ]] && export DRY_RUN=true

ts() { date -u "+%Y-%m-%dT%H:%M:%SZ"; }

if [[ ! -f "$SESSIONS_JSON" ]]; then
    echo "$(ts) sessions.json not found at $SESSIONS_JSON"
    exit 0
fi

# Find MAS session entries and their file ages
echo "$(ts) Starting MAS session cleanup (max_age=${MAX_AGE_HOURS}h, dry_run=${DRY_RUN})"

BEFORE_SIZE=$(stat -c%s "$SESSIONS_JSON" 2>/dev/null || stat -f%z "$SESSIONS_JSON")
BEFORE_COUNT=$(ls "$SESSIONS_DIR"/*.jsonl 2>/dev/null | wc -l)

# Use Python for atomic sessions.json update + file cleanup
python3 << 'PYEOF'
import json, os, sys, time, shutil

sessions_dir = os.environ.get("SESSIONS_DIR", os.path.expanduser("~/.f1crew/agents/main/sessions"))
sessions_json = os.path.join(sessions_dir, "sessions.json")
max_age_sec = int(os.environ.get("MAX_AGE_HOURS", "24")) * 3600
dry_run = os.environ.get("DRY_RUN", "false") == "true"

now = time.time()

with open(sessions_json) as f:
    data = json.load(f)

original_count = len(data)
to_remove_keys = []
to_remove_files = []

for key, val in data.items():
    # Only clean up MAS sessions (user field contains "mas:")
    if "mas:" not in key:
        continue

    # Get session ID to find the .jsonl file
    if isinstance(val, dict):
        sid = val.get("sessionId", "")
    else:
        continue

    session_file = os.path.join(sessions_dir, f"{sid}.jsonl")
    lock_file = f"{session_file}.lock"

    # Check file age
    if os.path.exists(session_file):
        file_age = now - os.path.getmtime(session_file)
        if file_age > max_age_sec:
            to_remove_keys.append(key)
            to_remove_files.append(session_file)
            if os.path.exists(lock_file):
                to_remove_files.append(lock_file)
    else:
        # Session file already gone — clean up orphan key
        to_remove_keys.append(key)

if not to_remove_keys:
    print(f"No expired MAS sessions found (checked {original_count} keys)")
    sys.exit(0)

print(f"Found {len(to_remove_keys)} expired MAS sessions to clean up")

if dry_run:
    for k in to_remove_keys:
        print(f"  [dry-run] Would remove: {k}")
    sys.exit(0)

# Remove entries from sessions.json
for key in to_remove_keys:
    del data[key]

# Atomic write: write temp file, then rename
tmp_path = sessions_json + ".tmp"
with open(tmp_path, "w") as f:
    json.dump(data, f)
os.replace(tmp_path, sessions_json)

# Remove session files
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
