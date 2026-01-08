import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { VentasService } from '../../../core/services/ventas.service';

/* =========================
   INTERFAZ LOCAL (AQUÍ MISMO)
========================= */
type CanalVenta = 'wallapop' | 'vinted' | 'web';
type Vendedor = 'maikol' | 'paola' | 'yenny';

interface CrearVentaPayload {
  variante_id: number;
  talla_id: number;
  precio_venta: number;
  cantidad: number;
  fecha: string;        // yyyy-mm-dd (backend espera "fecha")
  canal: CanalVenta;    // backend espera "canal"
  vendedor: Vendedor;
  comprador?: string;
}

@Component({
  selector: 'app-venta-create',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './venta-create.component.html',
  styleUrls: ['./venta-create.component.css']
})
export class VentaCreateComponent implements OnInit {

  busqueda = '';
  loadingBusqueda = false;
  errorBusqueda = '';

  varianteEncontrada: any = null;

  // 📋 ngModel
  precio_venta = 0;
  cantidad = 1;
  fecha = '';
  canal: CanalVenta = 'web';
  vendedor: Vendedor = 'maikol';
  comprador = '';

  loading = false;
  mensaje = '';

  vendedores: Vendedor[] = ['maikol', 'paola', 'yenny'];
  canales: CanalVenta[] = ['wallapop', 'vinted', 'web'];

  constructor(private ventasService: VentasService) {}

  ngOnInit(): void {}

  // 🔎 Buscar producto por talla
  buscarProducto(): void {
    if (!this.busqueda) return;

    this.loadingBusqueda = true;
    this.errorBusqueda = '';
    this.varianteEncontrada = null;

    this.ventasService.buscarProductoPorTalla(Number(this.busqueda)).subscribe({
      next: (data) => {
        if (!data) {
          this.errorBusqueda = '❌ Producto no encontrado';
          this.loadingBusqueda = false;
          return;
        }

        this.varianteEncontrada = {
          id: data.variante.id,
          talla: data.talla,
          nombre: data.nombre,
          color_nombre: data.variante.color_nombre,
          imagenes: data.variante.imagenes,
          precio: data.variante.precio
        };

        // Valores por defecto
        this.precio_venta = this.varianteEncontrada.precio;
        this.cantidad = 1;
        this.canal = 'web';
        this.vendedor = 'maikol';

        this.loadingBusqueda = false;
      },
      error: () => {
        this.errorBusqueda = '❌ Producto no encontrado';
        this.loadingBusqueda = false;
      }
    });
  }

  // 💾 Registrar venta
  submit(): void {
    if (!this.varianteEncontrada) {
      this.mensaje = '❌ Debes buscar un producto primero';
      return;
    }

    if (!this.fecha) {
      this.mensaje = '❌ Debes seleccionar una fecha';
      return;
    }

    if (this.cantidad <= 0) {
      this.mensaje = '❌ Cantidad inválida';
      return;
    }

    this.loading = true;
    this.mensaje = '';

    const payload: CrearVentaPayload = {
      variante_id: this.varianteEncontrada.id,
      talla_id: this.varianteEncontrada.talla.id,
      precio_venta: this.precio_venta,
      cantidad: this.cantidad,
      fecha: this.fecha,
      canal: this.canal,
      vendedor: this.vendedor,
      comprador: this.comprador || undefined
    };

    console.log('Payload venta:', payload);

    this.ventasService.registrarVenta(payload).subscribe({
      next: () => {
        this.mensaje = '✅ Venta registrada correctamente';

        // Reset
        this.precio_venta = 0;
        this.cantidad = 1;
        this.fecha = '';
        this.canal = 'web';
        this.vendedor = 'maikol';
        this.comprador = '';
        this.varianteEncontrada = null;
        this.busqueda = '';
        this.loading = false;
      },
      error: (err) => {
        console.error('Error backend:', err);
        this.mensaje = err?.error?.detail || '❌ Error registrando la venta';
        this.loading = false;
      }
    });
  }
}
