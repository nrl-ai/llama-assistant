import sys
import multiprocessing
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from llama_assistant.llama_assistant_app import LlamaAssistant


def main():
    # Enable high DPI scaling (handled automatically in PyQt6)
    app = QApplication(sys.argv)
    ex = LlamaAssistant()
    ex.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
