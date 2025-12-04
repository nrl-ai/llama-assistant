from typing import Set, Optional, Dict
from PyQt6.QtCore import (
    QThread,
    pyqtSignal,
)
from llama_assistant.model_handler import handler as model_handler
from llama_assistant.ocr_engine import ocr_engine


class ProcessingThread(QThread):
    preloader_signal = pyqtSignal(str)
    update_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(
        self,
        model: str,
        generation_setting: Dict,
        rag_setting: Dict,
        prompt: str,
        lookup_files: Optional[Set[str]] = None,
        image: str = None,
        ocr_img_path: str = None,
    ):
        super().__init__()
        self.model = model
        self.generation_setting = generation_setting
        self.rag_setting = rag_setting
        self.prompt = prompt
        self.image = image
        self.lookup_files = lookup_files
        self.preloading = False
        self.ocr_img_path = ocr_img_path

    def run(self):
        if self.ocr_img_path:
            self.set_preloading(True, "Thinking ....")
            ocr_output = ocr_engine.perform_ocr(self.ocr_img_path, streaming=False)
            ocr_output = f"Here is the OCR result:\n{ocr_output}\n"
            self.prompt = ocr_output + self.prompt
            print("Prompt with OCR context:", self.prompt)

        output = model_handler.chat_completion(
            self.model,
            self.generation_setting,
            self.rag_setting,
            self.prompt,
            image=self.image,
            lookup_files=self.lookup_files,
            stream=True,
            processing_thread=self,
        )
        full_response_str = ""
        for chunk in output:
            delta = chunk["choices"][0]["delta"]
            if "role" in delta:
                print(delta["role"], end=": ")
            elif "content" in delta:
                print(delta["content"], end="")
                full_response_str += delta["content"]
                self.update_signal.emit(delta["content"])

        # Add both user message and assistant response to history together
        model_handler.add_conversation_turn(self.prompt, full_response_str, self.image)
        self.finished_signal.emit()

    def clear_chat_history(self):
        model_handler.clear_chat_history()
        self.finished_signal.emit()

    def emit_preloading_message(self, message: str):
        self.preloader_signal.emit(message)

    def set_preloading(self, preloading: bool, message: str):
        self.preloading = preloading
        self.emit_preloading_message(message)

    def is_preloading(self):
        return self.preloading


class OCRThread(QThread):
    preloader_signal = pyqtSignal(str)
    update_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, img_path: str, streaming: bool = False):
        super().__init__()
        self.img_path = img_path
        self.preloading = False
        self.streaming = streaming
        self.is_ocr_done = False

    def emit_preloading_message(self, message: str):
        self.preloader_signal.emit(message)

    def set_preloading(self, preloading: bool, message: str):
        self.preloading = preloading
        self.emit_preloading_message(message)

    def is_preloading(self):
        return self.preloading

    def run(self):
        output = ocr_engine.perform_ocr(
            self.img_path, streaming=self.streaming, processing_thread=self
        )
        full_response_str = "Here is the OCR result:\n"
        self.is_ocr_done = True

        if not self.streaming and type(output) == str:
            self.update_signal.emit(full_response_str + output)
            return

        self.update_signal.emit(full_response_str)
        for chunk in output:
            self.update_signal.emit(chunk)
            full_response_str += chunk

        model_handler.update_chat_history("OCR this image:", "user")
        model_handler.update_chat_history(full_response_str, "assistant")
        self.finished_signal.emit()
