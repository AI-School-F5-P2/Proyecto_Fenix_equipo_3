from sqlalchemy.orm import Session
from datetime import datetime
from app.models.ventas_model import Venta, DetalleVenta


def registrar_venta(
    db: Session,
    stock_variante_id: int,
    cantidad: int,
    canal: str,
    vendedor: str,
    comprador: str | None = None
):
    # if cantidad <= 0:
    #     raise ValueError("Cantidad inválida")

    # stock_item = db.query(StockVariante).filter(
    #     StockVariante.id == stock_variante_id
    # ).first()

    # if not stock_item:
    #     raise ValueError("Item no existe")

    # if stock_item.stock < cantidad:
    #     raise ValueError("Stock insuficiente")

    # precio_unitario = stock_item.precio_venta
    # subtotal = precio_unitario * cantidad

    # venta = Venta(
    #     fecha=datetime.utcnow(),
    #     vendedor=vendedor.lower(),
    #     canal=canal.lower(),
    #     comprador=comprador,
    #     total=subtotal
    # )

    # db.add(venta)
    # db.flush()

    # detalle = DetalleVenta(
    #     venta_id=venta.id,
    #     stock_variante_id=stock_item.id,
    #     cantidad=cantidad,
    #     precio_unitario=precio_unitario,
    #     subtotal=subtotal
    # )

    # db.add(detalle)

    # stock_item.stock -= cantidad

    # db.commit()
    # db.refresh(venta)

    # return venta
    return []
