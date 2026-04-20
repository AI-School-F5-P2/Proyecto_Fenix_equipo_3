import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { VentasService } from '../../../core/services/ventas.service';
import { DateRange, DateSelectorComponent } from '../../../shared/components/selectors/date-selector/date-selector.component';
import { MarcaService } from '../../../core/services/marcas.service';
import { CategorySelectorComponent, CategorySelectionEvent } from '../../../shared/components/selectors/category-selector/category-selector.component';

@Component({
  selector: 'app-sales-list',
  standalone: true,
  imports: [CommonModule, FormsModule, DateSelectorComponent, CategorySelectorComponent],
  templateUrl: './sales-list.component.html',
  styleUrls: ['./sales-list.component.css']
})
export class SalesListComponent implements OnInit {
  ventas: any[] = [];
  cargando = true;
  marcas: any[] = [];
  totalItems = 0;
  page = 1;
  limit = 10;

  // ✨ VARIABLES DE BÚSQUEDA (Las 3 Cajas)
  searchProducto = '';
  tipoBusquedaProd = 'id_producto'; 
  searchCodigo = '';
  searchCliente = '';
  tipoBusquedaCliente = 'nombre'; // 👈 NUEVO: Selector de cliente

  // Otros filtros
  filtroEstado = '';
  filtroCanal = '';
  fechaInicio: string | null = null;
  fechaFin: string | null = null;
  filtroVendedor: string = '';
  filtroMarca: string = '';
  filtroCategoria: number | null = null; 

  totalRecaudado = 0;
  totalBeneficio = 0;

  constructor(
    private ventasService: VentasService, 
    private marcaService: MarcaService, 
    private router: Router
  ) {}

  ngOnInit() {
    this.cargarMarcas();
    this.cargarVentas();
  }

  cargarMarcas() {
    this.marcaService.listarMarcas().subscribe({
      next: (res) => this.marcas = res,
      error: (err) => console.error('Error al cargar marcas', err)
    });
  }

  onCategoriaSeleccionada(event: CategorySelectionEvent) {
    this.filtroCategoria = event.categoriaId;
    this.buscar();
  }

  cargarVentas() {
    this.cargando = true;
    this.ventasService.listarVentas(
      this.page, this.limit, 
      this.searchProducto, this.tipoBusquedaProd,         // Caja 1
      this.searchCodigo,                                  // Caja 2
      this.searchCliente, this.tipoBusquedaCliente,       // Caja 3 ✨
      this.filtroEstado, this.filtroCanal, 
      this.fechaInicio || undefined, this.fechaFin || undefined, 
      this.filtroVendedor,
      this.filtroMarca || undefined,        
      this.filtroCategoria || undefined
    ).subscribe({
      next: (res) => {
        console.log('Respuesta del backend:', res); // Para depuración
        this.ventas = res.items;
        this.totalItems = res.total;
        this.totalRecaudado = res.suma_recaudado;
        this.totalBeneficio = res.suma_beneficio;
        this.cargando = false;
      },
      error: (err) => {
        console.error(err);
        this.cargando = false;
      }
    });
  }

  onFechasCambiadas(rango: DateRange) {
    this.fechaInicio = rango.inicio;
    this.fechaFin = rango.fin;
    this.buscar(); 
  }

  buscar() {
    this.page = 1; 
    this.cargarVentas();
  }

  limpiarFiltros() {
    this.searchProducto = '';
    this.tipoBusquedaProd = 'id_producto';
    this.searchCodigo = '';
    this.searchCliente = '';
    this.tipoBusquedaCliente = 'nombre';
    
    this.filtroEstado = '';
    this.filtroCanal = '';
    this.filtroVendedor = ''; 
    this.fechaInicio = null; 
    this.fechaFin = null;
    this.filtroMarca = '';
    this.filtroCategoria = null; 
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