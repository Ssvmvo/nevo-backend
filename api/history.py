from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List
from db.database import get_db
from db.models import Analysis
from db.schemas import AnalysisResponse, StatsResponse
from core.security import get_current_user

router = APIRouter()

@router.get("/", response_model=List[AnalysisResponse])
def history(skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100),
            db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return db.query(Analysis).filter(Analysis.user_id == current_user["id"])\
             .order_by(Analysis.created_at.desc()).offset(skip).limit(limit).all()

@router.get("/stats", response_model=StatsResponse)
def stats(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    analyses = db.query(Analysis).filter(Analysis.user_id == current_user["id"]).all()
    if not analyses:
        return {"total":0,"by_risk":{},"by_condition":{},"avg_confidence":0.0}
    by_risk = {}; by_cond = {}; total_conf = 0
    for a in analyses:
        by_risk[a.risk_level] = by_risk.get(a.risk_level, 0) + 1
        by_cond[a.condition]  = by_cond.get(a.condition, 0)  + 1
        total_conf           += a.confidence
    return {"total": len(analyses), "by_risk": by_risk, "by_condition": by_cond,
            "avg_confidence": round(total_conf / len(analyses), 2)}

@router.delete("/{analysis_id}")
def delete(analysis_id: int, db: Session = Depends(get_db),
           current_user: dict = Depends(get_current_user)):
    a = db.query(Analysis).filter(Analysis.id == analysis_id,
                                  Analysis.user_id == current_user["id"]).first()
    if not a:
        raise HTTPException(status_code=404, detail="Análise não encontrada.")
    db.delete(a); db.commit()
    return {"message": "Análise removida."}