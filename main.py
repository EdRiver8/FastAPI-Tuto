# 1: Instalar fastAPI = pip install "fastapi[all]", incluye uvicorn
# Iniciar el servidor: uvicorn main:app --reload

from fastapi import FastAPI
from enum import Enum

app = FastAPI() # instancia de fastapi

# de la instancia, que decorador (operador http) voy a usar y que path "/"
@app.get("/") 
async def root(): # esta funcion maneja los request que van a este path "/"
    return {"message": "Hello cold world!"}

# path params con definicion de tipos usando hint, usar para validaciones =>
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}