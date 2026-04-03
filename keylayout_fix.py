#!/usr/bin/env python3
"""
Keyboard Layout Auto-Fix Tool v2.0
Detects and corrects text typed in the wrong keyboard layout.
Supports: Hebrew, Russian, Arabic ↔ English

Hotkey:     Cmd+Shift+Z — select wrong text, press hotkey, fixed!
Auto-detect: Fixes wrong-layout words automatically as you type.
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
from pynput import keyboard

from layouts import LAYOUTS
from config import load_config, save_config
from autodetect import AutoDetector
import launcher

# Path to the bell sound
SOUND_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sounds', 'bell.aiff')


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
        # Use the first enabled language as default target
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
    """Called when the hotkey is pressed."""
    ctrl = keyboard.Controller()

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

    print("=" * 55)
    print("  Keyboard Layout Fix Tool v2.0")
    print(f"  Hotkey: Cmd+Shift+Z")
    print(f"  Languages: {lang_list}")
    print(f"  Auto-detect: {'ON' if config['auto_detect'] else 'OFF'}")
    print(f"  Sound: {'ON' if config['sound_enabled'] else 'OFF'}")
    print("=" * 55)
    print()
    print("  NOTE: Make sure Terminal/Python has Accessibility")
    print("  permission in System Settings → Privacy & Security")
    print()

    # Auto-detect mode
    auto_detector = None
    if config.get('auto_detect', True):
        def on_auto_fix(original, converted):
            print(f"  [auto] '{original}' → '{converted}'")
            if config.get('sound_enabled', True):
                play_sound()

        auto_detector = AutoDetector(
            enabled_languages=config['languages'],
            on_fix_callback=on_auto_fix
        )
        auto_detector.start()
        print("  Auto-detect is running.")

    # Hotkey listener
    print("  Listening for Cmd+Shift+Z... (Ctrl+C to quit)")
    print()

    hotkey = keyboard.GlobalHotKeys({
        '<cmd>+<shift>+z': lambda: on_hotkey(config)
    })
    hotkey.start()

    try:
        hotkey.join()
    except KeyboardInterrupt:
        print("\n  Stopped.")
        if auto_detector:
            auto_detector.stop()


if __name__ == '__main__':
    main()
