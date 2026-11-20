import json
import os
from pathlib import Path

APP_DIR = Path(os.getenv("APPDATA", str(Path.home()))) / "LOKLauncher"
APP_DIR.mkdir(parents=True, exist_ok=True)

# Use the standard Minecraft directory by default, so existing installations
# (mods, saves, resource packs, shader packs) remain visible to the launcher.
STANDARD_GAME_DIR = Path(os.getenv("APPDATA", str(Path.home()))) / ".minecraft"
GAME_DIR = STANDARD_GAME_DIR
CONFIG_FILE = APP_DIR / "settings.json"

DEFAULTS = {
    "game_dir": str(GAME_DIR),
    "ram_gb": 2,
    "profile": "AUTO",
    "version": "release",
    "loader": "Vanilla",
    "loader_version": "",
    "first_run_setup_done": False
}

def load_config():
    try:
        data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        return {**DEFAULTS, **data}
    except Exception:
        return DEFAULTS.copy()

def save_config(data):
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
