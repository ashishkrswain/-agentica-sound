from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.core.model_manager import model_manager

router = APIRouter(prefix="/api/models", tags=["models"])

class DownloadModelRequest(BaseModel):
    repo_id: str

class HardwareModeRequest(BaseModel):
    mode: str

class ActivateModelRequest(BaseModel):
    model_id: str

@router.get("/installed")
def list_installed_models():
    return {
        "models": model_manager.list_installed_models(),
        "runtime": model_manager.get_runtime_status()
    }

@router.get("/status")
def get_model_status():
    return model_manager.get_runtime_status()

@router.post("/download")
def download_model(req: DownloadModelRequest):
    try:
        model_manager.download_huggingface_model(req.repo_id)
        return {"success": True, "message": f"Download initiated for {req.repo_id}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/hardware-mode")
def set_hardware_mode(req: HardwareModeRequest):
    try:
        model_manager.set_hardware_mode(req.mode)
        return {"success": True, "mode": req.mode}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/activate")
def activate_model(req: ActivateModelRequest):
    model_manager.set_active_model(req.model_id)
    return {"success": True, "active_model": req.model_id}
