import { Component, OnInit } from '@angular/core';
import { ProductsService } from '../../../core/services/products.service';
import { CommonModule, TitleCasePipe } from '@angular/common';
import { RouterLink } from "@angular/router";
import { FormsModule } from '@angular/forms';
import { CategorySelectionEvent, CategorySelectorComponent } from '../../../shared/components/selectors/category-selector/category-selector.component';
import { Subject } from 'rxjs';
import { debounceTime, distinctUntilChanged } from 'rxjs/operators';
import { ColorSelectorComponent } from "../../../shared/components/selectors/color-selector/color-selector.component";
import { Color } from '../add-product/product-form.config';
import { InventoryTableComponent } from "./components/inventory-table/inventory-table.component";
import { CatalogGridComponent } from "./components/catalog-grid/catalog-grid.component";
import { ProviderSelectorComponent } from "../components/provider-selector/provider-selector.component";
import { DateSelectorComponent } from "../../../shared/components/selectors/date-selector/date-selector.component";
import { Subscription } from 'rxjs';

export interface MisFiltros {
  search: string;
  tipo_busqueda: 'producto_id' | 'stock_id';
  categoria_id: number | null;
  marca_id: number | null;
  estado: string;
  precio_min: number | null;
  precio_max: number | null;
  ordenar_por: string;
  color: string | null;
  talla: string | null;
  proveedores_ids : number[],
  fecha_inicio: string | null;
  fecha_fin: string | null;
  disponibilidad: 'todos' | 'en_stock' | 'agotado';
}

@Component({
  selector: 'app-products-list',
  standalone: true,
  imports: [CommonModule, TitleCasePipe, RouterLink, FormsModule, CategorySelectorComponent, ColorSelectorComponent, InventoryTableComponent, CatalogGridComponent, ProviderSelectorComponent, DateSelectorComponent],
  templateUrl: './products-list.component.html',
  styleUrl: './products-list.component.css'
})
export class ProductsListComponent implements OnInit {

  stocks: any[] = []; 
  vistaActual: 'catalogo' | 'inventario' = 'catalogo'; // ✨ Cambiado a catálogo por defecto (mejor UX)
  productosPadre: any[] = []; 
  pagina: number = 1;       
  limite: number = 10;
  private querySubscription?: Subscription; // 2. Variable para controlar la petición activa
  cargando: boolean = false;
  sinMasResultados: boolean = false;
  totalStocks: number = 0; 
  // En tu clase ProductsListComponent
  totalResultados: number = 0; // Este es el total de la vista activa
  totalCatalogo: number = 0;    // ✨ Nuevo: Total específico de catálogo
  totalInventario: number = 0;  // ✨ Nuevo: Total específico de inventario

  filtros: MisFiltros = {
    search: '',
    tipo_busqueda: 'producto_id', // ✨ Sincronizado con vistaActual: 'catalogo'
    color: null,
    talla: null,
    categoria_id: null,
    marca_id: null,
    estado: '',
    precio_min: null,
    precio_max: null,
    ordenar_por: 'fecha_desc',
    proveedores_ids: [],
    fecha_inicio: null,
    fecha_fin: null,
    disponibilidad: 'todos',
  };

  private searchSubject = new Subject<string>();

  constructor(private productsService: ProductsService) {}

  ngOnInit(): void {
    // 💡 Recuperar vista preferida del usuario si existe en localStorage
    const savedView = localStorage.getItem('vinted_pref_vista');
    if (savedView === 'inventario' || savedView === 'catalogo') {
      this.vistaActual = savedView;
      this.limite = this.vistaActual === 'catalogo' ? 10 : 20;
    }

    this.searchSubject.pipe(
      debounceTime(400),
      distinctUntilChanged()
    ).subscribe(texto => {
      this.filtros.search = texto;
      this.aplicarFiltros();
    });

    this.cargarDatos();
  }

  cargarDatos(): void {
    // Si ya hay una petición en curso, la cancelamos para que no se mezclen los datos
    if (this.querySubscription) {
      this.querySubscription.unsubscribe();
    }

    if (this.sinMasResultados) return; 
    this.cargando = true;

    // Guardamos la suscripción
    if (this.vistaActual === 'inventario') {
      this.querySubscription = this.productsService.obtenerInventarioIndividual(this.pagina, this.limite, this.filtros)
        .subscribe({
          next: (res: any) => {
            this.procesarRespuesta(res.items, res.total, this.stocks);
          },
          error: (err) => { this.cargando = false; }
        });
    } else {
      this.querySubscription = this.productsService.obtenerProductos(this.pagina, this.limite, this.filtros)
        .subscribe({
          next: (res: any) => {
            this.procesarRespuesta(res.items, res.total, this.productosPadre);
          },
          error: (err) => { this.cargando = false; }
        });
    }
  }

  private procesarRespuesta(nuevosItems: any[], total: number, arrayDestino: any[]) {
    this.totalResultados = total;
  
  // ✨ Guardamos el conteo específico para cada pestaña
    if (this.vistaActual === 'catalogo') {
      this.totalCatalogo = total;
    } else {
      this.totalInventario = total;
    }

    console.log(nuevosItems)
    
    if (nuevosItems.length === 0) {
      this.sinMasResultados = true;
    } else {
      arrayDestino.push(...nuevosItems); 
      if (nuevosItems.length < this.limite) this.sinMasResultados = true;
      else this.pagina += 1;
    }
    this.cargando = false;
  }

  onProveedoresSelected(ids: number[]) {
    console.log(ids)
    this.filtros.proveedores_ids = ids;
    this.aplicarFiltros();
  }

  onFechasSelected(fechas: {inicio: string | null, fin: string | null}) {
    this.filtros.fecha_inicio = fechas.inicio;
    this.filtros.fecha_fin = fechas.fin;
    this.aplicarFiltros();
  }

  cambiarVista(nuevaVista: 'catalogo' | 'inventario') {
  if (this.vistaActual === nuevaVista) return;
  
  this.vistaActual = nuevaVista;
  this.cargando = false; // ✨ Desbloqueamos el cargando
  this.filtros.search = '';
  
  this.aplicarFiltros(); 
}

  onSearchInput(event: any): void {
    const valor = event.target.value;
    this.searchSubject.next(valor);
  }

  aplicarFiltros() {
    // ✨ ELIMINADO EL AUTO-SWITCHING. AHORA LA PESTAÑA MANDA.
    // Solo nos aseguramos de que el tipo de búsqueda coincida con la pestaña actual
    this.querySubscription?.unsubscribe();
    this.filtros.tipo_busqueda = this.vistaActual === 'catalogo' ? 'producto_id' : 'stock_id';

    this.pagina = 1;
    this.stocks = [];
    this.productosPadre = [];
    this.sinMasResultados = false;
    
    this.limite = this.vistaActual === 'catalogo' ? 10 : 20;
    
    this.cargarDatos();
  }

  limpiarFiltros() {
    // ✨ Mantenemos el tipo_busqueda de la pestaña actual al limpiar
    const tipoBusquedaActual = this.vistaActual === 'catalogo' ? 'producto_id' : 'stock_id';
    
    this.filtros = {
      search: '',
      tipo_busqueda: tipoBusquedaActual,
      color: null, talla: null, categoria_id: null,
      marca_id: null, estado: '', precio_min: null, precio_max: null,
      ordenar_por: 'fecha_desc',
      proveedores_ids: [],
      fecha_inicio: null,
      fecha_fin: null,
      disponibilidad: 'todos',
    };
    this.aplicarFiltros();
  }

  onCategorySelected(event: CategorySelectionEvent): void {
    this.filtros.categoria_id = event.categoriaId;
    this.aplicarFiltros();
  }

  onColorSelected(event: Color | null): void {
    this.filtros.color = event ? event.hex : null; 
    this.aplicarFiltros(); 
  }

  get filtrosActivos() {
    const activos = [];
    if (this.filtros.search) {
      let labelBusqueda = `Búsqueda: ${this.filtros.search}`;
      if (this.filtros.tipo_busqueda === 'producto_id') labelBusqueda = `ID Prod: #${this.filtros.search}`;
      if (this.filtros.tipo_busqueda === 'stock_id') labelBusqueda = `ID Stock: #${this.filtros.search}`;
      activos.push({ id: 'search', label: labelBusqueda });
    }
    if (this.filtros.proveedores_ids && this.filtros.proveedores_ids.length > 0) {
      activos.push({ id: 'proveedores', label: `${this.filtros.proveedores_ids.length} Proveedor(es)` });
    }
    if (this.filtros.disponibilidad !== 'todos') {
      const label = this.filtros.disponibilidad === 'en_stock' ? 'Solo en Stock' : 'Solo Agotados';
      activos.push({ id: 'disponibilidad', label: label });
    }
    if (this.filtros.fecha_inicio || this.filtros.fecha_fin) {
      let label = 'Fecha: ';
      if (this.filtros.fecha_inicio && this.filtros.fecha_fin) label += `${this.filtros.fecha_inicio} al ${this.filtros.fecha_fin}`;
      else if (this.filtros.fecha_inicio) label += `Desde ${this.filtros.fecha_inicio}`;
      else label += `Hasta ${this.filtros.fecha_fin}`;
      activos.push({ id: 'fechas', label: label });
    }
    if (this.filtros.categoria_id) activos.push({ id: 'categoria_id', label: 'Categoría seleccionada' });
    if (this.filtros.precio_min) activos.push({ id: 'precio_min', label: `Desde $${this.filtros.precio_min}` });
    if (this.filtros.precio_max) activos.push({ id: 'precio_max', label: `Hasta $${this.filtros.precio_max}` });
    if (this.filtros.estado) activos.push({ id: 'estado', label: `Estado: ${this.filtros.estado}` });
    if (this.filtros.color) activos.push({ id: 'color', label: 'Color', isColor: true, hex: this.filtros.color });
    return activos;
  }



  eliminarFiltro(id: string) {
  if (id === 'search') {
    this.filtros.search = '';
    this.filtros.tipo_busqueda = this.vistaActual === 'catalogo' ? 'producto_id' : 'stock_id';
  }
  if (id === 'proveedores') {
    this.filtros.proveedores_ids = [];
  }
  // 👇 ESTO DEBE ESTAR DENTRO DE SU PROPIO IF
  if (id === 'fechas') {
    this.filtros.fecha_inicio = null;
    this.filtros.fecha_fin = null;
  }
  
  if (id === 'categoria_id') this.filtros.categoria_id = null;
  if (id === 'precio_min') this.filtros.precio_min = null;
  if (id === 'precio_max') this.filtros.precio_max = null;
  if (id === 'estado') this.filtros.estado = '';
  if (id === 'color') this.filtros.color = null;
  if (id === 'disponibilidad') this.filtros.disponibilidad = 'todos';

  this.aplicarFiltros();
}

  
}