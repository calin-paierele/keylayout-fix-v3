#!/usr/bin/env python3
"""Settings GUI for Keyboard Layout Fix."""

import os
import subprocess
import threading
import customtkinter as ctk
from config import load_config, save_config

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON = os.path.join(PROJECT_DIR, 'venv', 'bin', 'python3')
PLIST = os.path.expanduser('~/Library/LaunchAgents/com.calin.keylayout-fix.plist')

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

MODIFIER_ORDER = ['cmd', 'ctrl', 'shift', 'alt']


def hotkey_display(hotkey_str):
    symbols = {'cmd': '⌘', 'shift': '⇧', 'ctrl': '⌃', 'alt': '⌥'}
    parts = hotkey_str.split('+')
    return ''.join(symbols.get(p, p.upper()) for p in parts)


class SettingsApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("KeyLayout Fix")
        self.geometry("340x420")
        self.resizable(False, False)

        self.cfg = load_config()
        self._recording = False
        self._pressed_keys = []

        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="KeyLayout Fix", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(16, 8))

        frame = ctk.CTkFrame(self, corner_radius=12)
        frame.pack(fill="both", expand=True, padx=16, pady=(0, 6))

        # --- Languages ---
        ctk.CTkLabel(frame, text="Languages", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=14, pady=(12, 2))
        ctk.CTkLabel(frame, text="✓  English  (always on)", text_color="gray50", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20, pady=(0, 2))

        self.heb_var = ctk.BooleanVar(value='hebrew' in self.cfg['languages'])
        self.rus_var = ctk.BooleanVar(value='russian' in self.cfg['languages'])
        self.ara_var = ctk.BooleanVar(value='arabic' in self.cfg['languages'])

        ctk.CTkCheckBox(frame, text="Hebrew", variable=self.heb_var, font=ctk.CTkFont(size=13)).pack(anchor="w", padx=20, pady=2)
        ctk.CTkCheckBox(frame, text="Russian", variable=self.rus_var, font=ctk.CTkFont(size=13)).pack(anchor="w", padx=20, pady=2)
        ctk.CTkCheckBox(frame, text="Arabic", variable=self.ara_var, font=ctk.CTkFont(size=13)).pack(anchor="w", padx=20, pady=(2, 8))

        ctk.CTkFrame(frame, height=1, fg_color="gray30").pack(fill="x", padx=12, pady=2)

        # --- Shortcut ---
        ctk.CTkLabel(frame, text="Shortcut", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=14, pady=(8, 4))

        row = ctk.CTkFrame(frame, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=(0, 8))

        self.shortcut_lbl = ctk.CTkLabel(
            row,
            text=hotkey_display(self.cfg.get('hotkey', 'cmd+shift+x')),
            font=ctk.CTkFont(size=16),
            width=140, anchor="w"
        )
        self.shortcut_lbl.pack(side="left")

        self.record_btn = ctk.CTkButton(row, text="Record", width=90, height=30, command=self._start_record)
        self.record_btn.pack(side="right")

        ctk.CTkFrame(frame, height=1, fg_color="gray30").pack(fill="x", padx=12, pady=2)

        # --- Toggles ---
        self.startup_var = ctk.BooleanVar(value=os.path.exists(PLIST))
        self.sound_var = ctk.BooleanVar(value=self.cfg.get('sound_enabled', True))

        self._toggle_row(frame, "Run on startup", self.startup_var)
        self._toggle_row(frame, "Sound feedback", self.sound_var)

        # --- Save ---
        self.save_btn = ctk.CTkButton(self, text="Save", height=38, font=ctk.CTkFont(size=14, weight="bold"), command=self._save)
        self.save_btn.pack(pady=10, padx=16, fill="x")

    def _toggle_row(self, parent, label, var):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=5)
        ctk.CTkLabel(row, text=label, font=ctk.CTkFont(size=13)).pack(side="left")
        ctk.CTkSwitch(row, text="", variable=var, width=44).pack(side="right")

    # --- Shortcut recording (tkinter key bindings — no pynput) ---

    def _start_record(self):
        if self._recording:
            return
        self._recording = True
        self._pressed_keys = []
        self.record_btn.configure(text="Press keys…", fg_color="#c0392b", hover_color="#922b21")
        self.shortcut_lbl.configure(text="…")
        self.focus_force()
        self.bind('<KeyPress>', self._on_key_press)
        self.bind('<KeyRelease>', self._on_key_release)

    def _on_key_press(self, event):
        if not self._recording:
            return
        name = self._tk_key_name(event)
        if name and name not in self._pressed_keys:
            self._pressed_keys.append(name)

    def _on_key_release(self, event):
        if not self._recording:
            return
        non_mods = [k for k in self._pressed_keys if k not in MODIFIER_ORDER]
        if non_mods:
            self._stop_record()

    def _tk_key_name(self, event):
        sym = event.keysym.lower()
        m = {
            'meta_l': 'cmd', 'meta_r': 'cmd', 'command': 'cmd',
            'shift_l': 'shift', 'shift_r': 'shift',
            'control_l': 'ctrl', 'control_r': 'ctrl',
            'alt_l': 'alt', 'alt_r': 'alt', 'option': 'alt',
        }
        return m.get(sym, sym if len(sym) == 1 else None)

    def _stop_record(self):
        self._recording = False
        self.unbind('<KeyPress>')
        self.unbind('<KeyRelease>')
        mods = [k for k in MODIFIER_ORDER if k in self._pressed_keys]
        others = [k for k in self._pressed_keys if k not in MODIFIER_ORDER]
        combo = '+'.join(mods + others)
        self.cfg['hotkey'] = combo
        self.shortcut_lbl.configure(text=hotkey_display(combo))
        self.record_btn.configure(text="Record", fg_color=["#3B8ED0", "#1F6AA5"], hover_color=["#36719F", "#144870"])

    # --- Save ---

    def _save(self):
        langs = []
        if self.heb_var.get():
            langs.append('hebrew')
        if self.rus_var.get():
            langs.append('russian')
        if self.ara_var.get():
            langs.append('arabic')
        if not langs:
            langs = ['hebrew']
            self.heb_var.set(True)

        self.cfg['languages'] = langs
        self.cfg['sound_enabled'] = self.sound_var.get()
        save_config(self.cfg)

        self._handle_startup(self.startup_var.get())
        threading.Thread(target=self._restart_listener, daemon=True).start()

        self.save_btn.configure(text="Saved ✓", fg_color="#27ae60", hover_color="#1e8449")
        self.after(1800, lambda: self.save_btn.configure(text="Save", fg_color=["#3B8ED0", "#1F6AA5"], hover_color=["#36719F", "#144870"]))

    def _handle_startup(self, enable):
        if enable and not os.path.exists(PLIST):
            subprocess.run(['launchctl', 'load', PLIST], capture_output=True)
        elif not enable and os.path.exists(PLIST):
            subprocess.run(['launchctl', 'unload', PLIST], capture_output=True)

    def _restart_listener(self):
        subprocess.run(['pkill', '-f', 'keylayout_fix.py'], capture_output=True)


if __name__ == '__main__':
    app = SettingsApp()
    app.mainloop()
