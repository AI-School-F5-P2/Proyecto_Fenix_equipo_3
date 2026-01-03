import { Component, OnInit } from '@angular/core';
import { ProductsService } from '../../../core/services/products.service';
import { CommonModule, TitleCasePipe } from '@angular/common';
import { RouterLink } from "@angular/router";

@Component({
  selector: 'app-products-list',
 imports: [CommonModule, TitleCasePipe, RouterLink],
  templateUrl: './products-list.component.html',
  styleUrl: './products-list.component.css'
})


export class ProductsListComponent implements OnInit {

  productos: any[] = [];
  pagina: number = 0;       // Página actual
  limite: number = 10;      // Cantidad de productos por página
  cargando: boolean = false;
  sinMasProductos: boolean = false;

  constructor(private productsService: ProductsService) {}

  ngOnInit(): void {
    this.cargarProductos();
  }

  cargarProductos(): void {
    if (this.cargando || this.sinMasProductos) return;

    this.cargando = true;
    const offset = this.pagina * this.limite;

    this.productsService.obtenerProductos(this.limite, offset)
      .subscribe({
        next: (res: any[]) => {
          if (res.length === 0) {
            this.sinMasProductos = true;  // No hay más productos
          } else {
            this.productos.push(...res);
            console.log(this.productos)
            this.pagina += 1;             // Incrementa la página
          }
          this.cargando = false;

        },
        error: (err) => {
          console.error('Error al cargar productos:', err);
          this.cargando = false;
        }
      });
  }

  // Método opcional para "Cargar más"
  cargarMas(): void {
    this.cargarProductos();
  }

}
