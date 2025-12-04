<p align="center">
  <img alt="Llama Assistant" style="width: 128px; max-width: 100%; height: auto;" src="https://raw.githubusercontent.com/nrl-ai/llama-assistant/refs/heads/main/logo.png"/>
  <h1 align="center">Llama Assistant</h1>
  <p align="center">Local AI Assistant That Respects Your Privacy! 🔒</p>
<p align="center"><b>Website:</b> <a href="https://llama-assistant.nrl.ai/" target="_blank">llama-assistant.nrl.ai</a></p>
</p>

[![Llama Assistant](https://user-images.githubusercontent.com/18329471/234640541-a6a65fbc-d7a5-4ec3-9b65-55305b01a7aa.png)](https://www.youtube.com/watch?v=kyRf8maKuDc)

![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Llama 3](https://img.shields.io/badge/Llama-3-green.svg)
![DeepSeek](https://img.shields.io/badge/DeepSeek-R1-blue.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Version](https://img.shields.io/badge/version-0.1.0-red.svg)
![Stars](https://img.shields.io/github/stars/nrl-ai/llama-assistant.svg)
![Forks](https://img.shields.io/github/forks/nrl-ai/llama-assistant.svg)
![Issues](https://img.shields.io/github/issues/nrl-ai/llama-assistant.svg)
[![Downloads](https://static.pepy.tech/badge/llama-assistant)](https://pepy.tech/project/llama-assistant)
[![Downloads](https://static.pepy.tech/badge/llama-assistant/month)](https://pepy.tech/project/llama-assistant)

<a href="https://www.producthunt.com/products/llama-assistant/reviews?utm_source=badge-product_review&utm_medium=badge&utm_souce=badge-llama&#0045;assistant" target="_blank"><img src="https://api.producthunt.com/widgets/embed-image/v1/product_review.svg?product_id=610711&theme=light" alt="Llama&#0032;Assistant - Local&#0032;AI&#0032;Assistant&#0032;That&#0032;Respects&#0032;Your&#0032;Privacy&#0033;&#0032;🔒 | Product Hunt" style="width: 250px; height: 54px;" width="250" height="54" /></a>

AI-powered assistant to help you with your daily tasks, powered by Llama 3.2. It can recognize your voice, process natural language, and perform various actions based on your commands: summarizing text, rephrasing sentences, answering questions, writing emails, and more.

This assistant can run offline on your local machine, and it respects your privacy by not sending any data to external servers.

[![Screenshot](https://raw.githubusercontent.com/nrl-ai/llama-assistant/refs/heads/main/screenshot.png)](https://www.youtube.com/watch?v=kyRf8maKuDc)

https://github.com/user-attachments/assets/af2c544b-6d46-4c44-87d8-9a051ba213db

![Settings](https://raw.githubusercontent.com/nrl-ai/llama-assistant/refs/heads/main/docs/custom-models.png)

## Supported Models

- 📝 Text-only models:
  - [Llama 3.2](https://github.com/facebookresearch/llama) - 1B, 3B (4/8-bit quantized).
  - [Qwen2.5-0.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF) (4-bit quantized).
  - [Qwen2.5-1.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF) (4-bit quantized).
  - [gemma-2-2b-it](https://huggingface.co/lmstudio-community/gemma-2-2b-it-GGUF-Q4_K_M) (4-bit quantized).
  - And other models that [LlamaCPP](https://github.com/ggerganov/llama.cpp) supports via custom models. [See the list](https://github.com/ggerganov/llama.cpp).

- 🧠 Text-only with reasoning models:
  - [DeepSeek-R1-Distill-Qwen-1.5B](https://huggingface.co/bartowski/DeepSeek-R1-Distill-Qwen-1.5B-GGUF) (4/6-bit quantized).
  - [DeepSeek-R1-Distill-Llama-8B](https://huggingface.co/bartowski/DeepSeek-R1-Distill-Llama-8B-GGUF) (4-bit quantized).

- 🖼️ Multimodal models:
  - [Moondream2](https://huggingface.co/vikhyatk/moondream2).
  - [MiniCPM-v2.6](https://huggingface.co/openbmb/MiniCPM-V-2_6-gguf).
  - [LLaVA 1.5/1.6](https://llava-vl.github.io/).
  - Besides supported models, you can try other variants via custom models.

## TODO

- [x] 🖼️ Support multimodal model: [moondream2](https://huggingface.co/vikhyatk/moondream2).
- [x] 🗣️ Add wake word detection: "Hey Llama!".
- [x] 🛠️ Custom models: Add support for custom models.
- [x] 📚 Support 5 other text models.
- [x] 🖼️ Support 5 other multimodal models.
- [x] ⚡ Streaming support for response.
- [x] 🎙️ Add offline STT support: WhisperCPP.
- [x] 🧠 Knowledge database: LlamaIndex
- [x] ⌖ Screen Spot: Screen capture and analyze with OCR
- [ ] 🔌 Plugin system for extensibility.
- [ ] 📰 News and weather updates.
- [ ] 📧 Email integration with Gmail and Outlook.
- [ ] 📝 Note-taking and task management.
- [ ] 🎵 Music player and podcast integration.
- [ ] 🤖 Workflow with multiple agents.
- [ ] 🌐 Multi-language support: English, Spanish, French, German, etc.
- [ ] 📦 Package for Windows, Linux, and macOS.
- [ ] 🔄 Automated tests and CI/CD pipeline.

## Features

- 🎙️ Voice recognition for hands-free interaction.
- 💬 Natural language processing with Llama 3.2.
- 🖼️ Image analysis capabilities (TODO).
- ⚡ Global hotkey for quick access (Cmd+Shift+Space on macOS).
- 🎨 Customizable UI with adjustable transparency.
- ⚙️ **Custom Actions**: Create, edit, hide, and reorder action buttons with custom prompts. [Learn more](docs/custom-actions.md)

**Note:** This project is a work in progress, and new features are being added regularly.

## Technologies Used

- ![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white)
- ![Llama](https://img.shields.io/badge/Llama-3.2-yellow?style=flat-square&logo=meta&logoColor=white)
- ![SpeechRecognition](https://img.shields.io/badge/SpeechRecognition-3.8-green?style=flat-square&logo=google&logoColor=white)
- ![yt](https://img.shields.io/badge/PyQt-5-41CD52?style=flat-square&logo=qt&logoColor=white)

## Installation

**Recommended Python Version:** 3.10.

**Install PortAudio:**

<details>
Install `PortAudio`_. This is required by the `PyAudio`_ library to stream
audio from your computer's microphone. PyAudio depends on PortAudio for cross-platform compatibility, and is installed differently depending on the
platform.

* For Mac OS X, you can use `Homebrew`_::

      brew install portaudio

  **Note**: if you encounter an error when running `pip install` that indicates
  it can't find `portaudio.h`, try running `pip install` with the following
  flags::

      pip install --global-option='build_ext' \
          --global-option='-I/usr/local/include' \
          --global-option='-L/usr/local/lib' \
          pyaudio

* For Debian / Ubuntu Linux::

      apt-get install portaudio19-dev python3-all-dev

* Windows may work without having to install PortAudio explicitly (it will get
  installed with PyAudio).

For more details, see the `PyAudio installation`_ page.


.. _PyAudio: https://people.csail.mit.edu/hubert/pyaudio/
.. _PortAudio: http://www.portaudio.com/
.. _PyAudio installation:
  https://people.csail.mit.edu/hubert/pyaudio/#downloads
.. _Homebrew: http://brew.sh
</details>

**On Windows: Installing the MinGW-w64 toolchain**

<details>
- Download and install with instructions from [here](https://code.visualstudio.com/docs/cpp/config-mingw).
- Direct download link: [MinGW-w64](https://github.com/msys2/msys2-installer/releases/download/2024-01-13/msys2-x86_64-20240113.exe).
</details>

**Install from PyPI:**

```bash
pip install pyaudio
pip install git+https://github.com/stlukey/whispercpp.py
pip install llama-assistant
```

**Or install from source:**

<details>

1. Clone the repository:

```bash
git clone https://github.com/nrl-ai/llama-assistant.git
cd llama-assistant
```

2. Install the required dependencies and install the package:

```bash
pip install pyaudio
pip install git+https://github.com/stlukey/whispercpp.py
pip install -r requirements.txt
pip install .
```

</details>

**Speed Hack for Apple Silicon (M1, M2, M3) users:** 🔥🔥🔥

<details>

- Install Xcode:

```bash
# check the path of your xcode install
xcode-select -p

# xcode installed returns
# /Applications/Xcode-beta.app/Contents/Developer

# if xcode is missing then install it... it takes ages;
xcode-select --install
```

- Build `llama-cpp-python` with METAL support:

```bash
pip uninstall llama-cpp-python -y
CMAKE_ARGS="-DGGML_METAL=on" pip install -U llama-cpp-python --no-cache-dir

# You should now have llama-cpp-python v0.1.62 or higher installed
# llama-cpp-python         0.1.68
```

</details>

## Usage

Run the assistant using the following command:

```bash
llama-assistant

# Or with a
python -m llama_assistant.main
```

Use the global hotkey (default: `Cmd+Shift+Space`) to quickly access the assistant from anywhere on your system.

## Configuration

The assistant's settings can be customized by editing the `settings.json` file located in your home directory: `~/llama_assistant/settings.json`.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the GPLv3 License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- This project uses [llama.cpp](https://github.com/ggerganov/llama.cpp), [llama-cpp-python](https://github.com/abetlen/llama-cpp-python) for running large language models. The default model is [Llama 3.2](https://github.com/facebookresearch/llama) by Meta AI Research.
- Speech recognition is powered by [whisper.cpp](hhttps://github.com/ggerganov/whisper.cpp) and [whispercpp.py](https://github.com/stlukey/whispercpp.py).

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=nrl-ai/llama-assistant&type=Date)](https://star-history.com/#nrl-ai/llama-assistant&Date)

## Contact

- **Website:** [https://llama-assistant.nrl.ai/](https://llama-assistant.nrl.ai/).
- **Contact Form:** [https://www.nrl.ai/contact](https://www.nrl.ai/contact).
