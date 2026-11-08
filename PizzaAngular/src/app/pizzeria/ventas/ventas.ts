import { ChangeDetectorRef, Component, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DetalleVenta, Pizzeria, Venta } from '../servicios/pizzeria';
import { Subscription, finalize, timeout } from 'rxjs';

@Component({
  selector: 'app-ventas',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './ventas.html',
  styleUrl: './ventas.css'
})
export class Ventas implements OnInit, OnDestroy {

  dia = 'domingo';
  mes = 'noviembre';

  ventas: Venta[] = [];
  cargando = false;
  errorVentas = "";
  total = 0;

  detalle: DetalleVenta | null = null;
  cargandoDetalle = false;
  errorDetalle = '';

  private detalleSubscription?: Subscription;

  constructor(
    private pizzeria: Pizzeria,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnDestroy(): void {
    this.detalleSubscription?.unsubscribe();
  }

  ngOnInit(): void {
    this.verTodas();
  }

  // Mostrar todas las ventas
  verTodas() {
    this.cargando = true;
    this.errorVentas = '';
    this.pizzeria.getPedidos().subscribe({
      next: (respuesta) => {
        this.cargando = false;
        this.ventas = respuesta.pedidos || [];

        this.total = this.ventas.reduce(
          (suma, venta) => suma + Number(venta.total),
          0
        );

        this.detalle = null;
        this.errorDetalle = '';
        this.cdr.markForCheck();
      },
      error: (error) => {
        this.cargando = false;
        this.errorVentas = error.error?.mensaje || 'No se pudieron cargar las ventas';
        console.error(error);
        this.cdr.markForCheck();
        alert('Error al cargar las ventas');
      }
    });
  }

  // Buscar ventas por día
  buscarDia() {
    this.cargando = true;
    this.errorVentas = '';
    this.pizzeria.getVentasDia(this.dia).subscribe({
      next: (respuesta) => {
        this.cargando = false;
        this.ventas = respuesta.ventas || [];
        this.total = Number(respuesta.total || 0);
        this.detalle = null;
        this.errorDetalle = '';
        this.cdr.markForCheck();
      },
      error: (error) => {
        this.cargando = false;
        this.errorVentas = error.error?.mensaje || 'No se pudieron cargar las ventas';
        console.error(error);
        this.cdr.markForCheck();
        alert('Error al consultar ventas por día');
      }
    });
  }

  // Buscar ventas por mes
  buscarMes() {
    this.cargando = true;
    this.errorVentas = '';
    this.pizzeria.getVentasMes(this.mes).subscribe({
      next: (respuesta) => {
        this.cargando = false;
        this.ventas = respuesta.ventas || [];
        this.total = Number(respuesta.total || 0);
        this.detalle = null;
        this.errorDetalle = '';
        this.cdr.markForCheck();
      },
      error: (error) => {
        this.cargando = false;
        this.errorVentas = error.error?.mensaje || 'No se pudieron cargar las ventas';
        console.error(error);
        this.cdr.markForCheck();
        alert('Error al consultar ventas por mes');
      }
    });
  }

  // Mostrar el detalle de una venta
  verDetalle(idpedido: number): void {
    // Cancela una consulta anterior si se abre otra venta.
    this.detalleSubscription?.unsubscribe();
    this.detalle = null;
    this.errorDetalle = '';
    this.cargandoDetalle = true;
    this.cdr.markForCheck();

    this.detalleSubscription = this.pizzeria.getDetallePedido(idpedido)
      .pipe(
        timeout({ first: 12000 }),
        finalize(() => {
          // Se ejecuta al terminar, fallar, agotar el tiempo o cancelar.
          this.cargandoDetalle = false;
          this.cdr.markForCheck();
        })
      )
      .subscribe({
        next: (respuesta) => {
          if (respuesta.exito && respuesta.pedido) {
            this.detalle = respuesta.pedido;
          } else {
            this.errorDetalle = respuesta.mensaje || 'No se encontró el pedido';
          }
          this.cdr.markForCheck();
        },
        error: (error) => {
          console.error('Error al consultar detalle:', error);
          this.errorDetalle = error?.name === 'TimeoutError'
            ? 'La consulta tardó demasiado. Revisa que Flask siga ejecutándose.'
            : error?.error?.mensaje || 'No se pudo cargar el detalle del pedido';
          this.cdr.markForCheck();
        }
      });
  }

  cerrarDetalle(): void {
    this.detalleSubscription?.unsubscribe();
    this.detalleSubscription = undefined;
    this.detalle = null;
    this.cargandoDetalle = false;
    this.errorDetalle = '';
    this.cdr.markForCheck();
  }
}
