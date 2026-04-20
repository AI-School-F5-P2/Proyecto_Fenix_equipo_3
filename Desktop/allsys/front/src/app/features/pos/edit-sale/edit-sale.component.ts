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
  identificadorCrm: string = '';
  formData: any = {
    fecha: '', 
    fecha_pago: '',  // ✨ NUEVO
    fecha_envio: '', // ✨ NUEVO
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

  // Adapta la fecha de la base de datos al formato del input HTML
  formatDateForInput(dateString: string): string {
    if (!dateString) return '';
    const date = new Date(dateString);
    const tzOffset = date.getTimezoneOffset() * 60000; 
    return new Date(date.getTime() - tzOffset).toISOString().slice(0, 16);
  }

  cargarVenta() {
    this.ventasService.obtenerVenta(this.ventaId!).subscribe({
      next: (res) => {
        this.venta = res;
        
        // ✨ LÓGICA MÁGICA: Extraemos el identificador real del CRM
        if (res.cliente) {
          if (res.canal === 'vinted') {
            this.identificadorCrm = res.cliente.usuario_vinted ? `@${res.cliente.usuario_vinted}` : 'Sin usuario Vinted';
          } else if (res.canal === 'wallapop') {
            this.identificadorCrm = res.cliente.usuario_wallapop ? `@${res.cliente.usuario_wallapop}` : 'Sin usuario Wallapop';
          } else if (res.canal === 'tienda_fisica') {
            this.identificadorCrm = res.cliente.telefono || res.cliente.dni_nie || 'Cliente de Tienda';
          } else {
            this.identificadorCrm = res.cliente.email || 'Sin email';
          }
        }
        
        // Purgamos los datos al formulario
        this.formData = {
          fecha: this.formatDateForInput(res.fecha), 
          fecha_pago: this.formatDateForInput(res.fecha_pago), 
          fecha_envio: this.formatDateForInput(res.fecha_envio),
          estado_venta: res.estado_venta || '',
          estado_pago: res.estado_pago || '',
          metodo_pago: res.metodo_pago || '',
          // Si por error en BD vieja el identificador está aquí, se mostrará, pero ya les avisamos que lo borren
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
  // Limpiamos fechas vacías antes de enviar al backend
  prepararDatosParaGuardar(): any {
    const dataToSend = { ...this.formData };
    
    // Si la fecha se borra en el input, enviamos null para que la BD lo acepte (en caso de pagos o envíos)
    if (!dataToSend.fecha) dataToSend.fecha = null;
    if (!dataToSend.fecha_pago) dataToSend.fecha_pago = null;
    if (!dataToSend.fecha_envio) dataToSend.fecha_envio = null;

    return dataToSend;
  }

  guardarCambios() {
    // ✨ QUITAMOS LA RESTRICCIÓN: En Vinted muchas veces usamos etiquetas prepagadas 
    // y no sabemos el nombre real del cliente, ni su email. Solo su @usuario, el cual ya está a salvo en el CRM.
    // Así que ya no bloquearemos el guardado si el nombre está vacío.
    
    this.guardando = true;
    
    if (this.formData.estado_venta === 'cancelada' && this.venta.estado_venta !== 'cancelada') {
      const confirma = confirm("⚠️ Vas a cancelar esta venta. El stock de estos artículos se devolverá al almacén. ¿Continuar?");
      if (!confirma) {
        this.guardando = false;
        return;
      }
    }

    const payload = this.prepararDatosParaGuardar();

    this.ventasService.editarVenta(this.ventaId!, payload).subscribe({
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
    this.router.navigate(['/sales-list']);
  }
}