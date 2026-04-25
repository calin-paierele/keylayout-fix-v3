# TypeFix — Keyboard Layout Fixer for macOS

Typed in the wrong language? Select the text, press a hotkey — fixed instantly.

**Default:** English ↔ Hebrew (Russian and Arabic available in settings)

---

## How it works

1. You type something with the wrong keyboard layout active
2. Select the garbled text
3. Press `Cmd+Shift+X` (or triple-tap Caps Lock)
4. Text is converted and replaced in place

---

## Setup

```bash
git clone https://github.com/calin-paierele/keylayout-fix-v3.git
cd keylayout-fix-v3
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Start the daemon:**
```bash
python3 keylayout_fix.py
```

**Start on every login (recommended):**
```bash
python3 keylayout_fix.py --install
```

---

## Settings GUI

Open **TypeFix.app** (or run `python3 gui.py`) to change:

- **Languages** — Hebrew, Russian, Arabic (English always on)
- **Shortcut** — Record any key combo
- **Run on startup** — Toggle LaunchAgent on/off
- **Sound feedback** — Toggle bell sound on fix

---

## macOS Permissions

Required: **System Settings → Privacy & Security → Accessibility** → enable Terminal or Python

---

## Examples

| Typed (wrong layout) | Fixed |
|----------------------|-------|
| `akuo` | `שלום` |
| `שדגכע` | `asdfg` |
| `ghbdtn` | `привет` |

---

## Requirements

- macOS 12+
- Python 3
- `pynput`, `customtkinter`, `pyobjc-framework-Quartz`, `pyobjc-framework-AppKit`

## Technical note

Uses `Quartz.CGEventTap` (not `pynput.Listener`) for keyboard monitoring — required for compatibility with macOS 26+ which enforces that Text Services Manager APIs run on the main thread.
