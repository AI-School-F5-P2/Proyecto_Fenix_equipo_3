import { Component, Input, Output, EventEmitter, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

// ✨ IMPORTA AMBOS DESDE EL CONFIG (Asegúrate de que la ruta sea correcta)
import { COLORES_PALETA, Color } from '../../../../features/products/add-product/product-form.config';

@Component({
  selector: 'app-color-selector',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './color-selector.component.html',
  styleUrl: './color-selector.component.css'
})
export class ColorSelectorComponent implements OnInit {
  // 1. Usamos la lista importada directamente
  listaColores: Color[] = COLORES_PALETA;

  // 2. El Input recibe el string hexadecimal
  @Input() set initialHex(hex: string | null | undefined) {
    if (!hex || hex === '#FFFFFF') {
      this.colorSeleccionado = null;
    } else {
      const encontrado = this.listaColores.find(c => c.hex.toLowerCase() === hex.toLowerCase());
      this.colorSeleccionado = encontrado || { hex: hex, nombre: 'Personalizado' };
    }
  }

  // 3. El Output emite el objeto Color completo para que el formulario lo entienda
  @Output() colorChanged = new EventEmitter<Color>();

  colorSeleccionado: Color | null = null;
  dropdownOpen = false;

  ngOnInit() { }

  selectColor(color: Color) {
    this.colorSeleccionado = color;
    this.colorChanged.emit(color); // ✅ Emitimos el objeto Color (el que importamos)
    this.dropdownOpen = false;
  }

  toggleDropdown() { this.dropdownOpen = !this.dropdownOpen; }
  closeDropdown() { setTimeout(() => { this.dropdownOpen = false; }, 200); }
}