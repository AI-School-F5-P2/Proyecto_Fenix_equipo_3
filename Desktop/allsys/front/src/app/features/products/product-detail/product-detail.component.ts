import { Component, OnInit } from '@angular/core';
import { CommonModule, TitleCasePipe } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { ProductsService } from '../../../core/services/products.service';

@Component({
  selector: 'app-product-detail',
  imports: [CommonModule, TitleCasePipe, RouterLink],
  templateUrl: './product-detail.component.html',
  styleUrls: ['./product-detail.component.css']
})
export class ProductDetailComponent implements OnInit {

  producto: any = null;
  cargando = true;

  constructor(
    private route: ActivatedRoute,
    private productsService: ProductsService
  ) {}

  ngOnInit() {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (id) {
      this.productsService.obtenerProducto(id)
        .subscribe({
          next: (data) => {
            this.producto = data;
            console.log(this.producto)
            this.cargando = false;
          },
          error: (err) => {
            console.error('Error al cargar producto:', err);
            this.cargando = false;
          }
        });
    } else {
      console.error('No se proporcionó ID de producto');
      this.cargando = false;
    }
  }

  

  // Ejemplo: ver imagen grande
  verImagen(imagen: string) {
    window.open(imagen, '_blank');
  }
}
