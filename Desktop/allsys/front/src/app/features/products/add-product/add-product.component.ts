import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ProductsService } from '../../../core/services/products.service';

interface Talla {
  talla: string;
  stock: number;
}


interface Variante {
  color: string;        // hex
  color_nombre: string;  // nombre legible
  precio: number | null;
  descuento: number | null;
  tallas: Talla[];
  imagenes: string[];
  imagenesFiles: File[];
}


@Component({
  selector: 'app-add-product',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './add-product.component.html',
  styleUrls: ['./add-product.component.css']
})
export class AddProductComponent implements OnInit {

  nombre = '';
  descripcion = '';
  precio: number | null = null;

  todasLasCategorias: any[] = [];
  categoriaActual: any[] = [];
  rutaCategorias: any[] = [];
  categoriaSeleccionadaFinal: number | null = null;

  lugarCompra: string = '';
  fechaCompra: string | null = null; // formato yyyy-mm-dd
  precioCompra: number | null = null;

  dropdownAbierto = false;
  tipo: string = 'General'; // no editable por el usuario

  marcas: any[] = [];
  marcaSeleccionada: number | null = null;


  coloresPredefinidos = [
  { hex: '#000000', nombre: 'Negro' },
  { hex: '#FFFFFF', nombre: 'Blanco' },
  { hex: '#FF0000', nombre: 'Rojo' },
  { hex: '#00FF00', nombre: 'Verde' },
  { hex: '#0000FF', nombre: 'Azul' },
  { hex: '#FFFF00', nombre: 'Amarillo' },
  { hex: '#FFA500', nombre: 'Naranja' },
  { hex: '#800080', nombre: 'Morado' },
  { hex: '#FFC0CB', nombre: 'Rosa' },
  { hex: '#808080', nombre: 'Gris' }
];

 variantes: Variante[] = [
  {
    color: '#000000',
    color_nombre: 'Negro',
    precio: null,
    descuento: null,
    tallas: [{ talla: '', stock: 0 }],
    imagenes: [],
    imagenesFiles: []
  }
];


  constructor(
    private productsService: ProductsService,
    private router: Router
  ) {}

  ngOnInit() {
    this.productsService.cargarCategorias().subscribe(data => {
      this.todasLasCategorias = data;
      console.log('categorias: ',data)
      this.categoriaActual = data.filter(c => c.parent_id === null);
    });

    // 🔥 Cargar marcas
    this.productsService.cargarMarcas().subscribe(data => {
      this.marcas = data;
      console.log('marcas: ',this.marcas)
    });
  }

  // ---------------- CATEGORÍAS ----------------

  tieneSubcategorias(cat: any): boolean {
    return this.todasLasCategorias.some(c => c.parent_id === cat.id);
  }

  determinarTipo(cat: string): void {
  const nombre = cat.toLowerCase();

  const tiposValidos = ['ropa', 'accesorio', 'calzado', 'electronica', 'electrónica'];

  const tipoEncontrado = tiposValidos.find(tipo =>
    nombre.includes(tipo)
  );

  //cambia el tipo si encuentra uno válido
  if (tipoEncontrado) {
    this.tipo = tipoEncontrado
    console.log('✅ Tipo detectado:', this.tipo);
  } 
}


  seleccionarCategoria(cat: any) {
    this.determinarTipo(cat.nombre)
  const subcategorias = this.todasLasCategorias.filter(
    c => c.parent_id === cat.id
  );

  this.rutaCategorias.push(cat);

  if (subcategorias.length > 0) {
    this.categoriaActual = subcategorias;
  } else {
    this.categoriaSeleccionadaFinal = cat.id;
    this.dropdownAbierto = false;
  }
}


  seleccionarColor(color: any, index: number) {
  this.variantes[index].color = color.hex;
  this.variantes[index].color_nombre = color.nombre;
}

onColorManualChange(hex: string, index: number) {
  const encontrado = this.coloresPredefinidos.find(
    c => c.hex.toLowerCase() === hex.toLowerCase()
  );

  if (encontrado) {
    this.variantes[index].color_nombre = encontrado.nombre;
  } else {
    this.variantes[index].color_nombre = 'Color personalizado';
  }
}

  volverCategoria() {
    this.rutaCategorias.pop();

    if (this.rutaCategorias.length === 0) {
      this.categoriaActual = this.todasLasCategorias.filter(
        c => c.parent_id === null
      );
    } else {
      const ultimo = this.rutaCategorias[this.rutaCategorias.length - 1];
      this.categoriaActual = this.todasLasCategorias.filter(
        c => c.parent_id === ultimo.id
      );
    }
  }

  getNombreCategoriaSeleccionada(): string {
    if (this.rutaCategorias.length === 0) return 'Seleccionar categoría';
    return this.rutaCategorias.map(c => c.nombre).join(' / ');
  }

  // ---------------- VARIANTES ----------------

 agregarVariante() {
  this.variantes.push({
    color: '#000000',
    color_nombre: 'Negro',
    precio: null,
    descuento: null,
    tallas: [{ talla: '', stock: 0 }],
    imagenes: [],
    imagenesFiles: []
  });
}

  eliminarVariante(index: number) {
    this.variantes.splice(index, 1);
  }

  agregarTalla(index: number) {
    this.variantes[index].tallas.push({ talla: '', stock: 0 });
  }

  eliminarTalla(i: number, j: number) {
    this.variantes[i].tallas.splice(j, 1);
  }

  onFilesSelected(event: Event, index: number) {
    const files = (event.target as HTMLInputElement).files;
    if (!files) return;

    Array.from(files).forEach(file => {
      this.variantes[index].imagenesFiles.push(file);

      const reader = new FileReader();
      reader.onload = e =>
        this.variantes[index].imagenes.push(
          (e.target as FileReader).result as string
        );
      reader.readAsDataURL(file);
    });
  }

  eliminarImagen(variantIndex: number, imageIndex: number) {
    this.variantes[variantIndex].imagenes.splice(imageIndex, 1);
    this.variantes[variantIndex].imagenesFiles.splice(imageIndex, 1);
  }

  // ---------------- SUBMIT ----------------
onSubmit(): void {
  // Validaciones básicas
  if (!this.marcaSeleccionada) {
    alert('Debes seleccionar una marca');
    return;
  }

  if (!this.categoriaSeleccionadaFinal) {
    alert('Debes seleccionar una categoría');
    return;
  }

  if (!this.nombre || !this.descripcion || this.precio === null) {
    alert('Debes completar todos los campos obligatorios');
    return;
  }

  if (!this.lugarCompra || !this.fechaCompra || this.precioCompra === null) {
    alert('Debes completar los datos de compra');
    return;
  }


  // Construir FormData
  const formData = new FormData();
  formData.append('lugar_compra', this.lugarCompra);
  formData.append('fecha_compra', this.fechaCompra!);
  formData.append('precio_compra', this.precioCompra!.toString());
  formData.append('nombre', this.nombre);
  formData.append('descripcion', this.descripcion);
  formData.append('tipo', this.tipo); // ya tiene el valor automático
  formData.append('precio', this.precio!.toString());
  formData.append('marca_id', this.marcaSeleccionada.toString());
  formData.append('categoria_id', this.categoriaSeleccionadaFinal.toString());

  // Convertir variantes a JSON string
  const variantesJson = JSON.stringify(this.variantes);
  formData.append('variantes', variantesJson);

  // Agregar imágenes de cada variante
  this.variantes.forEach((variante) => {
  if (variante.imagenesFiles && variante.imagenesFiles.length > 0) {
    variante.imagenesFiles.forEach((file: File) => {
      formData.append('imagenes', file); // nombre debe coincidir con FastAPI
    });
  }
});

  // Debug: imprimir FormData antes de enviarlo
  console.log('📦 FormData final:');
  for (let pair of formData.entries()) {
    console.log(pair[0], pair[1]);
  }

  // Enviar al backend
  this.productsService.crearProducto(formData).subscribe({
    next: (res) => {
      console.log('✅ Producto creado:', res);
      alert('Producto creado correctamente!');
      // Aquí podrías resetear el formulario o redirigir
    },
    error: (err) => {
      console.error('❌ Error al crear producto:', err);
      alert('Error al crear producto, revisa la consola para más detalles.');
    }
  });
  
}






}



// asiganr el tipo de producto, aqui, en el HttpBackend, dependiendo de que catagioria se seleciono