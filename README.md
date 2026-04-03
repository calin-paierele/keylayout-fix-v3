# Keyboard Layout Auto-Fix Tool v2.0

Instantly fix text typed in the wrong keyboard layout.

**Supports:** Hebrew, Russian, Arabic <-> English

## Features

- **Hotkey Fix** — Select wrong text, press `Cmd+Shift+Z`, fixed!
- **Auto-Detect** — Automatically fixes wrong-layout words as you type
- **Multi-Language** — Hebrew, Russian, Arabic (easy to add more)
- **Sound Feedback** — Pleasant bell ring when text is fixed (can be turned off)
- **Start on Login** — Runs automatically when your Mac boots

## Setup

```bash
git clone https://github.com/calin-paierele/keylayout-fix.git
cd keylayout-fix
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
source venv/bin/activate
python3 keylayout_fix.py
```

### Hotkey Mode
1. Type something in the wrong layout
2. Select the text
3. Press **Cmd+Shift+Z**
4. Text is converted in place + bell sound

### Auto-Detect Mode
Just type — when you finish a word (press space), the tool checks if it's in the wrong layout and fixes it automatically.

## Start on Login

```bash
python3 keylayout_fix.py --install     # Enable auto-start
python3 keylayout_fix.py --uninstall   # Disable auto-start
```

## Configuration

Settings are stored in `~/.keylayout-fix/config.json`:

```json
{
  "sound_enabled": true,
  "auto_detect": true,
  "hotkey": "cmd+shift+z",
  "languages": ["hebrew", "russian", "arabic"]
}
```

Edit this file to:
- Turn sound on/off
- Enable/disable auto-detect
- Choose which languages to support

## macOS Permissions

First time running, grant **Accessibility** permission:
**System Settings → Privacy & Security → Accessibility** → enable Terminal (or your Python app)

## Examples

| Input (wrong layout) | Output (fixed) |
|----------------------|----------------|
| שדגכע | asdfg |
| akuo | שלום |
| ghbdtn | привет |
| привет | privet |

## Requirements

- macOS
- Python 3
- `pynput`
