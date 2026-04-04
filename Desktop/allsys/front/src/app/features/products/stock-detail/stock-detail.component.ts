import { Component, OnInit } from '@angular/core';
import { CommonModule, TitleCasePipe } from '@angular/common';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { ProductsService } from '../../../core/services/products.service';

@Component({
  selector: 'app-stock-detail',
  standalone: true,
  imports: [CommonModule, TitleCasePipe, RouterLink],
  templateUrl: './stock-detail.component.html',
  styleUrls: ['./stock-detail.component.css'] // Puedes reutilizar los estilos del product-detail
})
export class StockDetailComponent implements OnInit {

  stock: any = null;
  cargando = true;

  constructor(
    private route: ActivatedRoute,
    private productsService: ProductsService,
    private router: Router
  ) {}

  ngOnInit() {
    // Capturamos el ID del stock desde la URL (ej: /stock-detail/15)
    const stockId = Number(this.route.snapshot.paramMap.get('id'));
    
    if (stockId) {
      // ⚠️ Asegúrate de tener este método en tu ProductsService
      this.productsService.obtenerStock(stockId).subscribe({
        next: (data) => {
          this.stock = data;
          this.cargando = false;
        },
        error: (err) => {
          console.error('Error al cargar el stock:', err);
          this.cargando = false;
        }
      });
    } else {
      console.error('No se proporcionó ID de stock');
      this.cargando = false;
    }
  }

  // Ejemplo: Volver atrás
  volver() {
    this.router.navigate(['/view-stocks']); // O la ruta que uses para tu lista
  }

  // Si quieres permitir edición rápida, puedes enviarlo al form de edición del producto padre
  editarStock() {
    if (this.stock?.producto_id) {
      this.router.navigate(['/edit-stock', this.stock.producto_id]);
    }
  }
}