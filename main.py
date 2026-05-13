from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
from db.database import engine, Base
import db.models
from api import auth, analysis, history

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando Nevo API...")
    Base.metadata.create_all(bind=engine)
    logger.info("Banco de dados pronto!")
    yield
    logger.info("Nevo API encerrada.")

app = FastAPI(
    title="Nevo API",
    description="Sistema de análise dermatológica com IA — TCC Ciência da Computação",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,     prefix="/auth",    tags=["Autenticação"])
app.include_router(analysis.router, prefix="/analyze", tags=["Análise"])
app.include_router(history.router,  prefix="/history", tags=["Histórico"])

@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0", "model": "MobileNetV2"}