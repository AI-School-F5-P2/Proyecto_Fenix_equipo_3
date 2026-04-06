import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { VentasService } from '../../../core/services/ventas.service';
import { DateRange, DateSelectorComponent } from '../../../shared/components/selectors/date-selector/date-selector.component';

@Component({
  selector: 'app-sales-list',
  standalone: true,
  imports: [CommonModule, FormsModule, DateSelectorComponent],
  templateUrl: './sales-list.component.html',
  styleUrls: ['./sales-list.component.css']
})
export class SalesListComponent implements OnInit {
  ventas: any[] = [];
  cargando = true;
  
  // Paginación y Filtros
  totalItems = 0;
  page = 1;
  limit = 10;
  searchQuery = '';
  filtroEstado = '';
  filtroCanal = '';
  fechaInicio: string | null = null;
  fechaFin: string | null = null;
  filtroVendedor: string = '';
  filtroComprador: string = '';

  constructor(private ventasService: VentasService, private router: Router) {}

  ngOnInit() {
    this.cargarVentas();
  }

  cargarVentas() {
    this.cargando = true;
    this.ventasService.listarVentas(this.page, this.limit, this.searchQuery, this.filtroEstado, this.filtroCanal, this.fechaInicio || undefined, this.fechaFin || undefined, this.filtroVendedor, this.filtroComprador )
      .subscribe({
        next: (res) => {
          this.ventas = res.items;
          this.totalItems = res.total;
          this.cargando = false;
          
        },
        error: (err) => {
          console.error(err);
          this.cargando = false;
        }
      });
  }

  // 👇 3. FUNCIÓN PARA RECIBIR LAS FECHAS DEL COMPONENTE
  onFechasCambiadas(rango: DateRange) {
    this.fechaInicio = rango.inicio;
    this.fechaFin = rango.fin;
    this.buscar(); // Ejecuta la búsqueda automáticamente al aplicar
  }

  buscar() {
    this.page = 1; // Reseteamos a la página 1 al buscar
    this.cargarVentas();
  }

  limpiarFiltros() {
    this.searchQuery = '';
    this.filtroEstado = '';
    this.filtroCanal = '';
    this.filtroVendedor = '';  // 👈 Limpiar
    this.filtroComprador = '';
    this.fechaInicio = null; // Limpiamos las fechas
    this.fechaFin = null;
    this.buscar();
  }

  cambiarPagina(nuevaPagina: number) {
    if (nuevaPagina >= 1 && nuevaPagina <= this.totalPages) {
      this.page = nuevaPagina;
      this.cargarVentas();
    }
  }

  get totalPages(): number {
    return Math.ceil(this.totalItems / this.limit);
  }

  irAEditar(ventaId: number) {
    this.router.navigate(['/edit-sale', ventaId]);
  }
}