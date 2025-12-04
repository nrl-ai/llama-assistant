from PyQt6.QtWidgets import (
    QApplication,
    QSystemTrayIcon,
    QMenu,
)
from PyQt6.QtGui import (
    QIcon,
)

from llama_assistant.utils import load_image


class TrayManager:
    def __init__(self, parent):
        self.parent = parent
        self.init_tray()

    def init_tray(self):
        self.tray_icon = QSystemTrayIcon(self.parent)
        self.tray_icon.setIcon(self.load_tray_icon())

        tray_menu = QMenu()
        show_action = tray_menu.addAction("Show")
        show_action.triggered.connect(self.parent.show)
        settings_action = tray_menu.addAction("Settings")
        settings_action.triggered.connect(self.parent.open_settings)
        quit_action = tray_menu.addAction("Quit")
        quit_action.triggered.connect(QApplication.quit)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.parent.tray_icon_activated)
        self.tray_icon.show()

    def load_tray_icon(self):
        icon_path = "llama_assistant/resources/logo.png"
        pixmap = load_image(icon_path, size=(48, 48))
        return QIcon(pixmap)
