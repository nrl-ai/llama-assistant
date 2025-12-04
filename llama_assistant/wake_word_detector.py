import pyaudio
import numpy as np
from openwakeword.model import Model
from openwakeword.utils import download_models
from PyQt6.QtCore import QThread, pyqtSignal
import time

from llama_assistant.utils import get_resource_path


class WakeWordDetector(QThread):
    wakeword_detected = pyqtSignal(str)

    def __init__(self, chunk_size=1280, inference_framework="onnx"):
        super().__init__()
        self.chunk_size = chunk_size
        self.inference_framework = inference_framework
        self.rate = 16000
        self.format = pyaudio.paInt16
        self.channels = 1
        self.running = False

        self.audio = pyaudio.PyAudio()
        self.mic_stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk_size,
        )

        self.owwModel = None
        self.n_models = 0

    def load_model(self):
        path = get_resource_path("llama_assistant/resources/wk_hey_llama.onnx")
        self.owwModel = Model(
            wakeword_models=[path],
            inference_framework=self.inference_framework,
        )
        self.n_models = len(self.owwModel.models.keys())

    def unload_model(self):
        self.owwModel = None
        self.n_models = 0

    def run(self):
        self.running = True
        download_models()
        self.load_model()
        while self.running:
            try:
                audio = np.frombuffer(self.mic_stream.read(self.chunk_size), dtype=np.int16)
                prediction = self.owwModel.predict(audio)
                self.process_prediction(prediction)
                time.sleep(0.01)  # Small delay to prevent CPU overuse
            except Exception as e:
                print(f"Error: {e}")
                self.stop()
        self.unload_model()

    def process_prediction(self, prediction):
        for mdl, scores in self.owwModel.prediction_buffer.items():
            if scores[-1] > 0.5:
                self.wakeword_detected.emit(mdl)
                print(f"Wakeword detected: {mdl}")

    def stop(self):
        self.running = False
        self.wait()

    def print_results(self):
        if not self.owwModel:
            print("Model not loaded")
            return

        n_spaces = 16
        output_string_header = """
            Model Name         | Score | Wakeword Status
            --------------------------------------
            """

        for mdl in self.owwModel.prediction_buffer.keys():
            scores = list(self.owwModel.prediction_buffer[mdl])
            curr_score = format(scores[-1], ".20f").replace("-", "")

            output_string_header += f"""{mdl}{" "*(n_spaces - len(mdl))}   | {curr_score[0:5]} | {"--"+" "*20 if scores[-1] <= 0.5 else "Wakeword Detected!"}
            """

        print("\033[F" * (4 * self.n_models + 1))
        print(output_string_header, "                             ", end="\r")
