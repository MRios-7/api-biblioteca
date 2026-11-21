#Importaciones
import json
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query, Response
from pydantic import BaseModel, Field, ValidationError

app = FastAPI()

#Ruta principal
@app.get("/")
def inicio():
    return {"mensaje": "API de la biblioteca"}

#Ruta para crear los libros
class LibroEntrada(BaseModel):
    titulo: str = Field(min_length=3, max_length=100)
    autor: str = Field(min_length=3, max_length=50)
    anio: int = Field(strict=True, ge=1000, le=2100) #ge= mayor o igual, le= menor o igual
    disponible: bool = True

#Ruta para mostrar los libros
class Libro(LibroEntrada):
    id: int

#Ruta para actualizar los libros (guarda de forma temporal)
class LibroPatch(BaseModel):
    titulo: str | None = Field(default=None, min_length=3, max_length=100)
    autor: str | None = Field(default=None, min_length=3, max_length=50)
    anio: int | None = Field(default=None, strict=True, ge=1000, le=2100) #Strict para que sea numero entero
    disponible: bool | None = None

#Crea la carpeta de datos y carga los libros guardados
CARPETA_DATOS = Path(__file__).parent / "datos"#Path hace que se ubique la carpeta de datos una carpeta arriba del main
CARPETA_DATOS.mkdir(exist_ok=True)#exist_ok=True, hace que no de error si ya existe la carpeta
ARCHIVO_LIBROS = CARPETA_DATOS / "libros.json" 

def cargar_libros():
    try:
        with ARCHIVO_LIBROS.open("r") as archivo:
            datos = json.load(archivo)

        if not isinstance(datos, list): #isinstance es como un if que revisa si el contenido es una lista de libros y ayuda a que
                                        #inicie la aplicacion aunque el archivo este vacio o tenga un contenido incorrecto
            raise ValueError("El contenido debe ser una lista de libros")

        return [Libro(**item) for item in datos]
    except FileNotFoundError:
        return [] #Devuelve una lista vacia para que pueda seguir funcionando aunque no exista el archivo
    except (ValueError, TypeError, ValidationError) as error:
        logging.warning("No se pudieron cargar los libros desde %s: %s", ARCHIVO_LIBROS, error)
        return []

libros = cargar_libros()
siguiente_id_libro = max((libro.id for libro in libros), default=0) + 1

#Guarda la lista actual de libros en el archivo JSON
def guardar_datos():
    with ARCHIVO_LIBROS.open("w") as archivo:
        json.dump([libro.model_dump() for libro in libros], archivo)


#Funcion para que el id de los libros sea unico y incremente sin importar que se eliminen libros
def siguiente_id():
    global siguiente_id_libro
    nuevo_id = siguiente_id_libro
    siguiente_id_libro += 1
    return nuevo_id

#Ruta para obtener los libros
@app.get("/libros")
def obtener_libros(
    autor: str | None = Query(default=None),
    disponible: bool | None = Query(default=None),
    desde: int = Query(default=0, ge=0),
    limite: int = Query(default=100, ge=1, le=100)#default es para muestre hasta 100 libros
):
    resultados = libros.copy()

#si el autor no esta vacio convierte a minusculas y revisa si hay un duplicado
    if autor is not None:
        autor_buscado = autor.lower()
        resultados = [
            libro for libro in resultados
            if libro.autor.lower() == autor_buscado
        ]
#revisa si esta disponible
    if disponible is not None:
        resultados = [
            libro for libro in resultados
            if libro.disponible == disponible
        ]

    return resultados[desde:desde + limite]

#Ruta para agregar mas libros
@app.post("/libros", status_code=201)
def agregar_libro(body: LibroEntrada):
    for libro in libros:
        if (
            libro.titulo.lower() == body.titulo.lower() #revisa si ya existe un libro con los mismos datos
            and libro.autor.lower() == body.autor.lower()
        ):
            raise HTTPException(
                status_code=409,
                detail="Ya existe un libro con el mismo titulo y autor"
            )

#Si no existe un libro igual lo crea y asigna un id
    nuevo_id = siguiente_id()
    nuevo_libro = Libro(id=nuevo_id, **body.model_dump())
    libros.append(nuevo_libro)
    guardar_datos()
    return nuevo_libro

#Ruta para buscar libros por texto en el titulo o autor
@app.get("/libros/buscar")
def buscar_libros(texto: str = Query(...)):
    texto_buscado = texto.lower()
    return [
        libro for libro in libros
        if texto_buscado in libro.titulo.lower()
        or texto_buscado in libro.autor.lower()
    ]

@app.get("/libros/{id}")
def obtener_libro(id: int):
    for libro in libros:
        if libro.id == id:
            return libro
    raise HTTPException(
        status_code=404,
        detail=f"No se encontró el libro con id {id}"
    )

#Ruta para eliminar un libro por id
@app.delete("/libros/{id}")
def borrar_libro(id: int):
    for libro in libros:
        if libro.id == id:
            libros.remove(libro)
            guardar_datos()
            return Response(status_code=200, content=f"Libro con id {id} eliminado")
    raise HTTPException(
        status_code=404,
        detail=f"No se pudo eliminar: no existe un libro con id {id}"
    )

#Ruta para reemplazar un libro completo por su id
@app.put("/libros/{id}") 
def reemplazar_libro(id: int, body: LibroEntrada):
    for libro in libros:
        if libro.id == id:
            libro.titulo = body.titulo
            libro.autor = body.autor
            libro.anio = body.anio
            libro.disponible = body.disponible
            guardar_datos()
            return libro
    raise HTTPException(
        status_code=404,
        detail=f"No se pudo reemplazar: no existe un libro con id {id}"
    )

#Ruta para actualizar una parte de un libro por su id
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
            guardar_datos()
            return libro
    raise HTTPException(
        status_code=404,
        detail=f"No se pudo actualizar: no existe un libro con id {id}"
    )