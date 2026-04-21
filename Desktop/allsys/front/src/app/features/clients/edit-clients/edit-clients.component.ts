// import { Component, OnInit } from '@angular/core';
// import { CommonModule } from '@angular/common';
// import { FormsModule } from '@angular/forms';
// import { ActivatedRoute, Router } from '@angular/router';
// import { ClientesService, ClienteData } from '../../../core/services/clientes.service';

// @Component({
//   selector: 'app-edit-clients',
//   standalone: true,
//   imports: [CommonModule, FormsModule],
//   templateUrl: './edit-clients.component.html',
//   styleUrl: './edit-clients.component.css'
// })
// export class EditClientsComponent implements OnInit {
//   clienteId!: number; 
//   cargando: boolean = true;
//   isSubmitting: boolean = false;

//   listaPaises = [
//     { nombre: 'España', bandera: '🇪🇸' },
//     { nombre: 'Francia', bandera: '🇫🇷' },
//     { nombre: 'Italia', bandera: '🇮🇹' },
//     { nombre: 'Portugal', bandera: '🇵🇹' },
//     { nombre: 'Bélgica', bandera: '🇧🇪' },
//     { nombre: 'Alemania', bandera: '🇩🇪' },
//     { nombre: 'Países Bajos', bandera: '🇳🇱' },
//     { nombre: 'Reino Unido', bandera: '🇬🇧' },
//     { nombre: 'Luxemburgo', bandera: '🇱🇺' },
//     { nombre: 'Otros', bandera: '🌍' }
//   ];

//   cliente: ClienteData = {
//     nombre: '',
//     apellidos: '',
//     email: '',
//     telefono: '',
//     usuario_vinted: '',
//     usuario_wallapop: '',
//     dni_nie: '',
//     direccion: '',
//     ciudad: '',
//     codigo_postal: '',
//     provincia: '',
//     pais: 'España',
//     notas_internas: '',
//     es_vip: false
//   };

//   constructor(
//     private clientesService: ClientesService,
//     private route: ActivatedRoute,
//     private router: Router
//   ) {}

//   ngOnInit(): void {
//     const idParam = this.route.snapshot.paramMap.get('id');
//     if (idParam) {
//       this.clienteId = Number(idParam);
//       this.cargarDatosCliente();
//     } else {
//       this.volver();
//     }
//   }

//   cargarDatosCliente() {
//     this.cargando = true;
//     this.clientesService.obtenerClientePorId(this.clienteId).subscribe({
//       next: (data) => {
//         this.cliente = { ...this.cliente, ...data };
//         this.cargando = false;
//       },
//       error: (err) => {
//         console.error('Error al cargar cliente:', err);
//         alert('❌ No se pudo cargar la información del cliente.');
//         this.volver();
//       }
//     });
//   }

//   actualizarCliente() {
//     if (!this.cliente.nombre?.trim() && !this.cliente.usuario_vinted?.trim()) {
//       alert('⚠️ Se necesita al menos el Nombre o el Usuario de Vinted.');
//       return;
//     }

//     this.isSubmitting = true;

//     // Limpieza de datos antes de enviar
//     const datosAEnviar = { ...this.cliente };
//     if (datosAEnviar.usuario_vinted) datosAEnviar.usuario_vinted = datosAEnviar.usuario_vinted.replace('@', '').trim();
//     if (datosAEnviar.usuario_wallapop) datosAEnviar.usuario_wallapop = datosAEnviar.usuario_wallapop.replace('@', '').trim();

//     this.clientesService.actualizarCliente(this.clienteId, datosAEnviar).subscribe({
//       next: () => {
//         alert('✅ Datos actualizados con éxito.');
//         this.isSubmitting = false;
//         this.volver();
//       },
//       error: (err) => {
//         alert('❌ Error: ' + (err.error?.detail || 'No se pudo guardar.'));
//         this.isSubmitting = false;
//       }
//     });
//   }

//   desactivar() {
//     const confirmar = confirm(`¿Quieres desactivar a ${this.cliente.nombre}?\nSeguirá en la base de datos pero no aparecerá en el día a día.`);
    
//     if (confirmar) {
//       this.isSubmitting = true;
//       this.clientesService.desactivarCliente(this.clienteId).subscribe({
//         next: () => {
//           alert('✅ Cliente desactivado.');
//           this.volver();
//         },
//         error: () => {
//           alert('❌ Hubo un error al intentar desactivar.');
//           this.isSubmitting = false;
//         }
//       });
//     }
//   }

//   volver() {
//     this.router.navigate(['/clientes']);
//   }
// }