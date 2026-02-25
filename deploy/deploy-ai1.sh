#!/usr/bin/env bash
set -euo pipefail

# MAS Deploy to ai1
# Usage: ./deploy/deploy-ai1.sh

SERVER="mayacrew@100.88.145.15"
SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

MAS_SCRIPTS="$HOME/.f1crew/scripts/mas"
MAS_DATA="$HOME/projects/mayacrew-f1crew/f1-mas"
SYSTEMD_DIR="$HOME/.config/systemd/user"

echo "=== MAS Deploy to ai1 ==="
echo "Source: $SCRIPT_DIR"

# 1. Python code → server scripts
echo "[1/9] Deploying Python code..."
scp "$SCRIPT_DIR"/mas/*.py "$SERVER:~/.f1crew/scripts/mas/"

# 2. Runtime config → server shared
echo "[2/9] Deploying runtime config..."
scp "$SCRIPT_DIR/config/mas-config.json" "$SERVER:~/.f1crew/shared/mas-config.json"

# 3. Characters → server data
echo "[3/9] Deploying characters..."
rsync -az --delete "$SCRIPT_DIR/characters/" "$SERVER:~/projects/mayacrew-f1crew/f1-mas/characters/"

# 4. Config MDs → server data
echo "[4/9] Deploying config files..."
rsync -az "$SCRIPT_DIR/config/persona-registry.md" \
          "$SCRIPT_DIR/config/selection-rules.md" \
          "$SCRIPT_DIR/config/task-templates.md" \
          "$SCRIPT_DIR/config/tribe-registry.md" \
          "$SERVER:~/projects/mayacrew-f1crew/f1-mas/config/"

# 5. Org → server data (domains.yaml, functions.yaml — hot-reloaded)
echo "[5/9] Deploying org..."
rsync -az "$SCRIPT_DIR/org/" "$SERVER:~/projects/mayacrew-f1crew/f1-mas/org/"

# 6. Routines → server data (routine YAML files — hot-reloaded)
echo "[6/9] Deploying routines..."
rsync -az "$SCRIPT_DIR/routines/" "$SERVER:~/projects/mayacrew-f1crew/f1-mas/routines/"

# 7. Library → server data (references only — exclude generated data)
# CAUTION: insights.md and memory-insights.md are generated at runtime.
# Overwriting them will destroy accumulated production knowledge.
echo "[7/9] Deploying library (excluding insights)..."
rsync -az --exclude='insights.md' --exclude='memory-insights.md' \
    "$SCRIPT_DIR/library/" "$SERVER:~/projects/mayacrew-f1crew/f1-mas/library/"

# 8. Scripts → server (library-scanner, cleanup, etc.)
echo "[8/9] Deploying scripts..."
scp "$SCRIPT_DIR"/scripts/*.py "$SERVER:~/.f1crew/scripts/mas/" 2>/dev/null || true
scp "$SCRIPT_DIR"/scripts/*.sh "$SERVER:~/.f1crew/scripts/mas/" 2>/dev/null || true

# 9. Systemd service (conditional daemon-reload — avoids cascade restarts)
echo "[9/9] Deploying systemd service..."
LOCAL_HASH=$(md5sum "$SCRIPT_DIR/systemd/mas.service" 2>/dev/null | cut -d' ' -f1)
REMOTE_HASH=$(ssh "$SERVER" 'md5sum ~/.config/systemd/user/mas.service 2>/dev/null | cut -d" " -f1')
if [ "$LOCAL_HASH" != "$REMOTE_HASH" ]; then
    echo "  Service file changed — copying + daemon-reload"
    scp "$SCRIPT_DIR/systemd/mas.service" "$SERVER:~/.config/systemd/user/mas.service"
    ssh "$SERVER" 'systemctl --user daemon-reload'
else
    echo "  Service file unchanged — skipping daemon-reload"
fi

echo ""
echo "=== Deploy complete ==="
echo "Restart: ssh $SERVER 'systemctl --user restart mas'"
echo "Health:  ssh $SERVER 'curl -s http://localhost:7720/health | python3 -m json.tool'"
