import { Component, OnInit, Output, EventEmitter, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ProductsService } from '../../core/services/products.service';

export interface CategorySelectionEvent {
  categoriaId: number;
  rutaCategorias: any[];
}

@Component({
  selector: 'app-category-selector',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './category-selector.component.html',
  styleUrls: ['./category-selector.component.css']
})
export class CategorySelectorComponent implements OnInit {
  todasLasCategorias: any[] = [];
  categoriaActual: any[] = [];
  rutaCategorias: any[] = [];
  dropdownAbierto = false;

  // ✨ NUEVO: Recibe el ID de la base de datos cuando estamos editando
  @Input() set categoriaInicial(id: number | null) {
    if (id && this.todasLasCategorias.length > 0) {
      this.reconstruirRutaDesdeId(id);
    } else if (id) {
      // Si el ID llega antes de que carguen las categorías de la API, lo guardamos temporalmente
      this.idPendiente = id;
    }
  }
  
  private idPendiente: number | null = null;

  @Output() categorySelected = new EventEmitter<CategorySelectionEvent>();

  constructor(private productsService: ProductsService) {}

  ngOnInit(): void {
    this.cargarCategorias();
  }

  private cargarCategorias(): void {
    this.productsService.cargarCategorias().subscribe({
      next: (data) => {
        this.todasLasCategorias = data;
        this.categoriaActual = data.filter((c: any) => c.parent_id === null);
        
        // Si teníamos un ID esperando en modo edición, ahora sí lo procesamos
        if (this.idPendiente) {
          this.reconstruirRutaDesdeId(this.idPendiente);
          this.idPendiente = null;
        }
      }
    });
  }

  // ✨ NUEVO: Esta función viaja hacia arriba para saber quiénes son los "padres" de la categoría
  private reconstruirRutaDesdeId(id: number) {
    this.rutaCategorias = [];
    let current = this.todasLasCategorias.find(c => c.id === id);
    
    while (current) {
      this.rutaCategorias.unshift(current); // Lo metemos al principio del array
      if (current.parent_id) {
        current = this.todasLasCategorias.find(c => c.id === current.parent_id);
      } else {
        current = undefined;
      }
    }
    
    // Le avisamos al padre (ProductFormComponent) para que cargue los atributos correctos
    this.categorySelected.emit({
      categoriaId: id,
      rutaCategorias: [...this.rutaCategorias]
    });
  }

  abrirCategorias(): void { 
    this.dropdownAbierto = !this.dropdownAbierto; 
  }

  seleccionarCategoria(cat: any): void {
    if (cat.parent_id === null) {
      this.rutaCategorias = [cat];
    } else {
      const parentIndex = this.rutaCategorias.findIndex(c => c.id === cat.parent_id);
      if (parentIndex !== -1) {
        this.rutaCategorias = this.rutaCategorias.slice(0, parentIndex + 1);
        this.rutaCategorias.push(cat);
      } else {
        this.rutaCategorias.push(cat);
      }
    }

    const sub = this.todasLasCategorias.filter(c => c.parent_id === cat.id);
    
    if (sub.length > 0) {
      this.categoriaActual = sub;
    } else {
      this.dropdownAbierto = false;
      this.categorySelected.emit({
        categoriaId: cat.id,
        rutaCategorias: [...this.rutaCategorias]
      });
    }
  }

  volverCategoria(): void {
    this.rutaCategorias.pop();
    const last = this.rutaCategorias.at(-1);
    this.categoriaActual = last ? 
      this.todasLasCategorias.filter(c => c.parent_id === last.id) : 
      this.todasLasCategorias.filter(c => c.parent_id === null);
  }

  getNombreCategoriaSeleccionada(): string {
    return this.rutaCategorias.length ? this.rutaCategorias.map(c => c.nombre).join(' / ') : 'Seleccionar categoría';
  }
}