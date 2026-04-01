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
  Variante, StockVariante, ProductoBackend, AtributoBackend, Marca, EstadoPrenda 
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
  cargarProductoParaEditar(id: number) {
    this.cargandoDatos = true;
    this.productsService.obtenerProducto(id).subscribe({
      next: (productoDB: ProductoBackend) => {
        this.nombre = productoDB.nombre;
        this.descripcion = productoDB.descripcion;
        this.estadoSeleccionado = productoDB.estado;
        this.publicoSeleccionado = productoDB.publico_objetivo;
        this.tipoProductoBase = productoDB.tipo;
        this.marcaSeleccionada = productoDB.marca || null;
        this.categoriaSeleccionadaFinal = productoDB.categoria_id;

        this.variantes = productoDB.variantes.sort((a,b) => (a.orden || 0) - (b.orden || 0)).map(vDB => ({
          id: vDB.id,
          temp_id: generarTempId(),
          identidad_variante: vDB.identidad_variante,
          hex_identidad: vDB.hex_identidad,
          descripcion: vDB.descripcion,
          imagenes: vDB.imagenes ? [...vDB.imagenes] : [],
          imagenesFiles: vDB.imagenes ? vDB.imagenes.map(() => null) : [],
          stocks: vDB.stocks.sort((a,b) => (a.orden || 0) - (b.orden || 0)).map(sDB => ({
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
            ubicacion: sDB.ubicacion || '', // ✨ Añadimos "|| ''" para evitar nulls
            atributos: this.hidratarAtributos(sDB.atributos)
          }))
        }));
        this.cargandoDatos = false;
        // ✨ LÓGICA DE SCROLL REFORZADA
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
    return molde.map(attrForm => {
      const match = atributosDB.find(a => a.nombre === attrForm.nombre);
      if (match) attrForm.valor = match.valor;
      return attrForm;
    });
  }

  // Helper para saber si alguna talla de esta variante tiene el switch activado
  varianteVaAPublicarse(v: Variante): boolean {
    return v.stocks.some(s => s.publicar_web || s.publicar_vinted || s.publicar_wallapop);
  }

  // // Helper para saber si EL PRODUCTO EN GENERAL se va a publicar en algún lado
  // productoVaAPublicarse(): boolean {
  //   return this.variantes.some(v => 
  //     v.stocks.some(s => s.publicar_web || s.publicar_vinted || s.publicar_wallapop)
  //   );
  // }

  // ================== EVENTOS SELECTORES ==================
  onBrandChanged(marca: Marca) { this.marcaSeleccionada = marca; }

  onSupplierChanged(prov: Proveedor, stock: StockVariante) {
    stock.proveedor = prov.nombre;
    stock.proveedor_id = prov.id || null;
    if (prov.isNew) (stock as any).proveedor_nombre_nuevo = prov.nombre;
  }

  // En add-product.component.ts

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
          
          if (!ignorar.includes(nuevoAttr.nombre)) {
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

// DENTRO DE AddProductComponent

sincronizarIdentidadVariante(variante: Variante): void {
  const nombreAtributoMaestro = this.mapeoIdentidadPorCategoria; // 'material' en joyeria
  const primerStock = variante.stocks[0];
  const atributoMaestro = primerStock.atributos.find(a => a.nombre === nombreAtributoMaestro);

  if (atributoMaestro && atributoMaestro.valor) {
    variante.identidad_variante = atributoMaestro.valor;

    // --- LÓGICA AUTOMÁTICA PARA JOYERÍA ---
    if (this.tipoProductoBase.startsWith('joyeria')) {
      // 1. Buscamos el color correspondiente al material
      const nombreColorAuto = MAPEO_MATERIAL_A_COLOR[atributoMaestro.valor];
      
      if (nombreColorAuto) {
        // 2. Buscamos el atributo 'color' en TODOS los stocks de la variante y lo rellenamos
        variante.stocks.forEach(s => {
          const attrColor = s.atributos.find(a => a.nombre === 'color');
          if (attrColor) {
            attrColor.valor = nombreColorAuto;
          }
        });

        // 3. Actualizamos el círculo visual (HEX) de la variante
        const found = this.colores.find(c => c.nombre === nombreColorAuto);
        variante.hex_identidad = found ? found.hex : '#E2E8F0';
      }
    } 
    // --- LÓGICA NORMAL PARA ROPA/CALZADO ---
    else if (nombreAtributoMaestro === 'color') {
      const found = this.colores.find(c => c.nombre === atributoMaestro.valor);
      variante.hex_identidad = found ? found.hex : '#FFFFFF';
    } 
    else {
      variante.hex_identidad = '#E2E8F0';
    }
  }

  // Sincronización Vertical del maestro (Material/Color/ML)
  variante.stocks.forEach(s => {
    const attr = s.atributos.find(at => at.nombre === nombreAtributoMaestro);
    if (attr) attr.valor = variante.identidad_variante;
  });
}
// 1. Primero, el helper que revisa si el producto entero va para la web
productoVaAPublicarse(): boolean {
  return this.variantes.some(v => 
    v.stocks.some(s => s.publicar_web || s.publicar_vinted || s.publicar_wallapop)
  );
}

// 2. La función de validación corregida
private validarFormulario(): boolean {
  // ✨ AQUÍ DEFINIMOS LA VARIABLE QUE TE DABA ERROR
  const vaAPublicarGlobal = this.productoVaAPublicarse();

  // 1. GLOBAL
  // Solo exigimos el nombre si el switch de publicar está encendido en alguna talla
  if (vaAPublicarGlobal && (!this.nombre || !this.nombre.trim())) {
    return this.lanzarError('El nombre del producto es obligatorio para poder publicarlo en la web.');
  }

  if (!this.categoriaSeleccionadaFinal) return this.lanzarError('Selecciona una categoría.');
  if (!this.marcaSeleccionada) return this.lanzarError('Selecciona una marca.');

  const maestro = this.mapeoIdentidadPorCategoria;

  for (let i = 0; i < this.variantes.length; i++) {
    const v = this.variantes[i];
    const nV = i + 1;

    // 2. INVENTARIO (Obligatorio para guardar)
    if (!v.identidad_variante) return this.lanzarError(`Variante ${nV}: El campo ${maestro} es obligatorio.`);
    if (!v.descripcion?.trim()) return this.lanzarError(`Variante ${nV}: Falta la descripción.`);

    for (let j = 0; j < v.stocks.length; j++) {
      const s = v.stocks[j];
      const nS = j + 1;
      if (!s.ubicacion?.trim()) return this.lanzarError(`Var ${nV}, Talla ${nS}: Falta la ubicación en almacén.`);
      if (s.stock <= 0) return this.lanzarError(`Var ${nV}, Talla ${nS}: Stock debe ser > 0.`);
      if (s.precio_compra <= 0) return this.lanzarError(`Var ${nV}, Talla ${nS}: Falta precio compra.`);
      if (!s.proveedor_id && !s.proveedor) return this.lanzarError(`Var ${nV}, Talla ${nS}: Falta proveedor.`);
      if (!s.fecha_compra) return this.lanzarError(`Var ${nV}, Talla ${nS}: Falta fecha compra.`);

      // 3. PUBLICACIÓN (Solo si algún canal está activo)
      const vaAPublicar = s.publicar_web || s.publicar_vinted || s.publicar_wallapop;

      if (vaAPublicar) {
        if (!v.imagenes || v.imagenes.length === 0) 
          return this.lanzarError(`Variante ${nV}: Sube al menos una foto para publicar.`);
        
        if (s.precio_venta <= 0) 
          return this.lanzarError(`Var ${nV}, Talla ${nS}: El precio de venta es obligatorio.`);
        
        const peso = s.atributos.find(a => a.nombre === 'peso_kg')?.valor;
        if (!peso || peso <= 0) 
          return this.lanzarError(`Var ${nV}, Talla ${nS}: El peso es obligatorio para el envío.`);
      }
    }
  }
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
async onFilesSelected(event: Event, i: number): Promise<void> {
  const files = (event.target as HTMLInputElement).files;
  if (!files) return;

  const filesArray = Array.from(files);
  
  for (const file of filesArray) {
    // 1. Añadimos el archivo al array de archivos
    this.variantes[i].imagenesFiles.push(file);
    
    // 2. Esperamos a que se lea para añadir la previa en el MISMO orden
    const base64 = await this.fileToBase64(file);
    this.variantes[i].imagenes.push(base64);
  }
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

  seleccionarColorAtributo(attr: any, color: any, v: Variante) {
    attr.valor = color.nombre; v.hex_identidad = color.hex; this.sincronizarIdentidadVariante(v);
  }

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
    fd.append('nombre', this.nombre);
    fd.append('descripcion', this.descripcion);
    fd.append('tipo', this.tipoProductoBase);
    fd.append('estado', this.estadoSeleccionado);
    fd.append('categoria_id', String(this.categoriaSeleccionadaFinal));
    fd.append('publico_objetivo', this.publicoSeleccionado);

    if (this.marcaSeleccionada) {
      if (this.marcaSeleccionada.isNew) fd.append('marca_nombre', this.marcaSeleccionada.nombre);
      else fd.append('marca_id', String(this.marcaSeleccionada.id));
    }

    const cleanV = this.variantes.map((v, idxV) => ({
      id: v.id || null, temp_id: v.temp_id, identidad_variante: v.identidad_variante, 
      hex_identidad: v.hex_identidad, descripcion: v.descripcion, orden: idxV, // ❌ Sin ubicacion
      imagenes: v.imagenes.map((img, idxI) => img.startsWith('http') ? img : `NUEVA_${idxI}`),
      stocks: v.stocks.map((s, idxS) => ({ 
        ...s, id_manual: s.id_manual, cantidad: s.stock, orden: idxS, ubicacion: s.ubicacion, atributos: s.atributos.filter(a => a.valor !== null) 
      }))
    }));

    fd.append('variantes', JSON.stringify(cleanV));

    this.variantes.forEach(v => {
      v.imagenes.forEach((img, idx) => {
        if (!img.startsWith('http')) {
          const f = v.imagenesFiles[idx];
          if (f) fd.append(`file_${v.temp_id}_NUEVA_${idx}`, f);
        }
      });
    });
    return fd;
  }

  // Helpers para HTML
  formatLabel(n: string): string { return formatLabel(n); }
  getPlaceholder(n: string): string { return getPlaceholder(n); }
  getHexColor(n: string): string { return this.colores.find(c => c.nombre === n)?.hex || '#fff'; }

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


