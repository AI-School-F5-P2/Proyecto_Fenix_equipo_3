import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { ProductsService } from '../../../core/services/products.service';
import { SupplierSelectorComponent, Proveedor } from "../add-product/components/supplier-selector/supplier-selector.component";
import { 
  ATRIBUTOS_BASE, 
  ATRIBUTOS_POR_TIPO,
  MATERIALES_ROPA,      // ✨ Añade esto
  MATERIALES_JOYERIA,   // ✨ Añade esto
  PIEDRAS_JOYERIA,      // ✨ Añade esto
  COLORES_PIEDRA        // ✨ Añade esto
} from '../add-product/product-form.config'; 


import { 
  formatLabel, 
  getPlaceholder 
} from '../add-product/product-utils';

@Component({
  selector: 'app-edit-stock',
  standalone: true,
  imports: [CommonModule, FormsModule, SupplierSelectorComponent],
  templateUrl: './edit-stock.component.html',
  styleUrls: ['./edit-stock.component.css']
})
export class EditStockComponent implements OnInit {
  stockId: number | null = null;
  cargandoDatos = true;
  isSubmitting = false;
  tipoProducto: string = 'ropa_superior'; 

  stockData: any = {
    cantidad: 0,
    precio_compra: 0,
    precio_venta: 0,
    descuento: 0,
    ubicacion: '',
    fecha_compra: '',
    proveedor_id: null,
    publicar_web: false,
    atributos: [] 
  };

  contexto: any = {};

  constructor(
    private route: ActivatedRoute,
    private productsService: ProductsService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.stockId = Number(this.route.snapshot.paramMap.get('id'));
    if (this.stockId) {
      this.cargarStock(this.stockId);
    }
  }

  // ================== GESTIÓN DE ATRIBUTOS DINÁMICOS ==================

  getAtributosVacios(tipo: string): any[] {
    const especificos = ATRIBUTOS_POR_TIPO[tipo] || [];
    return [...especificos, ...ATRIBUTOS_BASE].map(attr => ({ 
      ...attr, 
      valor: null 
    }));
  }



  hidratarAtributos(extrasBackend: any, tipo: string): any[] {
    const molde = this.getAtributosVacios(tipo);
    
    const atributosAExcluir = [
      'talla', 'color', 'identidad_variante', 'numero', 
      'talla_anillo', 'capacidad_ml', 'talla_guantes'
    ];

    return molde
      .filter(attr => !atributosAExcluir.includes(attr.nombre.toLowerCase()))
      .map(attr => {
        const keyBackend = attr.nombre.toLowerCase(); 
        
        // 1. Recuperamos el valor que viene de la base de datos
        if (extrasBackend && extrasBackend[keyBackend] !== undefined) {
          attr.valor = extrasBackend[keyBackend];
        }

        // 2. Convertimos los inputs en selects dinámicos
        if (keyBackend === 'material') {
          attr.tipo = 'select';
          attr.opciones = tipo.toLowerCase().includes('joyeria') ? MATERIALES_JOYERIA : MATERIALES_ROPA;
        }

        if (keyBackend === 'tipo_piedra' || keyBackend === 'piedras') {
          attr.tipo = 'select';
          attr.opciones = PIEDRAS_JOYERIA;
        }

        if (keyBackend === 'color_piedra') {
          attr.tipo = 'select';
          attr.opciones = COLORES_PIEDRA;
        }

        // =========================================================
        // ✨ EL AUTO-CORRECTOR PARA ANGULAR (LA SOLUCIÓN)
        // =========================================================
        // Si es un select y tiene un valor guardado, buscamos la opción exacta 
        // en tu lista ignorando mayúsculas y minúsculas.
        if (attr.tipo === 'select' && attr.valor) {
          const valorGuardado = String(attr.valor).toLowerCase().trim();
          const opcionExacta = attr.opciones.find((opt: string) => opt.toLowerCase().trim() === valorGuardado);
          
          if (opcionExacta) {
            attr.valor = opcionExacta; 
          }
        }

        return attr;
      });
  }

  formatLabel(n: string): string { return formatLabel(n); }
  getPlaceholder(n: string): string { return getPlaceholder(n); }

  // ================== CARGA DE DATOS ==================

  cargarStock(id: number) {
    this.productsService.obtenerStock(id).subscribe({
      next: (data) => {
        this.tipoProducto = data.tipo_producto || 'ropa_superior';

        // ✨ CORRECCIÓN 1: Extraemos el material de atributos_extra
        const materialBackend = data.atributos_extra && data.atributos_extra['material'] 
                                ? data.atributos_extra['material'] 
                                : null;
        
        this.contexto = {
          producto_id: data.producto_id,
          variante_id: data.variante_id,
          producto_nombre: data.producto_nombre,
          identidad_variante: data.identidad_variante,
          etiqueta: data.etiqueta,
          talla: data.talla,
          sku: data.stock_sku,
          imagen_cover: data.imagen_cover,
          hex_identidad: data.hex_identidad,
          material: materialBackend,
        };

        this.stockData = {
          cantidad: data.stock_disponible,
          precio_compra: data.precio_compra,
          precio_venta: data.precio_venta,
          descuento: data.descuento,
          ubicacion: data.ubicacion_almacen,
          fecha_compra: data.fecha_compra || '',
          proveedor_id: data.proveedor_id || null,
          publicar_web: data.canales?.web || false,
          atributos: this.hidratarAtributos(data.atributos_extra, this.tipoProducto),
          material: this.contexto.material,
        };
        console.log('Stock cargado:', this.stockData);
        this.cargandoDatos = false;
      },
      error: (err) => {
        console.error('Error al cargar', err);
        this.volver();
      }
    });
  }

  onSupplierChanged(prov: Proveedor) {
    this.stockData.proveedor_id = prov.id || null;
  }

  irAGestionarVariante() {
    if (this.contexto?.producto_id && this.contexto?.variante_id) {
      this.router.navigate(['/edit', this.contexto.producto_id], { 
        fragment: `variante-${this.contexto.variante_id}`
      });
    }
  }

  verProductoPadre() {
    if (this.contexto?.producto_id) {
      this.router.navigate(['/detail-product', this.contexto.producto_id]);
    }
  }

 private validarFormulario(): boolean {
    // 1. FORZAMOS A QUE LOS NÚMEROS BASE SEAN AL MENOS 0 SI ESTÁN VACÍOS
    this.stockData.cantidad = Number(this.stockData.cantidad) || 0;
    this.stockData.precio_compra = Number(this.stockData.precio_compra) || 0;
    this.stockData.precio_venta = Number(this.stockData.precio_venta) || 0;
    this.stockData.descuento = Number(this.stockData.descuento) || 0;

    // =======================================================
    // 2. VALIDACIONES ESTRICTAS (OBLIGATORIAS SIEMPRE)
    // =======================================================
    if (this.stockData.precio_compra <= 0) {
      alert('⚠️ El precio de compra es obligatorio y debe ser mayor a 0.');
      return false;
    }
    
    if (!this.stockData.fecha_compra || String(this.stockData.fecha_compra).trim() === '') {
      alert('⚠️ La fecha de compra es obligatoria.');
      return false;
    }
    
    if (!this.stockData.ubicacion || String(this.stockData.ubicacion).trim() === '') {
      alert('⚠️ La ubicación en el almacén es obligatoria.');
      return false;
    }
    
    if (!this.stockData.proveedor_id) {
      alert('⚠️ Debes seleccionar un proveedor válido.');
      return false;
    }

    // =======================================================
    // 3. VALIDACIONES WEB (SOLO SI SE PUBLICA EN TIENDA)
    // =======================================================
    const vaAWeb = this.stockData.publicar_web === true || String(this.stockData.publicar_web) === 'true';
    
    if (vaAWeb) {
      if (this.stockData.cantidad <= 0) {
        alert('🌐 Para publicar en la web, debes tener al menos 1 unidad en stock.');
        return false;
      }
      
      // Buscamos el peso para forzar que lo llenen
      const pesoAttr = this.stockData.atributos.find((a: any) => a.nombre === 'peso_kg');
      const pesoValor = pesoAttr && pesoAttr.valor ? Number(pesoAttr.valor) : 0;
      
      if (pesoValor <= 0) {
        alert('🌐 Para publicar en la web, el peso (kg) es obligatorio para los envíos.');
        return false;
      }
    }

    return true; // Si pasa todos los filtros, está listo para enviarse
  }

  onSubmit(): void {
    // Primero pasamos por la aduana (Validación)
    if (!this.validarFormulario()) {
      return; 
    }

    this.isSubmitting = true;

    // ✨ EL RELLENADOR AUTOMÁTICO DE ATRIBUTOS
    const atributosCompletos = this.stockData.atributos.map((attr: any) => {
      let valorCrudo = attr.valor;
      let valorFinal = String(valorCrudo).trim();

      // Detectamos si el campo está vacío, es null, o el usuario dejó "Selecciona..."
      const estaVacio = valorCrudo === null || 
                        valorCrudo === undefined || 
                        valorFinal === '' || 
                        valorFinal === 'null' || 
                        valorFinal === 'Selecciona...';

      if (estaVacio) {
        // Si el campo es de tipo numérico (medidas, capacidad, etc.), forzamos un 0
        if (attr.tipo === 'number') {
          valorFinal = '0';
        } else {
          // Si es un texto o un select (material, piedra), forzamos "No especificado"
          valorFinal = 'No especificado';
        }
      }

      return {
        nombre: attr.nombre,
        valor: valorFinal
      };
    });

    const dataParaEnviar = {
      ...this.stockData,
      atributos: atributosCompletos
    };

    console.log("🚀 ENVIANDO AL BACKEND (100% Lleno):", dataParaEnviar.atributos);

    this.productsService.actualizarStockIndividual(this.stockId!, dataParaEnviar).subscribe({
      next: () => {
        alert('✅ Inventario actualizado correctamente.');
        this.volver();
      },
      error: (err) => {
        this.isSubmitting = false;
        console.error(err);
        alert('❌ Error al guardar. Revisa tu conexión o contacta a soporte.');
      }
    });
  }

  volver() {
    this.router.navigate(['/stock-detail', this.stockId]);
  }
}