import { Component, Input, Output, EventEmitter, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

export interface Color {
  hex: string;
  nombre: string;
  claro?: boolean;
}

@Component({
  selector: 'app-color-selector',
  imports: [CommonModule, FormsModule],
  templateUrl: './color-selector.component.html',
  styleUrl: './color-selector.component.css'
})
export class ColorSelectorComponent implements OnInit {
  @Input() colores: Color[] = [];
  @Input() initialHex: string = '#FFFFFF';
  @Output() colorChanged = new EventEmitter<Color>();

  colorSeleccionado: Color | null = null;
  dropdownOpen = false;

  ngOnInit() {
    // Si viene un valor inicial (ej. al editar), buscamos el objeto completo
    if (this.initialHex) {
      const encontrado = this.colores.find(c => c.hex.toLowerCase() === this.initialHex.toLowerCase());
      this.colorSeleccionado = encontrado || { hex: this.initialHex, nombre: 'Personalizado' };
    }
  }

  toggleDropdown() {
    this.dropdownOpen = !this.dropdownOpen;
  }

  selectColor(color: Color) {
    this.colorSeleccionado = color;
    this.colorChanged.emit(color);
    this.dropdownOpen = false;
  }

  closeDropdown() {
    // Timeout para permitir que el click en el item se registre antes de cerrar
    setTimeout(() => {
      this.dropdownOpen = false;
    }, 200);
  }
}