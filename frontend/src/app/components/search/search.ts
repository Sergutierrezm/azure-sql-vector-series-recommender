import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ApiService, ShowItem } from '../../services/api';
import { CatalogComponent } from '../catalog/catalog';

@Component({
  selector: 'app-search',
  standalone: true,
  imports: [FormsModule, CatalogComponent], // <-- 2. Añádelo a los imports
  templateUrl: './search.html',
  styleUrls: ['./search.css']
})

export class SearchComponent {
  private api = inject(ApiService);

  searchQuery: string = '';
  results: ShowItem[] = [];
  isLoading: boolean = false;
  hasSearched: boolean = false;

  onSearch() {
    if (!this.searchQuery.trim()) return;

    this.isLoading = true;
    this.hasSearched = true;
    this.results = [];

    // Llamamos al FastAPI
    this.api.searchSemantic(this.searchQuery).subscribe({
      next: (data) => {
        this.results = data;
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Error conectando con FastAPI:', err);
        this.isLoading = false;
      }
    });
  }
}