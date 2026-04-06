from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.database import get_session
from app.repositories import statistics_repo
from typing import Optional

router = APIRouter(prefix="/stats", tags=["Estadísticas Avanzadas"])

@router.get("/dashboard-completo")
def get_stats_avanzadas(
    fecha_inicio: Optional[str] = Query(None),
    fecha_fin: Optional[str] = Query(None),
    db: Session = Depends(get_session)
):
    """
    Este endpoint devuelve TODA la inteligencia de negocio para el periodo seleccionado.
    """
    return statistics_repo.obtener_metricas_avanzadas(db, fecha_inicio, fecha_fin)