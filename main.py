from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def inicio():
    return {"mensaje": "Bienvenido a la API de la biblioteca"}

class Libro:
    def __init__(self, id: int, titulo: str, autor: str, anio: int, disponible: bool):
        self.id = id
        self.titulo = titulo
        self.autor = autor
        self.anio = anio
        self.disponible = disponible

libros = []

@app.get("/libros")
def obtener_libros():
    return libros

