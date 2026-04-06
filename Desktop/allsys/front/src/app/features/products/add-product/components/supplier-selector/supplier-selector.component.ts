import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { SuppliersService, TipoProveedor } from '../../../../../core/services/proveedores.service';

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
  // ✨ NUEVO: Define qué tipo de proveedores cargar. Por defecto 'inventario'.
  @Input() tipoProveedor: TipoProveedor = 'inventario'; 

  proveedores: Proveedor[] = [];
  proveedorInput: string = '';
  dropdownOpen: boolean = false;
  proveedorSeleccionado: Proveedor | null = null;
  cargandoProveedores = false;
  private idInicialPendiente: number | null = null;

  @Input() set proveedorInicialId(id: number | null | undefined) {
    if (id) {
      this.idInicialPendiente = id;
      this.vincularProveedor();
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
    
    // ✨ ACTUALIZADO: Pasamos el tipoProveedor al servicio
    this.suppliersService.getProveedores(this.tipoProveedor).subscribe({
      next: (data: any[]) => {
        this.proveedores = data.map(p => ({ 
          id: p.id, 
          nombre: p.nombre_proveedor || p.nombre 
        })).sort((a, b) => a.nombre.localeCompare(b.nombre));
        
        this.cargandoProveedores = false;
        this.vincularProveedor();
      },
      error: () => this.cargandoProveedores = false
    });
  }

  private vincularProveedor(): void {
    if (this.idInicialPendiente && this.proveedores.length > 0) {
      const provEncontrado = this.proveedores.find(p => p.id === this.idInicialPendiente);
      if (provEncontrado) {
        this.proveedorSeleccionado = provEncontrado;
        this.proveedorInput = provEncontrado.nombre; 
        this.idInicialPendiente = null; 
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
    
    // Si el usuario escribe algo que no existe, ofrece crearlo
    if (input && !this.proveedores.some(p => p.nombre.toLowerCase() === input)) {
      filtrados.unshift({ nombre: this.proveedorInput, isNew: true });
    }
    return filtrados;
  }

  selectProveedor(proveedor: Proveedor): void {
    this.dropdownOpen = false;
    this.proveedorSeleccionado = proveedor;
    this.proveedorInput = proveedor.nombre;
    this.supplierChanged.emit(proveedor);
  }

  onBlur(): void {
    setTimeout(() => {
      this.dropdownOpen = false;
      if (this.proveedorSeleccionado) {
        this.proveedorInput = this.proveedorSeleccionado.nombre;
      } else if (!this.proveedorInput.trim()) {
        this.proveedorInput = '';
      }
      // Nota: Si es nuevo (isNew), no lo borramos para permitir que el padre lo cree al hacer submit
    }, 200);
  }

  onInputChange(): void { 
    this.dropdownOpen = true; 
    this.proveedorSeleccionado = null;
    // Emitimos que es un proveedor nuevo para que el formulario padre sepa que debe crearlo
    this.supplierChanged.emit({ nombre: this.proveedorInput, isNew: true });
  }

  onFocus(): void { this.dropdownOpen = true; }
}