import { Component } from '@angular/core';
import { SearchComponent } from './components/search/search';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [SearchComponent],
  template: `
    <div style="padding: 20px;">
      <h1 style="text-align: center; font-family: system-ui; color: #333;">🎬 azureSQLSeries v3.0</h1>
      <app-search></app-search>
    </div>
  `
})
export class App {} // <-- ¡El cambio está aquí (App en lugar de AppComponent)!