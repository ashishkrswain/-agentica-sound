from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from backend.core.llm_brain import musical_intelligence

router = APIRouter(prefix="/api/intelligence", tags=["intelligence"])

class ConfigUpdateRequest(BaseModel):
    provider: Optional[str] = None
    nvidia_api_key: Optional[str] = None
    nvidia_model: Optional[str] = None
    openai_api_key: Optional[str] = None
    openai_base_url: Optional[str] = None
    openai_model: Optional[str] = None
    ollama_url: Optional[str] = None
    ollama_model: Optional[str] = None
    lm_studio_url: Optional[str] = None
    lm_studio_model: Optional[str] = None

class TestConnectionRequest(BaseModel):
    provider: str

class ComposeRequest(BaseModel):
    prompt: str
    genre_hint: Optional[str] = None

@router.get("/config")
def get_config():
    return musical_intelligence.get_config()

@router.post("/config")
def update_config(req: ConfigUpdateRequest):
    musical_intelligence.update_config(req.dict(exclude_none=True))
    return {"success": True, "config": musical_intelligence.get_config()}

@router.post("/test")
def test_connection(req: TestConnectionRequest):
    return musical_intelligence.test_connection(req.provider)

@router.post("/compose")
def compose_song(req: ComposeRequest):
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt is required for musical composition")
    
    blueprint = musical_intelligence.compose_blueprint(req.prompt, req.genre_hint)
    return {
        "success": True,
        "blueprint": blueprint
    }
