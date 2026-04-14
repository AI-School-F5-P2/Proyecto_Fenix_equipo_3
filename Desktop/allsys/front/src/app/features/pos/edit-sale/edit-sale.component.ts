import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { VentasService } from '../../../core/services/ventas.service';

@Component({
  selector: 'app-edit-sale',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './edit-sale.component.html',
  styleUrls: ['./edit-sale.component.css']
})
export class EditSaleComponent implements OnInit {
  ventaId: number | null = null;
  cargando = true;
  guardando = false;
  venta: any = {};

  formData: any = {
    estado_venta: '',
    estado_pago: '',
    metodo_pago: '',
    nombre_cliente: '',
    email_cliente: '',
    estado_envio: '',
    empresa_transporte: '',
    numero_seguimiento: '',
    notas_internas: '',
    total: 0
  };

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private ventasService: VentasService
  ) {}

  ngOnInit() {
    this.ventaId = Number(this.route.snapshot.paramMap.get('id'));
    if (this.ventaId) {
      this.cargarVenta();
    }
  }

  cargarVenta() {
    this.ventasService.obtenerVenta(this.ventaId!).subscribe({
      next: (res) => {
        this.venta = res;
        
        // Purgamos los datos al formulario, incluyendo el total
        this.formData = {
          estado_venta: res.estado_venta || '',
          estado_pago: res.estado_pago || '',
          metodo_pago: res.metodo_pago || '',
          nombre_cliente: res.nombre_cliente || '',
          email_cliente: res.email_cliente || '',
          estado_envio: res.estado_envio || '',
          empresa_transporte: res.empresa_transporte || '', 
          numero_seguimiento: res.numero_seguimiento || '',
          notas_internas: res.notas_internas || '',
          total: res.total || 0 
        };
        this.cargando = false;
      },
      error: () => {
        alert('Venta no encontrada');
        this.volver();
      }
    });
  }

  guardarCambios() {
    // Validación estricta adaptada a los canales online
    const canalesOnline = ['vinted', 'wallapop', 'web'];
    if (canalesOnline.includes(this.venta.canal) && !this.formData.nombre_cliente?.trim() && !this.formData.email_cliente?.trim()) {
      alert('Debes mantener al menos un Nombre o un Email de referencia para ventas online.');
      return;
    }

    this.guardando = true;
    
    if (this.formData.estado_venta === 'cancelada' && this.venta.estado_venta !== 'cancelada') {
      const confirma = confirm("⚠️ Vas a cancelar esta venta. El stock de estos artículos se devolverá al almacén. ¿Continuar?");
      if (!confirma) {
        this.guardando = false;
        return;
      }
    }

    this.ventasService.editarVenta(this.ventaId!, this.formData).subscribe({
      next: () => {
        alert('✅ Venta actualizada con éxito.');
        this.volver();
      },
      error: (err) => {
        alert('Error al guardar: ' + (err.error?.detail || 'Desconocido'));
        this.guardando = false;
      }
    });
  }

  volver() {
    this.router.navigate(['/ventas-history']);
  }
}