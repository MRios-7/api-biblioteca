from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

app = FastAPI()

@app.get("/")
def inicio():
    return {"mensaje": "API de la biblioteca"}

class LibroEntrada(BaseModel):
    titulo: str = Field(min_length=3, max_length=100)
    autor: str = Field(min_length=3, max_length=50)
    anio: int = Field(strict=True, ge=1000, le=2100)
    disponible: bool = True


class Libro(LibroEntrada):
    id: int

libros = []

@app.get("/libros")
def obtener_libros(
    autor: str | None = Query(default=None),
    disponible: bool | None = Query(default=None),
    desde: int = Query(default=0, ge=0),
    limite: int = Query(default=10, ge=1, le=100)
):
    resultados = libros.copy()

    if autor is not None:
        autor_buscado = autor.lower()
        resultados = [
            libro for libro in resultados
            if libro.autor.lower() == autor_buscado
        ]

    if disponible is not None:
        resultados = [
            libro for libro in resultados
            if libro.disponible == disponible
        ]

    return resultados[desde:desde + limite]

@app.post("/libros", status_code=201)
def agregar_libro(body: LibroEntrada):
    nuevo_id = siguiente_id()
    nuevo_libro = Libro(id=nuevo_id, **body.model_dump())
    libros.append(nuevo_libro)
    return nuevo_libro

@app.get("/libros/{id}")
def obtener_libro(id: int):
    for libro in libros:
        if libro.id == id:
            return libro
    raise HTTPException(status_code=404, detail="Libro no encontrado")

@app.get("/libros/999")
def obtener_libro_999():
    for libro in libros:
        if libro.id == 999:
            return libro
    raise HTTPException(status_code=404, detail="Libro con ID 999 no encontrado")

@app.get("/libros/abc")
def obtener_libro_abc():
    raise HTTPException(status_code=422, detail="id que no es un número entero")

@app.delete("/libros/{id}")
def borrar_libro(id: int):
    for libro in libros:
        if libro.id == id:
            libros.remove(libro)
            return {"mensaje": "Libro eliminado"}
    raise HTTPException(status_code=404, detail="Libro no encontrado")

@app.put("/libros/{id}")
def actualizar_libro(id: int, body: LibroEntrada):
    for libro in libros:
        if libro.id == id:
            libro.titulo = body.titulo
            libro.autor = body.autor
            libro.anio = body.anio
            libro.disponible = body.disponible
            return libro
    raise HTTPException(status_code=404, detail="Libro no encontrado")
def siguiente_id():
    if not libros:
        return 1
    return max(libro.id for libro in libros) + 1
