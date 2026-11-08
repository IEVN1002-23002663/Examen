
import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: 'pizzeria',
    children: [
      {
        path: 'pedido',
        loadComponent: () =>
          import('./pizzeria/pedido/pedido').then(c => c.Pedido)
      },
      {
        path: 'detalle',
        loadComponent: () =>
          import('./pizzeria/detalle/detalle').then(c => c.Detalle)
      },
      {
        path: 'ventas',
        loadComponent: () =>
          import('./pizzeria/ventas/ventas').then(c => c.Ventas)
      },
      {
        path: '',
        redirectTo: 'pedido',
        pathMatch: 'full'
      }
    ]
  },
  {
    path: '',
    redirectTo: 'pizzeria/pedido',
    pathMatch: 'full'
  },
  {
    path: '**',
    redirectTo: 'pizzeria/pedido'
  }
];
