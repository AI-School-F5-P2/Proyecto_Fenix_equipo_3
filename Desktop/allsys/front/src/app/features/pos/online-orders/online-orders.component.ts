import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { VentasService } from '../../../core/services/ventas.service';
import { ClientSelectorComponent } from '../../products/add-product/components/client-selector/client-selector.component';
import { DateSelectorComponent } from '../../../shared/components/selectors/date-selector/date-selector.component';

@Component({
  selector: 'app-online-orders',
  standalone: true,
  imports: [CommonModule, FormsModule, ClientSelectorComponent, DateSelectorComponent],
  templateUrl: './online-orders.component.html',
  styleUrls: ['./online-orders.component.css']
})
export class OnlineOrdersComponent implements OnInit {
  pedidos: any[] = [];
  cargando = false;
  totalItems = 0;
  
  // Paginación
  page = 1;
  limit = 20;

  // Filtros
  search = '';
  tipoBusqueda = 'codigo_venta'; // Puede ser codigo_venta, numero_seguimiento, stock_unit_id
  filtro_estado = ''; // Combinación lógica: pendiente, empaquetado, listo_envio, enviado, entregado, cancelado, devolucion
  fecha_inicio: string | null = null;
  fecha_fin: string | null = null;
  tipo_fecha = 'creacion'; // ✨ NUEVO: creacion, envio, entrega, finalizado, cancelado, devuelta
  cliente_id: number | null | undefined = null;

  constructor(private ventasService: VentasService) {}

  ngOnInit(): void {
    this.cargarPedidos();
  }

  aplicarFiltros() {
    this.page = 1;
    this.cargarPedidos();
  }

  cargarPedidos() {
    this.cargando = true;
    
    // Resolvemos el filtro de estado combinado (Ahora se filtra principalmente por estado_envio)
    let backend_estado_envio = '';
    
    if (this.filtro_estado === 'entregado') {
      backend_estado_envio = 'entregado';
    } else if (this.filtro_estado === 'enviado') {
      backend_estado_envio = 'enviado';
    } else if (this.filtro_estado === 'pendiente') {
      backend_estado_envio = 'pendiente_envio';
    } else if (this.filtro_estado === 'empaquetado') {
      backend_estado_envio = 'empaquetado';
    } else if (this.filtro_estado === 'listo_envio') {
      backend_estado_envio = 'listo_envio';
    } else if (this.filtro_estado === 'cancelado') {
      backend_estado_envio = 'cancelado';
    } else if (this.filtro_estado === 'devolucion') {
      backend_estado_envio = 'devuelto';
    }

    // Buscamos a través de listarVentas pero solo_online=true
    this.ventasService.listarVentas(
      this.page, this.limit,
      this.tipoBusqueda === 'stock_unit_id' ? this.search : undefined, 
      this.tipoBusqueda === 'stock_unit_id' ? 'stock_unit_id' : undefined,
      this.tipoBusqueda === 'codigo_venta' ? this.search : undefined, // searchCodigo
      undefined, undefined, // searchCliente, tipoBusquedaCliente
      this.cliente_id || undefined, // ✨ cliente_id (Filtrado en Backend)
      undefined, // ✨ estado_pago
      backend_estado_envio || undefined, // ✨ estado_envio
      undefined, // canal
      this.fecha_inicio || undefined, 
      this.fecha_fin || undefined,
      undefined, undefined, undefined, // vendedor, marca_id, categoria_id
      this.tipo_fecha, // ✨ tipo_fecha (Posición 17)
      true, // ✨ solo_online
      true // ✨ include_details
    ).subscribe({
      next: (res: any) => {
        this.totalItems = res.total;
        
        let items = res.items || [];
        
        // Filtrado por estado de envío (Si el backend no lo soporta directamente, lo hacemos aquí para precisión)
        if (backend_estado_envio) {
           items = items.filter((i: any) => i.estado_envio === backend_estado_envio || (backend_estado_envio === 'pendiente_envio' && !i.estado_envio));
        }

        if (this.tipoBusqueda === 'numero_seguimiento' && this.search) {
           items = items.filter((i: any) => i.numero_seguimiento?.toLowerCase().includes(this.search.toLowerCase()));
        }
        
        this.pedidos = items;
        this.cargando = false;
      },
      error: () => this.cargando = false
    });
  }

  onClienteSelected(id: number | null | undefined) {
    this.cliente_id = id;
    this.aplicarFiltros();
  }

  onFechasSelected(fechas: {inicio: string | null, fin: string | null}) {
    this.fecha_inicio = fechas.inicio;
    this.fecha_fin = fechas.fin;
    this.aplicarFiltros();
  }

  cambiarPagina(dif: number) {
    this.page += dif;
    this.cargarPedidos();
  }

  limpiarFiltros() {
    this.search = '';
    this.tipoBusqueda = 'codigo_venta';
    this.filtro_estado = '';
    this.fecha_inicio = null;
    this.fecha_fin = null;
    this.tipo_fecha = 'creacion';
    this.cliente_id = null;
    this.aplicarFiltros();
  }

  removerFiltro(tipo: string) {
    if (tipo === 'search') this.search = '';
    if (tipo === 'estado') this.filtro_estado = '';
    if (tipo === 'fechas') {
      this.fecha_inicio = null;
      this.fecha_fin = null;
    }
    if (tipo === 'cliente') this.cliente_id = null;
    
    this.aplicarFiltros();
  }

  get hasActiveFilters(): boolean {
    return !!(this.search || this.filtro_estado || this.fecha_inicio || this.fecha_fin || this.cliente_id);
  }

  getLabelEstado(valor: string): string {
    const mapa: any = {
      'pendiente': 'Pendiente de enviar',
      'empaquetado': 'Empaquetado',
      'listo_envio': 'Listo para enviar',
      'enviado': 'Enviado',
      'entregado': 'Finalizado (entregado)',
      'devolucion': 'Devolución',
      'cancelado': 'Cancelado'
    };
    return mapa[valor] || valor;
  }

  getEstatusInterpretado(pedido: any): string {
    if (pedido.estado_pago === 'reembolsado' || pedido.estado_envio === 'cancelado') {
      return 'Cancelado. (Venta anulada)';
    }
    if (pedido.estado_pago === 'reembolso_parcial' || pedido.estado_envio === 'devuelto') {
      return 'Devolución procesada.';
    }
    if (pedido.estado_envio === 'entregado') {
      return 'Pedido finalizado (Entregado).';
    }
    
    // Si no está finalizado/cancelado, vemos la logística
    const estado = pedido.estado_envio || 'pendiente_envio';
    const mapa: Record<string, string> = {
      'pendiente_envio': 'Pendiente de enviar',
      'empaquetado': 'Empaquetado (en almacén)',
      'listo_envio': 'Listo para enviar',
      'enviado': 'Enviado (en tránsito)'
    };
    
    return mapa[estado] || 'Procesando';
  }
}