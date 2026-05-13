from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base

class User(Base):
    __tablename__ = "users"
    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String(100), nullable=False)
    email         = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role          = Column(String(20), default="patient")
    is_active     = Column(Boolean, default=True)
    created_at    = Column(DateTime, server_default=func.now())
    analyses      = relationship("Analysis", back_populates="user", cascade="all, delete")

class Analysis(Base):
    __tablename__ = "analyses"
    id             = Column(Integer, primary_key=True, index=True)
    user_id        = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    condition      = Column(String(100), nullable=False)
    risk_level     = Column(String(20), nullable=False)
    confidence     = Column(Float, nullable=False)
    description    = Column(Text)
    recommendation = Column(Text)
    image_path     = Column(String(255))
    model_version  = Column(String(20), default="2.0.0")
    created_at     = Column(DateTime, server_default=func.now())
    user           = relationship("User", back_populates="analyses")
    feedback       = relationship("Feedback", back_populates="analysis", uselist=False)

class Feedback(Base):
    __tablename__ = "feedbacks"
    id            = Column(Integer, primary_key=True, index=True)
    analysis_id   = Column(Integer, ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False)
    correct       = Column(Boolean)
    correct_label = Column(String(100))
    notes         = Column(Text)
    created_at    = Column(DateTime, server_default=func.now())
    analysis      = relationship("Analysis", back_populates="feedback")