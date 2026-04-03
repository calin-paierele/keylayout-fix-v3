"""Configuration management for Keyboard Layout Fix."""

import json
import os

CONFIG_DIR = os.path.expanduser('~/.keylayout-fix')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')

DEFAULTS = {
    'sound_enabled': True,
    'auto_detect': False,
    'hotkey': 'cmd+shift+z',
    'languages': ['hebrew', 'russian', 'arabic'],
}


def load_config():
    """Load config from file, creating defaults if needed."""
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULTS)
        return DEFAULTS.copy()

    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)

    # Merge with defaults for any missing keys
    for key, value in DEFAULTS.items():
        if key not in config:
            config[key] = value

    return config


def save_config(config):
    """Save config to file."""
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
