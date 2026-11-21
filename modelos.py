from pydantic import BaseModel, Field


#Modelo para crear los libros
class LibroEntrada(BaseModel):
    titulo: str = Field(min_length=3, max_length=100)
    autor: str = Field(min_length=3, max_length=50)
    anio: int = Field(strict=True, ge=1000, le=2100)
    disponible: bool = True


#Modelo para mostrar los libros
class Libro(LibroEntrada):
    id: int


#Modelo para actualizar una parte del libro
class LibroPatch(BaseModel):
    titulo: str | None = Field(default=None, min_length=3, max_length=100)
    autor: str | None = Field(default=None, min_length=3, max_length=50)
    anio: int | None = Field(default=None, strict=True, ge=1000, le=2100)
    disponible: bool | None = None
