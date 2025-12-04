from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextBrowser,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QLabel,
)
from PyQt6.QtCore import (
    Qt,
    QSize,
)
from PyQt6.QtGui import (
    QColor,
    QKeySequence,
    QShortcut,
)

from llama_assistant.custom_plaintext_editor import CustomPlainTextEdit
from llama_assistant.icons import (
    create_icon_from_svg,
    copy_icon_svg,
    clear_icon_svg,
    microphone_icon_svg,
    crosshair_icon_svg,
    reasoning_icon_svg,
)


class CustomQTextBrowser(QTextBrowser):
    def __init__(self, parent):
        super().__init__(parent)

        # Apply stylesheet specific to generated text content
        self.document().setDefaultStyleSheet(
            """
            p {
                color: #FFFFFF;
                font-size: 16px;
                line-height: 1.3;
            }
            li {
                line-height: 1.3;
            }
            pre {
                color: #FFFFFF;
                background-color: #4A4949;
                border: 1px solid #686763;
                border-radius: 10px;
                font-size: 15px;
                font-family: Consolas, "Courier New", monospace;
                overflow: hidden;
            }
            div.think {
                display: block;
                padding: 10px;
                color: #666666;
                font-style: italic;
                margin: 10px 0;
            }
            div.think p {
                color: #666666;
                margin-top: 5px;
                margin-bottom: 5px;
                line-height: 1.5;
            }
        """
        )


class UIManager:
    def __init__(self, parent):
        self.parent = parent
        self.init_ui()
        self.update_styles()  # Call update_styles after initializing UI
        self.update_model_display()  # Initialize model display

    def init_ui(self):
        self.parent.setWindowTitle("AI Assistant")
        self.parent.setMinimumSize(600, 700)
        self.parent.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        self.parent.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        central_widget = QWidget(self.parent)
        self.parent.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)

        top_layout = QVBoxLayout()  # Changed to QVBoxLayout

        input_layout = QHBoxLayout()
        self.input_field = CustomPlainTextEdit(self.parent.on_submit, self.parent)
        self.input_field.setPlaceholderText("Ask me anything...")
        self.input_field.setAcceptDrops(True)
        self.input_field.setFixedHeight(100)
        self.input_field.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.input_field.dragEnterEvent = self.parent.dragEnterEvent
        self.input_field.dropEvent = self.parent.dropEvent
        input_layout.addWidget(self.input_field)

        button_layout = QVBoxLayout()
        self.mic_button = QPushButton(self.parent)
        self.mic_button.setIcon(create_icon_from_svg(microphone_icon_svg))
        self.mic_button.setIconSize(QSize(24, 24))
        self.mic_button.setFixedSize(40, 40)
        self.mic_button.clicked.connect(self.parent.toggle_voice_input)
        self.mic_button.setStyleSheet(
            """
            QPushButton {
                background-color: rgba(100, 100, 100, 200);
                border: none;
                border-radius: 20px;
            }
            QPushButton:hover {
                background-color: rgba(100, 100, 100, 230);
            }
        """
        )
        button_layout.addWidget(self.mic_button)

        self.screenshot_button = QPushButton(self.parent)
        self.screenshot_button.setIcon(create_icon_from_svg(crosshair_icon_svg))
        self.screenshot_button.setIconSize(QSize(24, 24))
        self.screenshot_button.setFixedSize(40, 40)
        self.screenshot_button.clicked.connect(self.parent.capture_screenshot)
        self.screenshot_button.setToolTip("Screen Spot")
        self.screenshot_button.setStyleSheet(
            """
            QPushButton {
                background-color: rgba(100, 100, 100, 200);
                border: none;
                border-radius: 20px;
            }
            QPushButton:hover {
                background-color: rgba(100, 100, 100, 230);
            }
        """
        )
        button_layout.addWidget(self.screenshot_button)

        input_layout.addLayout(button_layout)

        close_button = QPushButton("×", self.parent)
        close_button.clicked.connect(self.parent.hide)
        close_button.setStyleSheet(
            """
            QPushButton {
                background-color: rgba(255, 0, 0, 150);
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 20px;
                padding: 5px;
                width: 30px;
                height: 30px;
            }
            QPushButton:hover {
                background-color: rgba(255, 0, 0, 200);
            }
        """
        )
        input_layout.addWidget(close_button)

        top_layout.addLayout(input_layout)

        self.image_layout = QHBoxLayout()
        self.image_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        top_layout.addLayout(self.image_layout)

        # Add file layout
        self.file_layout = QHBoxLayout()
        self.file_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        top_layout.addLayout(self.file_layout)

        # Add tool layout
        self.tool_layout = QHBoxLayout()
        self.tool_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        top_layout.addLayout(self.tool_layout)

        self.reasoning_button = QPushButton("Reason", self.parent)
        # self.reasoning_button.setStyleSheet(self.get_reasoning_button_style())
        self.reasoning_button.setIcon(create_icon_from_svg(reasoning_icon_svg))
        self.reasoning_button.clicked.connect(self.parent.toggle_reasoning)
        self.tool_layout.addWidget(self.reasoning_button)

        # Dynamic action buttons layout
        self.action_button_layout = QHBoxLayout()
        self.action_button_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.action_buttons = {}
        self.create_action_buttons()
        top_layout.addLayout(self.action_button_layout)
        main_layout.addLayout(top_layout)

        result_layout = QHBoxLayout()
        result_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.copy_button = QPushButton("Copy Result", self.parent)
        self.copy_button.setIcon(create_icon_from_svg(copy_icon_svg))
        self.copy_button.setIconSize(QSize(18, 18))
        self.copy_button.clicked.connect(self.parent.copy_result)
        self.copy_button.hide()

        self.clear_button = QPushButton("Clear", self.parent)
        self.clear_button.setIcon(create_icon_from_svg(clear_icon_svg))
        self.clear_button.setIconSize(QSize(18, 18))
        self.clear_button.clicked.connect(self.parent.clear_chat)
        self.clear_button.hide()

        result_layout.addWidget(self.copy_button)
        result_layout.addWidget(self.clear_button)

        main_layout.addLayout(result_layout)

        self.scroll_area = QScrollArea(self.parent)
        self.scroll_area.setWidgetResizable(True)  # Allow the widget inside to resize
        self.scroll_area.setMinimumHeight(400)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet(
            """
            QScrollArea {
                border: none;
                background-color: transparent;
                border-radius: 20px;
            }
            QScrollBar:vertical {
                border: none;
                background: rgba(255, 255, 255, 200);
                width: 10px;
                margin: 0px 0px 0px 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 230);
                min-height: 20px;
                border-radius: 5px;
            }
            """
        )

        self.chat_box = CustomQTextBrowser(self.scroll_area)
        self.chat_box.setOpenExternalLinks(True)

        self.scroll_area.setWidget(self.chat_box)
        self.scroll_area.hide()  # Hide the scroll area initially

        # Ensure the scroll area can expand fully in the layout
        self.scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_layout.addWidget(self.scroll_area)

        self.parent.esc_shortcut = QShortcut(QKeySequence("Esc"), self.parent)
        self.parent.esc_shortcut.activated.connect(self.parent.hide)

        # Add an expanding spacer
        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        main_layout.addItem(spacer)

    def update_styles(self):
        opacity = self.parent.settings.get("transparency", 90) / 100
        base_style = f"""
            border: none;
            border-radius: 20px;
            color: white;
            padding: 10px 15px;
            font-size: 16px;
        """
        self.input_field.setStyleSheet(
            f"""
            QPlainTextEdit {{
                background-color: rgba{QColor(self.parent.settings["color"]).getRgb()[:3] + (opacity,)};
                {base_style}
            }}
            """
        )
        self.chat_box.setStyleSheet(
            f"""QTextBrowser {{ {base_style}
                                    background-color: rgba{QColor(self.parent.settings["color"]).lighter(120).getRgb()[:3] + (opacity,)};
                                    border-radius: 10px;
                                    }}"""
        )
        button_style = f"""
            QPushButton {{
                {base_style}
                padding: 2.5px 5px;
                border-radius: 5px;
                background-color: rgba{QColor(self.parent.settings["color"]).getRgb()[:3] + (opacity,)};
            }}
            QPushButton:hover {{
                background-color: rgba{QColor(self.parent.settings["color"]).lighter(120).getRgb()[:3] + (opacity,)};
            }}
        """
        for button in self.action_buttons.values():
            button.setStyleSheet(button_style)

        button_style = f"""
            QPushButton {{
                {base_style}
                padding: 2.5px 5px;
                border-radius: 5px;
                background-color: rgba{QColor(self.parent.settings["color"]).lighter(120).getRgb()[:3] + (opacity,)};
            }}
            QPushButton:hover {{
                background-color: rgba{QColor(self.parent.settings["color"]).lighter(150).getRgb()[:3] + (opacity,)};
            }}
        """
        for button in [self.copy_button, self.clear_button]:
            button.setStyleSheet(button_style)

        self.set_reasoning_button_style()

    def update_model_display(self):
        # Determine which model is currently active
        active_model_info = ""

        if self.parent.reasoning_enabled and self.parent.current_text_reasoning_model:
            # Find the model details for the text reasoning model
            for model in self.parent.config.models:
                if model["model_id"] == self.parent.current_text_reasoning_model:
                    active_model_info = f"{model['model_name']} (Reasoning)"
                    break
        elif self.parent.dropped_image and self.parent.current_multimodal_model:
            # Find the model details for the multimodal model
            for model in self.parent.config.models:
                if model["model_id"] == self.parent.current_multimodal_model:
                    active_model_info = f"{model['model_name']} (Multimodal)"
                    break
        elif self.parent.current_text_model:
            # Find the model details for the text model
            for model in self.parent.config.models:
                if model["model_id"] == self.parent.current_text_model:
                    active_model_info = f"{model['model_name']} (Text)"
                    break

        if not active_model_info:
            active_model_info = "No model active"

        # Update the input field placeholder
        self.input_field.set_model_info(active_model_info)

    def set_reasoning_button_style(self):
        opacity = self.parent.settings.get("transparency", 90) / 100
        base_style = f"""
            border: none;
            border-radius: 20px;
            color: white;
            padding: 10px 15px;
            font-size: 16px;
        """

        if self.parent.reasoning_enabled:
            button_style = f"""
                QPushButton {{
                    {base_style}
                    padding: 2.5px 5px;
                    border-radius: 5px;
                    background-color: rgba{QColor(self.parent.settings["color"]).lighter(300).getRgb()[:3] + (opacity,)};
                }}
            """
        else:
            button_style = f"""
                QPushButton {{
                    {base_style}
                    padding: 2.5px 5px;
                    border-radius: 5px;
                    background-color: rgba{QColor(self.parent.settings["color"]).lighter(120).getRgb()[:3] + (opacity,)};
                }}
            """
        self.reasoning_button.setStyleSheet(button_style)

    def create_action_buttons(self):
        # Clear existing buttons
        for button in self.action_buttons.values():
            button.deleteLater()
        self.action_buttons.clear()

        # Import config here to get latest actions
        from llama_assistant import config

        # Sort actions by order and filter visible ones
        visible_actions = [a for a in config.actions if a.get("visible", True)]
        sorted_actions = sorted(visible_actions, key=lambda x: x.get("order", 999))

        # Create buttons for each action
        for action in sorted_actions:
            button = QPushButton(action["label"], self.parent)
            button.setProperty("action_id", action["id"])
            button.setProperty("action_prompt", action["prompt"])
            button.clicked.connect(self.parent.on_task_button_clicked)
            self.action_button_layout.addWidget(button)
            self.action_buttons[action["id"]] = button

    def refresh_action_buttons(self):
        """Refresh action buttons when actions are updated"""
        self.create_action_buttons()
        self.update_styles()
