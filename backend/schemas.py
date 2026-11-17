from pydantic import BaseModel, Field
from typing import Optional

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=2, description="Descripción o tipo de serie que busca el usuario")
    top_k: int = Field(default=3, ge=1, le=10, description="Cantidad de recomendaciones a devolver")

class ShowItem(BaseModel):
    id: int
    title: str
    genre: str
    release_year: int
    synopsis: str
    affinity_pct: Optional[float] = None