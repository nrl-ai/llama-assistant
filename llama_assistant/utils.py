import base64
import os
import sys
from importlib import resources

from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt


def image_to_base64_data_uri(file_path):
    with open(file_path, "rb") as img_file:
        base64_data = base64.b64encode(img_file.read()).decode("utf-8")
        return f"data:image/png;base64,{base64_data}"


def get_resource_path(relative_path):
    """Get the path to a resource, works for dev and for PyInstaller"""
    if getattr(sys, "frozen", False):
        # Running in a bundle (PyInstaller)
        base_path = sys._MEIPASS
    else:
        # Running in normal Python environment
        base_path = os.path.dirname(os.path.abspath(__file__))

    path = os.path.join(base_path, relative_path)
    if not os.path.exists(path):
        # Fallback to reading from the package
        file_name = os.path.basename(path)
        package_name = os.path.dirname(relative_path).replace("/", ".")
        with resources.path(package_name, file_name) as p:
            path = str(p)

    return path


def load_image(relative_path, size=None):
    """Load an image from a relative path and optionally resize it"""
    full_path = get_resource_path(relative_path)
    if os.path.exists(full_path):
        pixmap = QPixmap(full_path)
        if size:
            pixmap = pixmap.scaled(size[0], size[1], Qt.AspectRatioMode.KeepAspectRatio)
        return pixmap
    else:
        print(f"Image not found at: {full_path}")
        return QPixmap()
