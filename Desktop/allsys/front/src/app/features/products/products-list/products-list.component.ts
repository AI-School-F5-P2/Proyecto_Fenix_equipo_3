import { Component, OnInit } from '@angular/core';
import { ProductsService } from '../../../core/services/products.service';
import { CommonModule, TitleCasePipe } from '@angular/common';
import { RouterLink } from "@angular/router";

@Component({
  selector: 'app-products-list',
  standalone: true, // Asumo que es standalone por cómo importas
  imports: [CommonModule, TitleCasePipe, RouterLink],
  templateUrl: './products-list.component.html',
  styleUrl: './products-list.component.css'
})
export class ProductsListComponent implements OnInit {

  productos: any[] = [];
  
  // ✨ CAMBIO: Empezamos en la página 1 (porque así lo definimos en FastAPI)
  pagina: number = 1;       
  limite: number = 10;      // Cantidad de productos por página
  totalProductos: number = 0; // ✨ NUEVO: Guardamos el total del inventario
  
  cargando: boolean = false;
  sinMasProductos: boolean = false;

  constructor(private productsService: ProductsService) {}

  ngOnInit(): void {
    this.cargarProductos();
  }

  cargarProductos(): void {
    if (this.cargando || this.sinMasProductos) return;

    this.cargando = true;

    // ✨ CAMBIO: Pasamos 'pagina' en lugar de 'offset'
    this.productsService.obtenerProductos(this.pagina, this.limite)
      .subscribe({
        // ✨ CAMBIO: res ya no es any[], es un objeto (o tipo PaginatedResponse)
        next: (res: any) => { 
          console.log('Respuesta del servidor:', res);
          
          this.totalProductos = res.total; // Guardamos el total general
          
          // ✨ AQUÍ ESTÁ LA MAGIA: Apuntamos a res.items
          if (res.items.length === 0) {
            this.sinMasProductos = true;  // Ya llegamos al final
          } else {
            // Hacemos el push SÓLO de la lista de ítems
            this.productos.push(...res.items); 
            console.log('Productos acumulados:', this.productos);
            
            // Si nos devolvieron menos del límite, significa que ya no hay más para la próxima
            if (res.items.length < this.limite) {
               this.sinMasProductos = true;
            } else {
               this.pagina += 1; // Preparamos la siguiente página
            }
          }
          this.cargando = false;
        },
        error: (err) => {
          console.error('Error al cargar productos:', err);
          this.cargando = false;
        }
      });
  }

  // Método opcional para el botón HTML "Cargar más"
  cargarMas(): void {
    this.cargarProductos();
  }
}