import json
from pathlib import Path
import pathlib

DEFAULT_LAUNCH_SHORTCUT = "<cmd>+<shift>+<space>"
DEFAULT_SETTINGS = {
    "shortcut": DEFAULT_LAUNCH_SHORTCUT,
    "color": "#1E1E1E",
    "transparency": 95,
    "text_model": "unsloth/gemma-3n-E4B-it-GGUF-Q4_K_M",
    "multimodal_model": "vikhyatk/moondream2",
    "text_reasoning_model": "bartowski/DeepSeek-R1-Distill-Qwen-1.5B-GGUF-Q4_K_M",
    "reasoning_enabled": False,
    "hey_llama_chat": False,
    "hey_llama_mic": False,
    "generation": {
        "context_len": 4096,
        "max_output_tokens": 1024,
        "top_k": 40,
        "top_p": 0.95,
        "temperature": 0.2,
    },
    "rag": {
        "embed_model_name": "BAAI/bge-base-en-v1.5",
        "chunk_size": 256,
        "chunk_overlap": 128,
        "max_retrieval_top_k": 3,
        "similarity_threshold": 0.6,
    },
}

VALIDATOR = {
    "generation": {
        "context_len": {"type": "int", "min": 2048},
        "max_output_tokens": {"type": "int", "min": 512, "max": 2048},
        "top_k": {"type": "int", "min": 1, "max": 100},
        "top_p": {"type": "float", "min": 0, "max": 1},
        "temperature": {"type": "float", "min": 0, "max": 1},
    },
    "rag": {
        "chunk_size": {"type": "int", "min": 64, "max": 512},
        "chunk_overlap": {"type": "int", "min": 64, "max": 256},
        "max_retrieval_top_k": {"type": "int", "min": 1, "max": 5},
        "similarity_threshold": {"type": "float", "min": 0, "max": 1},
    },
}

DEFAULT_EMBEDING_MODELS = [
    "BAAI/bge-small-en-v1.5",
    "BAAI/bge-base-en-v1.5",
    "BAAI/bge-large-en-v1.5",
]

DEFAULT_ACTIONS = [
    {
        "id": "summarize",
        "label": "Summarize",
        "prompt": "Please provide a concise summary of the following text:",
        "visible": True,
        "order": 0,
    },
    {
        "id": "rephrase",
        "label": "Rephrase",
        "prompt": "Please rephrase the following text in a different way while keeping the same meaning:",
        "visible": True,
        "order": 1,
    },
    {
        "id": "fix_grammar",
        "label": "Fix Grammar",
        "prompt": "Please correct any grammar, spelling, and punctuation errors in the following text:",
        "visible": True,
        "order": 2,
    },
    {
        "id": "brainstorm",
        "label": "Brainstorm",
        "prompt": "Please brainstorm creative ideas related to the following topic:",
        "visible": True,
        "order": 3,
    },
    {
        "id": "write_email",
        "label": "Write Email",
        "prompt": "Please write a professional email about the following topic:",
        "visible": True,
        "order": 4,
    },
]

DEFAULT_MODELS = [
    # LLMs
    {
        "model_name": "gemma-3n-E4B-it-Q4_K_M-GGUF",
        "model_id": "unsloth/gemma-3n-E4B-it-GGUF-Q4_K_M",
        "model_type": "text",
        "model_path": None,
        "repo_id": "unsloth/gemma-3n-E4B-it-GGUF",
        "filename": "gemma-3n-E4B-it-Q4_K_M.gguf",
    },
    {
        "model_name": "Llama-3.2-1B-Instruct-Q4_K_M-GGUF",
        "model_id": "hugging-quants/Llama-3.2-1B-Instruct-Q4_K_M-GGUF",
        "model_type": "text",
        "model_path": None,
        "repo_id": "hugging-quants/Llama-3.2-1B-Instruct-Q4_K_M-GGUF",
        "filename": "*q4_k_m.gguf",
    },
    {
        "model_name": "Llama-3.2-1B-Instruct-Q8_0-GGUF",
        "model_id": "hugging-quants/Llama-3.2-1B-Instruct-Q8_0-GGUF",
        "model_type": "text",
        "model_path": None,
        "repo_id": "hugging-quants/Llama-3.2-1B-Instruct-Q8_0-GGUF",
        "filename": "*q8_0.gguf",
    },
    {
        "model_name": "Llama-3.2-3B-Instruct-Q4_K_M-GGUF",
        "model_id": "hugging-quants/Llama-3.2-3B-Instruct-Q4_K_M-GGUF",
        "model_type": "text",
        "model_path": None,
        "repo_id": "hugging-quants/Llama-3.2-3B-Instruct-Q4_K_M-GGUF",
        "filename": "*q4_k_m.gguf",
    },
    {
        "model_name": "Llama-3.2-3B-Instruct-Q8_0-GGUF",
        "model_id": "hugging-quants/Llama-3.2-3B-Instruct-Q8_0-GGUF",
        "model_type": "text",
        "model_path": None,
        "repo_id": "hugging-quants/Llama-3.2-3B-Instruct-Q8_0-GGUF",
        "filename": "*q8_0.gguf",
    },
    {
        "model_name": "Qwen2.5-0.5B-Instruct-GGUF",
        "model_id": "Qwen/Qwen2.5-0.5B-Instruct-GGUF-q4_k_m",
        "model_type": "text",
        "model_path": None,
        "repo_id": "Qwen/Qwen2.5-0.5B-Instruct-GGUF",
        "filename": "*q4_k_m.gguf",
    },
    {
        "model_name": "Qwen2.5-1.5B-Instruct-GGUF",
        "model_id": "Qwen/Qwen2.5-1.5B-Instruct-GGUF-q4_k_m",
        "model_type": "text",
        "model_path": None,
        "repo_id": "Qwen/Qwen2.5-1.5B-Instruct-GGUF",
        "filename": "*q4_k_m.gguf",
    },
    {
        "model_name": "gemma-2-2b-it-GGUF-Q4_K_M",
        "model_id": "lmstudio-community/gemma-2-2b-it-GGUF-Q4_K_M",
        "model_type": "text",
        "model_path": None,
        "repo_id": "lmstudio-community/gemma-2-2b-it-GGUF",
        "filename": "gemma-2-2b-it-Q4_K_M.gguf",
    },
    # Reasoning Models
    {
        "model_name": "DeepSeek-R1-Distill-Qwen-1.5B-GGUF",
        "model_id": "bartowski/DeepSeek-R1-Distill-Qwen-1.5B-GGUF-Q4_K_M",
        "model_type": "text-reasoning",
        "model_path": None,
        "repo_id": "bartowski/DeepSeek-R1-Distill-Qwen-1.5B-GGUF",
        "filename": "DeepSeek-R1-Distill-Qwen-1.5B-Q4_K_M.gguf",
    },
    {
        "model_name": "DeepSeek-R1-Distill-Qwen-1.5B-GGUF",
        "model_id": "bartowski/DeepSeek-R1-Distill-Qwen-1.5B-GGUF-Q6_K",
        "model_type": "text-reasoning",
        "model_path": None,
        "repo_id": "bartowski/DeepSeek-R1-Distill-Qwen-1.5B-GGUF",
        "filename": "DeepSeek-R1-Distill-Qwen-1.5B-Q6_K.gguf",
    },
    {
        "model_name": "DeepSeek-R1-Distill-Llama-8B-GGUF",
        "model_id": "bartowski/DeepSeek-R1-Distill-Llama-8B-GGUF-Q4_K_M",
        "model_type": "text-reasoning",
        "model_path": None,
        "repo_id": "bartowski/DeepSeek-R1-Distill-Llama-8B-GGUF",
        "filename": "DeepSeek-R1-Distill-Llama-8B-Q4_K_M.gguf",
    },
    # VLMs
    {
        "model_name": "Moondream2",
        "model_id": "vikhyatk/moondream2",
        "model_type": "image",
        "model_path": None,
        "repo_id": "vikhyatk/moondream2",
        "filename": "*text-model*",
    },
    {
        "model_name": "Llava-1.5",
        "model_id": "mys/ggml_llava-v1.5-7b/q4_k",
        "model_type": "image",
        "model_path": None,
        "repo_id": "mys/ggml_llava-v1.5-7b",
        "filename": "*q4_k.gguf",
    },
    {
        "model_name": "Llava-1.5",
        "model_id": "mys/ggml_llava-v1.5-7b/f16",
        "model_type": "image",
        "model_path": None,
        "repo_id": "mys/ggml_llava-v1.5-7b",
        "filename": "*f16.gguf",
    },
    {
        "model_name": "MiniCPM-V-2_6-gguf",
        "model_id": "openbmb/MiniCPM-V-2_6-gguf-Q4_K_M",
        "model_type": "image",
        "model_path": None,
        "repo_id": "openbmb/MiniCPM-V-2_6-gguf",
        "filename": "*Q4_K_M.gguf",
    },
    {
        "model_name": "MiniCPM-V-2_6-gguf",
        "model_id": "openbmb/MiniCPM-V-2_6-gguf-Q8_0",
        "model_type": "image",
        "model_path": None,
        "repo_id": "openbmb/MiniCPM-V-2_6-gguf",
        "filename": "*Q8_0.gguf",
    },
]


home_dir = Path.home()
llama_assistant_dir = home_dir / "llama_assistant"
pathlib.Path.mkdir(llama_assistant_dir, parents=True, exist_ok=True)
custom_models_file = llama_assistant_dir / "custom_models.json"
settings_file = llama_assistant_dir / "settings.json"
actions_file = llama_assistant_dir / "actions.json"
document_icon = "llama_assistant/resources/document_icon.png"
ocr_tmp_file = llama_assistant_dir / "ocr_tmp.png"

if custom_models_file.exists():
    with open(custom_models_file, "r") as f:
        try:
            config_data = json.load(f)
        except json.JSONDecodeError:
            config_data = {"custom_models": []}
    custom_models = config_data.get("custom_models", [])
else:
    custom_models = []

models = DEFAULT_MODELS + custom_models

# Save the initial configuration if it doesn't exist
if not custom_models_file.exists():
    config_dir = custom_models_file.parent
    if not config_dir.exists():
        config_dir.mkdir(parents=True)
    with open(custom_models_file, "w") as f:
        json.dump({"custom_models": custom_models}, f, indent=2)


# Save the custom models to the file
def save_custom_models():
    global models
    with open(custom_models_file, "w") as f:
        json.dump({"custom_models": custom_models}, f, indent=2)
    models = DEFAULT_MODELS + custom_models


# Load actions
if actions_file.exists():
    with open(actions_file, "r") as f:
        try:
            actions_data = json.load(f)
        except json.JSONDecodeError:
            actions_data = {"actions": DEFAULT_ACTIONS.copy()}
    actions = actions_data.get("actions", DEFAULT_ACTIONS.copy())
else:
    actions = DEFAULT_ACTIONS.copy()

# Save the initial actions if it doesn't exist
if not actions_file.exists():
    with open(actions_file, "w") as f:
        json.dump({"actions": actions}, f, indent=2)


def save_actions():
    global actions
    with open(actions_file, "w") as f:
        json.dump({"actions": actions}, f, indent=2)
