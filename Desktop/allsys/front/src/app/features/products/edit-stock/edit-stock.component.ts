import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { ProductsService } from '../../../core/services/products.service';
import { SupplierSelectorComponent, Proveedor } from "../add-product/components/supplier-selector/supplier-selector.component";
import { 
  ATRIBUTOS_BASE, 
  ATRIBUTOS_POR_TIPO 
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
    
    // ✨ FILTRO CRÍTICO: Excluimos los que ya se muestran en la sección de Identidad
    // para que no aparezcan inputs editables de talla o color aquí.
    const atributosAExcluir = [
      'talla', 'color', 'identidad_variante', 'numero', 
      'talla_anillo', 'capacidad_ml', 'talla_guantes'
    ];

    return molde
      .filter(attr => !atributosAExcluir.includes(attr.nombre.toLowerCase()))
      .map(attr => {
        if (extrasBackend && extrasBackend[attr.nombre] !== undefined) {
          attr.valor = extrasBackend[attr.nombre];
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
        
        this.contexto = {
          producto_id: data.producto_id,
          variante_id: data.variante_id,
          producto_nombre: data.producto_nombre,
          identidad_variante: data.identidad_variante,
          etiqueta: data.etiqueta,
          talla: data.talla,
          sku: data.stock_sku,
          imagen_cover: data.imagen_cover,
          hex_identidad: data.hex_identidad
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
          atributos: this.hidratarAtributos(data.atributos_extra, this.tipoProducto)
        };
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

  onSubmit(): void {
    if (this.stockData.cantidad < 0) return alert('El stock no puede ser negativo.');
    this.isSubmitting = true;

    const dataParaEnviar = {
      ...this.stockData,
      atributos: this.stockData.atributos.reduce((acc: any, attr: any) => {
        if (attr.valor !== null && attr.valor !== '') {
          acc[attr.nombre] = attr.valor;
        }
        return acc;
      }, {})
    };

    this.productsService.actualizarStockIndividual(this.stockId!, dataParaEnviar).subscribe({
      next: () => {
        alert('Inventario actualizado.');
        this.volver();
      },
      error: (err) => {
        this.isSubmitting = false;
        alert('Error al guardar.');
      }
    });
  }

  volver() {
    this.router.navigate(['/stock-detail', this.stockId]);
  }
}