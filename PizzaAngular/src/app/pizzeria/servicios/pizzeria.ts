import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Pizza {
  tamano: string;
  ingredientes: string[];
  cantidad: number;
  subtotal: number;
}

export interface ClientePedido {
  nombre: string;
  direccion: string;
  telefono: string;
  fecha: string;
}

export interface Venta {
  idpedido: number;
  idcliente?: number;
  nombre: string;
  direccion?: string;
  telefono?: string;
  fecha: string;
  total: number;
}

export interface PizzaRegistrada {
  iddetalle: number;
  tamano: string;
  ingredientes: string; // Flask lo devuelve como texto separado por comas.
  cantidad: number;
  subtotal: number;
}

export interface DetalleVenta extends Venta {
  pizzas: PizzaRegistrada[];
}

export interface RespuestaPedido {
  exito: boolean;
  mensaje: string;
  idpedido: number;
  idcliente: number;
  total: number;
}

@Injectable({ providedIn: 'root' })
export class Pizzeria {
  private readonly http = inject(HttpClient);
  private readonly url = 'http://127.0.0.1:5000/api';

  cliente: ClientePedido = { nombre: '', direccion: '', telefono: '', fecha: '' };
  pizzas: Pizza[] = [];

  agregarPizza(pizza: Pizza): void {
    this.pizzas.push(pizza);
  }

  quitarPizza(indice: number): void {
    this.pizzas.splice(indice, 1);
  }

  limpiarPedido(): void {
    this.pizzas = [];
    this.cliente = { nombre: '', direccion: '', telefono: '', fecha: '' };
  }

  getClientes(): Observable<{ exito: boolean; clientes: unknown[] }> {
    return this.http.get<{ exito: boolean; clientes: unknown[] }>(`${this.url}/clientes`);
  }

  getPedidos(): Observable<{ exito: boolean; pedidos: Venta[] }> {
    return this.http.get<{ exito: boolean; pedidos: Venta[] }>(`${this.url}/pedidos`);
  }

  agregarPedido(datos: ClientePedido & { pizzas: Omit<Pizza, 'subtotal'>[] }): Observable<RespuestaPedido> {
    return this.http.post<RespuestaPedido>(`${this.url}/pedidos`, datos);
  }

  getDetallePedido(idpedido: number): Observable<{ exito: boolean; mensaje?: string; pedido?: DetalleVenta }> {
    return this.http.get<{ exito: boolean; pedido: DetalleVenta }>(`${this.url}/pedidos/${idpedido}`);
  }

  getVentasDia(dia: string): Observable<{ exito: boolean; ventas: Venta[]; total: number }> {
    return this.http.get<{ exito: boolean; ventas: Venta[]; total: number }>(`${this.url}/ventas/dia/${encodeURIComponent(dia)}`);
  }

  getVentasMes(mes: string): Observable<{ exito: boolean; ventas: Venta[]; total: number }> {
    return this.http.get<{ exito: boolean; ventas: Venta[]; total: number }>(`${this.url}/ventas/mes/${encodeURIComponent(mes)}`);
  }
}
