import { Component, inject, OnInit } from '@angular/core';
import { ApiService, ShowItem } from '../../services/api';

@Component({
  selector: 'app-catalog',
  standalone: true,
  templateUrl: './catalog.html',
  styleUrls: ['./catalog.css']
})
export class CatalogComponent implements OnInit {
  private api = inject(ApiService);
  
  catalog: ShowItem[] = [];
  isLoading: boolean = true;

  ngOnInit() {
    this.api.getCatalog().subscribe({
      next: (data) => {
        this.catalog = data;
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Error cargando el catálogo completo:', err);
        this.isLoading = false;
      }
    });
  }
}