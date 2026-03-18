import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { ProductsService } from '../../../core/services/products.service';
import { SuppliersService } from '../../../core/services/proveedores.service';
import { BrandSelectorComponent } from "../../../components/brand-selector/brand-selector.component";
import { Proveedor, SupplierSelectorComponent } from "../../../components/supplier-selector/supplier-selector.component";
import { Color, ColorSelectorComponent } from '../../../components/color-selector/color-selector.component';
import { CategorySelectionEvent, CategorySelectorComponent } from '../../../components/category-selector/category-selector.component';
import { DragDropModule, CdkDragDrop, moveItemInArray } from '@angular/cdk/drag-drop';

// ✨ IMPORTACIONES ESTRUCTURADAS
import { 
  ATRIBUTOS_BASE, ATRIBUTOS_POR_TIPO, COLORES_PALETA, MATERIALES_JOYERIA, MAPEO_IDENTIDAD_POR_TIPO,
  Variante, StockVariante, ProductoBackend, AtributoBackend, Marca, EstadoPrenda 
} from './product-form.config';

import { generarTempId, formatLabel, getPlaceholder, determinarTipoBase } from './product-utils';

@Component({
  selector: 'app-add-product',
  standalone: true,
  imports: [CommonModule, FormsModule, BrandSelectorComponent, DragDropModule, SupplierSelectorComponent, ColorSelectorComponent, CategorySelectorComponent],
  templateUrl: './add-product.component.html',
  styleUrls: ['./add-product.component.css']
})
export class AddProductComponent implements OnInit {

  productoId: number | null = null;
  isEditMode = false;
  cargandoDatos = false;
  isSubmitting = false;

  nombre = '';
  descripcion = '';
  listaPublicos = ['Mujer', 'Hombre', 'Unisex', 'Niña', 'Niño', 'Bebé'];
  publicoSeleccionado = '';
  estadoSeleccionado: EstadoPrenda = 'segunda_mano';
  categoriaSeleccionadaFinal: number | null = null;
  marcaSeleccionada: Marca | null = null;
  tipoProductoBase: string = 'ropa_superior';

  variantes: Variante[] = [];
  colores = COLORES_PALETA;

  constructor(private productsService: ProductsService, private router: Router, private route: ActivatedRoute) {}

  ngOnInit(): void {
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
          ubicacion: vDB.ubicacion,
          imagenes: vDB.imagenes ? [...vDB.imagenes] : [],
          imagenesFiles: vDB.imagenes ? vDB.imagenes.map(() => null) : [],
          stocks: vDB.stocks.sort((a,b) => (a.orden || 0) - (b.orden || 0)).map(sDB => ({
            id: sDB.id,
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
            atributos: this.hidratarAtributos(sDB.atributos)
          }))
        }));
        this.cargandoDatos = false;
      }
    });
  }

  private hidratarAtributos(atributosDB: AtributoBackend[]): any[] {
    const molde = this.getAtributosVacios();
    return molde.map(attrForm => {
      const match = atributosDB.find(a => a.nombre === attrForm.nombre);
      if (match) attrForm.valor = match.valor;
      return attrForm;
    });
  }

  // ================== EVENTOS SELECTORES ==================
  onBrandChanged(marca: Marca) { this.marcaSeleccionada = marca; }

  onSupplierChanged(prov: Proveedor, stock: StockVariante) {
    stock.proveedor = prov.nombre;
    stock.proveedor_id = prov.id || null;
    if (prov.isNew) (stock as any).proveedor_nombre_nuevo = prov.nombre;
  }

  onCategorySelected(event: CategorySelectionEvent): void {
    const esMisma = this.categoriaSeleccionadaFinal === event.categoriaId;
    this.categoriaSeleccionadaFinal = event.categoriaId;
    this.tipoProductoBase = determinarTipoBase(event.rutaCategorias);
    if (!esMisma) this.refrescarAtributosEnVariantes();
  }

  // ================== GESTIÓN DE VARIACIÓN ==================
  resetVariantes(): void { this.variantes = [this.nuevaVariante()]; }

  nuevaVariante(): Variante {
    return { 
        temp_id: generarTempId(), hex_identidad: '#FFFFFF', identidad_variante: '', 
        stocks: [this.nuevoStock()], imagenes: [], imagenesFiles: [], ubicacion: '', descripcion: '' 
    };
  }

  nuevoStock(): StockVariante {
    return { 
        sku: '', atributos: this.getAtributosVacios(), stock: 0, precio_compra: 0, 
        precio_venta: 0, descuento: 0, proveedor: '', proveedor_id: null, 
        fecha_compra: '', publicar_vinted: false, publicar_wallapop: false, publicar_web: false 
    };
  }

  agregarVariante(): void { this.variantes.push(this.nuevaVariante()); }
  agregarStock(i: number): void { this.variantes[i].stocks.push(this.nuevoStock()); }
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

  sincronizarIdentidadVariante(variante: Variante): void {
    const masterAttr = this.mapeoIdentidadPorCategoria;
    const primerStock = variante.stocks[0];
    const attr = primerStock.atributos.find(a => a.nombre === masterAttr);
    if (attr && attr.valor) {
      variante.identidad_variante = attr.valor;
      if (masterAttr === 'color') {
        const found = this.colores.find(c => c.nombre === attr.valor);
        variante.hex_identidad = found ? found.hex : '#FFFFFF';
      }
    }
    variante.stocks.forEach(s => {
      const a = s.atributos.find(at => at.nombre === masterAttr);
      if (a) a.valor = variante.identidad_variante;
    });
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
  onFilesSelected(event: Event, i: number): void {
    const files = (event.target as HTMLInputElement).files;
    if (!files) return;
    Array.from(files).forEach(file => {
      this.variantes[i].imagenesFiles.push(file);
      const reader = new FileReader();
      reader.onload = e => this.variantes[i].imagenes.push(e.target?.result as string);
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

  // ================== ENVÍO DE DATOS ==================
  private validarFormulario(): boolean {
    if (!this.nombre.trim() || !this.categoriaSeleccionadaFinal || !this.marcaSeleccionada) { 
        alert('Faltan datos obligatorios (Nombre, Categoría o Marca)'); 
        return false; 
    }
    return true;
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
      hex_identidad: v.hex_identidad, ubicacion: v.ubicacion, descripcion: v.descripcion, orden: idxV,
      imagenes: v.imagenes.map((img, idxI) => img.startsWith('http') ? img : `NUEVA_${idxI}`),
      stocks: v.stocks.map((s, idxS) => ({ 
        ...s, cantidad: s.stock, orden: idxS, atributos: s.atributos.filter(a => a.valor !== null) 
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
}


