# API de biblioteca

Esta API permite consultar, agregar, actualizar y borrar libros.
Los libros se guardan en el archivo `datos/libros.json`.

## Instalar y ejecutar

1_ Abre la carpeta del proyecto en Visual Studio Code y selecciona TERMINAL

2_
    A- Ejecuta los comandos desde esa terminal:
        pip install fastapi
        `pip install` descarga e instala FastAPI y el comando que permite iniciarlo.

    B- Luego ejecuta:
        fastapi dev main.py

Este comando inicia la API. Abre `http://127.0.0.1:8000/docs` en el navegador
para probar sus rutas.

Para probar el post puedes usar este libro:
{
  "titulo": "La sombra del viento",
  "autor": "Carlos Ruiz Zafón",
  "anio": 2001,
  "disponible": true
}