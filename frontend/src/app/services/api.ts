import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

// Definimos exactamente lo mismo que en backend/schemas.py
export interface ShowItem {
  id: number;
  title: string;
  genre: string;
  release_year: number;
  synopsis: string;
  affinity_pct?: number;
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private http = inject(HttpClient);
  private baseUrl = 'http://127.0.0.1:8000/api';

  // Llama al GET /api/shows
  getCatalog(): Observable<ShowItem[]> {
    return this.http.get<ShowItem[]>(`${this.baseUrl}/shows`);
  }

  // Llama al POST /api/search
  searchSemantic(queryText: string, topK: number = 3): Observable<ShowItem[]> {
    return this.http.post<ShowItem[]>(`${this.baseUrl}/search`, {
      query: queryText,
      top_k: topK
    });
  }
}