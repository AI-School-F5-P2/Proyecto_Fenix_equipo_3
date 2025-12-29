from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_session
from app.schemas.categoria_schema import CategoriaCreate, CategoriaOut
from app.repositories.categoria_repo import crear_categoria, listar_categorias, listar_subcategorias
from app.api.deps import get_current_admin  # proteger rutas admin

categorias_routers = APIRouter(prefix="/categorias", tags=["Categorías"])

# Crear categoría o subcategoría
@categorias_routers.post("/", response_model=CategoriaOut)
def crear_categoria_endpoint(
    categoria_in: CategoriaCreate,
    db: Session = Depends(get_session),
    current_admin=Depends(get_current_admin)
):
    return crear_categoria(db, categoria_in)

# Listar categorías raíz
@categorias_routers.get("/", response_model=List[CategoriaOut])
def listar_categorias_endpoint(db: Session = Depends(get_session)):
    return listar_categorias(db)

# Listar subcategorías de una categoría
@categorias_routers.get("/{categoria_id}/subcategorias", response_model=List[CategoriaOut])
def listar_subcategorias_endpoint(categoria_id: int, db: Session = Depends(get_session)):
    return listar_subcategorias(db, categoria_id)
