import { Component, OnInit, ViewChild, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { StatisticsService } from '../../core/services/statistics.service';
import { Chart, registerables } from 'chart.js';

@Component({
  selector: 'app-statistics',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './statistics.component.html',
  styleUrls: ['./statistics.component.css']
})
export class StatisticsComponent implements OnInit {
  @ViewChild('vendedoresCanvas') vCanvas!: ElementRef;
  @ViewChild('canalesCanvas') cCanvas!: ElementRef;

  fechaInicio: string = new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().split('T')[0];
  fechaFin: string = new Date().toISOString().split('T')[0];
  
  // Control de las 3 pestañas
  activeTab: 'financiero' | 'inversion' | 'proveedores' = 'financiero';

  // Variables para guardar los datos de cada endpoint de forma independiente
  stats: any = null;             // Datos pestaña 1 (Flujo de Caja)
  statsInversion: any = null;    // Datos pestaña 2 (Compras Globales)
  statsProveedores: any = null;  // Datos pestaña 3 (Ranking Proveedores)
  
  cargando = true;
  private charts: any[] = [];

  constructor(private statsService: StatisticsService) {
    Chart.register(...registerables);
  }

  ngOnInit() { 
    this.cargarDatos(); 
  }

  cambiarPestana(tab: 'financiero' | 'inversion' | 'proveedores') {
    this.activeTab = tab;
    this.cargarDatos();
  }

  cargarDatos() {
    this.cargando = true;
    
    // --- PESTAÑA 1: Flujo de Caja ---
    if (this.activeTab === 'financiero') {
      this.statsInversion = null; 
      this.statsProveedores = null; 
      
      this.statsService.obtenerEstadisticas(this.fechaInicio, this.fechaFin).subscribe({
        next: (data) => {
          this.stats = data;
          this.cargando = false;
          this.inicializarGraficas();
        },
        error: (err) => {
          console.error("Error cargando finanzas:", err);
          this.cargando = false;
        }
      });
    } 
    
    // --- PESTAÑA 2: Rendimiento de Compras ---
    else if (this.activeTab === 'inversion') {
      this.stats = null; 
      this.statsProveedores = null; 
      
      this.statsService.obtenerRendimientoCompras(this.fechaInicio, this.fechaFin).subscribe({
        next: (data) => {
          this.statsInversion = data.analisis_inversion;
          this.cargando = false;
        },
        error: (err) => {
          console.error("Error cargando inversiones:", err);
          this.cargando = false;
        }
      });
    }

    // --- PESTAÑA 3: Análisis de Proveedores ---
    else if (this.activeTab === 'proveedores') {
      this.stats = null; 
      this.statsInversion = null; 
      
      this.statsService.obtenerRendimientoProveedores(this.fechaInicio, this.fechaFin).subscribe({
        next: (data) => {
          // Guardamos el array del ranking que nos devuelve el backend
          this.statsProveedores = data.ranking_proveedores;
          this.cargando = false;
        },
        error: (err) => {
          console.error("Error cargando proveedores:", err);
          this.cargando = false;
        }
      });
    }
  }

  inicializarGraficas() {
    // Solo dibujamos gráficas si estamos en la pestaña financiera y hay datos
    if (this.activeTab !== 'financiero' || !this.stats) return;

    setTimeout(() => {
      this.charts.forEach(c => c.destroy());
      this.charts = [];

      if (!this.vCanvas || !this.cCanvas) return;

      const vChart = new Chart(this.vCanvas.nativeElement, {
        type: 'bar',
        data: {
          labels: this.stats.vendedores.map((v: any) => v.nombre),
          datasets: [{
            label: 'Ventas €',
            data: this.stats.vendedores.map((v: any) => v.total),
            backgroundColor: 'var(--primary)' // Usamos tu variable CSS
          }]
        },
        options: { responsive: true, maintainAspectRatio: false }
      });

      const cChart = new Chart(this.cCanvas.nativeElement, {
        type: 'doughnut',
        data: {
          labels: this.stats.canales.map((c: any) => c.nombre),
          datasets: [{
            data: this.stats.canales.map((c: any) => c.total),
            backgroundColor: ['var(--primary)', '#27ae60', '#e74c3c', '#f1c40f']
          }]
        },
        options: { responsive: true, maintainAspectRatio: false }
      });

      this.charts.push(vChart, cChart);
    }, 300);
  }
}