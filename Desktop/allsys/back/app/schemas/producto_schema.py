from typing import List, Optional
from pydantic import BaseModel
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

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
    precio_compra: float  # ✨ CAMBIO: Antes era precio_min
    precio_venta: float   # ✨ CAMBIO: Antes era precio_max
    colores: List[str] = []  # <--- Al poner = [] ya no es obligatorio que el repo lo envíe
    tallas: List[str] = []
    canales: Optional[dict] = None

# El esquema final paginado
class PaginatedProductosResponse(BaseModel):
    total: int
    items: List[ProductoItemList]




class StockIndividualItemList(BaseModel):
    # IDs y SKUs
    stock_id: int
    stock_sku: str
    variante_id: int
    producto_id: int
    producto_nombre: str
    
    # Categoría y Marca
    categoria: Optional[Dict[str, Any]]
    marca: Optional[Dict[str, Any]]
    
    # Identidad visual (El estilo/color)
    hex_identidad: str
    identidad_variante: str
    imagen_cover: Optional[str]
    
    # El corazón del stock (Tallas, etc)
    etiqueta: Optional[str]
    talla: Optional[str] # Extraído directamente de los atributos
    atributos_extra: Dict[str, str] # Otros atributos (peso, formato, etc.)
    
    # Cantidades y Dinero
    stock_disponible: int
    precio_compra: float
    precio_venta: float
    descuento: float
    
    # Ubicación física y digital
    ubicacion_almacen: Optional[str]
    canales: Dict[str, bool]

class PaginatedStockResponse(BaseModel):
    total: int
    items: List[StockIndividualItemList]



    
    # cantidad: int
    
    # precio_compra: float
    # precio_venta: float
    # descuento: float = 0
    # ubicacion: Optional[str] = ""
    # proveedor_id: Optional[int] = None
    # proveedor_nombre_nuevo: Optional[str] = None
    # publicar_web: bool = False
    # publicar_vinted: bool = False
    # publicar_wallapop: bool = False