from PyQt6.QtWidgets import QPlainTextEdit
from PyQt6.QtGui import QKeyEvent, QColor, QTextCharFormat, QBrush
from PyQt6.QtCore import Qt, pyqtSignal


class CustomPlainTextEdit(QPlainTextEdit):
    submit = pyqtSignal()

    def __init__(self, submit_callback, parent=None):
        super().__init__(parent)
        self.submit.connect(submit_callback)
        self.model_info = "No model active"
        self.updateStyleSheet()

    def updateStyleSheet(self):
        """Update the stylesheet with enhanced placeholder styling"""
        self.setStyleSheet(
            """
            QPlainTextEdit {
                border: none;
                border-radius: 20px;
                padding: 10px 15px;
            }
            QPlainTextEdit[placeholderText]::placeholder {
                color: #e0e0e0;
                text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.7);
            }
            """
        )

    def keyPressEvent(self, event: QKeyEvent):
        if (
            event.key() == Qt.Key.Key_Return
            and not event.modifiers() & Qt.KeyboardModifier.ShiftModifier
        ):
            self.submit.emit()
        else:
            super().keyPressEvent(event)

    def set_model_info(self, model_info):
        """Set the model info text to display in the input box"""
        self.model_info = model_info
        self.update_placeholder()

    def update_placeholder(self):
        """Update the placeholder text with model info"""
        model_part = f"[{self.model_info}]"
        placeholder = f"Ask me anything... {model_part}"
        self.setPlaceholderText(placeholder)
