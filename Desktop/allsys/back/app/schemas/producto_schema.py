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


# Un esquema genérico para Categoría y Marca (solo id y nombre)
class SimpleRef(BaseModel):
    id: int
    nombre: str

# El esquema de un producto individual en la lista
class ProductoItemList(BaseModel):
    id: int
    nombre: str
    sku: str
    tipo: str
    categoria: Optional[SimpleRef] = None
    marca: Optional[SimpleRef] = None
    imagen: Optional[str] = None
    stock_total: int
    precio_min: Optional[float] = None
    precio_max: Optional[float] = None
    colores: List[str] = []
    canales: Optional[dict] = None

# El esquema final paginado
class PaginatedProductosResponse(BaseModel):
    total: int
    items: List[ProductoItemList]