import { Component, HostListener, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { ProductsService } from '../../../core/services/products.service';

interface Talla {
  id?: number;
  talla: string;
  stock: number;
}

interface Variante {
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
    if (!confirm('¿Eliminar esta imagen?')) return;
    const idx = variante.imagenes.indexOf(imagen);
    if (idx >= 0) variante.imagenes.splice(idx, 1);
    if (variante.imagenesFiles) variante.imagenesFiles.splice(idx, 1);
  }

  verImagen(url: string) {
    window.open(url, '_blank');
  }

  // ================== GUARDAR ==================

  guardarProducto() {
  if (!this.producto) return;

  const formData = new FormData();
  formData.append('nombre', this.producto.nombre);
  formData.append('descripcion', this.producto.descripcion);
  formData.append('precio', this.producto.precio.toString());
  formData.append('tipo', this.producto.tipo);
  formData.append('categoria_id', this.categoriaSeleccionadaFinal!.toString());
  formData.append('marca_id', this.marcaSeleccionada!.toString());

  // Enviar variantes sin las imágenes
  const variantesPayload = this.producto.variantes.map((v: Variante) => ({
    id: v.id,
    color: v.color,
    color_nombre: v.color_nombre,
    precio: v.precio,
    descuento: v.descuento,
    tallas: v.tallas
  }));
  formData.append('variantes', JSON.stringify(variantesPayload));

  // Enviar imágenes como archivos separados con nombre variante-{id}
  this.producto.variantes.forEach((v: Variante, idx: number) => {
    if (v.imagenesFiles && v.imagenesFiles.length > 0) {
      v.imagenesFiles.forEach(file => {
        // "imagenes" será el nombre que FastAPI recibirá
        formData.append('imagenes', file, `variante-${v.id || idx}-${file.name}`);
      });
    }
  });

  this.productsService.actualizarProducto(this.producto.id, formData)
    .subscribe({
      next: () => alert('✅ Producto actualizado correctamente'),
      error: (err) => console.error(err)
    });
}


  // ================== SALIDA ==================

  @HostListener('window:beforeunload', ['$event'])
  confirmarSalida(event: any) {
    event.returnValue = true;
  }

}


// solo se esta actualixando proiducto mas no sus variantes
