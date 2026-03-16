from sqlalchemy.orm import Session
from app.models.proveedores_model import Proveedor

def obtener_todos(db: Session):
    """Lista todos los proveedores ordenados alfabéticamente."""
    return db.query(Proveedor).order_by(Proveedor.nombre_proveedor.asc()).all()

def obtener_por_id(db: Session, proveedor_id: int):
    """Busca un proveedor específico."""
    return db.query(Proveedor).filter(Proveedor.id == proveedor_id).first()

def buscar_o_crear(db: Session, nombre: str):
    """
    Lógica de oro: Si el proveedor existe lo devuelve, 
    si no, lo crea. Ideal para el flujo de productos.
    """
    if not nombre or not nombre.strip():
        return None
        
    nombre_clean = nombre.strip()
    # Buscamos ignorando mayúsculas/minúsculas
    proveedor = db.query(Proveedor).filter(
        Proveedor.nombre_proveedor.ilike(nombre_clean)
    ).first()
    
    if not proveedor:
        proveedor = Proveedor(nombre_proveedor=nombre_clean)
        db.add(proveedor)
        db.flush() # Para tener el ID disponible de inmediato
        
    return proveedor

def actualizar_proveedor(db: Session, proveedor_id: int, nuevo_nombre: str):
    """Actualiza los datos de un proveedor."""
    proveedor = obtener_por_id(db, proveedor_id)
    if proveedor:
        proveedor.nombre_proveedor = nuevo_nombre.strip()
        db.commit()
        db.refresh(proveedor)
    return proveedor