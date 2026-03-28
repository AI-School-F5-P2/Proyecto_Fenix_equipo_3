import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ProductsService } from '../../../../../core/services/products.service';

export interface Marca {
  id?: number;
  nombre: string;
  isNew?: boolean;
}

@Component({
  selector: 'app-brand-selector',
  imports: [CommonModule, FormsModule],
  templateUrl: './brand-selector.component.html',
  styleUrl: './brand-selector.component.css'
})
export class BrandSelectorComponent implements OnInit {
  // @Input() marcas: Marca[] = [];
  @Input() initialValue: string = ''; // Para edición: nombre de la marca actual
  @Output() brandChanged = new EventEmitter<Marca>();

  marcaInput: string = '';
  dropdownOpen: boolean = false;
  marcaSeleccionada: Marca | null = null;

  marcas: any[] = [];

  constructor(private productsService: ProductsService) {}

  ngOnInit() {
    
      this.cargarMarcas();
      // this.marcaInput = this.initialValue;
      // // Intentamos encontrar la marca en la lista inicial
      // const existente = this.marcas.find(m => m.nombre.toLowerCase() === this.initialValue.toLowerCase());
      // if (existente) this.marcaSeleccionada = existente;
    
  }

  cargarMarcas(): void {
    this.productsService.cargarMarcas().subscribe({
      next: (data: any[]) => {
        this.marcas = data.sort((a,b) => a.nombre.localeCompare(b.nombre));
      }
    });
  }

@Input() set marcaInicial(marca: any | null) {
    if (marca) {
      this.marcaSeleccionada = marca;
      this.marcaInput = marca.nombre;
    } else {
      // Si llega null (al darle a "Añadir Nuevo Producto"), limpiamos todo
      this.marcaSeleccionada = null;
      this.marcaInput = '';
    }
  }

  get marcasFiltradas(): Marca[] {
    const input = this.marcaInput.trim().toLowerCase();
    let filtradas = this.marcas.filter(m => m.nombre.toLowerCase().includes(input));

    // Si hay una seleccionada, la ponemos primero
    if (this.marcaSeleccionada) {
      filtradas = filtradas.filter(m => m.nombre !== this.marcaSeleccionada!.nombre);
      filtradas.unshift(this.marcaSeleccionada);
    }

    // Opción para marca nueva
    if (input && !this.marcas.some(m => m.nombre.toLowerCase() === input)) {
      filtradas.unshift({ nombre: this.marcaInput, isNew: true });
    }
    return filtradas;
  }

  selectMarca(marca: Marca): void {
    this.marcaSeleccionada = marca;
    this.marcaInput = marca.nombre;
    this.dropdownOpen = false;
    this.brandChanged.emit(marca);
  }

  onInputChange(): void {
    this.dropdownOpen = true;
  }

  onBlur(): void {
    setTimeout(() => {
      this.dropdownOpen = false;
      if (this.marcaSeleccionada) {
        this.marcaInput = this.marcaSeleccionada.nombre;
      } else if (this.marcaInput.trim()) {
        // Si no seleccionó nada pero escribió algo nuevo
        const nueva = { nombre: this.marcaInput, isNew: true };
        this.selectMarca(nueva);
      }
    }, 200);
  }

  onFocus(): void {
    this.dropdownOpen = true;
  }
}