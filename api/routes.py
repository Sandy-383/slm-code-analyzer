from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from core.input_handler import build_payload
from core.prompt_builder import build_prompt
from core import ollama_client

app = FastAPI(title="SLM Code Analyzer", version="0.1.0")


class AnalyzeRequest(BaseModel):
    code: str
    language: str = "auto"
    model: str = ollama_client.DEFAULT_MODEL
    analyses: list[str] = ["summary", "complexity", "workflow", "optimization"]


@app.get("/health")
def health():
    running = ollama_client.is_ollama_running()
    return {"status": "ok", "ollama": running}


@app.post("/analyze")
def analyze_code(req: AnalyzeRequest):
    if not ollama_client.is_ollama_running():
        raise HTTPException(status_code=503, detail="Ollama is not running. Start it with: ollama serve")

    try:
        payload = build_payload(req.code, req.language, req.analyses)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    prompt = build_prompt(payload)

    try:
        raw_response = ollama_client.generate(prompt, model=req.model)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model error: {str(e)}")

    return {
        "language": payload.language.value,
        "loc": payload.loc,
        "result": raw_response,
    }
