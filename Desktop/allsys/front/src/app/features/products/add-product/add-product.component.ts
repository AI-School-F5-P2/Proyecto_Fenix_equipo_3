import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { ProductsService } from '../../../core/services/products.service';
import { SuppliersService } from '../../../core/services/proveedores.service';
import { BrandSelectorComponent } from "./components/brand-selector/brand-selector.component";
import { SupplierSelectorComponent, Proveedor } from "./components/supplier-selector/supplier-selector.component";
import { ImageManagerComponent } from "./components/image-manager/image-manager.component";
import { CategorySelectorComponent,  CategorySelectionEvent} from "../../../shared/components/selectors/category-selector/category-selector.component";
import { ColorSelectorComponent} from "../../../shared/components/selectors/color-selector/color-selector.component";
import { DragDropModule, CdkDragDrop, moveItemInArray } from '@angular/cdk/drag-drop';


// ✨ IMPORTACIONES ESTRUCTURADAS
import { 
  ATRIBUTOS_BASE, ATRIBUTOS_POR_TIPO, COLORES_PALETA, MATERIALES_JOYERIA, 
  Variante, StockVariante, ProductoBackend, AtributoBackend, Marca, EstadoPrenda, 
  Color
} from './product-form.config';

import { generarTempId, formatLabel, getPlaceholder, determinarTipoBase, MAPEO_IDENTIDAD_POR_TIPO, MAPEO_MATERIAL_A_COLOR, determinarGenero } from './product-utils';
// import { ImageManagerComponent } from "../../../components/image-manager/image-manager.component";

@Component({
  selector: 'app-add-product',
  standalone: true,
  imports: [CommonModule, FormsModule, BrandSelectorComponent, DragDropModule, SupplierSelectorComponent, ColorSelectorComponent, CategorySelectorComponent, ImageManagerComponent],
  templateUrl: './add-product.component.html',
  styleUrls: ['./add-product.component.css']
})
export class AddProductComponent implements OnInit {

  productoId: number | null = null;
  isEditMode = false;
  cargandoDatos = false;
  isSubmitting = false;
  stockAEnfocar: number | null = null;
  nombre = '';
  descripcion = '';
  listaPublicos = ['Mujer', 'Hombre', 'Unisex', 'Niña', 'Niño', 'Bebé'];
  publicoSeleccionado = '';
  estadoSeleccionado: EstadoPrenda = 'segunda_mano';
  categoriaSeleccionadaFinal: number | null = null;
  marcaSeleccionada: Marca | null = null;
  tipoProductoBase: string = 'ropa_superior';
  fragmentAEnfocar: string | null = null;
  variantes: Variante[] = [];
  colores = COLORES_PALETA;
  esVintage: boolean = false;
  epoca: string | null = null;

  constructor(private productsService: ProductsService, private router: Router, private route: ActivatedRoute) {}

  ngOnInit(): void {

    this.route.fragment.subscribe(fragment => {
      if (fragment) {
        this.fragmentAEnfocar = fragment;
      }
    });

    this.route.paramMap.subscribe(params => {
      const id = params.get('id');
      if (id) {
        this.isEditMode = true;
        this.productoId = Number(id);
        this.cargarProductoParaEditar(this.productoId);
      } else {
        this.resetVariantes();
      }
    });
  }

  // ================== CARGA Y MAPEO ==================
  // ================== CARGA Y MAPEO ==================
  cargarProductoParaEditar(id: number) {
    this.cargandoDatos = true;
    this.productsService.obtenerProducto(id).subscribe({
      next: (productoDB: ProductoBackend) => {
        console.log(productoDB)
        
        this.nombre = productoDB.nombre;
        this.descripcion = productoDB.descripcion;
        this.estadoSeleccionado = productoDB.estado;
        this.publicoSeleccionado = productoDB.publico_objetivo;
        this.tipoProductoBase = productoDB.tipo;
        this.marcaSeleccionada = productoDB.marca || null;
        this.categoriaSeleccionadaFinal = productoDB.categoria_id;
        this.esVintage = productoDB.es_vintage || false;
        this.epoca = productoDB.epoca || null;

        this.variantes = productoDB.variantes.sort((a,b) => (a.orden || 0) - (b.orden || 0)).map(vDB => ({
          id: vDB.id,
          temp_id: generarTempId(),
          identidad_variante: vDB.identidad_variante,
          hex_identidad: vDB.hex_identidad,
          descripcion: vDB.descripcion,
          
          // ✨ CORRECCIÓN 1: Aseguramos que sea un texto puro (URL), no un objeto
          imagenes: vDB.imagenes ? vDB.imagenes.map((img: any) => typeof img === 'string' ? img : img.url) : [],
          imagenesFiles: vDB.imagenes ? vDB.imagenes.map(() => null) : [],
          
          stocks: vDB.stocks.sort((a,b) => (a.orden || 0) - (b.orden || 0)).map(sDB => {
             const attrTalla = sDB.atributos.find(a => ['talla', 'numero', 'capacidad_ml', 'talla_anillo'].includes(a.nombre.toLowerCase()));
             const tallaVisual = attrTalla ? attrTalla.valor : null;

             return {
                id: sDB.id,
                temp_id: generarTempId(),
                sku: sDB.sku,
                stock: sDB.cantidad,
                precio_compra: sDB.precio_compra,
                precio_venta: sDB.precio_venta,
                descuento: sDB.descuento || 0,
                fecha_compra: sDB.fecha_compra,
                proveedor: sDB.proveedor?.nombre_proveedor || '',
                proveedor_id: sDB.proveedor_id,
                publicar_web: sDB.publicar_web,
                publicar_vinted: sDB.publicar_vinted,
                publicar_wallapop: sDB.publicar_wallapop,
                etiqueta: sDB.etiqueta || '',
                ubicacion: sDB.ubicacion || '',
                 
                talla: tallaVisual, 
                atributos: this.hidratarAtributos(sDB.atributos)
             }
          })
        }));
        
        this.cargandoDatos = false;
        if (this.fragmentAEnfocar) {
          this.ejecutarScrollInteligente(this.fragmentAEnfocar);
        }
      }
    });
  }


  private ejecutarScrollInteligente(fragment: string, intentos = 0) {
  // Le damos un pequeño margen para que Angular renderice el *ngFor
  setTimeout(() => {
    const elemento = document.getElementById(fragment);

    if (elemento) {
      // 1. Calculamos la posición
      const yOffset = -100; // Margen para que no quede pegado al header
      const y = elemento.getBoundingClientRect().top + window.pageYOffset + yOffset;

      // 2. Intentamos scroll en la ventana
      window.scrollTo({ top: y, behavior: 'smooth' });

      // 3. Si tienes un contenedor interno que hace scroll, intentamos también:
      elemento.scrollIntoView({ behavior: 'smooth', block: 'start' });

      // 4. Efecto visual para confirmar que llegamos
      elemento.classList.add('highlight-pulse');
      setTimeout(() => elemento.classList.remove('highlight-pulse'), 2500);

      // Limpiamos el fragmento para que no scrollee de nuevo al azar
      this.fragmentAEnfocar = null;

    } else if (intentos < 10) {
      // Si no lo encuentra, reintenta (útil si las fotos tardan en cargar y empujar el layout)
      this.ejecutarScrollInteligente(fragment, intentos + 1);
    }
  }, 150); 
}

  

  private hidratarAtributos(atributosDB: AtributoBackend[]): any[] {
    const molde = this.getAtributosVacios();
    const sinonimosTalla = ['talla', 'numero', 'talla_anillo', 'capacidad_ml'];

    return molde.map(attrForm => {
      const nombreBuscado = attrForm.nombre.toLowerCase();
      
      const match = atributosDB.find(a => {
        const nombreDB = a.nombre.toLowerCase();
        if (nombreDB === nombreBuscado) return true;
        if (sinonimosTalla.includes(nombreBuscado) && sinonimosTalla.includes(nombreDB)) return true;
        return false;
      });

      if (match) {
        attrForm.valor = match.valor ? String(match.valor).trim() : null;
      }

      // ✨ EL AUTO-CORRECTOR PARA SELECTS (Arregla el Material)
      if (attrForm.tipo === 'select' && attrForm.valor) {
        const valorGuardado = String(attrForm.valor).toLowerCase().trim();
        const opcionExacta = attrForm.opciones?.find((opt: string) => opt.toLowerCase().trim() === valorGuardado);
        if (opcionExacta) {
          attrForm.valor = opcionExacta;
        }
      }

      return attrForm;
    });
  }

  // Helper para saber si alguna talla de esta variante tiene el switch activado
  varianteVaAPublicarse(v: Variante): boolean {
    return v.stocks.some(s => s.publicar_web || s.publicar_vinted || s.publicar_wallapop);
  }

  // ================== EVENTOS SELECTORES ==================
  // ================== EVENTOS SELECTORES ==================
  onBrandChanged(marca: Marca) { 
    // Escudo anti-bucles: Si la marca que llega es exactamente la misma que ya tenemos, 
    // ignoramos el evento para no disparar un ciclo infinito de recargas.
    if (this.marcaSeleccionada && marca && this.marcaSeleccionada.id === marca.id && this.marcaSeleccionada.nombre === marca.nombre) {
      return;
    }
    
    this.marcaSeleccionada = marca; 
  }

  onSupplierChanged(prov: Proveedor, stock: StockVariante) {
    stock.proveedor = prov.nombre;
    stock.proveedor_id = prov.id || null;
    if (prov.isNew) (stock as any).proveedor_nombre_nuevo = prov.nombre;
  }

onCategorySelected(event: CategorySelectionEvent): void {
  // 1. Guardamos el estado previo para saber si cambió la categoría
  const esMisma = this.categoriaSeleccionadaFinal === event.categoriaId;
  this.categoriaSeleccionadaFinal = event.categoriaId;

  // 2. Si la categoría es null (limpieza), reseteamos valores y salimos
  if (event.categoriaId === null) {
    this.tipoProductoBase = '';
    this.publicoSeleccionado = '';
    return;
  }

  // ✨ EL ARREGLO: Usamos (event.rutaCategorias || []) para asegurar que siempre sea un Array
  const rutaSegura = event.rutaCategorias || [];

  // 3. Determinamos si es Ropa Superior, Inferior, Calzado, etc.
  this.tipoProductoBase = determinarTipoBase(rutaSegura);

  // 4. 🔥 AUTOMATIZACIÓN DEL GÉNERO
  // Extraemos el género usando la función de utils enviando la ruta segura
  const generoDetectado = determinarGenero(rutaSegura);

  // Si el género detectado no es 'unisex', lo asignamos automáticamente
  if (generoDetectado && generoDetectado !== 'unisex') {
    // Mapeamos el valor del backend al valor de tu listaPublicos
    this.publicoSeleccionado = this.capitalizar(generoDetectado);
  }

  // 5. Si la categoría cambió realmente, refrescamos los atributos de las variantes (Talla, Material, etc.)
  if (!esMisma) {
    this.refrescarAtributosEnVariantes();
  }
}

// Pequeño helper para pasar de 'mujer' a 'Mujer'
private capitalizar(s: string): string {
  if (!s) return '';
  return s.charAt(0).toUpperCase() + s.slice(1);
}

  // ================== GESTIÓN DE VARIACIÓN ==================
  resetVariantes(): void { this.variantes = [this.nuevaVariante()]; }

  nuevaVariante(): Variante {
    return { 
        temp_id: generarTempId(), hex_identidad: '#FFFFFF', identidad_variante: '', 
        stocks: [this.nuevoStock()], imagenes: [], imagenesFiles: [], descripcion: '' 
    };
  }

  nuevoStock(): StockVariante {
    return { 
        id_manual: null, sku: '', atributos: this.getAtributosVacios(), stock: 0, precio_compra: 0, ubicacion: '',
        precio_venta: 0, descuento: 0, proveedor: '', proveedor_id: null, 
        fecha_compra: '', publicar_vinted: false, publicar_wallapop: false, publicar_web: false, temp_id: generarTempId(),
        talla: null // Inicializamos
    };
  }

  agregarVariante(): void { this.variantes.push(this.nuevaVariante()); }
  
 agregarStock(i: number): void { 
    const nuevoStock = this.nuevoStock();
    const variante = this.variantes[i];

    if (variante.stocks.length > 0) {
      const ultimoStock = variante.stocks[variante.stocks.length - 1]; 

      // 1. Copiar TODOS los atributos compartidos (Color, Material, Peso...), menos la Talla
      nuevoStock.atributos = nuevoStock.atributos.map(nuevoAttr => {
        const attrHermano = ultimoStock.atributos.find(a => a.nombre === nuevoAttr.nombre);
        if (attrHermano) {
          // Lista de atributos que NO se deben copiar porque definen el tamaño de la variante
          const ignorar = ['talla', 'numero', 'capacidad_ml', 'talla_anillo', 'cantidad_ml_g', 'talla_guantes'];
          
          if (!ignorar.includes(nuevoAttr.nombre.toLowerCase())) {
            nuevoAttr.valor = attrHermano.valor;
          }
        }
        return nuevoAttr;
      });

      // 2. Copiar Datos Logísticos (Con protección contra vacíos)
      nuevoStock.proveedor = ultimoStock.proveedor || '';
      nuevoStock.proveedor_id = ultimoStock.proveedor_id || null;
      nuevoStock.precio_compra = ultimoStock.precio_compra || 0;
      nuevoStock.precio_venta = ultimoStock.precio_venta || 0;
      nuevoStock.fecha_compra = ultimoStock.fecha_compra || '';
      
      // 3. Copiar Ubicación
      nuevoStock.ubicacion = ultimoStock.ubicacion || ''; 
    }

    variante.stocks.push(nuevoStock); 
  }


  eliminarStock(i: number, j: number): void { this.variantes[i].stocks.splice(j, 1); }
  eliminarVariante(index: number): void { this.variantes.splice(index, 1); }

  getAtributosVacios(): any[] {
    const especificos = ATRIBUTOS_POR_TIPO[this.tipoProductoBase] || [];
    return [...especificos, ...ATRIBUTOS_BASE].map(attr => ({ ...attr, valor: null }));
  }

  private refrescarAtributosEnVariantes(): void {
    const nuevos = this.getAtributosVacios();
    this.variantes.forEach(v => v.stocks.forEach(s => s.atributos = JSON.parse(JSON.stringify(nuevos))));
  }


// 1. Primero, el helper que revisa si el producto entero va para la web
productoVaAPublicarse(): boolean {
  return this.variantes.some(v => 
    v.stocks.some(s => s.publicar_web || s.publicar_vinted || s.publicar_wallapop)
  );
}


// ✨ NUEVO: Limpia la época si el usuario desmarca el switch
  onVintageChange(): void {
    if (!this.esVintage) {
      this.epoca = null;
    }
  }








private validarFormulario(): boolean {
  // 1. DETERMINAR ESTADO GLOBAL DE PUBLICACIÓN
  // Usamos esta variable para saber si el nombre es obligatorio
  const vaAPublicarGlobal = this.productoVaAPublicarse();

  // 2. VALIDACIONES GLOBALES DEL PRODUCTO
  if (vaAPublicarGlobal && (!this.nombre || !this.nombre.trim())) {
    return this.lanzarError('El nombre del producto es obligatorio para poder publicarlo en la web.');
  }

  if (!this.categoriaSeleccionadaFinal) {
    return this.lanzarError('Selecciona una categoría para continuar.');
  }

  if (!this.marcaSeleccionada) {
    return this.lanzarError('Debes seleccionar una marca (o crear una nueva).');
  }

  if (!this.marcaSeleccionada) {
    return this.lanzarError('Debes seleccionar una marca (o crear una nueva).');
  }

  // ✨ NUEVA VALIDACIÓN VINTAGE
  if (this.esVintage && !this.epoca) {
    return this.lanzarError('Has indicado que la prenda es Vintage. Por favor, selecciona la Época/Década.');
  }

  // Obtenemos el nombre del atributo maestro (Color, Material, etc.) según el tipo de producto
  const maestro = this.mapeoIdentidadPorCategoria;

  // 3. RECORRIDO DE VARIANTES (Colores/Estilos)
  for (let i = 0; i < this.variantes.length; i++) {
    const v = this.variantes[i];
    const nV = i + 1; // Número de variante para el mensaje de error

    if (!v.identidad_variante) {
      return this.lanzarError(`Variante ${nV}: El campo "${formatLabel(maestro)}" es obligatorio.`);
    }

    if (!v.descripcion || !v.descripcion.trim()) {
      return this.lanzarError(`Variante ${nV}: Debes añadir una descripción específica.`);
    }

    // 4. RECORRIDO DE STOCKS (Tallas/Medidas dentro de la variante)
    for (let j = 0; j < v.stocks.length; j++) {
      const s = v.stocks[j];
      const nS = j + 1; // Número de stock para el mensaje de error

      // A. Validación de Ubicación
      if (!s.ubicacion || !s.ubicacion.trim()) {
        return this.lanzarError(`Var ${nV}, Talla ${nS}: Indica la ubicación en el almacén.`);
      }

      // B. ✨ LÓGICA DINÁMICA DE STOCK (CANTIDAD)
      if (!this.isEditMode) {
        // CASO: CREACIÓN NUEVA -> El stock siempre debe ser mayor a 0
        if (s.stock <= 0) {
          return this.lanzarError(`Var ${nV}, Talla ${nS}: El stock inicial debe ser mayor a 0.`);
        }
      } else {
        // CASO: MODO EDICIÓN
        const esTallaNuevaEnEdicion = !s.id; // No tiene ID de base de datos aún

        if (esTallaNuevaEnEdicion && s.stock <= 0) {
          // Si el usuario agrega una talla nueva durante la edición, debe traer mercancía
          return this.lanzarError(`Var ${nV}, Talla ${nS}: Al añadir una nueva talla, el stock debe ser mayor a 0.`);
        }

        if (!esTallaNuevaEnEdicion && s.stock < 0) {
          // Si la talla ya existía, permitimos 0 (agotado), pero nunca negativo
          return this.lanzarError(`Var ${nV}, Talla ${nS}: El stock no puede ser un número negativo.`);
        }
      }

      // C. Validaciones Logísticas Obligatorias
      if (s.precio_compra <= 0) {
        return this.lanzarError(`Var ${nV}, Talla ${nS}: El precio de compra debe ser mayor a 0.`);
      }

      if (!s.proveedor_id && !s.proveedor) {
        return this.lanzarError(`Var ${nV}, Talla ${nS}: Selecciona o escribe un proveedor.`);
      }

      if (!s.fecha_compra) {
        return this.lanzarError(`Var ${nV}, Talla ${nS}: La fecha de compra es obligatoria.`);
      }

      // 5. VALIDACIONES DE PUBLICACIÓN (Solo si algún canal está activo en este stock)
      const vaAPublicarEsteStock = s.publicar_web || s.publicar_vinted || s.publicar_wallapop;

      if (vaAPublicarEsteStock) {
        // Verificar imágenes en la variante padre
        if (!v.imagenes || v.imagenes.length === 0) {
          return this.lanzarError(`Variante ${nV}: Debes subir al menos una foto para poder publicar este artículo.`);
        }

        // Verificar precio de venta
        if (s.precio_venta <= 0) {
          return this.lanzarError(`Var ${nV}, Talla ${nS}: Para publicar, el precio de venta debe ser mayor a 0.`);
        }

        // Verificar peso (esencial para envíos automáticos)
        const pesoAttr = s.atributos.find(a => a.nombre === 'peso_kg');
        const pesoValor = pesoAttr ? pesoAttr.valor : null;
        
        if (pesoValor === null || pesoValor === undefined || pesoValor <= 0) {
          return this.lanzarError(`Var ${nV}, Talla ${nS}: El peso es obligatorio para calcular los costos de envío.`);
        }
      }
    }
  }

  // Si llegamos hasta aquí, todo está en orden
  return true;
}









  get mapeoIdentidadPorCategoria(): string {
    return MAPEO_IDENTIDAD_POR_TIPO[this.tipoProductoBase] || 'color';
  }

  get ejeVariacion() {
    const configuracionEjes: Record<string, any> = {
      ropa_superior: { tipo: 'color', titulo: 'Estilo / Color', label: 'Color principal' },
      calzado: { tipo: 'color', titulo: 'Estilo / Color', label: 'Color principal' },
      joyeria_anillos: { tipo: 'dropdown', titulo: 'Variante de Metal', label: 'Metal / Material', opciones: MATERIALES_JOYERIA },
      perfumeria: { tipo: 'texto', titulo: 'Formato', label: 'Capacidad', placeholder: 'Ej: 100ml' }
    };
    return configuracionEjes[this.tipoProductoBase] || { tipo: 'color', titulo: 'Estilo / Color', label: 'Color principal' };
  }

  // ================== TRIPLE DRAG AND DROP ==================
  onVariantDrop(event: CdkDragDrop<Variante[]>) { moveItemInArray(this.variantes, event.previousIndex, event.currentIndex); }
  
  onImageDrop(event: CdkDragDrop<string[]>, variantIndex: number) {
    const v = this.variantes[variantIndex];
    moveItemInArray(v.imagenes, event.previousIndex, event.currentIndex);
    moveItemInArray(v.imagenesFiles, event.previousIndex, event.currentIndex);
  }
  
  onStockDrop(event: CdkDragDrop<StockVariante[]>, variantIndex: number) { 
    moveItemInArray(this.variantes[variantIndex].stocks, event.previousIndex, event.currentIndex); 
  }

  // ================== GESTIÓN DE ARCHIVOS ==================
  // Reemplaza tu onFilesSelected por este:
// ================== GESTIÓN DE ARCHIVOS (PADRE) ==================
  async onFilesSelected(event: Event, i: number): Promise<void> {
    const files = (event.target as HTMLInputElement).files;
    if (!files) return;

    const filesArray = Array.from(files);
    
    for (const file of filesArray) {
      const base64 = await this.fileToBase64(file);
      
      // El padre asigna la foto a la variante específica
      this.variantes[i].imagenesFiles = [...this.variantes[i].imagenesFiles, file];
      this.variantes[i].imagenes = [...this.variantes[i].imagenes, base64];
    }
    
    // Limpiamos el input
    (event.target as HTMLInputElement).value = '';
  }

// Función auxiliar para convertir a base64 con promesas
private fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => resolve(e.target?.result as string);
    reader.onerror = (e) => reject(e);
    reader.readAsDataURL(file);
  });
}

  eliminarImagen(i: number, j: number): void {
    this.variantes[i].imagenes.splice(j, 1);
    this.variantes[i].imagenesFiles.splice(j, 1);
  }

  // seleccionarColorAtributo(attr: any, color: any, v: Variante) {
  //   attr.valor = color.nombre; v.hex_identidad = color.hex; this.sincronizarIdentidadVariante(v);
  // }

// Helper para limpiar el código
private lanzarError(msj: string): boolean {
  alert(msj);
  return false;
}

// Helper para que el alert sea amigable
private getMensajeErrorAtributo(tipo: string): string {
  const mensajes: Record<string, string> = {
    'color': 'Debes seleccionar un color.',
    'material': 'Debes indicar el material/metal (ej: Oro, Plata).',
    'capacidad': 'Debes indicar la capacidad (ej: 100ml).',
    'identidad': 'El campo de identidad es obligatorio.'
  };
  return mensajes[tipo] || 'Falta el atributo principal de la variante.';
}





  onSubmit(): void {
  if (!this.validarFormulario()) return;
  this.isSubmitting = true;
  const formData = this.construirFormData();

  const req = (this.isEditMode && this.productoId) 
    ? this.productsService.editarProducto(this.productoId, formData) 
    : this.productsService.crearProducto(formData);

  req.subscribe({
    next: (res: any) => {
      this.isSubmitting = false;
      
      // 🧪 LOG DE CONTROL: Mira tu consola para ver qué devuelve el Back
      console.log('Respuesta del Backend:', res);

      // Intentamos capturar el ID de varias formas posibles
      const idFinal = res?.id || res?.producto_id || this.productoId;

      if (idFinal) {
        this.router.navigate(['/detail-product', idFinal]);
      } else {
        console.warn('⚠️ No se encontró ID para navegar. Volviendo a la lista.');
        this.router.navigate(['/view-products']); 
      }
    },
    error: (err) => {
      this.isSubmitting = false;
      console.error('Error en el servidor:', err);
      alert('Error al guardar: ' + (err.error?.detail || 'Error desconocido'));
    }
  });
}


private construirFormData(): FormData {
    const fd = new FormData();

    // 1. CAMPOS BÁSICOS DEL PRODUCTO
    fd.append('nombre', this.nombre);
    fd.append('descripcion', this.descripcion);
    fd.append('tipo', this.tipoProductoBase);
    fd.append('estado', this.estadoSeleccionado);
    fd.append('categoria_id', String(this.categoriaSeleccionadaFinal));
    fd.append('publico_objetivo', this.publicoSeleccionado);
    fd.append('es_vintage', String(this.esVintage));
    if (this.esVintage && this.epoca) {
      fd.append('epoca', this.epoca);
    }

    // 2. GESTIÓN DE MARCA
    if (this.marcaSeleccionada) {
      if (this.marcaSeleccionada.isNew) {
        fd.append('marca_nombre', this.marcaSeleccionada.nombre);
      } else {
        fd.append('marca_id', String(this.marcaSeleccionada.id));
      }
    }

    // 3. PROCESAMIENTO DE VARIANTES Y STOCKS
    const cleanV = this.variantes.map((v, idxV) => {
      const identidadPadre = v.identidad_variante || 'ÚNICA';

      return {
        id: v.id || null,
        temp_id: v.temp_id,
        identidad_variante: identidadPadre,
        hex_identidad: v.hex_identidad,
        descripcion: v.descripcion,
        orden: idxV,
        
        // ✨ CORRECCIÓN CLAVE: 
        // Si hay un archivo físico (no es null), marcamos como NUEVA. Si no, dejamos la URL original.
        imagenes: v.imagenes.map((img, idxI) => 
          v.imagenesFiles[idxI] !== null ? `NUEVA_${idxI}` : img
        ),
        
        stocks: v.stocks.map((s, idxS) => {
          const attrTallaEditado = s.atributos.find(a => 
            ['talla', 'numero', 'talla_anillo', 'capacidad_ml'].includes(a.nombre.toLowerCase())
          );

          const valorFinalTalla = attrTallaEditado?.valor || s.talla || 'UNICA';
          const etiquetaCompuesta = `${identidadPadre} / ${valorFinalTalla}`.trim().toUpperCase();

          let atributosBlindados = s.atributos.filter(a => 
            !['talla', 'numero', 'talla_anillo', 'capacidad_ml'].includes(a.nombre.toLowerCase()) &&
            a.valor !== null && a.valor !== ''
          );

          atributosBlindados.push({ nombre: 'talla', valor: valorFinalTalla });

          return { 
            ...s, 
            id_manual: s.id_manual,
            cantidad: s.stock,
            orden: idxS, 
            ubicacion: s.ubicacion,
            etiqueta: etiquetaCompuesta,
            atributos: atributosBlindados 
          };
        })
      };
    });

    fd.append('variantes', JSON.stringify(cleanV));

    // 4. ADJUNCIÓN DE ARCHIVOS BINARIOS (IMÁGENES NUEVAS)
    let contadorArchivos = 0; // Para depuración
    this.variantes.forEach(v => {
      v.imagenesFiles.forEach((file, idx) => {
        // ✨ CORRECCIÓN CLAVE: Solo subimos si de verdad hay un archivo seleccionado
        if (file !== null) {
          fd.append(`file_${v.temp_id}_NUEVA_${idx}`, file);
          contadorArchivos++;
        }
      });
    });

    console.log(`🚀 Se están enviando ${contadorArchivos} archivos físicos nuevos al backend.`);
    
    return fd;
  }




















// =====================================================
  // EVENTOS DE IDENTIDAD DE LA VARIANTE
  // =====================================================
  
  onVariantColorChanged(v: Variante, color: Color) {
    v.identidad_variante = color.nombre;
    v.hex_identidad = color.hex;
  }

  onVariantDropdownChanged(v: Variante) {
    // Si estamos en joyería, asignamos un color Hex automático al círculo
    if (this.tipoProductoBase.startsWith('joyeria')) {
      const nombreColorAuto = MAPEO_MATERIAL_A_COLOR[v.identidad_variante];
      if (nombreColorAuto) {
        const found = this.colores.find(c => c.nombre === nombreColorAuto);
        v.hex_identidad = found ? found.hex : '#E2E8F0';
      } else {
        v.hex_identidad = '#E2E8F0';
      }
    } else {
      v.hex_identidad = '#E2E8F0'; // Fallback por defecto
    }
  }





















  // Helpers para HTML
  formatLabel(n: string): string { return formatLabel(n); }
  getPlaceholder(n: string): string { return getPlaceholder(n); }
  
  // ✨ CORRECCIÓN: Ignoramos mayúsculas para que atrape el "ROJO" de la BD
  getHexColor(n: string): string { 
    if (!n) return '#fff';
    const colorGuardado = String(n).toLowerCase().trim();
    return this.colores.find(c => c.nombre.toLowerCase().trim() === colorGuardado)?.hex || '#fff'; 
  }

  moverProductoPapelera(): void {
    if (!this.productoId) return;

    // Mensaje súper sencillo, estilo Windows/Mac
    const confirmar = confirm('¿Quieres mover este producto a la papelera?');

    if (confirmar) {
      this.cargandoDatos = true;
      
      // Asumiendo que llamas a tu endpoint de "mover a papelera"
      this.productsService.moverProductoPapelera(this.productoId).subscribe({
        next: (res: any) => {
          alert(res.mensaje || '🗑️ Movido a la papelera.');
          this.router.navigate(['/view-products']); 
        },
        error: (err) => {
          this.cargandoDatos = false;
          alert('❌ Error: ' + (err.error?.detail || 'Inténtalo de nuevo.'));
        }
      });
    }
  }



  
}