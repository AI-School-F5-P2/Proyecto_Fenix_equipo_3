import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { SuppliersService } from '../../../../../core/services/proveedores.service'; // Ajusta la ruta

export interface Proveedor {
  id?: number;
  nombre: string;
  isNew?: boolean;
}

@Component({
  selector: 'app-supplier-selector',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './supplier-selector.component.html',
  styleUrls: ['./supplier-selector.component.css']
})
export class SupplierSelectorComponent implements OnInit {
  proveedores: Proveedor[] = [];
  proveedorInput: string = '';
  dropdownOpen: boolean = false;
  proveedorSeleccionado: Proveedor | null = null;
  cargandoProveedores = false;
  private idInicialPendiente: number | null = null;

  // ✨ ESCUCHA EL DATO QUE VIENE DE LA BASE DE DATOS
@Input() set proveedorInicialId(id: number | null | undefined) {
    if (id) {
      this.idInicialPendiente = id;
      this.vincularProveedor(); // Intentamos vincularlo inmediatamente
    } else {
      this.proveedorSeleccionado = null;
      this.proveedorInput = '';
    }
  }

  @Output() supplierChanged = new EventEmitter<Proveedor>();

  constructor(private suppliersService: SuppliersService) {}

  ngOnInit(): void {
    this.cargarProveedores();
  }

  cargarProveedores(): void {
    this.cargandoProveedores = true;
    this.suppliersService.getProveedores().subscribe({
      next: (data: any[]) => {
        this.proveedores = data.map(p => ({ 
          id: p.id, 
          nombre: p.nombre_proveedor || p.nombre 
        })).sort((a, b) => a.nombre.localeCompare(b.nombre));
        
        this.cargandoProveedores = false;

        // ✨ 2. CUANDO LLEGAN LOS DATOS, BUSCAMOS EL ID PENDIENTE
        this.vincularProveedor();
      },
      error: () => this.cargandoProveedores = false
    });
  }

  // ✨ 3. FUNCIÓN QUE UNE EL ID CON EL NOMBRE
  private vincularProveedor(): void {
    if (this.idInicialPendiente && this.proveedores.length > 0) {
      const provEncontrado = this.proveedores.find(p => p.id === this.idInicialPendiente);
      if (provEncontrado) {
        this.proveedorSeleccionado = provEncontrado;
        this.proveedorInput = provEncontrado.nombre; 
        this.idInicialPendiente = null; 

        // ✨ LA PIEZA FALTANTE: ¡Avisarle al padre del nombre que acabamos de descubrir!
        this.supplierChanged.emit(provEncontrado);
      }
    }
  }

  get proveedoresFiltrados(): Proveedor[] {
    const input = this.proveedorInput.trim().toLowerCase();
    let filtrados = this.proveedores.filter(p => p.nombre.toLowerCase().includes(input));
    
    if (this.proveedorSeleccionado) {
      filtrados = filtrados.filter(p => p.nombre !== this.proveedorSeleccionado!.nombre);
      filtrados.unshift(this.proveedorSeleccionado);
    }
    
    if (input && !this.proveedores.some(p => p.nombre.toLowerCase() === input)) {
      filtrados.unshift({ nombre: this.proveedorInput, isNew: true });
    }
    return filtrados;
  }

  selectProveedor(proveedor: Proveedor): void {
    this.dropdownOpen = false;
    this.proveedorSeleccionado = proveedor;
    this.proveedorInput = proveedor.nombre;
    // ✨ AVISAMOS AL PADRE (a la fila de stock correspondiente)
    this.supplierChanged.emit(proveedor);
  }

  onBlur(): void {
    setTimeout(() => {
      this.dropdownOpen = false;
      if (this.proveedorSeleccionado) {
        this.proveedorInput = this.proveedorSeleccionado.nombre;
      } else {
        this.proveedorInput = '';
      }
    }, 200);
  }

  onInputChange(): void { 
    this.dropdownOpen = true; 
    this.proveedorSeleccionado = null;
    this.supplierChanged.emit({ nombre: this.proveedorInput, isNew: true });
  }

  onFocus(): void { this.dropdownOpen = true; }
}