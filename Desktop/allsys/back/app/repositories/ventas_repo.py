from sqlalchemy.orm import Session
from datetime import datetime

from app.models.ventas_model import Venta, DetalleVenta
from app.models.variantes_model import Variante
from app.models.talla_model import Talla


# =========================
# REGISTRAR VENTA
# =========================
def registrar_venta(
    db: Session,
    variante_id: int,
    talla_id: int,
    cantidad: int,
    precio_venta: float,
    fecha: str,
    canal: str,
    vendedor: str,
    comprador: str | None = None
):
    if cantidad <= 0:
        raise ValueError("La cantidad debe ser mayor a 0")

    # 🔎 Variante
    variante = db.query(Variante).filter(Variante.id == variante_id).first()
    if not variante:
        raise ValueError("La variante no existe")

    # 🔎 Talla (stock real)
    talla = db.query(Talla).filter(
        Talla.id == talla_id,
        Talla.variante_id == variante.id
    ).first()
    if not talla:
        raise ValueError("La talla no pertenece a la variante")

    if talla.stock < cantidad:
        raise ValueError("Stock insuficiente para esta talla")

    fecha = datetime.strptime(fecha, "%Y-%m-%d")

    # 🧾 Venta
    venta = Venta(
        fecha=fecha,
        vendedor=vendedor.lower(),
        canal=canal.lower(),
        comprador=comprador,
        total=precio_venta * cantidad
    )
    db.add(venta)
    db.flush()  # obtener venta.id

    # 📄 Detalle
    detalle = DetalleVenta(
        venta_id=venta.id,
        variante_id=variante.id,
        talla_id=talla.id,
        cantidad=cantidad,
        precio_unitario=precio_venta,
        subtotal=precio_venta * cantidad
    )
    db.add(detalle)

    # ➖ Descontar stock SOLO de la talla
    talla.stock -= cantidad

    db.commit()
    db.refresh(venta)

    return venta


# =========================
# CONSULTAR PRODUCTO POR TALLA
# =========================
def obtener_producto_por_talla(db: Session, talla_id: int):
    from app.models.producto_model import Producto

    talla = db.query(Talla).filter(Talla.id == talla_id).first()
    if not talla:
        return None

    variante = talla.variante
    if not variante:
        return None

    producto = variante.producto
    if not producto:
        return None

    producto_dict = {
        "id": producto.id,
        "nombre": producto.nombre,
        "sku": producto.sku,
        "tipo": producto.tipo,
        "stock": producto.stock,
        "precio": producto.precio,
        "descripcion": producto.descripcion,
        "categoria": {
            "id": producto.categoria.id,
            "nombre": producto.categoria.nombre,
            "descripcion": producto.categoria.descripcion,
            "parent_id": producto.categoria.parent_id
        } if producto.categoria else None,
        "marca": {
            "id": producto.marca.id,
            "nombre": producto.marca.nombre,
            "descripcion": producto.marca.descripcion
        } if producto.marca else None,
        "variante": {
            "id": variante.id,
            "sku": variante.sku,
            "color": variante.color,
            "color_nombre": variante.color_nombre,
            "precio": variante.precio,
            "descuento": variante.descuento,
            "stock_total": sum([t.stock for t in variante.tallas]),
            "imagenes": [{"url": img.url} for img in variante.imagenes]
        },
        "talla": {
            "id": talla.id,
            "talla": talla.talla,
            "stock": talla.stock
        }
    }

    return producto_dict
