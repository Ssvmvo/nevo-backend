from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import Analysis, Feedback
from db.schemas import AnalysisResponse, FeedbackCreate
from core.security import get_current_user
from ml.predictor import predictor
import os, uuid

router = APIRouter()
os.makedirs("./uploads", exist_ok=True)

@router.post("/", response_model=AnalysisResponse)
async def analyze(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if file.content_type not in {"image/jpeg", "image/png"}:
        raise HTTPException(status_code=422, detail="Formato inválido. Envie JPG ou PNG.")
    img_bytes = await file.read()
    if len(img_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=422, detail="Imagem muito grande. Máximo 10MB.")
    if len(img_bytes) == 0:
        raise HTTPException(status_code=422, detail="Arquivo vazio.")
    try:
        result = predictor.predict(img_bytes)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Erro interno ao processar imagem.")
    path = f"./uploads/{uuid.uuid4()}.jpg"
    with open(path, "wb") as f:
        f.write(img_bytes)
    analysis = Analysis(user_id=current_user["id"], image_path=path, **result)
    db.add(analysis); db.commit(); db.refresh(analysis)
    return analysis

@router.post("/feedback")
def feedback(payload: FeedbackCreate, db: Session = Depends(get_db),
             current_user: dict = Depends(get_current_user)):
    a = db.query(Analysis).filter(Analysis.id == payload.analysis_id,
                                  Analysis.user_id == current_user["id"]).first()
    if not a:
        raise HTTPException(status_code=404, detail="Análise não encontrada.")
    fb = Feedback(analysis_id=payload.analysis_id, correct=payload.correct,
                  correct_label=payload.correct_label, notes=payload.notes)
    db.add(fb); db.commit()
    return {"message": "Feedback registrado!"}