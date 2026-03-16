import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { ProductsService } from '../../../core/services/products.service';
import { BrandSelectorComponent, Marca } from "../../../components/brand-selector/brand-selector.component";

@Component({
  selector: 'app-product-edit',
  standalone: true,
  imports: [FormsModule, CommonModule, BrandSelectorComponent],
  templateUrl: './product-edit.component.html',
  styleUrls: ['./product-edit.component.css']
})
export class ProductEditComponent implements OnInit {
  producto: any = null;
  cargando = true;
  marcas: any[] = [];
  todasLasCategorias: any[] = [];
  marcaSeleccionada: Marca | null = null;
  // Para la gestión de borrado de imágenes existentes
  imagenesEliminadasIds: number[] = [];
  // marcaSeleccionada: number | null = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private productsService: ProductsService
  ) {}

  ngOnInit() {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    
    // Carga paralela de datos maestros
    this.productsService.cargarMarcas().subscribe(m => this.marcas = m);
    this.productsService.cargarCategorias().subscribe(c => this.todasLasCategorias = c);

    this.productsService.obtenerProducto(id).subscribe({
  next: (data) => {
    // 1. Guardamos el producto
    this.producto = data;

    console.log(this.producto)

    if (this.producto.id) {
      this.marcaSeleccionada = {
        id: this.producto.marca.id,
        nombre: this.producto.marca?.nombre
      };
    }
    // 2. ✨ MAGIA: Mapeamos los atributos a la propiedad etiqueta para que el HTML los vea
    this.producto.variantes.forEach((v: any) => {
      v.stocks.forEach((s: any) => {
        // Si la etiqueta está vacía, buscamos en los atributos
        if (!s.etiqueta || s.etiqueta === "") {
          const attrTalla = s.atributos.find((a: any) => 
            a.nombre.toLowerCase() === 'talla' || 
            a.nombre.toLowerCase() === 'numero' ||
            a.nombre.toLowerCase() === 'talla_anillo'
          );
          
          if (attrTalla) {
            s.etiqueta = attrTalla.valor; // Ahora 'M' pasa a ser la etiqueta
          }
        }
      });
    });


    this.cargando = false;
  },
  error: () => this.cargando = false
});
  }

  // ================== GESTIÓN DE VARIANTES ==================
  agregarVariante() {
    this.producto.variantes.push({
      identidad_variante: 'Nuevo Color',
      hex_identidad: '#ffffff',
      ubicacion: '',
      stocks: [{
        etiqueta: 'Única',
        cantidad: 0,
        precio_compra: 0,
        precio_venta: 0,
        fecha_compra: new Date().toISOString().split('T')[0],
        atributos: []
      }],
      imagenes: [],
      imagenesFiles: [] // Para nuevas fotos
    });
  }

  eliminarVariante(index: number) {
    if(confirm('¿Eliminar esta variante completa y todos sus stocks?')) {
      this.producto.variantes.splice(index, 1);
    }
  }

  // ================== GESTIÓN DE STOCKS ==================
  agregarStock(variante: any) {
    variante.stocks.push({
      etiqueta: '',
      cantidad: 0,
      precio_compra: 0,
      precio_venta: 0,
      fecha_compra: new Date().toISOString().split('T')[0],
      atributos: []
    });
  }

  eliminarStock(variante: any, index: number) {
    variante.stocks.splice(index, 1);
  }

  // ================== IMÁGENES ==================
  onFilesSelected(event: any, variante: any) {
    const files = event.target.files;
    if (!variante.imagenesFiles) variante.imagenesFiles = [];
    
    for (let file of files) {
      variante.imagenesFiles.push(file);
      const reader = new FileReader();
      reader.onload = (e: any) => {
        // Añadimos a la vista previa local
        variante.imagenes.push(e.target.result);
      };
      reader.readAsDataURL(file);
    }
  }

  eliminarImagenExistente(variante: any, imgUrl: string) {
    // Aquí necesitarías el ID de la imagen si quieres borrarla del servidor específicamente
    // Por ahora la quitamos del array visual
    variante.imagenes = variante.imagenes.filter((i: string) => i !== imgUrl);
    // Nota: Deberías registrar este ID para avisar al backend que la borre en S3
  }

  // ================== GUARDADO ==================
 guardarProducto() {
  if (!this.producto) return;
  
  // 1. Validación de seguridad
  if (!this.marcaSeleccionada || (!this.marcaSeleccionada.id && !this.marcaSeleccionada.nombre)) {
    alert('⚠️ Error: Debes seleccionar una marca válida.');
    return;
  }

  this.cargando = true;
  const formData = new FormData();

  // 2. Datos básicos
  formData.append('nombre', this.producto.nombre || '');
  formData.append('descripcion', this.producto.descripcion || '');
  formData.append('tipo', this.producto.tipo || '');
  formData.append('publico_objetivo', this.producto.publico_objetivo || '');
  formData.append('categoria_id', (this.producto.categoria_id || 0).toString());

  // ✨ LÓGICA DE MARCA REUTILIZABLE
  if (this.marcaSeleccionada.isNew) {
    // Si el usuario escribió algo nuevo, enviamos marca_nombre
    formData.append('marca_nombre', this.marcaSeleccionada.nombre);
  } else if (this.marcaSeleccionada.id) {
    // Si seleccionó una de la lista, enviamos el ID
    formData.append('marca_id', this.marcaSeleccionada.id.toString());
  }

  // 2. ✨ Limpieza profunda de Variantes (Solo enviamos lo que el modelo necesita)
  const variantesPayload = this.producto.variantes.map((v: any) => {
    // Sincronizamos la etiqueta con el atributo talla por si acaso
    const stocksLimpios = v.stocks.map((s: any) => {
      const tallaAttr = s.atributos?.find((a: any) => 
        ['talla', 'numero'].includes(a.nombre.toLowerCase())
      );
      if (tallaAttr) tallaAttr.valor = s.etiqueta;

      return {
        id: s.id || null,
        etiqueta: s.etiqueta || '',
       cantidad: Number(s.cantidad) || 0,
        precio_compra: s.precio_compra || 0,
        precio_venta: s.precio_venta || 0,
        fecha_compra: s.fecha_compra || null,
        proveedor_id: s.proveedor_id || null,
        atributos: s.atributos || []
      };
    });

    return {
      id: v.id || null,
      temp_id: v.temp_id || v.id?.toString(), // Usamos temp_id para las fotos
      identidad_variante: v.identidad_variante,
      hex_identidad: v.hex_identidad,
      ubicacion: v.ubicacion || '',
      stocks: stocksLimpios
    };
  });

  // Enviamos el JSON limpio
  formData.append('variantes', JSON.stringify(variantesPayload));

  // 3. ✨ Ajuste de Imágenes (La clave debe coincidir con lo que espera el Back)
  this.producto.variantes.forEach((v: any) => {
    if (v.imagenesFiles && v.imagenesFiles.length > 0) {
      // Usamos el ID o el temp_id como clave para que el back sepa de qué variante es cada foto
      const key = v.id ? v.id.toString() : v.temp_id;
      
      v.imagenesFiles.forEach((file: File) => {
        formData.append(key, file);
      });
    }
  });

  // 4. Petición con log de error detallado
  this.productsService.actualizarProducto(this.producto.id, formData).subscribe({
    next: () => {
      alert("✅ Producto actualizado correctamente");
      this.cargando = false;
      window.history.back();
    },
    error: (err) => {
      this.cargando = false;
      console.error('❌ Error 400 - Detalles de validación:', err.error);
      // Esto te mostrará en la consola del navegador exactamente qué campo falló
      alert("Error al actualizar: Revisa que todos los campos obligatorios estén llenos.");
    }
  });
}

onBrandChanged(marca: Marca) {
  this.marcaSeleccionada = marca; 
  // Ahora this.marcaSeleccionada tendrá {id: 316, nombre: 'tiammy'} 
  // o {nombre: 'Nike', isNew: true}
}

  eliminarProducto() {
  // 1. Confirmación de seguridad
  const confirmar = confirm('⚠️ ¿Estás seguro de que deseas eliminar este producto? Esta acción borrará todas sus variantes, fotos y registros de stock de forma permanente.');

  if (confirmar) {
    this.cargando = true; // Mostramos estado de carga
    
    this.productsService.eliminarProducto(this.producto.id).subscribe({
      next: () => {
        alert('✅ Producto eliminado correctamente.');
        // 2. Redirigimos a la lista de productos
        this.router.navigate(['/products']); 
      },
      error: (err) => {
        this.cargando = false;
        console.error('Error al eliminar:', err);
        alert('❌ No se pudo eliminar el producto. Inténtalo de nuevo.');
      }
    });
  }}
}