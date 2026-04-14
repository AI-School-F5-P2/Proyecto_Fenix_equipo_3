import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { VentasService, VentaData } from '../../../core/services/ventas.service';

@Component({
  selector: 'app-pos',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './pos.component.html',
  styleUrls: ['./pos.component.css']
})
export class PosComponent {
  codigoBusqueda: string = '';
  procesando: boolean = false;
  
  // Novedad: Historial del cliente
  comprasPreviasCliente: number | null = null;

  carrito: any[] = [];
  subtotal: number = 0;
  total: number = 0;

  // Listas para los desplegables de Tienda Física
  prefijosPaises = [
    { codigo: '+34', pais: 'España (+34)' },
    { codigo: '+58', pais: 'Venezuela (+58)' },
    { codigo: '+57', pais: 'Colombia (+57)' },
    { codigo: '+52', pais: 'México (+52)' },
    { codigo: '+1', pais: 'EE.UU/Canadá (+1)' },
    { codigo: '+33', pais: 'Francia (+33)' },
    { codigo: '+39', pais: 'Italia (+39)' }
  ];

  tiposDocumentos = [
    { id: 'DNI', nombre: 'DNI (España)' },
    { id: 'NIE', nombre: 'NIE (España)' },
    { id: 'CEDULA', nombre: 'Cédula (Vzla/Col)' },
    { id: 'PASAPORTE', nombre: 'Pasaporte' },
    { id: 'RFC', nombre: 'RFC/CURP (México)' },
    { id: 'OTRO', nombre: 'Otro Documento' }
  ];

  datosVenta: VentaData = {
    fecha: new Date().toISOString().split('T')[0],
    canal: 'vinted',
    vendedor: '', 
    metodo_pago: 'vinted',
    estado_venta: 'procesando',
    estado_pago: 'pendiente',  
    
    // ✨ Campos Estructurados
    tipo_identificador: 'telefono', // Por defecto
    prefijo_telefono: '+34',        // Por defecto
    tipo_documento: 'DNI',          // Por defecto
    identificador_cliente: '',
    nombre_cliente: '',
    
    descuento_total: 0,
    costo_envio: 0,
    empresa_transporte: '',
    numero_seguimiento: '',
    detalles: []
  };

  constructor(private ventasService: VentasService) {
    this.onCanalChange();
  }

  // ==========================================
  // LÓGICA DE CANALES Y ESTADOS AUTOMÁTICOS
  // ==========================================
  onCanalChange() {
    if (this.datosVenta.canal === 'tienda_fisica') {
      this.datosVenta.estado_venta = 'completada';
      this.datosVenta.estado_pago = 'pagado';
      this.datosVenta.metodo_pago = 'efectivo';
    } else {
      this.datosVenta.estado_venta = 'procesando';
      this.datosVenta.estado_pago = 'pendiente';
      this.datosVenta.metodo_pago = this.datosVenta.canal === 'web' ? 'plataforma' : this.datosVenta.canal;
    }
  }

  // ==========================================
  // LÓGICA DEL CLIENTE (HISTORIAL)
  // ==========================================
  buscarHistorialCliente() {
    let idParaBuscar = '';

    if (this.datosVenta.canal === 'tienda_fisica') {
      if (!this.datosVenta.identificador_cliente?.trim()) {
        this.comprasPreviasCliente = null;
        return;
      }
      
      if (this.datosVenta.tipo_identificador === 'telefono') {
        idParaBuscar = `${this.datosVenta.prefijo_telefono}${this.datosVenta.identificador_cliente.trim()}`;
      } else {
         idParaBuscar = this.datosVenta.identificador_cliente.trim();
      }
    } else {
      // Para Web o Apps, usamos el identificador tal cual
      idParaBuscar = this.datosVenta.identificador_cliente?.trim() || '';
    }

    if (!idParaBuscar) return;

    // Simulación de búsqueda en base de datos
    console.log(`Buscando historial de: ${idParaBuscar}`);
    setTimeout(() => {
      this.comprasPreviasCliente = idParaBuscar.toLowerCase().includes('yenny') ? 3 : 0;
    }, 300);
  }

  // ==========================================
  // LÓGICA DEL CARRITO
  // ==========================================
  buscarYAgregarProducto() {
    if (!this.codigoBusqueda.trim()) return;

    const stockId = Number(this.codigoBusqueda);
    if (isNaN(stockId)) {
      alert('Por ahora ingresa el ID numérico del stock');
      return;
    }

    this.ventasService.buscarProductoPorStock(stockId).subscribe({
      next: (res) => {
        if (res.alerta) {
          alert(res.alerta);
          return;
        }

        const existe = this.carrito.find(item => item.stock_id === res.stock_id);
        if (existe) {
          if (existe.cantidad_venta < res.stock_disponible) {
            existe.cantidad_venta += 1;
          } else {
            alert('No hay más stock disponible de este artículo.');
          }
        } else {
          this.carrito.push({
            ...res,
            cantidad_venta: 1,
            precio_unitario: res.precio_venta
          });
        }
        this.codigoBusqueda = '';
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
    this.subtotal = this.carrito.reduce((acc, item) => acc + (item.cantidad_venta * item.precio_unitario), 0);
    let d = Number(this.datosVenta.descuento_total) || 0;
    let e = Number(this.datosVenta.costo_envio) || 0;
    this.total = (this.subtotal + e) - d;
    if (this.total < 0) this.total = 0;
  }

  // ==========================================
  // COMPLETAR LA VENTA
  // ==========================================
  completarVenta() {
    if (this.carrito.length === 0) return;

    // ✨ VALIDACIÓN ESTRICTA DEL CLIENTE
    if (['vinted', 'wallapop', 'web'].includes(this.datosVenta.canal) && !this.datosVenta.identificador_cliente?.trim()) {
      alert('El Identificador del Cliente (Usuario o Email) es OBLIGATORIO para este canal.');
      return;
    }

    this.procesando = true;

    this.datosVenta.detalles = this.carrito.map(item => ({
      stock_id: item.stock_id,
      cantidad: item.cantidad_venta,
      precio_unitario: Number(item.precio_unitario)
    }));

    this.ventasService.registrarVenta(this.datosVenta).subscribe({
      next: (res) => {
        alert(`✅ VENTA REGISTRADA\nCódigo: ${res.codigo}`);
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
    this.datosVenta.identificador_cliente = '';
    this.datosVenta.nombre_cliente = '';
    this.datosVenta.descuento_total = 0;
    this.datosVenta.costo_envio = 0;
    this.datosVenta.numero_seguimiento = '';
    this.datosVenta.empresa_transporte = '';
    this.comprasPreviasCliente = null;
    this.datosVenta.fecha = new Date().toISOString().split('T')[0];
    this.onCanalChange(); 
    this.calcularTotales();
    this.procesando = false;
  }
}