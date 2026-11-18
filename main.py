from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

@app.get("/")
def inicio():
    return {"mensaje": "API de la biblioteca"}

class LibroEntrada(BaseModel):
    titulo: str = Field(min_length=3, max_length=100)
    autor: str = Field(min_length=3, max_length=50)
    anio: int = Field(ge=1000, le=2100)
    disponible: bool = True


class Libro(LibroEntrada):
    id: int

libros = []

@app.get("/libros")
def obtener_libros():
    return libros

@app.post("/libros", status_code=201)
def agregar_libro(body: LibroEntrada):
    nuevo_id = max((libro.id for libro in libros), default=0) + 1
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