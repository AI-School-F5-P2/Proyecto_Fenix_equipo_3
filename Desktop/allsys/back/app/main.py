from fastapi import FastAPI
from app.db.database import Base, engine  # Importa el engine de SQLAlchemy
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.auth import auth_routers
from app.api.v1.productos import producto_routers
from app.api.v1.categorias import categorias_routers
from app.api.v1.marcas import marcas_router

# Models
from app.models.producto_model import Producto
from app.models.categorias_model import Categoria
from app.models.marcas_model import Marca
from app.models.variante_imagen_model import Imagen



app = FastAPI(title="Mi Tienda Online")

# Crear las tablas al arrancar la app
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://bunglo.vercel.app", "http://localhost:4200"],       # Permite los orígenes listados
    allow_credentials=True,
    allow_methods=["*"],         # Permite todos los métodos HTTP (GET, POST, etc)
    allow_headers=["*"],         # Permite todos los headers
)

app.include_router(auth_routers)
app.include_router(producto_routers)
app.include_router(categorias_routers)
app.include_router(marcas_router)


@app.get("/")
def read_root():
    # Intentar conectarse a la base de datos
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))  # pequeña consulta de prueba
        return {"mensaje": "¡API y Base de Datos funcionando 🚀!"}
    except Exception as e:
        return {"error": f"No se pudo conectar a la base de datos: {str(e)}"}
