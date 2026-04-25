"""macOS Launch Agent manager — start on login."""

import os
import sys
import plistlib

PLIST_NAME = 'com.calin.keylayout-fix.plist'
PLIST_DIR = os.path.expanduser('~/Library/LaunchAgents')
PLIST_PATH = os.path.join(PLIST_DIR, PLIST_NAME)


def get_script_path():
    """Get the absolute path to keylayout_fix.py."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'keylayout_fix.py')


def get_python_path():
    """Get the path to the venv Python."""
    venv_python = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'venv', 'bin', 'python3')
    if os.path.exists(venv_python):
        return venv_python
    return sys.executable


def install():
    """Install the Launch Agent to start on login."""
    os.makedirs(PLIST_DIR, exist_ok=True)

    plist = {
        'Label': 'com.keylayout-fix',
        'ProgramArguments': [get_python_path(), get_script_path()],
        'RunAtLoad': True,
        'KeepAlive': False,
        'StandardOutPath': os.path.expanduser('~/.keylayout-fix/stdout.log'),
        'StandardErrorPath': os.path.expanduser('~/.keylayout-fix/stderr.log'),
    }

    with open(PLIST_PATH, 'wb') as f:
        plistlib.dump(plist, f)

    os.system(f'launchctl load {PLIST_PATH}')
    print(f"  Installed! Will start on login.")
    print(f"  Plist: {PLIST_PATH}")


def uninstall():
    """Remove the Launch Agent."""
    if os.path.exists(PLIST_PATH):
        os.system(f'launchctl unload {PLIST_PATH}')
        os.remove(PLIST_PATH)
        print("  Uninstalled. Will no longer start on login.")
    else:
        print("  Not installed.")


def is_installed():
    """Check if the Launch Agent is installed."""
    return os.path.exists(PLIST_PATH)
