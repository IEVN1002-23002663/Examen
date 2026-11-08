
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  FormBuilder,
  FormGroup,
  ReactiveFormsModule,
  Validators
} from '@angular/forms';
import { Router } from '@angular/router';
import { Pizzeria } from '../servicios/pizzeria';

@Component({
  selector: 'app-pedido',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './pedido.html',
  styleUrl: './pedido.css'
})
export class Pedido implements OnInit {

  formulario: FormGroup;

  precios: any = {
    Chica: 40,
    Mediana: 80,
    Grande: 120
  };

  constructor(
    private fb: FormBuilder,
    private pizzeria: Pizzeria,
    private router: Router
  ) {

    const hoy = new Date();

    const fecha =
      hoy.getFullYear() + '-' +
      String(hoy.getMonth() + 1).padStart(2, '0') + '-' +
      String(hoy.getDate()).padStart(2, '0');

    this.formulario = this.fb.group({
      nombre: ['', Validators.required],
      direccion: ['', Validators.required],
      telefono: ['', Validators.required],
      fecha: [fecha, Validators.required],
      tamano: ['Chica', Validators.required],
      jamon: [false],
      pina: [false],
      champinones: [false],
      cantidad: [1, [
        Validators.required,
        Validators.min(1),
        Validators.pattern(/^[1-9]\d*$/)
      ]]
    });

  }

  ngOnInit(): void {

    if (this.pizzeria.cliente.nombre) {
      this.formulario.patchValue(this.pizzeria.cliente);
    }

  }

  agregarPizza() {

    if (this.formulario.invalid) {
      alert('Completa todos los campos correctamente');
      return;
    }

    const datos = this.formulario.value;

    // Evitar registrar espacios vacíos como datos del cliente.
    const nombre = String(datos.nombre || '').trim();
    const direccion = String(datos.direccion || '').trim();
    const telefono = String(datos.telefono || '').trim();
    if (!nombre || !direccion || !telefono) {
      alert('Completa los datos del cliente correctamente');
      return;
    }

    const ingredientes: string[] = [];

    if (datos.jamon) {
      ingredientes.push('Jamon');
    }

    if (datos.pina) {
      ingredientes.push('Pina');
    }

    if (datos.champinones) {
      ingredientes.push('Champinones');
    }

    const cantidad = Number(datos.cantidad);

    const subtotal = (
      this.precios[datos.tamano] +
      ingredientes.length * 10
    ) * cantidad;

    // Guardar los datos del cliente
    this.pizzeria.cliente = {
      nombre,
      direccion,
      telefono,
      fecha: datos.fecha
    };

    // Guardar temporalmente la pizza
    this.pizzeria.agregarPizza({
      tamano: datos.tamano,
      ingredientes: ingredientes,
      cantidad: cantidad,
      subtotal: subtotal
    });

    // Ir automáticamente a Detalle
    this.router.navigate(['/pizzeria/detalle']);

  }

}
