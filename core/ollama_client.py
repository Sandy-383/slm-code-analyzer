import json
import requests
from typing import Generator

OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "deepseek-r1:8b"


def is_ollama_running() -> bool:
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3)
        return resp.status_code == 200
    except requests.ConnectionError:
        return False


def list_models() -> list[str]:
    resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags")
    resp.raise_for_status()
    return [m["name"] for m in resp.json().get("models", [])]


def generate(
    prompt: str,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.2,
    stream: bool = False,
) -> str:
    """Send a prompt to Ollama and return the full response text."""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": stream,
        "options": {
            "temperature": temperature,
            "num_predict": 2048,
        },
    }

    if stream:
        return _stream_generate(payload)

    resp = requests.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json=payload,
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json().get("response", "")


def _stream_generate(payload: dict) -> Generator[str, None, None]:
    with requests.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json={**payload, "stream": True},
        stream=True,
        timeout=120,
    ) as resp:
        resp.raise_for_status()
        for line in resp.iter_lines():
            if line:
                chunk = json.loads(line)
                yield chunk.get("response", "")
                if chunk.get("done"):
                    break
