# TypeFix — Design Document
**Date:** 2026-04-25  
**Status:** Shipped

## What It Is

TypeFix is a macOS utility that fixes text typed in the wrong keyboard language. You type something with the wrong layout active (e.g. typing English keys while Hebrew is selected), select the garbled text, press a hotkey — it converts it instantly and replaces the selection.

## Architecture

Two independent processes:

| Process | File | How it runs |
|---|---|---|
| Background daemon | `keylayout_fix.py` | LaunchAgent — starts on login, always on |
| Settings GUI | `gui.py` | `TypeFix.app` in /Applications — open on demand |

They communicate only through `~/.keylayout-fix/config.json`. No IPC, no sockets.

## Keyboard Monitoring

**Problem solved:** `pynput.keyboard.Listener` and `GlobalHotKeys` call `TSMGetInputSourceProperty` from a background thread. macOS 26 added a hard assertion this must be on the main thread → `EXC_BREAKPOINT` crash.

**Fix:** Replaced pynput listening with `Quartz.CGEventTapCreate` using `kCGEventTapOptionDefault` (active tap, not listen-only). The tap runs on the main thread via `CFRunLoop` / `NSApp.run()`. Events are consumed (`return None`) on hotkey match to prevent the macOS error beep.

`pynput.keyboard.Controller` is kept for simulating Cmd+C / Cmd+V — it only sends events and doesn't listen, so it doesn't trigger the crash.

## Hotkey Flow

1. User selects wrong-language text
2. Presses hotkey (`Cmd+Shift+X` default, or triple-tap Caps Lock)
3. CGEventTap fires on main thread → spawns background thread for the action
4. Background thread: release modifiers → Cmd+C → read clipboard → convert → Cmd+V → restore clipboard
5. Modifier release step is critical: without it, Shift still held → Cmd+Shift+C instead of Cmd+C → selection lost → text appended instead of replaced

## Language Conversion

Bidirectional mapping per layout (`layouts/hebrew.py`, `layouts/russian.py`, `layouts/arabic.py`):
- Detect language by character range
- English → Foreign: map each char through `from_en` dict
- Foreign → English: map through `to_en` dict

Default: English ↔ Hebrew only.

## Settings GUI

Built with `customtkinter`. No `pynput` — shortcut recording uses tkinter's native `<KeyPress>/<KeyRelease>` bindings which run on the main thread.

Settings:
- Languages (checkboxes: Hebrew, Russian, Arabic; English always on)
- Shortcut (record button → press keys → saved)
- Run on startup (toggle → launchctl load/unload)
- Sound feedback (toggle)

Save → writes config.json → kills daemon → LaunchAgent auto-restarts it with new config.

## Files

```
keylayout-fix-v2/
  keylayout_fix.py     — daemon: CGEventTap + conversion
  gui.py               — settings window (customtkinter)
  config.py            — load/save ~/.keylayout-fix/config.json
  autodetect.py        — auto-detect mode (disabled by default)
  launcher.py          — LaunchAgent plist install/uninstall
  layouts/             — hebrew.py, russian.py, arabic.py
  sounds/bell.aiff     — played on successful fix
  venv/                — Python dependencies

/Applications/TypeFix.app          — GUI launcher
~/Library/LaunchAgents/com.calin.keylayout-fix.plist  — daemon autostart
~/.keylayout-fix/config.json       — user settings
```

## Known Constraints

- Requires Accessibility permission (System Settings → Privacy & Security → Accessibility)
- `CGEventTapOptionDefault` requires the process to have Input Monitoring permission on some macOS versions
- Caps Lock triple-tap uses `kCGEventFlagsChanged` (not `kCGEventKeyDown`) since macOS doesn't send standard key events for Caps Lock
