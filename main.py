from fastapi import FastAPI, HTTPException, Query, Response
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


class LibroPatch(BaseModel):
    titulo: str | None = Field(default=None, min_length=3, max_length=100)
    autor: str | None = Field(default=None, min_length=3, max_length=50)
    anio: int | None = Field(default=None, strict=True, ge=1000, le=2100)
    disponible: bool | None = None

libros = []
siguiente_id_libro = 1

@app.get("/libros")
def obtener_libros(
    autor: str | None = Query(default=None),
    disponible: bool | None = Query(default=None),
    desde: int = Query(default=0, ge=0),
    limite: int = Query(default=100, ge=1, le=100)
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
    for libro in libros:
        if (
            libro.titulo.lower() == body.titulo.lower()
            and libro.autor.lower() == body.autor.lower()
        ):
            raise HTTPException(
                status_code=409,
                detail="Ya existe un libro con el mismo titulo y autor"
            )

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

@app.delete("/libros/{id}")
def borrar_libro(id: int):
    for libro in libros:
        if libro.id == id:
            libros.remove(libro)
            return Response(status_code=200)
    raise HTTPException(status_code=404, detail="Libro no encontrado")

@app.put("/libros/{id}")
def reemplazar_libro(id: int, body: LibroEntrada):
    for libro in libros:
        if libro.id == id:
            libro.titulo = body.titulo
            libro.autor = body.autor
            libro.anio = body.anio
            libro.disponible = body.disponible
            return libro
    raise HTTPException(status_code=404, detail="Libro no encontrado")


@app.patch("/libros/{id}")
def actualizar_libro(id: int, body: LibroPatch):
    for libro in libros:
        if libro.id == id:
            if body.titulo is not None:
                libro.titulo = body.titulo
            if body.autor is not None:
                libro.autor = body.autor
            if body.anio is not None:
                libro.anio = body.anio
            if body.disponible is not None:
                libro.disponible = body.disponible
            return libro
    raise HTTPException(status_code=404, detail="Libro no encontrado")


def siguiente_id():
    global siguiente_id_libro
    nuevo_id = siguiente_id_libro
    siguiente_id_libro += 1
    return nuevo_id
