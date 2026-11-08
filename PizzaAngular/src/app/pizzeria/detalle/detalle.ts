
import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { Pizzeria } from '../servicios/pizzeria';

@Component({
  selector: 'app-detalle',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './detalle.html',
  styleUrl: './detalle.css'
})
export class Detalle {

  guardando = false;

  constructor(
    public pizzeria: Pizzeria,
    private router: Router
  ) {}

  // Calcular el total del pedido
  get total(): number {
    return this.pizzeria.pizzas.reduce(
      (suma, pizza) => suma + pizza.subtotal,
      0
    );
  }

  // Quitar una pizza del pedido
  quitarPizza(indice: number) {
    this.pizzeria.quitarPizza(indice);
  }

  // Regresar para agregar otra pizza
  agregarOtra() {
    this.router.navigate(['/pizzeria/pedido']);
  }

  // Terminar y guardar el pedido
  terminarPedido() {

    if (this.guardando) {
      return;
    }

    if (this.pizzeria.pizzas.length === 0) {
      alert('Primero agrega una pizza');
      return;
    }

    if (!this.pizzeria.cliente.nombre ||
        !this.pizzeria.cliente.direccion ||
        !this.pizzeria.cliente.telefono ||
        !this.pizzeria.cliente.fecha) {
      alert('Faltan los datos del cliente');
      this.router.navigate(['/pizzeria/pedido']);
      return;
    }

    const confirmar = confirm(
      '¿Deseas terminar el pedido?\nTotal: $' + this.total
    );

    if (!confirmar) {
      return;
    }

    const datos = {
      nombre: this.pizzeria.cliente.nombre,
      direccion: this.pizzeria.cliente.direccion,
      telefono: this.pizzeria.cliente.telefono,
      fecha: this.pizzeria.cliente.fecha,

      pizzas: this.pizzeria.pizzas.map(pizza => ({
        tamano: pizza.tamano,
        ingredientes: pizza.ingredientes,
        cantidad: pizza.cantidad
      }))
    };

    this.guardando = true;

    // Enviar el pedido a Flask
    this.pizzeria.agregarPedido(datos).subscribe({

      next: (respuesta) => {

        this.guardando = false;

        if (respuesta.exito) {

          alert(
            'Pedido registrado correctamente\n' +
            'Número de pedido: ' + respuesta.idpedido +
            '\nTotal: $' + respuesta.total
          );

          // Limpiar el pedido temporal
          this.pizzeria.limpiarPedido();

          // Ir a consultar ventas
          this.router.navigate(['/pizzeria/ventas']);

        } else {
          alert(
            respuesta.mensaje || 'No se pudo guardar el pedido'
          );
        }

      },

      error: (error) => {

        this.guardando = false;

        console.error('Error al guardar pedido:', error);

        alert(
          'Error al guardar el pedido: ' +
          (error.error?.mensaje || error.message)
        );

      }

    });

  }

}
