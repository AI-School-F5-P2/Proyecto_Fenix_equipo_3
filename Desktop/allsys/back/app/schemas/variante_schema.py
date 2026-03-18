from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

from app.schemas.stock_schema import StockSchema

class TallaCreate(BaseModel):
    talla: str
    stock: int

class ImagenVarianteCreate(BaseModel):
    url: str

class VarianteCreate(BaseModel):
    color: str
    color_nombre: str
    precio: float | None = None
    descuento: float | None = None
    tallas: list[TallaCreate]


class VarianteSchema(BaseModel):
    temp_id: Optional[str] = None
    id: Optional[int] = None # Útil para la edición
    
    # Reglas estrictas:
    identidad_variante: str = Field(..., min_length=1, description="El color o material es obligatorio")
    hex_identidad: str = Field(..., min_length=1)
    ubicacion: str = Field(..., min_length=1, description="La ubicación es obligatoria")
    descripcion: str
    imagenes: List[str] = []
    orden: Optional[int] = 0
    stocks: List[StockSchema] = Field(..., min_items=1)