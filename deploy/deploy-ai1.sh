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
echo "[1/5] Deploying Python code..."
scp "$SCRIPT_DIR"/mas/*.py "$SERVER:~/.f1crew/scripts/mas/"

# 2. Runtime config → server scripts
echo "[2/5] Deploying runtime config..."
scp "$SCRIPT_DIR/config/mas-config.json" "$SERVER:~/.f1crew/shared/mas-config.json"

# 3. Characters → server data
echo "[3/5] Deploying characters..."
rsync -az --delete "$SCRIPT_DIR/characters/" "$SERVER:~/projects/mayacrew-f1crew/f1-mas/characters/"

# 4. Config MDs → server data
echo "[4/5] Deploying config files..."
rsync -az "$SCRIPT_DIR/config/persona-registry.md" \
          "$SCRIPT_DIR/config/selection-rules.md" \
          "$SCRIPT_DIR/config/task-templates.md" \
          "$SERVER:~/projects/mayacrew-f1crew/f1-mas/config/"

# 5. Systemd service
echo "[5/5] Deploying systemd service..."
scp "$SCRIPT_DIR/systemd/mas.service" "$SERVER:~/.config/systemd/user/mas.service"
ssh "$SERVER" 'systemctl --user daemon-reload'

echo ""
echo "=== Deploy complete ==="
echo "Restart: ssh $SERVER 'systemctl --user restart mas'"
echo "Health:  ssh $SERVER 'curl -s http://localhost:7720/health | python3 -m json.tool'"
