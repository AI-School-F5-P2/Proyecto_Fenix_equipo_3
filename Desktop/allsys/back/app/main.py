from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.db.database import Base, engine

# =========================
# ROUTERS (Nombres actualizados)
# =========================
from app.api.v1.auth import auth_routers
from app.api.v1.productos import producto_routers
from app.api.v1.categorias import categorias_routers
from app.api.v1.marcas import marcas_router
from app.api.v1.ventas import venta_router
from app.api.v1.proveedores import proveedores_router

# =========================
# MODELS (Nomenclatura Limpia)
# Importarlos aquí asegura que Base.metadata.create_all los encuentre
# =========================
from app.models.producto_model import Producto  # Cambiado de producto_model
from app.models.variantes_model import Variante
from app.models.stock_model import Stock
from app.models.atributo_model import Atributo, ValorAtributo   # Nuevo archivo de atributos
from app.models.categorias_model import Categoria
from app.models.marcas_model import Marca
from app.models.variante_imagen_model import Imagen
from app.models.ventas_model import Venta, DetalleVenta
from app.models.proveedores_model import Proveedor          # Cambiado de Proveedores (Singular)

app = FastAPI(
    title="Bunglo API",
    version="1.1.0",
    description="E-commerce con arquitectura EAV: Producto -> Variante -> Stock -> Atributos"
)

# =========================
# STARTUP
# =========================
@app.on_event("startup")
def on_startup():
    # Esto crea las tablas con los nuevos nombres (productos, variantes, stocks, etc.)
    Base.metadata.create_all(bind=engine)

# =========================
# CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://bunglo.vercel.app",
        "http://localhost:4200",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# ROUTERS
# =========================
# Nota: Si cambiaste los archivos de router, asegúrate que los nombres coincidan
app.include_router(auth_routers, prefix="/api/v1")
app.include_router(producto_routers, prefix="/api/v1")
app.include_router(categorias_routers, prefix="/api/v1")
app.include_router(marcas_router, prefix="/api/v1")
app.include_router(venta_router, prefix="/api/v1")
app.include_router(proveedores_router, prefix="/api/v1")

# =========================
# HEALTH CHECK
# =========================
@app.get("/")
def health_check():
    try:
        with engine.connect() as connection:
            # Usar .execute(text(...)) para verificar salud de DB
            connection.execute(text("SELECT 1"))
        return {
            "status": "online", 
            "mensaje": "Bunglo API funcionando correctamente 🚀",
            "arquitectura": "EAV (Entidad-Atributo-Valor)"
        }
    except Exception as e:
        return {"status": "error", "detalle": str(e)}