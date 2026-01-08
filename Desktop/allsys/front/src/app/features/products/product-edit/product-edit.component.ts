import { Component, HostListener, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { ProductsService } from '../../../core/services/products.service';
import { runPostSignalSetFn } from '@angular/core/primitives/signals';

interface Talla {
  id?: number;
  talla: string;
  stock: number;
}

interface Variante {
  imagenes_eliminadas: any;
  id?: number;
  color: string;
  color_nombre: string;
  precio: number;
  descuento: number;
  tallas: Talla[];
  imagenes: any[];
  imagenesFiles?: File[];
}

@Component({
  selector: 'app-product-edit',
  standalone: true,
  imports: [FormsModule, CommonModule],
  templateUrl: './product-edit.component.html',
  styleUrls: ['./product-edit.component.css']
})
export class ProductEditComponent implements OnInit {

  producto: any = null;
  cargando = true;

  // Categorías
  todasLasCategorias: any[] = [];
  categoriaActual: any[] = [];
  rutaCategorias: any[] = [];
  categoriaSeleccionadaFinal: number | null = null;
  dropdownAbierto = false;

  // Marcas
  marcas: any[] = [];
  marcaSeleccionada: number | null = null;

  constructor(
    private route: ActivatedRoute,
    private productsService: ProductsService
  ) {}

  ngOnInit() {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (!id) {
      this.cargando = false;
      return;
    }

    this.productsService.cargarCategorias().subscribe(data => {
      this.todasLasCategorias = data;

      this.productsService.obtenerProducto(id).subscribe({
        next: (data) => {
          this.producto = data;
          console.log(this.producto)
          this.marcaSeleccionada = this.producto.marca?.id || null;

          this.inicializarCategorias();
          this.cargando = false;
        },
        error: () => this.cargando = false
      });
    });

    this.productsService.cargarMarcas().subscribe(data => {
      this.marcas = data;
    });
  }

  // ================== CATEGORÍAS ==================

  private inicializarCategorias() {
    if (!this.producto?.categoria) {
      this.rutaCategorias = [];
      this.categoriaActual = this.todasLasCategorias.filter(c => c.parent_id === null);
      this.categoriaSeleccionadaFinal = null;
      this.dropdownAbierto = false;
      return;
    }

    const ruta: any[] = [];
    let cat = this.producto.categoria;

    while (cat) {
      ruta.unshift(cat);
      cat = this.todasLasCategorias.find(c => c.id === cat.parent_id);
    }

    this.rutaCategorias = [...ruta];

    const ultima = this.rutaCategorias[this.rutaCategorias.length - 1];
    const hijos = this.todasLasCategorias.filter(c => c.parent_id === ultima.id);
    this.categoriaActual = hijos.length > 0 ? hijos : this.todasLasCategorias.filter(c => c.parent_id === ultima.parent_id);

    this.categoriaSeleccionadaFinal = ultima.id;
    this.dropdownAbierto = false;
  }

  getNombreCategoriaSeleccionada(): string {
    if (this.rutaCategorias.length === 0) return 'Seleccionar categoría';
    return this.rutaCategorias.map(c => c.nombre).join(' / ');
  }

  tieneSubcategorias(cat: any): boolean {
    return this.todasLasCategorias.some(c => c.parent_id === cat.id);
  }

  esCategoriaSeleccionada(cat: any): boolean {
    return cat.id === this.categoriaSeleccionadaFinal;
  }

  seleccionarCategoria(cat: any) {
    const hijos = this.todasLasCategorias.filter(c => c.parent_id === cat.id);

    if (hijos.length > 0) {
      this.rutaCategorias.push(cat);
      this.categoriaActual = hijos;
      this.dropdownAbierto = true;
    } else {
      this.rutaCategorias.push(cat);
      this.categoriaActual = this.todasLasCategorias.filter(c => c.parent_id === cat.parent_id);
      this.categoriaSeleccionadaFinal = cat.id;
      this.dropdownAbierto = false;
    }
  }

  volverCategoria() {
  if (this.rutaCategorias.length === 0) return;

  // Si la última categoría es final (es decir, categoriaSeleccionadaFinal está en la última)
  const ultima = this.rutaCategorias[this.rutaCategorias.length - 1];
  if (this.categoriaSeleccionadaFinal === ultima.id) {
    // Retrocedemos **2 niveles**: desmarcar final + subir al padre
    this.rutaCategorias.pop(); // eliminar la categoría final
    this.categoriaSeleccionadaFinal = null;

    // Luego otro pop si aún queda un nivel
    if (this.rutaCategorias.length > 0) {
      this.rutaCategorias.pop();
    }
  } else {
    // No es final, solo retrocedemos un nivel
    this.rutaCategorias.pop();
  }

  // Actualizar categoriaActual
  if (this.rutaCategorias.length === 0) {
    this.categoriaActual = this.todasLasCategorias.filter(c => c.parent_id === null);
  } else {
    const nuevaUltima = this.rutaCategorias[this.rutaCategorias.length - 1];
    this.categoriaActual = this.todasLasCategorias.filter(c => c.parent_id === nuevaUltima.id);
  }

  this.dropdownAbierto = true;
}


eliminarProducto() {
  if (!confirm('⚠️ ¿Eliminar este producto? Esta acción no se puede deshacer')) {
    return;
  }

  this.productsService.eliminarProducto(this.producto.id).subscribe({
    next: () => {
      alert('✅ Producto eliminado correctamente');
      window.history.back(); // o navegar a listado
    },
    error: (err) => {
      console.error(err);
      alert('❌ Error al eliminar el producto');
    }
  });
}




  // ================== VARIANTES ==================

  agregarVariante() {
    this.producto.variantes.push({
      color: '#000000',
      color_nombre: 'Negro',
      precio: 0,
      descuento: 0,
      tallas: [{ talla: '', stock: 0 }],
      imagenes: [],
      imagenesFiles: []
    });
  }

  eliminarVariante(index: number) {
    this.producto.variantes.splice(index, 1);
  }

  agregarTalla(variante: Variante) {
    variante.tallas.push({ talla: '', stock: 0 });
  }

  eliminarTalla(variante: Variante, index: number) {
    variante.tallas.splice(index, 1);
  }

  onFilesSelected(event: any, variante: Variante) {
    const files: FileList = event.target.files;
    if (!files) return;

    Array.from(files).forEach(file => {
      if (!variante.imagenesFiles) variante.imagenesFiles = [];
      variante.imagenesFiles.push(file);

      const reader = new FileReader();
      reader.onload = e =>
        variante.imagenes.push({ url: (e.target as FileReader).result as string });
      reader.readAsDataURL(file);
    });
  }

eliminarImagen(variante: Variante, imagen: any) {
  if (!confirm('¿Eliminar imagen?')) return;

  if (!variante.imagenes_eliminadas) {
    variante.imagenes_eliminadas = [];
  }

  if (imagen.id) {
    variante.imagenes_eliminadas.push(imagen.id);
  }

  variante.imagenes = variante.imagenes.filter(i => i !== imagen);
}

  verImagen(url: string) {
    window.open(url, '_blank');
  }

  // ================== GUARDAR ==================

  guardarProducto() {
  if (!this.producto) return;

  const formData = new FormData();

  // ===== PRODUCTO =====
  formData.append('nombre', this.producto.nombre);
  formData.append('descripcion', this.producto.descripcion || '');
  formData.append('precio', this.producto.precio.toString());
  formData.append('tipo', this.producto.tipo || '');
  formData.append('categoria_id', this.categoriaSeleccionadaFinal!.toString());
  formData.append('marca_id', this.marcaSeleccionada!.toString());

  // ===== DATOS DE COMPRA =====
  if (this.producto.lugar_compra) {
    formData.append('lugar_compra', this.producto.lugar_compra);
  }

  if (this.producto.fecha_compra) {
    formData.append(
      'fecha_compra',
      this.producto.fecha_compra.substring(0, 10)
    );
  }

  if (this.producto.precio_compra !== null) {
    formData.append(
      'precio_compra',
      this.producto.precio_compra.toString()
    );
  }

  // ===== VARIANTES =====
  const variantesPayload = this.producto.variantes.map((v: any) => ({
    id: v.id,
    color: v.color,
    color_nombre: v.color_nombre,
    precio: v.precio,
    descuento: v.descuento,
    tallas: v.tallas,
    imagenes_eliminadas: v.imagenes_eliminadas || []
  }));

  formData.append('variantes', JSON.stringify(variantesPayload));

  // ===== IMÁGENES =====
  this.producto.variantes.forEach((v: any, idx: number) => {
    v.imagenesFiles?.forEach((file: File) => {
      const filename = v.id
        ? `variante-${v.id}-${file.name}`
        : `imagenes_nueva_variante_${idx}-${file.name}`;

      formData.append('imagenes', file, filename);
    });
  });

  this.productsService
    .actualizarProducto(this.producto.id, formData)
    .subscribe({
      next: () => alert('✅ Producto actualizado correctamente'),
      error: err => console.error(err)
    });
}




  // ================== SALIDA ==================

  @HostListener('window:beforeunload', ['$event'])
  confirmarSalida(event: any) {
    event.returnValue = true;
  }

}


