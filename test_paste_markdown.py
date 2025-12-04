#!/usr/bin/env python3
"""
Test script to verify rich text paste conversion to markdown
"""
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from llama_assistant.custom_plaintext_editor import CustomPlainTextEdit
from llama_assistant.setting_dialog import MarkdownTextEdit


class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Rich Text Paste to Markdown")
        self.setGeometry(100, 100, 600, 400)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Test CustomPlainTextEdit
        layout.addWidget(QLabel("CustomPlainTextEdit (Main Chat Input):"))
        self.plain_text_edit = CustomPlainTextEdit(lambda: None)
        self.plain_text_edit.setPlaceholderText("Paste rich text here...")
        layout.addWidget(self.plain_text_edit)

        # Test MarkdownTextEdit
        layout.addWidget(QLabel("\nMarkdownTextEdit (Settings Dialog):"))
        self.markdown_text_edit = MarkdownTextEdit()
        self.markdown_text_edit.setPlaceholderText("Paste rich text here...")
        layout.addWidget(self.markdown_text_edit)

        layout.addWidget(
            QLabel(
                "\nInstructions: Copy formatted text from a webpage or document and paste it above."
            )
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())
