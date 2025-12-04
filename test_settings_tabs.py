#!/usr/bin/env python3
"""
Test script to verify the tabbed settings dialog structure.
"""

import sys
from PyQt6.QtWidgets import QApplication
from llama_assistant.setting_dialog import SettingsDialog


def main():
    app = QApplication(sys.argv)

    # Create settings dialog
    dialog = SettingsDialog()

    # Print tab information
    print("=== Settings Dialog Tab Structure ===")
    print(f"Total tabs: {dialog.tab_widget.count()}")
    print("\nTabs:")
    for i in range(dialog.tab_widget.count()):
        tab_name = dialog.tab_widget.tabText(i)
        print(f"  {i + 1}. {tab_name}")

    print("\n✓ Settings dialog created successfully with tabbed interface!")
    print("\nTab descriptions:")
    print("  • General: Shortcuts, appearance, and voice activation")
    print("  • Models: Model selection and generation parameters")
    print("  • RAG: Embedding models and retrieval settings")
    print("  • Actions: Custom action button management")

    # Optionally show the dialog (comment out if running headless)
    # dialog.show()
    # sys.exit(app.exec())


if __name__ == "__main__":
    main()
