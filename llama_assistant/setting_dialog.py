import json
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog,
    QFormLayout,
    QPushButton,
    QSlider,
    QComboBox,
    QColorDialog,
    QVBoxLayout,
    QHBoxLayout,
    QCheckBox,
    QGroupBox,
    QLineEdit,
    QMessageBox,
    QListWidget,
    QLabel,
    QScrollArea,
    QWidget,
    QGridLayout,
    QTabWidget,
    QTextEdit,
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor
from pynput import keyboard
import html2text

from llama_assistant.shortcut_recorder import ShortcutRecorder
from llama_assistant import config
from llama_assistant.setting_validator import validate_numeric_field


class MarkdownTextEdit(QTextEdit):
    """Custom QTextEdit that converts rich text paste to markdown"""

    def insertFromMimeData(self, source):
        """Override paste to convert rich text to markdown"""
        if source.hasHtml():
            # Convert HTML to markdown
            html_content = source.html()
            h = html2text.HTML2Text()
            h.ignore_links = False
            h.ignore_images = False
            h.ignore_emphasis = False
            h.body_width = 0  # Don't wrap lines
            markdown_text = h.handle(html_content).strip()

            # Insert as plain text
            cursor = self.textCursor()
            cursor.insertText(markdown_text)
        elif source.hasText():
            # Insert plain text normally
            cursor = self.textCursor()
            cursor.insertText(source.text())
        else:
            # Fallback to default behavior
            super().insertFromMimeData(source)


class SettingsDialog(QDialog):
    settingsSaved = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(850)
        self.setMinimumHeight(650)

        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 10)

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(
            """
            QTabWidget::pane {
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
            }
            QTabBar::tab {
                padding: 6px 12px;
                margin-right: 2px;
                border: 1px solid #ccc;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                background-color: #f0f0f0;
                font-size: 13px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
                font-weight: bold;
            }
            QTabBar::tab:hover:!selected {
                background-color: #e8e8e8;
            }
        """
        )
        main_layout.addWidget(self.tab_widget)

        # Create tabs
        self.create_general_tab()
        self.create_models_tab()
        self.create_rag_tab()
        self.create_actions_tab()

        # Create a horizontal layout for the save button
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(10, 5, 10, 0)
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.accept)
        self.save_button.setMinimumWidth(100)
        self.save_button.setStyleSheet(
            """
            QPushButton {
                padding: 10px 24px;
                border: none;
                border-radius: 4px;
                background-color: #0078d4;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """
        )
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)

        # Add the button layout to the main layout
        main_layout.addLayout(button_layout)

        self.load_settings()

    def create_general_tab(self):
        """Create the General tab with shortcuts, appearance, and voice settings"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Shortcut Settings Group
        shortcut_group = QGroupBox("Shortcut Settings")
        shortcut_layout = QVBoxLayout()

        shortcut_input_layout = QHBoxLayout()
        shortcut_label = QLabel("Global Shortcut:")
        self.shortcut_recorder = ShortcutRecorder()
        shortcut_input_layout.addWidget(shortcut_label)
        shortcut_input_layout.addWidget(self.shortcut_recorder)
        shortcut_input_layout.addStretch()
        shortcut_layout.addLayout(shortcut_input_layout)

        self.reset_shortcut_button = QPushButton("Reset Shortcut")
        self.reset_shortcut_button.clicked.connect(self.reset_shortcut)
        shortcut_layout.addWidget(self.reset_shortcut_button)

        shortcut_group.setLayout(shortcut_layout)
        layout.addWidget(shortcut_group)

        # Appearance Settings Group
        appearance_group = QGroupBox("Appearance Settings")
        appearance_layout = QVBoxLayout()

        color_layout = QHBoxLayout()
        color_label = QLabel("Background Color:")
        self.color_button = QPushButton("Choose Color")
        self.color_button.clicked.connect(self.choose_color)
        color_layout.addWidget(color_label)
        color_layout.addWidget(self.color_button)
        color_layout.addStretch()
        appearance_layout.addLayout(color_layout)

        transparency_layout = QHBoxLayout()
        transparency_label = QLabel("Transparency:")
        self.transparency_slider = QSlider(Qt.Orientation.Horizontal)
        self.transparency_slider.setRange(10, 100)
        self.transparency_slider.setValue(90)
        transparency_layout.addWidget(transparency_label)
        transparency_layout.addWidget(self.transparency_slider)
        appearance_layout.addLayout(transparency_layout)

        appearance_group.setLayout(appearance_layout)
        layout.addWidget(appearance_group)

        # Voice Activation Settings Group
        voice_group = QGroupBox("Voice Activation Settings")
        voice_layout = QVBoxLayout()

        self.hey_llama_chat_checkbox = QCheckBox('Say "Hey Llama" to open chat form')
        self.hey_llama_chat_checkbox.stateChanged.connect(self.update_hey_llama_mic_state)
        voice_layout.addWidget(self.hey_llama_chat_checkbox)

        self.hey_llama_mic_checkbox = QCheckBox('Say "Hey Llama" to activate microphone')
        voice_layout.addWidget(self.hey_llama_mic_checkbox)

        voice_group.setLayout(voice_layout)
        layout.addWidget(voice_group)

        layout.addStretch()
        self.tab_widget.addTab(tab, "⚙️ General")

    def create_models_tab(self):
        """Create the Models tab with model selection and generation parameters"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Model Selection Group
        model_group = QGroupBox("Model Selection")
        models_form = QFormLayout()
        models_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)

        self.text_model_combo = QComboBox()
        self.text_model_combo.addItems(self.get_model_names_by_type("text"))
        models_form.addRow("Text-only Model:", self.text_model_combo)

        self.text_reasoning_model_combo = QComboBox()
        self.text_reasoning_model_combo.addItems(self.get_model_names_by_type("text-reasoning"))
        models_form.addRow("Text-reasoning Model:", self.text_reasoning_model_combo)

        self.multimodal_model_combo = QComboBox()
        self.multimodal_model_combo.addItems(self.get_model_names_by_type("image"))
        models_form.addRow("Multimodal Model:", self.multimodal_model_combo)

        model_group.setLayout(models_form)
        layout.addWidget(model_group)

        # Generation Parameters Group
        gen_group = QGroupBox("Generation Parameters")
        grid_layout = QGridLayout()
        grid_layout.setColumnStretch(1, 1)
        grid_layout.setColumnStretch(3, 1)

        self.context_len_input = QLineEdit()
        grid_layout.addWidget(QLabel("Context Length:"), 0, 0)
        grid_layout.addWidget(self.context_len_input, 0, 1)

        self.temperature_input = QLineEdit()
        grid_layout.addWidget(QLabel("Temperature:"), 0, 2)
        grid_layout.addWidget(self.temperature_input, 0, 3)

        self.top_p_input = QLineEdit()
        grid_layout.addWidget(QLabel("Top p:"), 1, 0)
        grid_layout.addWidget(self.top_p_input, 1, 1)

        self.top_k_input = QLineEdit()
        grid_layout.addWidget(QLabel("Top k:"), 1, 2)
        grid_layout.addWidget(self.top_k_input, 1, 3)

        gen_group.setLayout(grid_layout)
        layout.addWidget(gen_group)

        # Custom Models Button
        self.manage_custom_models_button = QPushButton("Manage Custom Models")
        self.manage_custom_models_button.clicked.connect(self.open_custom_models_dialog)
        layout.addWidget(self.manage_custom_models_button)

        layout.addStretch()
        self.tab_widget.addTab(tab, "🤖 Models")

    def create_rag_tab(self):
        """Create the RAG tab with embedding and retrieval settings"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Embed Model Group
        embed_group = QGroupBox("Embedding Model")
        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)

        self.embed_model_combo = QComboBox()
        self.embed_model_combo.addItems(config.DEFAULT_EMBEDING_MODELS)
        form_layout.addRow("Embed Model:", self.embed_model_combo)

        embed_group.setLayout(form_layout)
        layout.addWidget(embed_group)

        # RAG Parameters Group
        rag_group = QGroupBox("RAG Parameters")
        params_layout = QGridLayout()
        params_layout.setColumnStretch(1, 1)
        params_layout.setColumnStretch(3, 1)

        self.chunk_size_input = QLineEdit()
        params_layout.addWidget(QLabel("Chunk Size:"), 0, 0)
        params_layout.addWidget(self.chunk_size_input, 0, 1)

        self.chunk_overlap_input = QLineEdit()
        params_layout.addWidget(QLabel("Chunk Overlap:"), 0, 2)
        params_layout.addWidget(self.chunk_overlap_input, 0, 3)

        self.max_retrieval_top_k_input = QLineEdit()
        params_layout.addWidget(QLabel("Max Retrieval Top k:"), 1, 0)
        params_layout.addWidget(self.max_retrieval_top_k_input, 1, 1)

        self.similarity_threshold_input = QLineEdit()
        params_layout.addWidget(QLabel("Similarity Threshold:"), 1, 2)
        params_layout.addWidget(self.similarity_threshold_input, 1, 3)

        rag_group.setLayout(params_layout)
        layout.addWidget(rag_group)

        layout.addStretch()
        self.tab_widget.addTab(tab, "📚 RAG")

    def create_actions_tab(self):
        """Create the Actions tab for managing custom actions"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Info label
        info_label = QLabel(
            "Manage action buttons that appear in the main interface. " "Drag to reorder actions."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; padding: 5px; font-size: 12px;")
        layout.addWidget(info_label)

        # Action list
        list_label = QLabel("Actions:")
        list_label.setStyleSheet("font-weight: bold; margin-top: 5px;")
        layout.addWidget(list_label)

        self.action_list = QListWidget()
        self.action_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.action_list.itemSelectionChanged.connect(self.load_selected_action)
        self.action_list.setMinimumHeight(120)
        self.action_list.setMaximumHeight(150)
        self.action_list.setStyleSheet(
            """
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 5px;
                border-radius: 3px;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
        """
        )
        layout.addWidget(self.action_list)

        # Form for editing actions
        form_group = QGroupBox("Action Details")
        form_group.setStyleSheet(
            """
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """
        )
        form_layout = QVBoxLayout()
        form_layout.setSpacing(8)

        # ID field
        id_layout = QHBoxLayout()
        id_label = QLabel("ID:")
        id_label.setMinimumWidth(80)
        id_label.setStyleSheet("font-weight: normal;")
        self.action_id_input = QLineEdit()
        self.action_id_input.setPlaceholderText("unique_id (no spaces)")
        self.action_id_input.setStyleSheet(
            "padding: 5px; border: 1px solid #ccc; border-radius: 3px;"
        )
        id_layout.addWidget(id_label)
        id_layout.addWidget(self.action_id_input)
        form_layout.addLayout(id_layout)

        # Label field
        label_layout = QHBoxLayout()
        label_label = QLabel("Label:")
        label_label.setMinimumWidth(80)
        label_label.setStyleSheet("font-weight: normal;")
        self.action_label_input = QLineEdit()
        self.action_label_input.setPlaceholderText("Button Label")
        self.action_label_input.setStyleSheet(
            "padding: 5px; border: 1px solid #ccc; border-radius: 3px;"
        )
        label_layout.addWidget(label_label)
        label_layout.addWidget(self.action_label_input)
        form_layout.addLayout(label_layout)

        # Prompt field
        prompt_label = QLabel("Prompt:")
        prompt_label.setStyleSheet("font-weight: normal; margin-top: 5px;")
        form_layout.addWidget(prompt_label)

        self.action_prompt_input = MarkdownTextEdit()
        self.action_prompt_input.setPlaceholderText(
            "Prompt to send to the model (e.g., 'Summarize the following text:')"
        )
        self.action_prompt_input.setMinimumHeight(60)
        self.action_prompt_input.setMaximumHeight(100)
        self.action_prompt_input.setStyleSheet(
            """
            QTextEdit {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
                font-family: inherit;
            }
        """
        )
        form_layout.addWidget(self.action_prompt_input)

        # Visible checkbox
        visible_layout = QHBoxLayout()
        visible_label = QLabel("Visible:")
        visible_label.setMinimumWidth(80)
        visible_label.setStyleSheet("font-weight: normal;")
        self.action_visible_checkbox = QCheckBox()
        self.action_visible_checkbox.setChecked(True)
        visible_layout.addWidget(visible_label)
        visible_layout.addWidget(self.action_visible_checkbox)
        visible_layout.addStretch()
        form_layout.addLayout(visible_layout)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        button_style = """
            QPushButton {
                padding: 8px 16px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #f0f0f0;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border-color: #999;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """

        self.add_action_button = QPushButton("Add")
        self.add_action_button.clicked.connect(self.add_action)
        self.add_action_button.setStyleSheet(button_style)

        self.update_action_button = QPushButton("Update")
        self.update_action_button.clicked.connect(self.update_action)
        self.update_action_button.setStyleSheet(button_style)

        self.reset_action_button = QPushButton("Reset to Default")
        self.reset_action_button.clicked.connect(self.reset_action)
        self.reset_action_button.setStyleSheet(button_style)

        self.remove_action_button = QPushButton("Remove")
        self.remove_action_button.clicked.connect(self.remove_action)
        self.remove_action_button.setStyleSheet(button_style)

        button_layout.addWidget(self.add_action_button)
        button_layout.addWidget(self.update_action_button)
        button_layout.addWidget(self.reset_action_button)
        button_layout.addWidget(self.remove_action_button)
        button_layout.addStretch()

        layout.addLayout(button_layout)
        layout.addStretch()

        self.tab_widget.addTab(tab, "⚡ Actions")

        # Load actions after tab is created
        self.refresh_action_list()

    def accept(self):
        valid, message = validate_numeric_field(
            "Context Length",
            self.context_len_input.text(),
            constraints=config.VALIDATOR["generation"]["context_len"],
        )
        if not valid:
            QMessageBox.warning(self, "Validation Error", message)
            return

        valid, message = validate_numeric_field(
            "Temperature",
            self.temperature_input.text(),
            constraints=config.VALIDATOR["generation"]["temperature"],
        )
        if not valid:
            QMessageBox.warning(self, "Validation Error", message)
            return

        valid, message = validate_numeric_field(
            "Top p", self.top_p_input.text(), constraints=config.VALIDATOR["generation"]["top_p"]
        )
        if not valid:
            QMessageBox.warning(self, "Validation Error", message)
            return

        valid, message = validate_numeric_field(
            "Top k", self.top_k_input.text(), constraints=config.VALIDATOR["generation"]["top_k"]
        )
        if not valid:
            QMessageBox.warning(self, "Validation Error", message)
            return

        valid, message = validate_numeric_field(
            "Chunk Size",
            self.chunk_size_input.text(),
            constraints=config.VALIDATOR["rag"]["chunk_size"],
        )
        if not valid:
            QMessageBox.warning(self, "Validation Error", message)
            return

        valid, message = validate_numeric_field(
            "Chunk Overlap",
            self.chunk_overlap_input.text(),
            constraints=config.VALIDATOR["rag"]["chunk_overlap"],
        )
        if not valid:
            QMessageBox.warning(self, "Validation Error", message)
            return

        valid, message = validate_numeric_field(
            "Max Retrieval Top k",
            self.max_retrieval_top_k_input.text(),
            constraints=config.VALIDATOR["rag"]["max_retrieval_top_k"],
        )

        if not valid:
            QMessageBox.warning(self, "Validation Error", message)
            return

        valid, message = validate_numeric_field(
            "Similarity Threshold",
            self.similarity_threshold_input.text(),
            constraints=config.VALIDATOR["rag"]["similarity_threshold"],
        )

        if not valid:
            QMessageBox.warning(self, "Validation Error", message)
            return

        # Update action order based on current list position
        for i in range(self.action_list.count()):
            item_text = self.action_list.item(i).text()
            # Extract ID from the item text
            action_id = item_text.split("(")[-1].rstrip(")")
            for action in config.actions:
                if action["id"] == action_id:
                    action["order"] = i
                    break

        # Save actions
        config.save_actions()

        self.save_settings()
        self.settingsSaved.emit()
        super().accept()

    def get_model_names_by_type(self, model_type):
        return [model["model_id"] for model in config.models if model["model_type"] == model_type]

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color = color

    def reset_shortcut(self):
        self.shortcut_recorder.setText(config.DEFAULT_LAUNCH_SHORTCUT)

    def update_hey_llama_mic_state(self, state):
        self.hey_llama_mic_checkbox.setEnabled(state == Qt.CheckState.Checked)

    def load_settings(self):
        if config.settings_file.exists():
            with open(config.settings_file, "r") as f:
                settings = json.load(f)
            try:
                keyboard.HotKey(keyboard.HotKey.parse(settings["shortcut"]), lambda: None)
            except ValueError:
                settings["shortcut"] = config.DEFAULT_LAUNCH_SHORTCUT
                self.save_settings(settings)
            self.shortcut_recorder.setText(settings.get("shortcut", config.DEFAULT_LAUNCH_SHORTCUT))
            self.color = QColor(settings.get("color", "#1E1E1E"))
            self.transparency_slider.setValue(int(settings.get("transparency", 90)))

            text_model = settings.get("text_model")
            if text_model in self.get_model_names_by_type("text"):
                self.text_model_combo.setCurrentText(text_model)

            multimodal_model = settings.get("multimodal_model")
            if multimodal_model in self.get_model_names_by_type("image"):
                self.multimodal_model_combo.setCurrentText(multimodal_model)

            text_reasoning_model = settings.get("text_reasoning_model")
            if text_reasoning_model in self.get_model_names_by_type("text-reasoning"):
                self.text_reasoning_model_combo.setCurrentText(text_reasoning_model)

            self.hey_llama_chat_checkbox.setChecked(settings.get("hey_llama_chat", False))
            self.hey_llama_mic_checkbox.setChecked(settings.get("hey_llama_mic", False))
            self.update_hey_llama_mic_state(settings.get("hey_llama_chat", False))

            # Load new settings
            if "generation" not in settings:
                settings["generation"] = {}
            if "rag" not in settings:
                settings["rag"] = {}

            embed_model = settings["rag"].get(
                "embed_model_name", config.DEFAULT_SETTINGS["rag"]["embed_model_name"]
            )
            if embed_model in config.DEFAULT_EMBEDING_MODELS:
                self.embed_model_combo.setCurrentText(embed_model)

            self.chunk_size_input.setText(
                str(settings["rag"].get("chunk_size", config.DEFAULT_SETTINGS["rag"]["chunk_size"]))
            )
            self.chunk_overlap_input.setText(
                str(
                    settings["rag"].get(
                        "chunk_overlap", config.DEFAULT_SETTINGS["rag"]["chunk_overlap"]
                    )
                )
            )
            self.max_retrieval_top_k_input.setText(
                str(
                    settings["rag"].get(
                        "max_retrieval_top_k", config.DEFAULT_SETTINGS["rag"]["max_retrieval_top_k"]
                    )
                )
            )
            self.similarity_threshold_input.setText(
                str(
                    settings["rag"].get(
                        "similarity_threshold",
                        config.DEFAULT_SETTINGS["rag"]["similarity_threshold"],
                    )
                )
            )
            self.context_len_input.setText(
                str(
                    settings["generation"].get(
                        "context_len", config.DEFAULT_SETTINGS["generation"]["context_len"]
                    )
                )
            )

            self.temperature_input.setText(
                str(
                    settings["generation"].get(
                        "temperature", config.DEFAULT_SETTINGS["generation"]["temperature"]
                    )
                )
            )
            self.top_p_input.setText(
                str(
                    settings["generation"].get(
                        "top_p", config.DEFAULT_SETTINGS["generation"]["top_p"]
                    )
                )
            )
            self.top_k_input.setText(
                str(
                    settings["generation"].get(
                        "top_k", config.DEFAULT_SETTINGS["generation"]["top_k"]
                    )
                )
            )
        else:
            self.color = QColor("#1E1E1E")
            self.shortcut_recorder.setText("<cmd>+<shift>+<space>")

    def get_settings(self):
        return {
            "shortcut": self.shortcut_recorder.text(),
            "color": self.color.name(),
            "transparency": self.transparency_slider.value(),
            "text_model": self.text_model_combo.currentText(),
            "multimodal_model": self.multimodal_model_combo.currentText(),
            "text_reasoning_model": self.text_reasoning_model_combo.currentText(),
            "hey_llama_chat": self.hey_llama_chat_checkbox.isChecked(),
            "hey_llama_mic": self.hey_llama_mic_checkbox.isChecked(),
            "generation": {
                "context_len": int(self.context_len_input.text()),
                "temperature": float(self.temperature_input.text()),
                "top_p": float(self.top_p_input.text()),
                "top_k": int(self.top_k_input.text()),
            },
            "rag": {
                "embed_model_name": self.embed_model_combo.currentText(),
                "chunk_size": int(self.chunk_size_input.text()),
                "chunk_overlap": int(self.chunk_overlap_input.text()),
                "max_retrieval_top_k": int(self.max_retrieval_top_k_input.text()),
                "similarity_threshold": float(self.similarity_threshold_input.text()),
            },
        }

    def save_settings(self, settings=None):
        if settings is None:
            settings = self.get_settings()

        with open(config.settings_file, "w") as f:
            json.dump(settings, f)

    def open_custom_models_dialog(self):
        dialog = CustomModelsDialog(self)
        if dialog.exec():
            # Refresh the model combos after managing custom models
            self.refresh_model_combos()
        self.refresh_model_combos()  # Run refresh_model_combos after closing the custom models editor

    def refresh_action_list(self):
        self.action_list.clear()
        # Sort by order
        sorted_actions = sorted(config.actions, key=lambda x: x.get("order", 999))
        for action in sorted_actions:
            visibility = "✓" if action.get("visible", True) else "✗"
            self.action_list.addItem(f"{visibility} {action['label']} ({action['id']})")

    def load_selected_action(self):
        selected_items = self.action_list.selectedItems()
        if selected_items:
            selected_index = self.action_list.row(selected_items[0])
            sorted_actions = sorted(config.actions, key=lambda x: x.get("order", 999))
            action = sorted_actions[selected_index]

            self.action_id_input.setText(action["id"])
            self.action_label_input.setText(action["label"])
            self.action_prompt_input.setPlainText(action["prompt"])
            self.action_visible_checkbox.setChecked(action.get("visible", True))

    def add_action(self):
        action_id = self.action_id_input.text().strip()
        action_label = self.action_label_input.text().strip()
        action_prompt = self.action_prompt_input.toPlainText().strip()

        if not all([action_id, action_label, action_prompt]):
            QMessageBox.warning(self, "Missing Information", "Please fill in all fields.")
            return

        # Check if ID already exists
        if any(a["id"] == action_id for a in config.actions):
            QMessageBox.warning(
                self, "Duplicate ID", f"Action with ID '{action_id}' already exists."
            )
            return

        new_action = {
            "id": action_id,
            "label": action_label,
            "prompt": action_prompt,
            "visible": self.action_visible_checkbox.isChecked(),
            "order": len(config.actions),
            "custom": True,
        }

        config.actions.append(new_action)
        config.save_actions()  # Auto-save
        self.refresh_action_list()
        self.clear_action_inputs()
        QMessageBox.information(
            self, "Action Added", f"Action '{action_label}' has been added successfully."
        )

    def update_action(self):
        selected_items = self.action_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select an action to update.")
            return

        selected_index = self.action_list.row(selected_items[0])
        sorted_actions = sorted(config.actions, key=lambda x: x.get("order", 999))
        action = sorted_actions[selected_index]

        # Find the action in the original list
        original_index = config.actions.index(action)

        action_id = self.action_id_input.text().strip()
        action_label = self.action_label_input.text().strip()
        action_prompt = self.action_prompt_input.toPlainText().strip()

        if not all([action_id, action_label, action_prompt]):
            QMessageBox.warning(self, "Missing Information", "Please fill in all fields.")
            return

        # Check if ID already exists (excluding current action)
        if action_id != action["id"] and any(a["id"] == action_id for a in config.actions):
            QMessageBox.warning(
                self, "Duplicate ID", f"Action with ID '{action_id}' already exists."
            )
            return

        config.actions[original_index]["id"] = action_id
        config.actions[original_index]["label"] = action_label
        config.actions[original_index]["prompt"] = action_prompt
        config.actions[original_index]["visible"] = self.action_visible_checkbox.isChecked()

        config.save_actions()  # Auto-save
        self.refresh_action_list()
        self.clear_action_inputs()
        QMessageBox.information(
            self, "Action Updated", f"Action '{action_label}' has been updated successfully."
        )

    def reset_action(self):
        selected_items = self.action_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select an action to reset.")
            return

        selected_index = self.action_list.row(selected_items[0])
        sorted_actions = sorted(config.actions, key=lambda x: x.get("order", 999))
        action = sorted_actions[selected_index]

        # Check if it's a default action
        default_action = next((a for a in config.DEFAULT_ACTIONS if a["id"] == action["id"]), None)

        if not default_action:
            QMessageBox.information(
                self, "Not a Default Action", "This is a custom action. Use 'Remove' to delete it."
            )
            return

        # Find the action in the original list
        original_index = config.actions.index(action)

        # Reset to default values but keep the order
        current_order = config.actions[original_index].get("order", default_action["order"])
        config.actions[original_index] = default_action.copy()
        config.actions[original_index]["order"] = current_order

        config.save_actions()  # Auto-save
        self.refresh_action_list()
        self.clear_action_inputs()
        QMessageBox.information(
            self, "Action Reset", f"Action '{action['label']}' has been reset to default."
        )

    def remove_action(self):
        selected_items = self.action_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select an action to remove.")
            return

        selected_index = self.action_list.row(selected_items[0])
        sorted_actions = sorted(config.actions, key=lambda x: x.get("order", 999))
        action = sorted_actions[selected_index]

        # Find the action in the original list
        original_index = config.actions.index(action)
        action_label = action["label"]

        del config.actions[original_index]

        config.save_actions()  # Auto-save
        self.refresh_action_list()
        self.clear_action_inputs()
        QMessageBox.information(
            self, "Action Removed", f"Action '{action_label}' has been removed successfully."
        )

    def clear_action_inputs(self):
        self.action_id_input.clear()
        self.action_label_input.clear()
        self.action_prompt_input.clear()
        self.action_visible_checkbox.setChecked(True)

    def refresh_model_combos(self):
        current_text_model = self.text_model_combo.currentText()
        current_multimodal_model = self.multimodal_model_combo.currentText()

        self.text_model_combo.clear()
        self.text_model_combo.addItems(self.get_model_names_by_type("text"))
        self.multimodal_model_combo.clear()
        self.multimodal_model_combo.addItems(self.get_model_names_by_type("image"))

        # Restore previously selected models if they still exist
        if current_text_model in self.get_model_names_by_type("text"):
            self.text_model_combo.setCurrentText(current_text_model)
        if current_multimodal_model in self.get_model_names_by_type("image"):
            self.multimodal_model_combo.setCurrentText(current_multimodal_model)


class CustomModelsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Custom Models")
        self.layout = QVBoxLayout(self)

        self.model_list = QListWidget()
        self.model_list.itemSelectionChanged.connect(self.load_selected_model)
        self.layout.addWidget(self.model_list)

        form_layout = QFormLayout()
        self.model_name_input = QLineEdit()
        self.model_id_input = QLineEdit()
        self.model_type_input = QComboBox()
        self.model_type_input.addItems(["text", "image"])
        self.repo_id_input = QLineEdit()
        self.filename_input = QLineEdit()

        form_layout.addRow("Model Name:", self.model_name_input)
        form_layout.addRow("Model ID:", self.model_id_input)
        form_layout.addRow("Model Type:", self.model_type_input)
        form_layout.addRow("Repo ID:", self.repo_id_input)
        form_layout.addRow("Filename:", self.filename_input)

        self.layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Model")
        self.add_button.clicked.connect(self.add_model)
        self.update_button = QPushButton("Update Model")
        self.update_button.clicked.connect(self.update_model)
        self.remove_button = QPushButton("Remove Model")
        self.remove_button.clicked.connect(self.remove_model)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.remove_button)

        self.layout.addLayout(button_layout)

        self.refresh_model_list()

    def refresh_model_list(self):
        self.model_list.clear()
        for model in config.custom_models:
            self.model_list.addItem(f"{model['model_name']} ({model['model_type']})")

    def load_selected_model(self):
        selected_items = self.model_list.selectedItems()
        if selected_items:
            selected_index = self.model_list.row(selected_items[0])
            model = config.custom_models[selected_index]
            self.model_name_input.setText(model["model_name"])
            self.model_id_input.setText(model["model_id"])
            self.model_type_input.setCurrentText(model["model_type"])
            self.repo_id_input.setText(model["repo_id"])
            self.filename_input.setText(model["filename"])

    def add_model(self):
        model_name = self.model_name_input.text()
        model_id = self.model_id_input.text()
        model_type = self.model_type_input.currentText()
        repo_id = self.repo_id_input.text()
        filename = self.filename_input.text()

        if not all([model_name, model_id, model_type, repo_id, filename]):
            QMessageBox.warning(self, "Missing Information", "Please fill in all fields.")
            return

        new_model = {
            "model_name": model_name,
            "model_id": model_id,
            "model_type": model_type,
            "model_path": None,
            "repo_id": repo_id,
            "filename": filename,
        }

        config.custom_models.append(new_model)
        config.save_custom_models()
        self.refresh_model_list()
        self.clear_inputs()
        QMessageBox.information(
            self, "Model Added", f"Model '{model_name}' has been added successfully."
        )

    def update_model(self):
        selected_items = self.model_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a model to update.")
            return

        selected_index = self.model_list.row(selected_items[0])
        model_name = self.model_name_input.text()
        model_id = self.model_id_input.text()
        model_type = self.model_type_input.currentText()
        repo_id = self.repo_id_input.text()
        filename = self.filename_input.text()

        if not all([model_name, model_id, model_type, repo_id, filename]):
            QMessageBox.warning(self, "Missing Information", "Please fill in all fields.")
            return

        updated_model = {
            "model_name": model_name,
            "model_id": model_id,
            "model_type": model_type,
            "model_path": None,
            "repo_id": repo_id,
            "filename": filename,
        }

        config.custom_models[selected_index] = updated_model
        config.models = config.DEFAULT_MODELS + config.custom_models
        config.save_custom_models()
        self.refresh_model_list()
        self.clear_inputs()
        QMessageBox.information(
            self, "Model Updated", f"Model '{model_name}' has been updated successfully."
        )

    def remove_model(self):
        selected_items = self.model_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a model to remove.")
            return

        selected_index = self.model_list.row(selected_items[0])
        model_name = config.custom_models[selected_index]["model_name"]
        del config.custom_models[selected_index]
        config.models = config.DEFAULT_MODELS + config.custom_models
        config.save_custom_models()
        self.refresh_model_list()
        self.clear_inputs()
        QMessageBox.information(
            self, "Model Removed", f"Model '{model_name}' has been removed successfully."
        )

    def clear_inputs(self):
        self.model_name_input.clear()
        self.model_id_input.clear()
        self.model_type_input.setCurrentIndex(0)
        self.repo_id_input.clear()
        self.filename_input.clear()
