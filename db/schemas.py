from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "patient"

    @field_validator("password")
    @classmethod
    def senha_forte(cls, v):
        if len(v) < 8:
            raise ValueError("Senha deve ter no mínimo 8 caracteres.")
        if not any(c.isdigit() for c in v):
            raise ValueError("Senha deve conter ao menos um número.")
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int; name: str; email: str; role: str; is_active: bool; created_at: datetime
    class Config: from_attributes = True

class TokenResponse(BaseModel):
    access_token: str; token_type: str = "bearer"; user: UserResponse

class AnalysisResponse(BaseModel):
    id: int; condition: str; risk_level: str; confidence: float
    description: str; recommendation: str; model_version: str; created_at: datetime
    class Config: from_attributes = True

class FeedbackCreate(BaseModel):
    analysis_id: int; correct: bool
    correct_label: Optional[str] = None; notes: Optional[str] = None

class StatsResponse(BaseModel):
    total: int; by_risk: dict; by_condition: dict; avg_confidence: float