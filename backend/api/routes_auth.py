from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional
from backend.core.security import verify_credentials, generate_token, verify_token
from backend.config import DEFAULT_USER

router = APIRouter(prefix="/api/auth", tags=["auth"])

class LoginRequest(BaseModel):
    username: str
    password: str
    remember: Optional[bool] = True

class UserResponse(BaseModel):
    username: str
    display_name: str
    role: str
    hardware_plan: str
    token: str

@router.post("/login")
def login(req: LoginRequest):
    user = req.username.strip()
    if not user:
        raise HTTPException(status_code=400, detail="Username is required")
    if not verify_credentials(user, req.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = generate_token(user)
    return {
        "success": True,
        "token": token,
        "user": {
            "username": user,
            "display_name": user.replace("_", " ").title(),
            "role": "Studio Master",
            "hardware_plan": "NVIDIA GTX 1650 (Local GPU)"
        }
    }

@router.get("/me")
def get_current_user(authorization: Optional[str] = Header(None)):
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
    
    if not token:
        # Fallback to local default user for desktop studio convenience
        return {
            "authenticated": True,
            "user": {
                "username": DEFAULT_USER,
                "display_name": DEFAULT_USER.replace("_", " ").title(),
                "role": "Studio Master",
                "hardware_plan": "NVIDIA GTX 1650 (Local GPU)"
            }
        }

    username = verify_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    return {
        "authenticated": True,
        "user": {
            "username": username,
            "display_name": username.replace("_", " ").title(),
            "role": "Studio Master",
            "hardware_plan": "NVIDIA GTX 1650 (Local GPU)"
        }
    }

@router.post("/logout")
def logout():
    return {"success": True, "message": "Signed out successfully"}
