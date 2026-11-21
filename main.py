from fastapi import FastAPI

from rutas_libros import router

app = FastAPI()
app.include_router(router)
