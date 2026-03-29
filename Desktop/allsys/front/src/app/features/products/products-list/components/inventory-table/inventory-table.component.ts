import { Component, Input } from '@angular/core';
import { CommonModule, TitleCasePipe } from '@angular/common';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-inventory-table',
  standalone: true,
  imports: [CommonModule, RouterLink, TitleCasePipe],
  templateUrl: './inventory-table.component.html',
  styleUrl: './inventory-table.component.css'
})
export class InventoryTableComponent {
  // ✨ Aquí recibe los datos del padre
  @Input() stocks: any[] = []; 
  
}