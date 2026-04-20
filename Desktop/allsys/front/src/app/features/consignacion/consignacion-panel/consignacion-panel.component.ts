import { Component, Input, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ConsignacionService } from '../../../core/services/consignacion.service';
import { EstadisticasConsignacion, PagoCreate, PagoRead } from '../../../core/services/consignacion.service';

@Component({
  selector: 'app-consignacion-panel',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './consignacion-panel.component.html',
  styleUrls: ['./consignacion-panel.component.css']
})
export class ConsignacionPanelComponent implements OnInit {
  @Input() clienteId!: number; // Lo recibe del componente padre

  stats: EstadisticasConsignacion | null = null;
  pagos: PagoRead[] = [];
  cargando = false;
  isSubmitting = false;

  // Formulario para el nuevo pago
  nuevoPago: PagoCreate = {
    monto: 0,
    metodo_pago: 'Transferencia',
    referencia: '',
    notas: ''
  };

  metodosPago = ['Transferencia', 'Bizum', 'Efectivo', 'PayPal'];

  constructor(private consignacionService: ConsignacionService) {}

  ngOnInit() {
    
    if (this.clienteId) {
      this.cargarDatos();
    }
  }

  cargarDatos() {
    this.cargando = true;
    // Cargamos stats y pagos al mismo tiempo
    this.consignacionService.getStats(this.clienteId).subscribe(res => {
      console.log('Estadísticas de consignación:', res);
      this.stats = res;
      // Pre-rellenamos el monto con lo que se le debe por defecto
      if (this.stats.saldo_pendiente > 0) {
        this.nuevoPago.monto = this.stats.saldo_pendiente;
      }
    });

    this.consignacionService.getPagos(this.clienteId).subscribe(res => {
      this.pagos = res;
      this.cargando = false;
    });
  }

  procesarPago() {
    if (this.nuevoPago.monto <= 0) {
      alert('⚠️ El monto debe ser mayor a 0');
      return;
    }

    this.isSubmitting = true;
    this.consignacionService.registrarPago(this.clienteId, this.nuevoPago).subscribe({
      next: (pago) => {
        alert('✅ Pago registrado con éxito');
        this.isSubmitting = false;
        
        // Limpiamos formulario
        this.nuevoPago.referencia = '';
        this.nuevoPago.notas = '';
        
        // Refrescamos los datos para que el saldo baje y la tabla se actualice
        this.cargarDatos();
      },
      error: (err) => {
        this.isSubmitting = false;
        alert('❌ Error al registrar el pago: ' + (err.error?.detail || 'Inténtalo de nuevo'));
      }
    });
  }
}