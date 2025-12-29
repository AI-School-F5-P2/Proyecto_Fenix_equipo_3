from pydantic import BaseModel
from typing import List, Optional

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
