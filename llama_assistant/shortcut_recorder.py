import sys

from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent, QKeySequence


def is_macos():
    return sys.platform == "darwin"


class ShortcutRecorder(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setPlaceholderText("Press a key combination")
        self.recorded_shortcut = None

        # Set the style sheet for rounded corners
        self.setStyleSheet(
            """
            QLineEdit {
                border: 1px solid #a0a0a0;
                border-radius: 7.5px;
                padding: 2px 5px;
                background-color: #fefefe;
                color: #333333;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """
        )

    def keyPressEvent(self, event: QKeyEvent):
        modifiers = []
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if is_macos():
                modifiers.append("<cmd>")
            else:
                modifiers.append("<ctrl>")
        if event.modifiers() & Qt.KeyboardModifier.AltModifier:
            modifiers.append("<alt>")
        if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            modifiers.append("<shift>")
        if event.modifiers() & Qt.KeyboardModifier.MetaModifier:
            if is_macos():
                modifiers.append("<ctrl>")
            else:
                modifiers.append("<cmd>")

        key = event.key()
        if key not in (
            Qt.Key.Key_Control,
            Qt.Key.Key_Shift,
            Qt.Key.Key_Alt,
            Qt.Key.Key_Meta,
        ):
            qt_key = QKeySequence(key).toString()
            pynput_key = self.qt_to_pynput_key(qt_key)
            key_string = "+".join(modifiers + [pynput_key])
            self.setText(key_string)
            self.recorded_shortcut = key_string

        event.accept()

    def qt_to_pynput_key(self, qt_key):
        # Map Qt key names to pynput key names
        key_map = {
            "PgUp": "<page_up>",
            "PgDown": "<page_down>",
            "Left": "<left>",
            "Right": "<right>",
            "Up": "<up>",
            "Down": "<down>",
            "Enter": "<enter>",
            "Return": "<enter>",
            "Ins": "<insert>",
            "Del": "<delete>",
            "Home": "<home>",
            "End": "<end>",
            "Space": "<space>",
            "Tab": "<tab>",
            "Esc": "<esc>",
            "Backspace": "<backspace>",
            # Function keys
            "F1": "<f1>",
            "F2": "<f2>",
            "F3": "<f3>",
            "F4": "<f4>",
            "F5": "<f5>",
            "F6": "<f6>",
            "F7": "<f7>",
            "F8": "<f8>",
            "F9": "<f9>",
            "F10": "<f10>",
            "F11": "<f11>",
            "F12": "<f12>",
        }
        return key_map.get(qt_key, qt_key.lower())

    def get_pynput_hotkey(self):
        return self.recorded_shortcut
