from typing import TYPE_CHECKING
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QFrame,
)
from PyQt6.QtCore import Qt, QRect, QTimer, QSize, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QKeyEvent, QPainterPath, QScreen

from llama_assistant import config
from llama_assistant.ocr_engine import OCREngine

if TYPE_CHECKING:
    from llama_assistant.llama_assistant_app import LlamaAssistantApp

LEFT_BOTTOM_MARGIN = 64


class ScreenCaptureWidget(QWidget):
    def __init__(self, parent: "LlamaAssistantApp"):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        self.parent = parent
        self.ocr_engine = OCREngine()

        # Get screen size
        screen = QApplication.primaryScreen().geometry()
        self.screen_width = screen.width()
        self.screen_height = screen.height()
        self.setGeometry(0, 0, self.screen_width, self.screen_height)

        # Set crosshairs cursor
        self.setCursor(Qt.CursorShape.CrossCursor)

        # To store the start and end points of the mouse region
        self.start_point = None
        self.end_point = None
        self.captured = False

        # Buttons to appear after selection
        self.button_widget = QWidget()

        # Create a frame for the preview with rounded corners
        self.preview_frame = QFrame(self.button_widget)
        self.preview_frame.setObjectName("previewFrame")
        self.preview_frame.setStyleSheet(
            """
            #previewFrame {
                background-color: white;
                border: 2px solid #808080;
                border-radius: 10px;
                padding: 4px;
            }
        """
        )
        preview_layout = QVBoxLayout(self.preview_frame)
        preview_layout.setContentsMargins(4, 4, 4, 4)

        # Add close button container at the top
        close_container = QWidget()
        close_layout = QHBoxLayout(close_container)
        close_layout.setContentsMargins(0, 0, 0, 0)
        close_layout.addStretch()

        # Create close button
        self.close_button = QPushButton("×", close_container)
        self.close_button.setFixedSize(24, 24)
        self.close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_button.setStyleSheet(
            """
            QPushButton {
                background-color: #ff4444;
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff6666;
            }
            QPushButton:pressed {
                background-color: #cc3333;
            }
        """
        )
        self.close_button.clicked.connect(self.discard_capture)
        close_layout.addWidget(self.close_button)

        preview_layout.addWidget(close_container)

        self.preview_label = QLabel()
        self.preview_label.setMinimumSize(QSize(400, 250))  # Bigger preview
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("background-color: transparent;")
        self.preview_label.setScaledContents(True)  # Make content scale to fit label
        preview_layout.addWidget(self.preview_label)

        # Modern button styling
        self.ocr_button = QPushButton("OCR", self.button_widget)
        self.ask_button = QPushButton("Ask", self.button_widget)
        self.ocr_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ask_button.setCursor(Qt.CursorShape.PointingHandCursor)
        opacity = self.parent.settings.get("transparency", 90) / 100
        base_style = """
            border: none;
            border-radius: 8px;
            color: white;
            padding: 12px 24px;
            font-size: 14px;
            font-weight: 600;
            min-width: 100px;
        """
        button_style = f"""
            QPushButton {{
                {base_style}
                background-color: rgba{QColor(self.parent.settings["color"]).lighter(120).getRgb()[:3] + (opacity,)};
                transition: background-color 0.2s;
            }}
            QPushButton:hover {{
                background-color: rgba{QColor(self.parent.settings["color"]).lighter(150).getRgb()[:3] + (opacity,)};
            }}
            QPushButton:pressed {{
                background-color: rgba{QColor(self.parent.settings["color"]).darker(120).getRgb()[:3] + (opacity,)};
            }}
        """
        self.ocr_button.setStyleSheet(button_style)
        self.ask_button.setStyleSheet(button_style)

        # Layout for buttons and preview
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.ocr_button)
        button_layout.addWidget(self.ask_button)
        button_layout.addStretch()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.preview_frame)
        main_layout.addSpacing(10)
        main_layout.addLayout(button_layout)

        self.button_widget.setLayout(main_layout)
        self.button_widget.hide()

        # Connect button signals
        self.ocr_button.clicked.connect(self.parent.on_ocr_button_clicked)
        self.ask_button.clicked.connect(self.parent.on_ask_with_ocr_context)

    def show(self, reset=True):
        if reset:
            # remove painting if any
            self.start_point = None
            self.end_point = None
            self.captured = False
            self.update()

            # Set window opacity to 50%
            self.setWindowOpacity(0.5)
        else:
            self.setWindowOpacity(0.0)
            self.button_widget.show()
        super().show()

    def hide(self):
        self.button_widget.hide()
        super().hide()

    def discard_capture(self):
        self.start_point = None
        self.end_point = None
        self.captured = False
        self.button_widget.hide()
        self.hide()
        self.parent.show()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            if self.captured:
                self.discard_capture()
            else:
                self.hide()
                self.parent.show()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and not self.captured:
            self.start_point = event.position().toPoint()  # Capture start position
            self.end_point = event.position().toPoint()  # Initialize end point to start position
            print(f"Mouse press at {self.start_point}")

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and not self.captured:
            self.end_point = event.position().toPoint()  # Capture end position

            print(f"Mouse release at {self.end_point}")

            # Capture the region between start and end points
            if self.start_point and self.end_point:
                self.capture_region(self.start_point, self.end_point)
                self.captured = True

            # Trigger repaint to show the red rectangle
            self.update()

            self.show_buttons()

    def mouseMoveEvent(self, event):
        if self.start_point and not self.captured:
            # Update the end_point to the current mouse position as it moves
            self.end_point = event.position().toPoint()

            # Trigger repaint to update the rectangle
            self.update()

    def capture_region(self, start_point, end_point):
        # Store current visibility state
        was_visible = self.isVisible()

        # Hide the window before capturing to avoid including it in the screenshot
        self.hide()

        # Small delay to ensure window is fully hidden
        QTimer.singleShot(100, lambda: self._do_capture(start_point, end_point, was_visible))

    def _do_capture(self, start_point, end_point, restore_visibility=True):
        # Convert local widget coordinates to global screen coordinates
        start_global = self.mapToGlobal(start_point)
        end_global = self.mapToGlobal(end_point)

        # Create a QRect from the global start and end points
        region_rect = QRect(start_global, end_global)

        # Ensure the rectangle is valid (non-negative width/height)
        region_rect = region_rect.normalized()

        # Capture the screen region
        screen = QApplication.primaryScreen()
        pixmap = screen.grabWindow(
            0, region_rect.x(), region_rect.y(), region_rect.width(), region_rect.height()
        )

        # Save the captured region as an image
        pixmap.save(str(config.ocr_tmp_file), "PNG")
        print(f"Captured region saved at '{config.ocr_tmp_file}'.")

        # Update preview label with captured image
        self.preview_label.setPixmap(pixmap)

        # Restore visibility if needed
        if restore_visibility:
            self.show(reset=False)

    def paintEvent(self, event):
        # If the start and end points are set, draw the rectangle
        if self.start_point and self.end_point:
            # Create a painter object
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # Set the pen color to red with a modern look
            pen = QPen(QColor(255, 69, 58))  # Apple-style red
            pen.setWidth(2)
            painter.setPen(pen)

            # Draw the rectangle from start_point to end_point
            self.region_rect = QRect(self.start_point, self.end_point)
            self.region_rect = self.region_rect.normalized()

            # Draw rectangle with slightly rounded corners
            path = QPainterPath()
            path.addRoundedRect(QRectF(self.region_rect), 4, 4)
            painter.drawPath(path)

        super().paintEvent(event)

    def show_buttons(self):
        if self.start_point and self.end_point:
            # Get normalized rectangle
            rect = QRect(self.start_point, self.end_point).normalized()

            # Calculate widget size based on preview and buttons
            widget_width = 450
            widget_height = 350

            # Calculate position to ensure buttons stay within screen bounds
            # Add LEFT_BOTTOM_MARGIN pixels offset from left to avoid macOS dock
            x_pos = min(
                max(LEFT_BOTTOM_MARGIN, rect.left() + (rect.width() - widget_width) // 2),
                self.screen_width - widget_width,
            )

            # Check if there's enough space below the selection
            y_pos = rect.bottom() + LEFT_BOTTOM_MARGIN
            if y_pos + widget_height > self.screen_height:
                # If not enough space below, place above the selection
                y_pos = max(0, rect.top() - widget_height - LEFT_BOTTOM_MARGIN)

            self.button_widget.setGeometry(x_pos, y_pos, widget_width, widget_height)
            self.button_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            self.button_widget.setWindowFlags(Qt.WindowType.FramelessWindowHint)
            self.button_widget.show()
