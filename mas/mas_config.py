"""MAS Configuration Loader — hot reload from mas-config.json"""

import json
import os
import threading
import time

from f1common.paths import HOME, F1CREW_ROOT

F1CREW = str(F1CREW_ROOT)
CONFIG_FILE = f"{F1CREW}/shared/mas-config.json"

_DEFAULTS = {
    "port": 7720,
    "anthropic_api_key": "",         # direct API key (sk-ant-api-*)
    "anthropic_api_key_file": "",    # or read from file
    "claude_api_base": "https://api.anthropic.com",
    "xapi_url": "http://localhost:7750",
    "claude_model": "sonnet",
    "synthesis_model": "sonnet",
    "max_agents": 5,
    "agent_timeout_seconds": 120,
    "thread_pool_workers": 5,
    "persona_registry_path": "",  # auto-detected
    "characters_base_dir": "",    # auto-detected
    "selection_rules_path": "",   # auto-detected
    "task_templates_path": "",    # auto-detected
    "state_file": f"{F1CREW}/shared/mas-state.json",
    "slack": {
        "enabled": False,
        "bot_token": "",
        "app_token": "",
        "channel_id": "",
    },
    "constitution": {
        "enabled": True,
        "p0_block": True,
        "p1_refuse": True,
    },
    "metrics_enabled": True,
    "hot_reload_interval": 30,
    "persona_cache_ttl": 300,
    "character_extract_sections": [
        "Quick Reference Card",
        "Quick Reference",
        "Thinking Patterns",
        "Communication Style",
        "AI Interaction Notes",
        "Collaboration Dynamics",
    ],
    "log_level": "info",
}

_config = {}
_config_lock = threading.Lock()
_config_mtime = 0.0


def _find_mas_paths():
    """Auto-detect f1-mas directory paths."""
    candidates = [
        f"{HOME}/F1/f1-mas",
        f"{HOME}/projects/mayacrew-f1crew/f1-mas",
        f"{HOME}/.f1crew/f1-mas",
    ]
    for base in candidates:
        if os.path.isdir(base):
            return {
                "persona_registry_path": f"{base}/config/persona-registry.md",
                "characters_base_dir": f"{base}/characters",
                "selection_rules_path": f"{base}/config/selection-rules.md",
                "task_templates_path": f"{base}/config/task-templates.md",
            }
    return {}


def _deep_merge(base, override):
    """Merge override dict into base dict (1 level deep for nested dicts)."""
    result = dict(base)
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = {**result[k], **v}
        else:
            result[k] = v
    return result


def load_config(force=False):
    """Load config from JSON file, merging with defaults."""
    global _config, _config_mtime

    with _config_lock:
        try:
            mtime = os.path.getmtime(CONFIG_FILE)
            if not force and mtime == _config_mtime and _config:
                return _config
            _config_mtime = mtime
        except OSError:
            if _config:
                return _config

        file_config = {}
        try:
            with open(CONFIG_FILE, "r") as f:
                file_config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            pass

        merged = _deep_merge(_DEFAULTS, file_config)

        # Auto-detect paths if not explicitly set
        if not merged.get("persona_registry_path"):
            auto_paths = _find_mas_paths()
            for k, v in auto_paths.items():
                if not merged.get(k):
                    merged[k] = v

        _config = merged
        return _config


def get(key, default=None):
    """Get a config value by key."""
    cfg = load_config()
    return cfg.get(key, default)


def get_nested(section, key, default=None):
    """Get a nested config value (e.g., slack.bot_token)."""
    cfg = load_config()
    return cfg.get(section, {}).get(key, default)


def _reload_loop():
    """Background thread: reload config on file change."""
    while True:
        time.sleep(get("hot_reload_interval", 30))
        try:
            load_config()
        except Exception:
            pass


def start_hot_reload():
    """Start background config reload thread."""
    t = threading.Thread(target=_reload_loop, daemon=True)
    t.start()


# Load config on import
load_config()
