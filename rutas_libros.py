import json
import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import ValidationError

from modelos import Libro, LibroEntrada, LibroPatch

# Logger para mostrar avisos desde este archivo.
logger = logging.getLogger(__name__)
router = APIRouter()

#Ruta principal
@router.get("/")
def inicio():
    return {"mensaje": "API de la biblioteca"}

#Crea la carpeta de datos y carga los libros guardados
CARPETA_DATOS = Path(__file__).parent / "datos"
CARPETA_DATOS.mkdir(exist_ok=True)
ARCHIVO_LIBROS = CARPETA_DATOS / "libros.json"

def cargar_libros():
    try:
        with ARCHIVO_LIBROS.open("r") as archivo:
            datos = json.load(archivo)

        if not isinstance(datos, list):
            raise TypeError("El contenido debe ser una lista de libros")

        return [Libro(**item) for item in datos]
    except FileNotFoundError:
        return []
    except (ValueError, TypeError, ValidationError) as error:
        # Avisa si falla la lectura, es mejor que print y no detiene el programa
        logger.warning(
            f"No se pudieron cargar los libros desde {ARCHIVO_LIBROS}: {error}"
        )
        # %s es un marcador donde recibe el primer valor y el segundo %s es otro marcador donde recibe el segundo valor
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
@router.get("/libros")
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

#Ruta para agregar mas libros
@router.post("/libros", status_code=201)
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
    guardar_datos()
    return nuevo_libro

#Ruta para buscar libros por texto en el titulo o autor
@router.get("/libros/buscar")
def buscar_libros(texto: str = Query(...)):
    texto_buscado = texto.lower()
    return [
        libro for libro in libros
        if texto_buscado in libro.titulo.lower()
        or texto_buscado in libro.autor.lower()
    ]

@router.get("/libros/{id}")
def obtener_libro(id: int):
    for libro in libros:
        if libro.id == id:
            return libro
    raise HTTPException(
        status_code=404,
        detail=f"No se encontró el libro con id {id}"
    )

#Ruta para eliminar un libro por id
@router.delete("/libros/{id}")
def borrar_libro(id: int):
    for libro in libros:
        if libro.id == id:
            libros.remove(libro)
            guardar_datos()
            return Response(status_code=204)
    raise HTTPException(
        status_code=404,
        detail=f"No se pudo eliminar: no existe un libro con id {id}"
    )

#Ruta para reemplazar un libro completo por su id
@router.put("/libros/{id}")
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
@router.patch("/libros/{id}")
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

