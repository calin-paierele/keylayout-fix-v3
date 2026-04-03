"""Auto-detect wrong keyboard layout and fix in real-time."""

import time
import subprocess
from pynput import keyboard
from layouts import LAYOUTS


class AutoDetector:
    """Monitors keystrokes and auto-fixes wrong layout words."""

    def __init__(self, enabled_languages, on_fix_callback=None):
        self.enabled_languages = enabled_languages
        self.on_fix_callback = on_fix_callback
        self.word_buffer = []
        self.listener = None
        self.ctrl = keyboard.Controller()
        # Characters that end a word
        self.word_boundaries = {' ', '\r', '\n', '\t'}

    def _is_wrong_layout(self, word):
        """Check if word looks like it was typed in the wrong layout.

        Returns (from_lang, to_lang) if wrong layout detected, None otherwise.
        """
        if len(word) < 2:
            return None

        for lang_name in self.enabled_languages:
            if lang_name not in LAYOUTS:
                continue
            layout = LAYOUTS[lang_name]
            lo, hi = layout['range']

            # Check if word is in this foreign script → should be English
            foreign_chars = sum(1 for ch in word if lo <= ch <= hi)
            if foreign_chars > len(word) * 0.6:
                # Check if it maps to valid-looking English
                mapped = ''.join(layout['to_en'].get(ch, ch) for ch in word)
                ascii_chars = sum(1 for ch in mapped if ch.isascii() and ch.isalpha())
                if ascii_chars > len(mapped) * 0.6:
                    return (lang_name, 'english')

            # Check if word is English ASCII → should be this foreign language
            ascii_chars = sum(1 for ch in word if ch.isascii() and ch.isalpha())
            if ascii_chars > len(word) * 0.6:
                mapped = ''.join(layout['from_en'].get(ch, ch) for ch in word)
                foreign_mapped = sum(1 for ch in mapped if lo <= ch <= hi)
                if foreign_mapped > len(mapped) * 0.6:
                    # This could be any language — don't auto-fix English
                    # Only fix if we have strong signal (all chars map)
                    if foreign_mapped == len(word):
                        return ('english', lang_name)

        return None

    def _fix_last_word(self, word):
        """Select and replace the last typed word."""
        # Select the last word: press Shift+Cmd+Left to select word
        # First, we need to go back by the word length + 1 (for the space)
        # Use Option+Shift+Left to select the previous word on macOS
        self.ctrl.press(keyboard.Key.shift)
        self.ctrl.press(keyboard.Key.alt)
        self.ctrl.press(keyboard.Key.left)
        self.ctrl.release(keyboard.Key.left)
        self.ctrl.release(keyboard.Key.alt)
        self.ctrl.release(keyboard.Key.shift)
        time.sleep(0.05)

        # Copy selected text
        old_clipboard = self._get_clipboard()
        self.ctrl.press(keyboard.Key.cmd)
        self.ctrl.press('c')
        self.ctrl.release('c')
        self.ctrl.release(keyboard.Key.cmd)
        time.sleep(0.15)

        selected = self._get_clipboard()
        if not selected or selected == old_clipboard:
            return False

        # Determine conversion direction and convert
        result = self._is_wrong_layout(selected.strip())
        if not result:
            # Deselect by pressing right arrow
            self.ctrl.press(keyboard.Key.right)
            self.ctrl.release(keyboard.Key.right)
            self._set_clipboard(old_clipboard)
            return False

        from_lang, to_lang = result
        converted = self._convert(selected.strip(), from_lang, to_lang)
        if not converted:
            self.ctrl.press(keyboard.Key.right)
            self.ctrl.release(keyboard.Key.right)
            self._set_clipboard(old_clipboard)
            return False

        # Paste the fix
        self._set_clipboard(converted + ' ')
        self.ctrl.press(keyboard.Key.cmd)
        self.ctrl.press('v')
        self.ctrl.release('v')
        self.ctrl.release(keyboard.Key.cmd)
        time.sleep(0.1)

        # Restore clipboard
        time.sleep(0.2)
        self._set_clipboard(old_clipboard)

        if self.on_fix_callback:
            self.on_fix_callback(selected.strip(), converted)

        return True

    def _convert(self, text, from_lang, to_lang):
        """Convert text between layouts."""
        if from_lang == 'english':
            layout = LAYOUTS.get(to_lang)
            if not layout:
                return None
            return ''.join(layout['from_en'].get(ch, ch) for ch in text)
        else:
            layout = LAYOUTS.get(from_lang)
            if not layout:
                return None
            return ''.join(layout['to_en'].get(ch, ch) for ch in text)

    def _get_clipboard(self):
        result = subprocess.run(['pbpaste'], capture_output=True, text=True)
        return result.stdout

    def _set_clipboard(self, text):
        process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
        process.communicate(text.encode('utf-8'))

    def _on_key_press(self, key):
        """Handle each keypress."""
        try:
            char = key.char
            if char:
                self.word_buffer.append(char)
        except AttributeError:
            # Special key
            if key == keyboard.Key.space or key == keyboard.Key.enter:
                word = ''.join(self.word_buffer)
                self.word_buffer.clear()
                if len(word) >= 2 and self._is_wrong_layout(word):
                    self._fix_last_word(word)
            elif key == keyboard.Key.backspace:
                if self.word_buffer:
                    self.word_buffer.pop()
            else:
                # Other special keys reset the buffer
                self.word_buffer.clear()

    def start(self):
        """Start listening for keystrokes."""
        self.listener = keyboard.Listener(on_press=self._on_key_press)
        self.listener.start()

    def stop(self):
        """Stop listening."""
        if self.listener:
            self.listener.stop()
