from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_session
from app.repositories import analytics_repo, statistics_repo

analytics_router = APIRouter(prefix="/analytics", tags=["Analytics"])

@analytics_router.get("/dashboard-completo")
def get_stats_avanzadas(
    fecha_inicio: str = None,
    fecha_fin: str = None,
    db: Session = Depends(get_session)
):
    return statistics_repo.obtener_metricas_avanzadas(db, fecha_inicio, fecha_fin)