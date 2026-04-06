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
  // Referencias a los diferentes Canvas
  @ViewChild('chartVendedores') chartVendedoresRef!: ElementRef<HTMLCanvasElement>;
  @ViewChild('chartCanales') chartCanalesRef!: ElementRef<HTMLCanvasElement>;

  // Filtros
  fechaInicio: string = this.getPrimerDiaMes();
  fechaFin: string = this.getFechaHoy();
  
  stats: any = null;
  cargando = true;

  // Instancias de Chart.js para destruirlas al actualizar
  private chartVendedoresInstance: any;
  private chartCanalesInstance: any;

  constructor(private statsService: StatisticsService) {
    Chart.register(...registerables);
  }

  ngOnInit(): void {
    this.cargarEstadisticas();
  }

  getFechaHoy(): string { return new Date().toISOString().split('T')[0]; }
  getPrimerDiaMes(): string {
    const d = new Date();
    return new Date(d.getFullYear(), d.getMonth(), 1).toISOString().split('T')[0];
  }

  cargarEstadisticas() {
    this.cargando = true;
    this.statsService.getDashboardCompleto(this.fechaInicio, this.fechaFin).subscribe({
      next: (data) => {
        this.stats = data;
        this.renderizarGraficas();
        this.cargando = false;
      },
      error: (err) => {
        console.error("Error cargando estadísticas", err);
        this.cargando = false;
      }
    });
  }

  renderizarGraficas() {
    // Timeout para asegurar que el DOM cargó los canvas
    setTimeout(() => {
      this.initChartVendedores();
      this.initChartCanales();
    }, 200);
  }

  initChartVendedores() {
    if (this.chartVendedoresInstance) this.chartVendedoresInstance.destroy();
    
    const ctx = this.chartVendedoresRef.nativeElement.getContext('2d');
    if (!ctx) return;

    this.chartVendedoresInstance = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: this.stats.por_vendedor.map((v: any) => v.nombre),
        datasets: [{
          label: 'Ventas Totales (€)',
          data: this.stats.por_vendedor.map((v: any) => v.total),
          backgroundColor: '#007782',
          borderRadius: 8
        }]
      },
      options: { responsive: true, maintainAspectRatio: false }
    });
  }

  initChartCanales() {
    if (this.chartCanalesInstance) this.chartCanalesInstance.destroy();
    
    const ctx = this.chartCanalesRef.nativeElement.getContext('2d');
    if (!ctx) return;

    this.chartCanalesInstance = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: this.stats.por_canal.map((c: any) => c.canal),
        datasets: [{
          data: this.stats.por_canal.map((c: any) => c.total),
          backgroundColor: ['#007782', '#27ae60', '#3498db', '#e74c3c', '#f1c40f']
        }]
      },
      options: { 
        responsive: true, 
        maintainAspectRatio: false,
        plugins: { legend: { position: 'bottom' } }
      }
    });
  }
}