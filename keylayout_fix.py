#!/usr/bin/env python3
"""
Keyboard Layout Auto-Fix Tool v2.0
Detects and corrects text typed in the wrong keyboard layout.
Supports: Hebrew, Russian, Arabic ↔ English

Hotkey:     Cmd+Shift+X — select wrong text, press hotkey, fixed!
Triple-tap: Caps Lock × 3 — same action
Sound:       Plays a bell when text is fixed (toggle in config).

Usage:
    python keylayout_fix.py              # Run normally
    python keylayout_fix.py --install    # Start on login
    python keylayout_fix.py --uninstall  # Remove from login
"""

import os
import sys
import subprocess
import time
import threading

import Quartz
import AppKit
from pynput import keyboard

from layouts import LAYOUTS
from config import load_config, save_config
import launcher

# Path to the bell sound
SOUND_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sounds', 'bell.aiff')

# Physical keycode → character mapping (layout-independent)
KEYCODES = {
    0: 'a', 1: 's', 2: 'd', 3: 'f', 4: 'h', 5: 'g', 6: 'z', 7: 'x',
    8: 'c', 9: 'v', 11: 'b', 12: 'q', 13: 'w', 14: 'e', 15: 'r',
    16: 'y', 17: 't', 18: '1', 19: '2', 20: '3', 21: '4', 22: '6',
    23: '5', 24: '=', 25: '9', 26: '7', 27: '-', 28: '8', 29: '0',
    30: ']', 31: 'o', 32: 'u', 33: '[', 34: 'i', 35: 'p', 37: 'l',
    38: 'j', 39: "'", 40: 'k', 41: ';', 42: '\\', 43: ',', 44: '/',
    45: 'n', 46: 'm', 47: '.', 50: '`',
}

CAPS_LOCK_KEYCODE = 57


def get_clipboard():
    """Read current clipboard content."""
    result = subprocess.run(['pbpaste'], capture_output=True, text=True)
    return result.stdout


def set_clipboard(text):
    """Write text to clipboard."""
    process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
    process.communicate(text.encode('utf-8'))


def play_sound():
    """Play the bell sound asynchronously."""
    if os.path.exists(SOUND_PATH):
        subprocess.Popen(['afplay', SOUND_PATH],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def detect_language(text, enabled_languages):
    """Detect which language the text is in."""
    counts = {'english': 0}
    for lang_name in enabled_languages:
        if lang_name in LAYOUTS:
            counts[lang_name] = 0

    for ch in text:
        if ch.isascii() and ch.isalpha():
            counts['english'] += 1
        else:
            for lang_name in enabled_languages:
                if lang_name in LAYOUTS:
                    lo, hi = LAYOUTS[lang_name]['range']
                    if lo <= ch <= hi:
                        counts[lang_name] += 1
                        break

    best = max(counts, key=counts.get)
    if counts[best] == 0:
        return 'unknown'
    return best


def convert_text(text, enabled_languages):
    """Convert text between keyboard layouts."""
    lang = detect_language(text, enabled_languages)
    if lang == 'unknown':
        return None

    if lang == 'english':
        # English text → try to find which foreign layout it maps to
        best_lang = None
        best_score = 0
        for lang_name in enabled_languages:
            if lang_name not in LAYOUTS:
                continue
            mapping = LAYOUTS[lang_name]['from_en']
            lo, hi = LAYOUTS[lang_name]['range']
            mapped = ''.join(mapping.get(ch, ch) for ch in text)
            score = sum(1 for ch in mapped if lo <= ch <= hi)
            if score > best_score:
                best_score = score
                best_lang = lang_name
        if best_lang and best_score > 0:
            mapping = LAYOUTS[best_lang]['from_en']
            return ''.join(mapping.get(ch, ch) for ch in text)
        return None
    else:
        # Foreign text → English
        if lang in LAYOUTS:
            mapping = LAYOUTS[lang]['to_en']
            return ''.join(mapping.get(ch, ch) for ch in text)
        return None


def on_hotkey(config):
    """Called when the hotkey is pressed. Runs in a background thread."""
    ctrl = keyboard.Controller()

    # Release all modifiers — hotkey keys are still physically held when this runs
    for mod in [keyboard.Key.cmd, keyboard.Key.shift, keyboard.Key.ctrl, keyboard.Key.alt]:
        try:
            ctrl.release(mod)
        except Exception:
            pass
    time.sleep(0.08)

    # Save current clipboard
    old_clipboard = get_clipboard()

    # Copy selected text (Cmd+C)
    ctrl.press(keyboard.Key.cmd)
    ctrl.press('c')
    ctrl.release('c')
    ctrl.release(keyboard.Key.cmd)
    time.sleep(0.15)

    # Read copied text
    selected_text = get_clipboard()
    if not selected_text or selected_text == old_clipboard:
        print("  No text selected or clipboard unchanged.")
        return

    # Convert
    converted = convert_text(selected_text, config['languages'])
    if converted is None:
        print("  Could not determine language, skipping.")
        set_clipboard(old_clipboard)
        return

    print(f"  '{selected_text}' → '{converted}'")

    # Paste converted text
    set_clipboard(converted)
    ctrl.press(keyboard.Key.cmd)
    ctrl.press('v')
    ctrl.release('v')
    ctrl.release(keyboard.Key.cmd)
    time.sleep(0.1)

    # Play sound
    if config.get('sound_enabled', True):
        play_sound()

    # Restore original clipboard
    time.sleep(0.3)
    set_clipboard(old_clipboard)


def parse_hotkey(hotkey_str):
    """Parse 'cmd+shift+x' into (frozenset_of_mods, key_char)."""
    mods_set = {'cmd', 'shift', 'ctrl', 'alt'}
    parts = hotkey_str.lower().split('+')
    mods = frozenset(p for p in parts if p in mods_set)
    keys = [p for p in parts if p not in mods_set]
    return mods, keys[0] if keys else ''


def flags_to_mods(flags):
    """Convert CGEvent flags to a frozenset of modifier names."""
    mods = set()
    if flags & Quartz.kCGEventFlagMaskCommand:
        mods.add('cmd')
    if flags & Quartz.kCGEventFlagMaskShift:
        mods.add('shift')
    if flags & Quartz.kCGEventFlagMaskControl:
        mods.add('ctrl')
    if flags & Quartz.kCGEventFlagMaskAlternate:
        mods.add('alt')
    return frozenset(mods)


def run_event_loop(config):
    """
    Install a CGEventTap and run the main CFRunLoop.
    This MUST be called from the main thread. Blocking.
    """
    hotkey_str = config.get('hotkey', 'cmd+shift+x')
    hotkey_mods, hotkey_key = parse_hotkey(hotkey_str)

    caps_tap_times = []
    TAP_WINDOW = 0.6  # seconds — 3 taps must land within this window
    # Track last caps-lock flags state to detect key-down vs key-up
    last_caps_flags = [0]

    def handler(proxy, event_type, event, refcon):
        keycode = Quartz.CGEventGetIntegerValueField(
            event, Quartz.kCGKeyboardEventKeycode)
        flags = Quartz.CGEventGetFlags(event)

        if event_type == Quartz.kCGEventKeyDown:
            # Regular hotkey match — return None to swallow event (no system beep)
            pressed_mods = flags_to_mods(flags)
            pressed_key = KEYCODES.get(keycode, '')
            if pressed_mods == hotkey_mods and pressed_key == hotkey_key:
                threading.Thread(
                    target=on_hotkey, args=(config,), daemon=True).start()
                return None  # consume event, prevents macOS error sound

        elif event_type == Quartz.kCGEventFlagsChanged:
            if keycode == CAPS_LOCK_KEYCODE:
                # kCGEventFlagsChanged fires on both press and release.
                # Caps-lock pressed: the caps-lock bit transitions low→high.
                caps_on = bool(flags & Quartz.kCGEventFlagMaskAlphaShift)
                was_on = bool(last_caps_flags[0] & Quartz.kCGEventFlagMaskAlphaShift)
                last_caps_flags[0] = flags

                # Count only the press edge (was_on=False → caps_on=True OR
                # was_on=True → caps_on=False, depending on toggle behaviour).
                # We count every transition (each physical tap toggles the bit).
                now = time.time()
                caps_tap_times.append(now)
                # Evict old taps outside the window
                while caps_tap_times and now - caps_tap_times[0] > TAP_WINDOW:
                    caps_tap_times.pop(0)
                if len(caps_tap_times) >= 3:
                    caps_tap_times.clear()
                    threading.Thread(
                        target=on_hotkey, args=(config,), daemon=True).start()

        return event  # pass event through unchanged

    mask = (Quartz.CGEventMaskBit(Quartz.kCGEventKeyDown) |
            Quartz.CGEventMaskBit(Quartz.kCGEventFlagsChanged))

    tap = Quartz.CGEventTapCreate(
        Quartz.kCGSessionEventTap,
        Quartz.kCGHeadInsertEventTap,
        Quartz.kCGEventTapOptionDefault,  # active tap — can swallow events
        mask,
        handler,
        None,
    )

    if tap is None:
        print("ERROR: Could not create event tap.")
        print("  Grant Accessibility permission in:")
        print("  System Settings → Privacy & Security → Accessibility")
        sys.exit(1)

    run_loop_source = Quartz.CFMachPortCreateRunLoopSource(None, tap, 0)
    Quartz.CFRunLoopAddSource(
        Quartz.CFRunLoopGetMain(),
        run_loop_source,
        Quartz.kCFRunLoopCommonModes,
    )
    Quartz.CGEventTapEnable(tap, True)

    print("  Listening for hotkey and triple-tap Caps Lock... (Ctrl+C to quit)")
    print()

    # Run the main AppKit/CF run loop — blocking until process exits
    AppKit.NSApplication.sharedApplication()
    AppKit.NSApp.run()


def main():
    # Handle --install / --uninstall
    if '--install' in sys.argv:
        launcher.install()
        return
    if '--uninstall' in sys.argv:
        launcher.uninstall()
        return

    config = load_config()
    lang_list = ', '.join(config['languages'])
    hotkey_str = config.get('hotkey', 'cmd+shift+x')

    print("=" * 55)
    print("  Keyboard Layout Fix Tool v2.0")
    print(f"  Hotkey: {hotkey_str} or triple-tap Caps Lock")
    print(f"  Languages: {lang_list}")
    print(f"  Sound: {'ON' if config['sound_enabled'] else 'OFF'}")
    print("=" * 55)
    print()
    print("  NOTE: Make sure Terminal/Python has Accessibility")
    print("  permission in System Settings → Privacy & Security")
    print()

    # run_event_loop is blocking and must run on the main thread
    run_event_loop(config)


if __name__ == '__main__':
    main()
