from typing import List, Optional
from pydantic import BaseModel

class TallaCreate(BaseModel):
    talla: str
    stock: int

class VarianteCreate(BaseModel):
    color: str
    colorNombre: str
    precio: float
    descuento: float
    tallas: List[TallaCreate]

class ProductoCreate(BaseModel):
    nombre: str
    descripcion: str
    precio: float
    categoria_id: int
    marca_id: int
    variantes: List[VarianteCreate]
