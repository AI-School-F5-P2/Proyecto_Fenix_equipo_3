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


// ================== INTERFACES DEL BACKEND ==================
export interface AtributoBackend {
  id?: number;
  nombre: string;
  valor: any; 
}

export interface ImagenBackend {
  id: number;
  url: string;
}

export interface StockBackend {
  id: number;
  sku: string;
  cantidad: number; // ✨ Ojo: En DB se llama 'cantidad', en tu front 'stock'
  precio_compra: number;
  precio_venta: number;
  fecha_compra: string; 
  proveedor_id?: number | null;
  proveedor?: { id: number; nombre_proveedor: string }; // Si tu backend hace el JOIN
  etiqueta?: string | null;
  descuento?: number; // Si lo tienes en la DB
  publicar_web: boolean;
  publicar_vinted: boolean;
  publicar_wallapop: boolean;
  atributos: AtributoBackend[];
}

export interface VarianteBackend {
  id: number;
  sku: string;
  identidad_variante: string;
  hex_identidad: string;
  ubicacion: string;
  descripcion: string;
  imagenes: string[];
  stocks: StockBackend[];
}

export interface ProductoBackend {
  id: number;
  nombre: string;
  descripcion: string;
  tipo: string;
  estado: EstadoPrenda;
  publico_objetivo: string;
  categoria_id: number;
  marca_id: number;
  sku: string;
  variantes: VarianteBackend[];
  marca?: Marca;
}
// ================== INTERFACES ==================

interface StockVariante {
  id?: number;
  sku: string;
  atributos: any[];
  stock: number;
  precio_compra: number;
  precio_venta: number;
  descuento: number;
  proveedor: string;
  proveedor_id?: number | null;
  fecha_compra: string;
  estado: EstadoPrenda;
  publicar_vinted: boolean;
  publicar_wallapop: boolean;
  publicar_web: boolean;
  etiqueta?: string;
  proveedorSeleccionado?: { id?: number; nombre: string; isNew?: boolean };
  showProveedores?: boolean;
}

interface Marca {
  id?: number;
  nombre: string;
  descripcion?: string | null;
  isNew?: boolean;
}

type EstadoPrenda = 'nuevo' | 'segunda_mano';

interface Variante {
  [key: string]: any;
  id?: number;
  temp_id: string;
  identidad_variante: string; // Antes: valor_visual_nombre
  hex_identidad: string; 
  showColorDropdown?: boolean;
  stocks: StockVariante[];
  imagenes: string[];
  imagenesFiles: File[];
  ubicacion: string;
  descripcion:string
}

@Component({
  selector: 'app-add-product',
  standalone: true,
  imports: [CommonModule, FormsModule, BrandSelectorComponent, SupplierSelectorComponent, ColorSelectorComponent, CategorySelectorComponent],
  templateUrl: './add-product.component.html',
  styleUrls: ['./add-product.component.css']
})
export class AddProductComponent implements OnInit {

  productoId: number | null = null;
  isEditMode = false;
  cargandoDatos = false;


  // ================== DATOS BÁSICOS ==================
  nombre = '';
  descripcion = '';
  isSubmitting = false;
  
  // ✨ NUEVO: Lista de públicos y variable seleccionada
  listaPublicos = ['Mujer', 'Hombre', 'Unisex', 'Niña', 'Niño', 'Bebé'];
  publicoSeleccionado = '';

  // Tipos extendidos para cubrir todo tu árbol de categorías
  tipoProductoBase: 'ropa_superior' | 'ropa_inferior' | 'calzado' | 'bolsos' | 'accesorios' | 'joyeria_anillos' | 'joyeria_collares' | 'joyeria_general' | 'perfumeria' | 'belleza' | 'guantes' = 'ropa_superior';
  
atributosBase = [
    { nombre: 'peso_kg', tipo: 'number' },
    { nombre: 'color', tipo: 'color-dropdown' }
    
  ];

  // ================== LISTAS DE OPCIONES REUTILIZABLES ==================
  MATERIALES_ROPA = [
  'Algodón', 'Poliéster', 'Lino', 'Lana / Cachemira', 'Seda', 
  'Cuero / Piel', 'Piel Sintética (Polipiel)', 'Denim / Vaquero', 
  'Viscosa / Rayón', 'Elastano / Lycra', 'Pana', 'Terciopelo', 
  'Mezcla (Blend)', 'Otro'
];

TALLAS_ROPA = [
    // Tallas por letras
    'XXS', 'XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL',
    
    // Tallas numéricas (Pantalones, faldas, blusas, trajes...)
    '32', '34', '36', '38', '40', '42', '44', '46', '48', '50', '52', '54', '56',
    
    // Especiales
    'Única'
  ];

MATERIALES_CALZADO_BOLSOS = [
  'Cuero / Piel', 'Piel Sintética (Polipiel)', 'Ante / Gamuza', 
  'Charol', 'Lona / Tela', 'Nylon / Impermeable', 'Goma / Caucho', 
  'Materiales Reciclados', 'Rafia / Paja / Mimbre', 'Neopreno', 'Otro'
];

TALLAS_CALZADO = ['30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45']

MATERIALES_JOYERIA = [
  'Oro Amarillo 18K', 'Oro Amarillo 14K', 'Oro Amarillo 9K',
  'Oro Blanco 18K', 'Oro Blanco 14K', 'Oro Blanco 9K',
  'Oro Rosa 18K', 'Oro Rosa 14K',
  'Plata de Ley (925)', 'Plata Bañada en Oro (Vermeil)',
  'Platino', 'Acero Inoxidable', 'Titanio', 
  'Latón Bañado en Oro', 'Aleación / Bisutería', 'Cuero', 'Madera'
];

PIEDRAS_JOYERIA = [
  'Sin piedra', 'Circonita Cúbica', 'Cristal / Swarovski', 
  'Diamante', 'Esmeralda', 'Rubí', 'Zafiro', 'Perla', 
  'Amatista', 'Cuarzo (Rosa, Blanco, etc.)', 'Ópalo', 
  'Turquesa', 'Ágata', 'Aguamarina', 'Jade', 'Otra'
];
  
atributosPorTipo: Record<string, { nombre: string; tipo: string; opciones?: string[] }[]> = {
    ropa_superior: [
      { nombre: 'talla', tipo: 'select' , opciones: this.TALLAS_ROPA},
      { nombre: 'sisa_a_sisa_cm', tipo: 'number' },
      { nombre: 'hombros_cm', tipo: 'number' },
      { nombre: 'largo_total_cm', tipo: 'number' },
      { nombre: 'material', tipo: 'select', opciones: this.MATERIALES_ROPA } // Usamos la variable
    ],
    ropa_inferior: [
      { nombre: 'talla', tipo: 'select' , opciones: this.TALLAS_ROPA},
      { nombre: 'cintura_cm', tipo: 'number' },
      { nombre: 'cadera_cm', tipo: 'number' },
      { nombre: 'largo_pierna_cm', tipo: 'number' },
      { nombre: 'material', tipo: 'select', opciones: this.MATERIALES_ROPA } // Usamos la variable
    ],
    calzado: [
      { nombre: 'numero', tipo: 'select' , opciones: this.TALLAS_CALZADO},
      { nombre: 'longitud_plantilla_cm', tipo: 'number' },
      { nombre: 'material', tipo: 'select', opciones: this.MATERIALES_CALZADO_BOLSOS }
    ],
    bolsos: [
      { nombre: 'ancho_cm', tipo: 'number' },
      { nombre: 'alto_cm', tipo: 'number' },
      { nombre: 'profundidad_cm', tipo: 'number' },
      { nombre: 'material', tipo: 'select', opciones: this.MATERIALES_CALZADO_BOLSOS }
    ],
    joyeria_anillos: [
      { nombre: 'talla_anillo', tipo: 'text' }, // Ej: 14, 16, 52...
      { nombre: 'material', tipo: 'select', opciones: this.MATERIALES_JOYERIA },
      { nombre: 'piedra', tipo: 'select', opciones: this.PIEDRAS_JOYERIA },
      { nombre: 'color_piedra', tipo: 'select', opciones: ['Azul', 'Verde', 'Rojo', 'Blanco', 'Rosa', 'Multicolor'] }
    ],
    joyeria_collares: [
      { nombre: 'largo_cm', tipo: 'number' },
      { nombre: 'material', tipo: 'select', opciones: this.MATERIALES_JOYERIA },
      { nombre: 'piedra', tipo: 'select', opciones: this.PIEDRAS_JOYERIA },
      { nombre: 'color_piedra', tipo: 'select', opciones: ['Azul', 'Verde', 'Rojo', 'Blanco', 'Rosa', 'Multicolor'] }
    ],
    joyeria_general: [ // Para pendientes, pulseras, broches, etc.
      { nombre: 'material', tipo: 'select', opciones: this.MATERIALES_JOYERIA },
      { nombre: 'piedra', tipo: 'select', opciones: this.PIEDRAS_JOYERIA },
      { nombre: 'color_piedra', tipo: 'select', opciones: ['Azul', 'Verde', 'Rojo', 'Blanco', 'Rosa', 'Multicolor'] }
    ],
    perfumeria: [
      { nombre: 'capacidad_ml', tipo: 'number' },
      { nombre: 'formato', tipo: 'text' }, 
      { 
        nombre: 'concentracion', 
        tipo: 'select', 
        opciones: [
          'Eau Fraîche', 'Eau de Cologne - EDC', 'Eau de Toilette - EDT', 
          'Eau de Parfum - EDP', 'Parfum / Extrait de Parfum', 'Body Mist / Splash'
        ] 
      }
    ],
    accesorios: [
      { nombre: 'talla_unica', tipo: 'text' },
      // Los accesorios suelen mezclar materiales de bolsos y ropa, usamos el de ropa + cuero
      { nombre: 'material', tipo: 'select', opciones: this.MATERIALES_ROPA }, 
      { nombre: 'dimensiones_notas', tipo: 'text' }
    ],
    guantes: [
      // ✨ Corrección aquí: 'select' en lugar de 'selct'
      { nombre: 'talla_guantes', tipo: 'select', opciones: this.TALLAS_ROPA },
      { nombre: 'material', tipo: 'select', opciones: this.MATERIALES_ROPA }, 
      { nombre: 'dimensiones_notas', tipo: 'text' }
    ],
    belleza: [
      { nombre: 'cantidad_ml_g', tipo: 'number' },
      { nombre: 'tipo_piel_cabello', tipo: 'text' },
      { nombre: 'formato', tipo: 'text' }
    ]
  };

  lugarCompra = '';
  fechaCompra: string | null = null;

  // ================== MOTOR DE ESCALABILIDAD ==================
  // Este diccionario controla cómo se comporta el formulario para CUALQUIER categoría futura.
  get ejeVariacion() {
    const configuracionEjes: Record<string, any> = {
      // Categorías que usan paleta de COLORES
      ropa_superior: { tipo: 'color', titulo: 'Estilo / Color', label: 'Color principal' },
      ropa_inferior: { tipo: 'color', titulo: 'Estilo / Color', label: 'Color principal' },
      calzado:       { tipo: 'color', titulo: 'Estilo / Color', label: 'Color principal' },
      bolsos:        { tipo: 'color', titulo: 'Estilo / Color', label: 'Color principal' },

      // 💎 CATEGORÍAS CON SELECTOR DE METALES (JOYERÍA)
      joyeria_anillos:  { tipo: 'dropdown', titulo: 'Variante de Metal', label: 'Metal / Material Principal', opciones: this.MATERIALES_JOYERIA },
      joyeria_collares: { tipo: 'dropdown', titulo: 'Variante de Metal', label: 'Metal / Material Principal', opciones: this.MATERIALES_JOYERIA },
      joyeria_general:  { tipo: 'dropdown', titulo: 'Variante de Metal', label: 'Metal / Material Principal', opciones: this.MATERIALES_JOYERIA },
      accesorios:    { tipo: 'color', titulo: 'Estilo / Color', label: 'Color principal' },
      guantes: { tipo: 'color', titulo: 'Estilo / Color', label: 'Color de los guantes' },
      // Categorías que usan TEXTO
      perfumeria: { tipo: 'texto', titulo: 'Formato / Presentación', label: 'Formato / Capacidad', placeholder: 'Ej: Frasco 100ml' },
      belleza:    { tipo: 'texto', titulo: 'Formato / Presentación', label: 'Formato / Capacidad', placeholder: 'Ej: Pack 2, 50ml' },
      
      // ✨ ¡TUS FUTURAS CATEGORÍAS YA ESTÁN PENSADAS AQUÍ! ✨
      telefonos:  { tipo: 'texto', titulo: 'Capacidad / Versión', label: 'Almacenamiento / RAM', placeholder: 'Ej: 256GB / 8GB RAM' },
      neveras:    { tipo: 'color', titulo: 'Acabado Exterior', label: 'Color / Material Exterior', placeholder: '' },
      muebles:    { tipo: 'color', titulo: 'Acabado / Tapizado', label: 'Color de madera o tela', placeholder: '' }

      
    };

    // Si la categoría no existe en el diccionario, por defecto usará 'Color'
    return configuracionEjes[this.tipoProductoBase] || { tipo: 'color', titulo: 'Estilo / Color', label: 'Color principal' };
  }

  estadoSeleccionado: EstadoPrenda = 'nuevo';

  // ================== PUBLICACIÓN ==================
  canalesPublicacion = { web: false, vinted: false, wallapop:false };
  estadoGestion: 'borrador' | 'inventario' | 'publicado' = 'borrador';

  // ================== CATEGORÍAS ==================
  todasLasCategorias: any[] = [];
  categoriaActual: any[] = [];
  rutaCategorias: any[] = [];
  categoriaSeleccionadaFinal: number | null = null;
  dropdownAbierto = false;

  // ================== MARCAS ==================
  marcas: Marca[] = [];
  marcaInput: string = '';
  dropdownOpen: boolean = false;
  marcaSeleccionada: Marca | null = null;

  // ================== PROVEEDORES ==================
  proveedores: any[] = [];
  cargandoProveedores = false;
  dropdownProveedorOpen: boolean = false;

  // ================== VARIANTES ==================
  variantes: Variante[] = [];

  // ================== PALETA DE COLORES ==================
// En tu AddProductComponent

colores = [
  // ⚪ Neutros y Básicos
  { hex: '#000000', nombre: 'Negro', claro: false },
  { hex: '#FFFFFF', nombre: 'Blanco', claro: true },
  { hex: '#4B4B4B', nombre: 'Gris Oscuro', claro: false },
  { hex: '#BEBEBE', nombre: 'Gris Claro', claro: true },
  { hex: '#F5F5DC', nombre: 'Beige', claro: true },
  { hex: '#FFFDD0', nombre: 'Crema / Marfil', claro: true },
  { hex: '#483C32', nombre: 'Topo (Taupe)', claro: false },

  // 🟤 Tonos Tierra
  { hex: '#4B3621', nombre: 'Marrón Oscuro', claro: false },
  { hex: '#8B5A2B', nombre: 'Marrón Claro / Camel', claro: false },
  { hex: '#C3B091', nombre: 'Caqui', claro: true },
  { hex: '#D2B48C', nombre: 'Canela / Tan', claro: true },

  // 🔵 Azules
  { hex: '#000080', nombre: 'Azul Marino', claro: false },
  { hex: '#1560BD', nombre: 'Azul Denim / Vaquero', claro: false },
  { hex: '#0000FF', nombre: 'Azul', claro: false },
  { hex: '#4169E1', nombre: 'Azul Real', claro: false },
  { hex: '#87CEEB', nombre: 'Azul Cielo', claro: true },
  { hex: '#40E0D0', nombre: 'Turquesa', claro: true },

  // 🟢 Verdes
  { hex: '#006400', nombre: 'Verde Bosque', claro: false },
  { hex: '#556B2F', nombre: 'Verde Oliva', claro: false },
  { hex: '#50C878', nombre: 'Verde Esmeralda', claro: false },
  { hex: '#00FF00', nombre: 'Verde', claro: true },
  { hex: '#98FF98', nombre: 'Verde Menta', claro: true },

  // 🔴 Rojos y Rosas
  { hex: '#FF0000', nombre: 'Rojo', claro: false },
  { hex: '#800000', nombre: 'Granate / Burdeos', claro: false },
  { hex: '#FF7F50', nombre: 'Coral', claro: true },
  { hex: '#FFC0CB', nombre: 'Rosa Pastel', claro: true },
  { hex: '#FF69B4', nombre: 'Rosa Fucsia', claro: false },

  // 🟣 Morados
  { hex: '#800080', nombre: 'Morado / Púrpura', claro: false },
  { hex: '#E6E6FA', nombre: 'Lila / Lavanda', claro: true },
  { hex: '#4B0082', nombre: 'Berenjena', claro: false },

  // 🟡 Amarillos y Naranjas
  { hex: '#FFFF00', nombre: 'Amarillo', claro: true },
  { hex: '#FFDB58', nombre: 'Mostaza', claro: true },
  { hex: '#FFA500', nombre: 'Naranja', claro: true },
  { hex: '#FFE5B4', nombre: 'Melocotón', claro: true },

  // ✨ Metálicos y Especiales
  { hex: '#FFD700', nombre: 'Dorado', claro: true },
  { hex: '#C0C0C0', nombre: 'Plateado', claro: true },
  { hex: '#CD7F32', nombre: 'Bronce', claro: false },
  { hex: '#B76E79', nombre: 'Oro Rosa', claro: false },
  { hex: '#E3FF00', nombre: 'Neón', claro: true }
];

  constructor(
    private productsService: ProductsService, 
    private router: Router, 
    private route: ActivatedRoute,
    private suppliersService: SuppliersService
  ) {}

  ngOnInit(): void {
    this.cargarCategorias();
    this.cargarMarcas();
    this.cargarProveedores();
    this.resetVariantes();

    // 2. Comprobamos la URL
    this.route.paramMap.subscribe(params => {
      const id = params.get('id');
      if (id) {
        this.isEditMode = true;
        this.productoId = Number(id);
        this.cargarProductoParaEditar(this.productoId);
      } else {
        this.isEditMode = false;
        this.resetVariantes(); // Empezamos en blanco
      }

      console.log(id)
    });
  }

  cargarProductoParaEditar(id: number) {
  this.cargandoDatos = true;
  
  this.productsService.obtenerProducto(id).subscribe({
    next: (productoDB: ProductoBackend) => {
      console.log(productoDB)
      // 1. Rellenar datos básicos
      this.nombre = productoDB.nombre;
      this.descripcion = productoDB.descripcion;
      this.estadoSeleccionado = productoDB.estado;
      this.publicoSeleccionado = productoDB.publico_objetivo;
      this.categoriaSeleccionadaFinal = productoDB.categoria_id;
      
      // 1. Asignamos el tipo (ej: 'joyeria_anillos') ANTES de procesar los atributos
        this.tipoProductoBase = (productoDB.tipo as any) || 'ropa_superior';
        
        // 2. Le damos un pequeñísimo respiro a Angular para que el componente 
        // hijo del selector de categorías detecte el cambio y arme la ruta correcta.
        setTimeout(() => {
          this.categoriaSeleccionadaFinal = productoDB.categoria_id;
        });
        // ✨ FIN DEL CÓDIGO NUEVO ✨

        // Opcional: Cargar marca si viene del back
        if (productoDB.marca) {
          this.marcaSeleccionada = productoDB.marca;
          this.marcaInput = productoDB.marca.nombre;
        }

      // 2. Mapeo Tipado de Variantes y Stock
      this.variantes = productoDB.variantes.map((vDB: VarianteBackend) => {
        return {
          id: vDB.id, 
          temp_id: this.generarTempId(),
          identidad_variante: vDB.identidad_variante,
          hex_identidad: vDB.hex_identidad,
          descripcion: vDB.descripcion,
          ubicacion: vDB.ubicacion,
          
          
          // Extraemos solo los strings de las URLs
          imagenes: vDB.imagenes ? [...vDB.imagenes] : [],
          imagenesFiles: [], // Empieza vacío para las nuevas fotos
          
          stocks: vDB.stocks.map((sDB: StockBackend) => {
            // Reconstruimos el proveedor
           const nombreProv = sDB.proveedor ? (sDB.proveedor.nombre_proveedor || (sDB.proveedor as any).nombre) : '';
            
            return {
               id: sDB.id,
               sku: sDB.sku,
               stock: sDB.cantidad, // ✨ Mapeo DB -> Frontend
               precio_compra: sDB.precio_compra,
               precio_venta: sDB.precio_venta,
               descuento: sDB.descuento || 0,
               fecha_compra: sDB.fecha_compra,
               proveedor: nombreProv,
               proveedor_id: sDB.proveedor_id,
               proveedorSeleccionado: sDB.proveedor ? { id: sDB.proveedor.id, nombre: nombreProv } : undefined,
               etiqueta: sDB.etiqueta || '',
               publicar_web: sDB.publicar_web,
               publicar_vinted: sDB.publicar_vinted,
               publicar_wallapop: sDB.publicar_wallapop,
               estado: this.estadoSeleccionado,
               
               // Formateamos los atributos para que Angular los entienda igual que al crear
               atributos: this.hidratarAtributos(sDB.atributos) 
            };
          })
        };
      });

      this.cargandoDatos = false;
    },
    error: (err) => {
      console.error('Error al cargar producto:', err);
      this.cargandoDatos = false;
    }
  });
}

// ✨ Método auxiliar para fusionar los atributos que vienen de la DB 
// con la estructura que necesita tu formulario HTML
private hidratarAtributos(atributosDB: AtributoBackend[]): any[] {
  // Obtenemos el molde vacío según la categoría (ej. ropa_superior)
  const atributosBase = this.getAtributosVacios(); 

  // Rellenamos el molde con los valores que vienen de la base de datos
  return atributosBase.map(attrForm => {
    const dbMatch = atributosDB.find(a => a.nombre === attrForm.nombre);
    if (dbMatch) {
      attrForm.valor = dbMatch.valor;
    }
    return attrForm;
  });
}

  // ================== GESTIÓN DE MARCAS ==================
  cargarMarcas(): void {
    this.productsService.cargarMarcas().subscribe({
      next: (data: Marca[]) => {
        console.log(data)
        this.marcas = data.sort((a,b) => a.nombre.localeCompare(b.nombre));
      }
    });
  }

  onBrandChanged(marca: Marca) {
    this.marcaSeleccionada = marca; 
    // Ahora this.marcaSeleccionada tendrá {id: 316, nombre: 'tiammy'} 
    // o {nombre: 'Nike', isNew: true}
  }

  get marcasFiltradas(): Marca[] {
    const input = this.marcaInput.trim().toLowerCase();
    let filtradas = this.marcas.filter(m => m.nombre.toLowerCase().includes(input));
    if (this.marcaSeleccionada) {
      filtradas = filtradas.filter(m => m.nombre !== this.marcaSeleccionada!.nombre);
      filtradas.unshift(this.marcaSeleccionada);
    }
    if (input && !this.marcas.some(m => m.nombre.toLowerCase() === input)) {
      filtradas.unshift({ nombre: this.marcaInput, isNew: true });
    }
    return filtradas;
  }

  selectMarca(marca: Marca): void {
    this.dropdownOpen = false;
    this.marcaSeleccionada = marca;
    this.marcaInput = marca.nombre;
  }

onBlur(): void {
    setTimeout(() => {
      this.dropdownOpen = false;
      // Si ya hay una marca seleccionada, forzamos que el input recupere ese nombre, 
      // sin importar si el usuario escribió otra cosa o borró todo.
      if (this.marcaSeleccionada) {
        this.marcaInput = this.marcaSeleccionada.nombre;
      } else {
        // Solo se vacía si NUNCA se llegó a seleccionar nada
        this.marcaInput = '';
      }
    }, 200);
  }

  onInputChange(): void { this.dropdownOpen = true; }
  onMarcaFocus(): void { this.dropdownOpen = true; }
  esMarcaSeleccionada(marca: Marca): boolean { return this.marcaSeleccionada?.nombre === marca.nombre; }

  // ================== GESTIÓN DE PROVEEDORES ==================
  cargarProveedores(): void {
    this.cargandoProveedores = true;
    this.suppliersService.getProveedores().subscribe({
      next: (data) => {
        console.log(data)
        this.proveedores = data.map(p => ({ id: p.id, nombre: p.nombre_proveedor }))
          .sort((a, b) => a.nombre.localeCompare(b.nombre));
        this.cargandoProveedores = false;
      },
      error: () => this.cargandoProveedores = false
    });
  }

  proveedoresFiltrados(stock: StockVariante) {
    const input = (stock.proveedor || '').trim().toLowerCase();
    let coincidencias = this.proveedores.filter(p => p.nombre.toLowerCase().includes(input));
    if (stock.proveedorSeleccionado) {
      coincidencias = coincidencias.filter(p => p.nombre !== stock.proveedorSeleccionado!.nombre);
      coincidencias.unshift(stock.proveedorSeleccionado);
    }
    if (input && !this.proveedores.some(p => p.nombre.toLowerCase() === input)) {
      coincidencias.unshift({ nombre: stock.proveedor, isNew: true });
    }
    return coincidencias;
  }


  onProveedoresFocus(stock: StockVariante): void { 
    stock.showProveedores = true; 
    if(this.proveedores.length === 0) this.cargarProveedores(); 
  }

  onProveedorInputChange(stock: StockVariante): void { 
    stock.showProveedores = true; 
  }

onProveedorBlur(stock: StockVariante): void {
    setTimeout(() => {
      stock.showProveedores = false;
      // Igual para el proveedor: forzamos el nombre si ya hay uno seleccionado
      if (stock.proveedorSeleccionado) {
        stock.proveedor = stock.proveedorSeleccionado.nombre;
      } else {
        stock.proveedor = '';
      }
    }, 200);
  }



  selectProveedor(proveedor: any, stock: StockVariante) {
    stock.proveedor = proveedor.nombre;
    stock.proveedorSeleccionado = proveedor;
    stock.showProveedores = false;
  }

  // Comprueba si un proveedor específico es el que está seleccionado actualmente
  esProveedorSeleccionado(proveedor: any, stock: StockVariante): boolean {
    return stock.proveedorSeleccionado?.nombre === proveedor.nombre;
  }

  onSupplierChanged(prov: Proveedor, stock: StockVariante) {
    stock.proveedor = prov.nombre; 
    stock.proveedor_id = prov.id || null;
    
    if (prov.isNew) {
      // Como proveedor_nombre_nuevo no está en la interfaz, 
      // puedes agregarlo a la interfaz como opcional, o pasarlo en el formData directamente.
      (stock as any).proveedor_nombre_nuevo = prov.nombre; 
    }
  }
  // ================== GESTIÓN DE CATEGORÍAS ==================
onCategorySelected(event: CategorySelectionEvent): void {
    const esLaMismaCategoria = Number(this.categoriaSeleccionadaFinal) === Number(event.categoriaId);

    this.categoriaSeleccionadaFinal = event.categoriaId;
    this.rutaCategorias = event.rutaCategorias; 

    // RECALCULAMOS EL TIPO 
    this.determinarTipoProductoBase();
    
    if (!esLaMismaCategoria) {
      this.refrescarAtributosEnVariantes();
    } else {
      // ✨ ESTO ES LO QUE HACE QUE EL ANILLO RECUPERE "Talla de anillo" y "Material" ✨
      this.variantes.forEach(v => {
         v.stocks.forEach(s => {
             s.atributos = this.hidratarAtributos(s.atributos);
         });
      });
    }
  }

  private cargarCategorias(): void {
    this.productsService.cargarCategorias().subscribe({
      next: (data) => {
        console.log(data)
        this.todasLasCategorias = data;
        this.categoriaActual = data.filter(c => c.parent_id === null);
      }
    });
  }

  abrirCategorias(): void { this.dropdownAbierto = !this.dropdownAbierto; }

seleccionarCategoria(cat: any): void {
    // 1. RECONSTRUIMOS LA RUTA CORRECTAMENTE PARA EVITAR DUPLICADOS
    if (cat.parent_id === null) {
      // Si es una categoría principal (ej. Accesorios), reiniciamos la ruta
      this.rutaCategorias = [cat];
    } else {
      // Si es una subcategoría, buscamos dónde está su padre en la ruta actual
      const parentIndex = this.rutaCategorias.findIndex(c => c.id === cat.parent_id);
      if (parentIndex !== -1) {
        // Cortamos la ruta exactamente hasta el padre, y luego añadimos la nueva opción
        this.rutaCategorias = this.rutaCategorias.slice(0, parentIndex + 1);
        this.rutaCategorias.push(cat);
      } else {
        // Respaldo de seguridad
        this.rutaCategorias.push(cat);
      }
    }

    // 2. COMPROBAMOS SI TIENE SUBCATEGORÍAS
    const sub = this.todasLasCategorias.filter(c => c.parent_id === cat.id);
    
    if (sub.length > 0) {
      // Aún quedan niveles por bajar
      this.categoriaActual = sub;
      this.categoriaSeleccionadaFinal = null; 
    } else {
      // Es una categoría final (hoja). ¡Cerramos y calculamos atributos!
      this.categoriaSeleccionadaFinal = cat.id;
      this.dropdownAbierto = false;
      this.determinarTipoProductoBase();
      this.refrescarAtributosEnVariantes();
    }
  }

// Esta función se asegura de que el "Valor Visual" se replique en los atributos de stock
sincronizarAtributosConEje(variante: Variante): void {
  const valor = variante.identidad_variante;
  
  variante.stocks.forEach(s => {
    // Si estamos en ropa, buscamos el atributo 'color' y le ponemos el valor
    // Si estamos en joyería, buscamos el atributo 'material' y le ponemos el valor
    const attrASincronizar = s.atributos.find(a => 
      a.nombre.toLowerCase() === 'color' || 
      a.nombre.toLowerCase() === 'material' ||
      a.nombre.toLowerCase() === 'capacidad_ml'
    );

    if (attrASincronizar) {
      attrASincronizar.valor = valor;
    }
  });
}

private determinarTipoProductoBase(): void {
    if (!this.rutaCategorias.length) return;

    const raizId = Number(this.rutaCategorias[0].id); 
    const nivel2Id = this.rutaCategorias.length > 1 ? Number(this.rutaCategorias[1].id) : null;
    const nivel3Id = this.rutaCategorias.length > 2 ? Number(this.rutaCategorias[2].id) : null;

    switch (raizId) {
      case 1: // ROPA
        const idsInferiores = [2, 34, 87, 96]; // Faldas, Pantalones, Ropa Interior, Baño
        this.tipoProductoBase = (nivel2Id && idsInferiores.includes(nivel2Id)) ? 'ropa_inferior' : 'ropa_superior';
        break;

      case 100: // CALZADO
        this.tipoProductoBase = 'calzado';
        break;

      case 119: // BOLSOS
        this.tipoProductoBase = 'bolsos';
        break;

      case 138: // ACCESORIOS
        if (nivel2Id === 152) { 
          // 💎 ESTAMOS EN JOYERÍA
          if (nivel3Id === 161) {
            this.tipoProductoBase = 'joyeria_anillos';
            console.log('estamos en aniloos')
          } else if (nivel3Id === 160 || nivel3Id === 157) { // Collares o Colgantes
            this.tipoProductoBase = 'joyeria_collares';
          } else {
            // Pendientes, pulseras, broches, etc.
            this.tipoProductoBase = 'joyeria_general';
          }
        } 
        
        else if(nivel2Id === 141){
          this.tipoProductoBase = 'guantes'
        }


        else {
          // Gafas, bufandas, sombreros...
          this.tipoProductoBase = 'accesorios';
        }
        break;

      case 167: // CUIDADO Y BELLEZA
        this.tipoProductoBase = (nivel2Id === 169) ? 'perfumeria' : 'belleza';
        break;

      default:
        this.tipoProductoBase = 'accesorios';
    }
  }

  private refrescarAtributosEnVariantes(): void {
    const nuevosAtributos = this.getAtributosVacios();
    this.variantes.forEach(v => {
      v.stocks.forEach(s => {
        s.atributos = JSON.parse(JSON.stringify(nuevosAtributos));
      });
    });
  }

  volverCategoria(): void {
    this.rutaCategorias.pop();
    const last = this.rutaCategorias.at(-1);
    this.categoriaActual = last ? 
      this.todasLasCategorias.filter(c => c.parent_id === last.id) : 
      this.todasLasCategorias.filter(c => c.parent_id === null);
  }

  getNombreCategoriaSeleccionada(): string {
    return this.rutaCategorias.length ? this.rutaCategorias.map(c => c.nombre).join(' / ') : 'Seleccionar categoría';
  }

  // ================== LÓGICA DE VARIANTES Y STOCK ==================
  private generarTempId(): string { return crypto.randomUUID(); }
  
  resetVariantes(): void { this.variantes = [this.nuevaVariante()]; }

nuevaVariante(): Variante {
    return { 
      temp_id: this.generarTempId(), 
      hex_identidad: '#FFFFFF', // Blanco por defecto
      identidad_variante: '',     // ✨ CAMBIO: Empezamos vacío, no en "Negro"
      showColorDropdown: false, 
      stocks: [this.nuevoStock()], 
      imagenes: [], 
      imagenesFiles: [], 
      ubicacion: '',
      descripcion: ''
    };
}

  nuevoStock(): StockVariante {
    return { 
      sku: '', 
      atributos: this.getAtributosVacios(), 
      stock: 0, 
      precio_compra: 0, 
      precio_venta: 0, 
      descuento: 0, 
      proveedor: '', 
      proveedor_id: null,
      fecha_compra: '', 
      estado: 'nuevo', 
      publicar_vinted: false, 
      publicar_wallapop: false,
      publicar_web: false,
      etiqueta: '' ,
      showProveedores: false
    };
  }

  agregarVariante(): void { this.variantes.push(this.nuevaVariante()); }
  agregarStock(i: number): void { this.variantes[i].stocks.push(this.nuevoStock()); }
  eliminarStock(i: number, j: number): void { this.variantes[i].stocks.splice(j, 1); }
  
  eliminarVariante(index: number): void { 
    if (this.variantes.length === 1) { alert('Debe existir al menos una variante'); return; } 
    this.variantes.splice(index, 1); 
  }

  getAtributosVacios(): any[] {
    const especificos = this.atributosPorTipo[this.tipoProductoBase] || [];
    return [...especificos, ...this.atributosBase].map(attr => ({ ...attr, valor: null }));
  }

  // Helpers para labels y placeholders en HTML
  formatLabel(nombre: string): string {
    const diccionario: Record<string, string> = {
      'sisa_a_sisa_cm': 'Sisa a Sisa (cm)',
      'hombros_cm': 'Hombros (cm)',
      'largo_total_cm': 'Largo Total (cm)',
      'cintura_cm': 'Cintura (cm)',
      'cadera_cm': 'Cadera (cm)',
      'largo_pierna_cm': 'Largo Pierna (cm)',
      'longitud_plantilla_cm': 'Plantilla (cm)',
      'capacidad_ml': 'Capacidad (ml)',
      'concentracion': 'Concentración (EDP/EDT)',
      'cantidad_ml_g': 'Contenido (ml/g)',
      'tipo_piel_cabello': 'Para piel/cabello:',
      'ancho_cm': 'Ancho (cm)',
      'alto_cm': 'Alto (cm)',
      'profundidad_cm': 'Fondo (cm)',
      'talla_anillo': 'Talla de Anillo',
    };
    return diccionario[nombre] || nombre.replace(/_/g, ' ').toUpperCase();
  }

  getPlaceholder(nombre: string): string {
    if (nombre.includes('_cm')) return '0';
    if (nombre.includes('_ml')) return '100';
    if (nombre === 'concentracion') return 'Ej: Eau de Parfum';
    if (nombre === 'material') return 'Ej: Cuero, Algodón, Oro 18k...';
    return '...';
  }

  actualizarMetalVariante(variante: Variante): void {
    const metalElegido = variante.identidad_variante;
    
    // 1. Asignamos un HEX aproximado para la base de datos
    const nombre = metalElegido.toLowerCase();
    if (nombre.includes('oro')) variante.hex_identidad = '#FFD700';
    else if (nombre.includes('plata') || nombre.includes('platino') || nombre.includes('acero')) variante.hex_identidad = '#C0C0C0';
    else if (nombre.includes('cobre') || nombre.includes('bronce')) variante.hex_identidad = '#CD7F32';
    else variante.hex_identidad = '#FFFFFF';

    // 2. Sincronizamos con el atributo "material" en todos los stocks de esta variante
    variante.stocks.forEach(s => {
      const attrMaterial = s.atributos.find(a => a.nombre === 'material');
      if (attrMaterial) attrMaterial.valor = metalElegido;
    });

    this.sincronizarAtributosConEje(variante);
  }

  onColorChanged(color: Color, variante: Variante) {
  variante.hex_identidad = color.hex;
  variante.identidad_variante = color.nombre;
  
    // Si necesitas sincronizar con atributos (como hacíamos antes)
    this.sincronizarAtributosConEje(variante);
  }

  // ================== VALIDACIÓN Y ENVÍO ==================
// Reemplaza tu antigua función validarFormulario por esta:

private validarFormulario(): boolean {
  // 1. VALIDACIONES BÁSICAS OBLIGATORIAS SIEMPRE
  if (!this.categoriaSeleccionadaFinal) { alert('Debes seleccionar una categoría.'); return false; }
  if (!this.publicoSeleccionado) { alert('El género / público objetivo es obligatorio.'); return false; }
  if (!this.marcaSeleccionada) { alert('La marca es obligatoria.'); return false; }
  if (!this.nombre.trim()) { alert('El nombre del producto es obligatorio.'); return false; }

  if (this.variantes.length === 0) { alert('Debes añadir al menos una variante.'); return false; }

  // 2. RECORRIDO DE VARIANTES
  for (let i = 0; i < this.variantes.length; i++) {
    const v = this.variantes[i];

    // Descripción de variante siempre obligatoria (regla de negocio)
    if (!v.descripcion || !v.descripcion.trim()) { 
      alert(`La descripción de la Variante #${i + 1} (${v.identidad_variante || 'Sin nombre'}) es obligatoria.`); 
      return false; 
    }

    if (!v.identidad_variante.trim()) { alert(`Falta seleccionar el Color/Material en la Variante ${i + 1}`); return false; }
    if (!v.ubicacion?.trim()) { alert(`Falta indicar la Ubicación en la Variante ${i + 1}`); return false; }

    // DETECTAR SI ESTA VARIANTE TIENE ALGÚN STOCK PARA PUBLICAR
    // Añadimos s.publicar_web que faltaba en tu lógica
    const varianteSeVaAPublicar = v.stocks.some(s => s.publicar_web || s.publicar_vinted || s.publicar_wallapop);

    // Si se publica, exigir al menos una foto
    if (varianteSeVaAPublicar && v.imagenes.length === 0) { 
      alert(`La Variante #${i + 1} se va a publicar en la web/plataformas. Debes subir al menos una foto.`); 
      return false; 
    }

    if (v.stocks.length === 0) {
      alert(`La Variante #${i + 1} debe tener al menos una fila de stock.`);
      return false;
    }

    // 3. RECORRIDO DE STOCKS DENTRO DE LA VARIANTE
    for (let j = 0; j < v.stocks.length; j++) {
      const s = v.stocks[j];

      // Validación de inventario base (Siempre obligatorio)
      if (s.stock === null || s.stock === undefined || s.stock <= 0) { 
        alert(`Variante ${i + 1}, fila ${j + 1}: El stock debe ser mayor a 0.`); 
        return false; 
      }
      
      if (s.precio_compra === null || s.precio_compra === undefined || s.precio_compra < 0) { 
        alert(`Variante ${i + 1}, fila ${j + 1}: El precio de compra no puede estar vacío.`); 
        return false; 
      }
      
      if (!s.proveedor?.trim()) { alert(`Variante ${i + 1}, fila ${j + 1}: Falta el proveedor.`); return false; }
      if (!s.fecha_compra) { alert(`Variante ${i + 1}, fila ${j + 1}: Falta la fecha de compra.`); return false; }

      // --- VALIDACIONES ESPECÍFICAS PARA PUBLICACIÓN ---
      const stockSePublica = s.publicar_web || s.publicar_vinted || s.publicar_wallapop;

      if (stockSePublica) {
        // Exigir Precio de Venta
        if (!s.precio_venta || s.precio_venta <= 0) { 
          alert(`Variante ${i + 1}, fila ${j + 1}: El precio de venta es obligatorio para publicar en la web.`); 
          return false; 
        }
        
        // Exigir Peso (OBLIGATORIO para envíos)
        const attrPeso = s.atributos.find(a => a.nombre === 'peso_kg');
        if (!attrPeso || attrPeso.valor === null || attrPeso.valor === '' || attrPeso.valor <= 0) { 
          alert(`Variante ${i + 1}, fila ${j + 1}: El Peso (kg) es obligatorio para calcular envíos en la web.`); 
          return false; 
        }
      }

      // Validación de Talla según tipo de producto
      const categoriasConTalla = ['ropa_superior', 'ropa_inferior', 'calzado', 'guantes'];
      if (categoriasConTalla.includes(this.tipoProductoBase)) {
        const tieneTalla = s.atributos.some(a => (a.nombre.includes('talla') || a.nombre === 'numero') && a.valor);
        if (!tieneTalla) {
          alert(`Variante ${i + 1}, fila ${j + 1}: Debes seleccionar una Talla/Número.`); 
          return false;
        }
      }
    }
  }

  return true;
}



private construirFormData(): FormData {
  const formData = new FormData();
  formData.append('nombre', this.nombre);
  formData.append('descripcion', this.descripcion); 
  formData.append('tipo', this.tipoProductoBase);
  formData.append('estado', this.estadoSeleccionado);
  formData.append('categoria_id', String(this.categoriaSeleccionadaFinal));
  formData.append('publico_objetivo', this.publicoSeleccionado);

  if (this.marcaSeleccionada) {
    if (this.marcaSeleccionada.isNew) formData.append('marca_nombre', this.marcaSeleccionada.nombre);
    else formData.append('marca_id', String(this.marcaSeleccionada.id));
  }

  const variantesLimpias = this.variantes.map(v => ({
    id: v.id || null,
    temp_id: v.temp_id,
    identidad_variante: v.identidad_variante,
    hex_identidad: v.hex_identidad,
    ubicacion: v.ubicacion,
    descripcion: v.descripcion,
    
    // ✨ FOTOS: Le decimos al backend cuáles URLs viejas queremos conservar
    imagenes: v.imagenes.filter(img => img.startsWith('http')),
    
    stocks: v.stocks.map(s => {
      const proveedor_nuevo = s.proveedorSeleccionado?.isNew ? s.proveedor : null;

      return {
        id: s.id || null,
        sku: s.sku,
        
        // ✨ MANDAMOS AMBOS NOMBRES: 'stock' para Pydantic (POST) y 'cantidad' para Editar (PUT)
        stock: Number(s.stock) || 0,
        cantidad: Number(s.stock) || 0,
        
        precio_compra: Number(s.precio_compra) || 0,
        precio_venta: Number(s.precio_venta) || 0,
        descuento: Number(s.descuento) || 0,
        fecha_compra: s.fecha_compra,
        
        // ✨ MANDAMOS AMBOS: 'proveedor' para Pydantic (POST) y los IDs para Editar (PUT)
        proveedor: s.proveedor || 'Proveedor Desconocido', 
        proveedor_id: s.proveedor_id,
        proveedor_nombre_nuevo: proveedor_nuevo,
        
        etiqueta: s.etiqueta,
        publicar_web: s.publicar_web,
        publicar_vinted: s.publicar_vinted,
        publicar_wallapop: s.publicar_wallapop,
        
        atributos: s.atributos.filter(a => a.valor !== null && a.valor !== '')
      };
    })
  }));

  formData.append('variantes', JSON.stringify(variantesLimpias));
  
  // Envío de imágenes nuevas (Files)
  this.variantes.forEach(v => {
    v.imagenesFiles.forEach(f => formData.append(`imagenes_${v.temp_id}`, f));
  });

  return formData;
}

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
    this.variantes[i].imagenes.splice(j,1); 
    this.variantes[i].imagenesFiles.splice(j,1); 
  }

  // Obtiene el color HEX para pintar el cuadrito en el desplegable
  getHexColor(nombreColor: string): string {
    const color = this.colores.find(c => c.nombre === nombreColor);
    return color ? color.hex : '#ffffff';
  }

  // Cierra el desplegable y asigna el valor
seleccionarColorAtributo(attr: any, color: any, variante: Variante): void {
  attr.valor = color.nombre;
  // Sincronizamos con la identidad de la variante para actualizar el círculo visual
  variante.identidad_variante = color.nombre;
  variante.hex_identidad = color.hex;
  
  // Llamamos a la sincronización global de la variante
  this.sincronizarIdentidadVariante(variante);
}


// Actualiza tu función de selección de color para que llame a la sincronización
seleccionarColorVariante(variante: Variante, color: any): void {
  variante.identidad_variante = color.nombre;
  variante.hex_identidad = color.hex;
  variante.showColorDropdown = false;
  this.sincronizarAtributosConEje(variante); // <--- Sincroniza!
}

// 🧠 Define qué atributo de la tabla de stock es el "ADN" de la variante
  get mapeoIdentidadPorCategoria() {
    const reglas: Record<string, string> = {
      ropa_superior:   'color',
      ropa_inferior:   'color',
      calzado:         'color',
      joyeria_anillos: 'material', // En joyería manda el material (Oro/Plata)
      perfumeria:      'capacidad_ml',
      belleza:         'cantidad_ml_g',
      accesorios:      'color',
      guantes:         'color'
    };
    return reglas[this.tipoProductoBase] || 'color';
  }

  // ⚡ Sincroniza automáticamente la identidad de la variante desde la tabla de atributos
  sincronizarIdentidadVariante(variante: Variante): void {
    const nombreAtributoMaestro = this.mapeoIdentidadPorCategoria;

    // 1. Buscamos el valor en el primer registro de stock (el primero define la identidad)
    const primerStock = variante.stocks[0];
    const atributoMaestro = primerStock.atributos.find(a => a.nombre === nombreAtributoMaestro);

    if (atributoMaestro && atributoMaestro.valor) {
      // 2. Actualizamos el nombre de identidad (Ej: "Oro 18K")
      variante.identidad_variante = atributoMaestro.valor;

      // 3. Actualizamos el color representativo (HEX)
      if (nombreAtributoMaestro === 'color') {
        const colorEncontrado = this.colores.find(c => c.nombre === atributoMaestro.valor);
        variante.hex_identidad = colorEncontrado ? colorEncontrado.hex : '#FFFFFF';
      } 
      else if (nombreAtributoMaestro === 'material') {
        this.aplicarColorSegunMaterial(variante); 
      }
      else {
        variante.hex_identidad = '#FFFFFF'; // Color neutro para ml, unidades, etc.
      }
    }

    // 4. Mantenemos la consistencia: Todas las tallas/stocks deben compartir el mismo atributo maestro
    variante.stocks.forEach(s => {
      const attr = s.atributos.find(a => a.nombre === nombreAtributoMaestro);
      if (attr) attr.valor = variante.identidad_variante;
    });
  }

  // 💎 Función auxiliar para metales
  private aplicarColorSegunMaterial(variante: Variante): void {
    const material = (variante.identidad_variante || '').toLowerCase();
    if (material.includes('oro amarillo')) variante.hex_identidad = '#FFD700';
    else if (material.includes('oro rosa')) variante.hex_identidad = '#B76E79';
    else if (material.includes('plata') || material.includes('platino') || material.includes('acero')) {
      variante.hex_identidad = '#E5E4E2';
    } else {
      variante.hex_identidad = '#FFFFFF';
    }
  }


  
onSubmit(): void {
  if (!this.validarFormulario()) return;

  this.isSubmitting = true;

  const formData = this.construirFormData();

  if (this.isEditMode && this.productoId) {
    // 🟠 MODO EDICIÓN -> PUT
    this.productsService.editarProducto(this.productoId, formData).subscribe({
      next: (data: any) => {
        this.isSubmitting = false;
        
        // ✨ LA MAGIA DE LA REDIRECCIÓN
        // Cambia '/productos/detalle' por la ruta real que uses en tu app-routing para ver un producto
        this.router.navigate(['/detail-product/', this.productoId]); 
      },
      error: (err) => {
        this.isSubmitting = false;
        // ✨ ESTO TE DIRÁ EXACTAMENTE QUÉ CAMPO FALLÓ EN EL BACKEND
        const detalleError = err.error?.detail || err.message;
        console.error('Error al crear:', detalleError);
        alert('Hubo un error al crear el producto: ' + detalleError);
      }
    });

  } else {
    // 🟢 MODO CREACIÓN -> POST
    this.productsService.crearProducto(formData).subscribe({
      next: (data: any) => {
        this.isSubmitting = false;
        
        // ✨ REDIRECCIÓN AL CREAR
        // Ojo: asegúrate de que tu backend devuelve el ID del nuevo producto en "data.producto_id" o "data.id"
        const nuevoId = data.producto_id || data.id;
        if (nuevoId) {
          this.router.navigate(['/detail-product/', nuevoId]);
        } else {
          // Si el back no devuelve el ID, lo mandamos a la lista general
          this.router.navigate(['/view-products']); 
        }
      },
      error: (err) => {
        this.isSubmitting = false;
        // ✨ ESTO TE DIRÁ EXACTAMENTE QUÉ CAMPO FALLÓ EN EL BACKEND
        const detalleError = err.error?.detail || err.message;
        console.error('Error al crear:', detalleError);
        alert('Hubo un error al crear el producto: ' + detalleError);
      }
    });
  }
}
  guardarBorrador(): void { console.log('Borrador guardado'); }
}