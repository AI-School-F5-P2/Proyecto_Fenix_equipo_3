import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { VentasService, VentaData } from '../../core/services/ventas.service'; // Ajusta la ruta

@Component({
  selector: 'app-pos',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './pos.component.html',
  styleUrls: ['./pos.component.css']
})
export class PosComponent {
  // Estado de la interfaz
  codigoBusqueda: string = '';
  procesando: boolean = false;

  // Variables financieras
  carrito: any[] = [];
  subtotal: number = 0;
  total: number = 0;

  // Datos del formulario de venta
  datosVenta: VentaData = {
    fecha: new Date().toISOString().split('T')[0], // 👈 Inicia con la fecha de hoy (YYYY-MM-DD)
    canal: 'tienda_fisica',
    vendedor: 'Yenny', 
    metodo_pago: 'efectivo',
    nombre_cliente: '',
    descuento_total: 0,
    costo_envio: 0,
    detalles: []
  };

  constructor(private ventasService: VentasService) {}

  // ==========================================
  // LÓGICA DEL CARRITO
  // ==========================================
  
  buscarYAgregarProducto() {
    if (!this.codigoBusqueda.trim()) return;

    // Asumimos que escanean el ID del Stock por ahora
    const stockId = Number(this.codigoBusqueda);
    if (isNaN(stockId)) {
      alert('Por ahora ingresa el ID numérico del stock');
      return;
    }

    this.ventasService.buscarProductoPorStock(stockId).subscribe({
      next: (res) => {
        if (res.alerta) {
          alert(res.alerta); // Avisa si está agotado
          return;
        }

        // Verificamos si ya está en el carrito para solo sumar cantidad
        const existe = this.carrito.find(item => item.stock_id === res.stock_id);
        
        if (existe) {
          if (existe.cantidad_venta < res.stock_disponible) {
            existe.cantidad_venta += 1;
          } else {
            alert('No hay más stock disponible de este artículo.');
          }
        } else {
          // Lo añadimos nuevo al carrito
          this.carrito.push({
            ...res,
            cantidad_venta: 1, // Iniciamos en 1
            precio_unitario: res.precio_venta // Precio sugerido
          });
        }

        this.codigoBusqueda = ''; // Limpiamos el buscador para el siguiente producto
        this.calcularTotales();
      },
      error: (err) => alert('No se encontró el producto.')
    });
  }

  cambiarCantidad(index: number, cambio: number) {
    const item = this.carrito[index];
    const nuevaCantidad = item.cantidad_venta + cambio;

    if (nuevaCantidad > 0 && nuevaCantidad <= item.stock_disponible) {
      item.cantidad_venta = nuevaCantidad;
      this.calcularTotales();
    } else if (nuevaCantidad === 0) {
      this.eliminarDelCarrito(index);
    } else {
      alert(`Solo hay ${item.stock_disponible} unidades en stock.`);
    }
  }

  eliminarDelCarrito(index: number) {
    this.carrito.splice(index, 1);
    this.calcularTotales();
  }

  calcularTotales() {
    // Suma de (cantidad * precio)
    this.subtotal = this.carrito.reduce((acc, item) => acc + (item.cantidad_venta * item.precio_unitario), 0);
    
    // Total = Subtotal + Envío - Descuentos
    let d = Number(this.datosVenta.descuento_total) || 0;
    let e = Number(this.datosVenta.costo_envio) || 0;
    
    this.total = (this.subtotal + e) - d;
    
    if (this.total < 0) this.total = 0; // El total no puede ser negativo
  }

  // ==========================================
  // COMPLETAR LA VENTA
  // ==========================================
  
  completarVenta() {
    if (this.carrito.length === 0) return;

    this.procesando = true;

    // Preparamos el array "detalles" que pide el backend
    this.datosVenta.detalles = this.carrito.map(item => ({
      stock_id: item.stock_id,
      cantidad: item.cantidad_venta,
      precio_unitario: Number(item.precio_unitario)
    }));

    this.ventasService.registrarVenta(this.datosVenta).subscribe({
      next: (res) => {
        alert(`✅ VENTA COMPLETADA\nCódigo: ${res.codigo}`);
        this.limpiarCaja();
      },
      error: (err) => {
        alert('❌ Error al registrar la venta: ' + (err.error?.detail || 'Desconocido'));
        this.procesando = false;
      }
    });
  }

  limpiarCaja() {
    this.carrito = [];
    this.datosVenta.nombre_cliente = '';
    this.datosVenta.descuento_total = 0;
    this.datosVenta.costo_envio = 0;
    this.datosVenta.fecha = new Date().toISOString().split('T')[0]; // Restaurar a hoy
    this.calcularTotales();
    this.procesando = false;
  }
}