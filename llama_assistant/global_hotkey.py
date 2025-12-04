from PyQt6.QtCore import QObject, pyqtSignal
from pynput import keyboard

from llama_assistant.config import DEFAULT_LAUNCH_SHORTCUT


class GlobalHotkey(QObject):
    activated = pyqtSignal()

    def __init__(self, hotkey):
        super().__init__()
        try:
            self.hotkey = keyboard.HotKey(keyboard.HotKey.parse(hotkey), self.on_activate)
        except ValueError:
            self.hotkey = keyboard.HotKey(
                keyboard.HotKey.parse(DEFAULT_LAUNCH_SHORTCUT), self.on_activate
            )
        self.listener = keyboard.Listener(
            on_press=self.for_canonical(self.hotkey.press),
            on_release=self.for_canonical(self.hotkey.release),
        )
        self.listener.start()

    def on_activate(self):
        self.activated.emit()

    def for_canonical(self, f):
        return lambda k: f(self.listener.canonical(k))

    def stop(self):
        if self.listener:
            self.listener.stop()
