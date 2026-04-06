import { Component, OnInit, ViewChild, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms'; // ✨ Necesario para los filtros [(ngModel)]
import { DashboardService } from '../../core/services/dashboard.service';
import { Chart, registerables } from 'chart.js';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule], // ✨ Importamos FormsModule aquí
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  // ✨ Acceso seguro al canvas
  @ViewChild('canvasGrafica') canvasRef!: ElementRef<HTMLCanvasElement>;
  
  // ✨ Estado de Filtros (Inicia con el mes actual)
  filtros = {
    fecha_inicio: this.getPrimerDiaMes(),
    fecha_fin: this.getFechaHoy()
  };

  resumen: any = {
    ingresos_totales: 0,
    inversion_en_stock: 0,
    gastos_operativos: 0,
    ganancia_real: 0,
    saldo_teorico_banco: 0
  };
  
  cargando = true;
  chart: any;

  constructor(private dashboardService: DashboardService) {
    // Registramos los componentes de Chart.js
    Chart.register(...registerables);
  }

  ngOnInit(): void {
    this.cargarTodo();
  }

  // ==========================================
  // HELPERS DE FECHAS
  // ==========================================
  getFechaHoy(): string {
    return new Date().toISOString().split('T')[0];
  }

  getPrimerDiaMes(): string {
    const d = new Date();
    return new Date(d.getFullYear(), d.getMonth(), 1).toISOString().split('T')[0];
  }

  // ✨ Lógica para botones de acceso rápido
  setFiltroRapido(periodo: string) {
    const hoy = new Date();
    this.filtros.fecha_fin = this.getFechaHoy();

    if (periodo === 'hoy') {
      this.filtros.fecha_inicio = this.getFechaHoy();
    } else if (periodo === 'mes') {
      this.filtros.fecha_inicio = this.getPrimerDiaMes();
    } else if (periodo === 'año') {
      this.filtros.fecha_inicio = `${hoy.getFullYear()}-01-01`;
    }
    
    this.cargarTodo();
  }

  // ==========================================
  // CARGA DE DATOS
  // ==========================================
  cargarTodo() {
    this.cargando = true;
    
    // 1. Obtener KPIs enviando los filtros actuales
    this.dashboardService.getResumen(this.filtros).subscribe({
      next: (data) => {
        this.resumen = data;
        this.cargando = false;
      },
      error: (err) => {
        console.error("❌ Error al obtener el resumen:", err);
        this.cargando = false;
      }
    });

    // 2. Obtener datos para la Gráfica (Tendencia mensual)
    this.dashboardService.getDatosGrafica().subscribe({
      next: (datos) => {
        this.inicializarGrafica(datos);
      },
      error: (err) => console.error("❌ Error en datos de gráfica:", err)
    });
  }

  // ==========================================
  // LÓGICA DE LA GRÁFICA
  // ==========================================
  inicializarGrafica(datos: any[]) {
    if (!datos || datos.length === 0) return;

    // ✨ Un solo timeout de seguridad para asegurar que el DOM y el CSS están listos
    setTimeout(() => {
      if (!this.canvasRef) return;

      const canvas = this.canvasRef.nativeElement;
      const ctx = canvas.getContext('2d');

      if (!ctx) return;

      // Destruir instancia previa si existe para evitar solapamientos
      if (this.chart) {
        this.chart.destroy();
      }

      this.chart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: datos.map(d => d.mes),
          datasets: [
            {
              label: 'Ventas (€)',
              data: datos.map(d => d.ventas),
              backgroundColor: '#007782', // Teal Vinted
              borderRadius: 5
            },
            {
              label: 'Gastos (€)',
              data: datos.map(d => d.gastos),
              backgroundColor: '#e74c3c', // Danger Red
              borderRadius: 5
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false, // 👈 Vital para respetar el alto del CSS
          animation: {
            duration: 500
          },
          plugins: {
            legend: {
              position: 'top',
              labels: {
                usePointStyle: true,
                pointStyle: 'circle'
              }
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              grid: { color: '#f0f2f5' }
            },
            x: {
              grid: { display: false }
            }
          }
        }
      });
      
      // ✨ Forzamos ajuste al contenedor
      this.chart.resize();
    }, 200); 
  }
}