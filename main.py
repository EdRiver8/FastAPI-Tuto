# 1: Instalar fastAPI = pip install "fastapi[all]", incluye uvicorn
# Iniciar el servidor: uvicorn main:app --reload

from fastapi import FastAPI, Query
from enum import Enum
from typing import Union
from pydantic import BaseModel

app = FastAPI() # instancia de fastapi

# hereda de str (valores deben ser tipo string) y Enum
class ModelName(str, Enum): 
    java = "java"
    php = "php"
    python = "python"

# de la instancia, que decorador (operador http) voy a usar y que path "/"
@app.get("/") 
async def root(): # esta funcion maneja los request que van a este path "/"
    return {"message": "Hello cold world!"}

# # path params con definicion de tipos usando hint, usar para validaciones =>
# @app.get("/items/{item_id}")
# async def read_item(item_id: int):
#     return {"item_id": item_id}

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.java:
        return {"model_name": model_name, "message": "Use Spring"}

    if model_name.value == "php":
        return {"model_name": model_name, "message": "Use Laravel"}

    return {"model_name": model_name, "message": "Use Fastapi 😁"}


# query params, no hacen parte del path, estan en key-value, van despues '?' en URl
fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]
# mostrar solo uno http://127.0.0.1:8000/items?skip=1&limit=1
# @app.get("/items")
# async def read_items(skip: int = 0, limit: int = 10): # var, tipo dato y valor defecto
#     return fake_items_db[skip : skip + limit] #desde skip hasta skip + limit

# Parametros opcionales usando None por defecto y Union o |, q = quantity
# http://127.0.0.1:8000/items/1?q=2
# @app.get("/items/{item_id}")
# async def read_item(item_id: str, q: Union[str, None] = None):
#     if q:
#         return {"item_id": item_id, "q": q}
#     return {"item_id": item_id}

# http://127.0.0.1:8000/items/foo?short=1
# http://127.0.0.1:8000/items/foo?short=true
# http://127.0.0.1:8000/items/foo?short=on
# http://127.0.0.1:8000/items/foo?short=yes
@app.get("/items/{item_id}")
async def read_item(item_id: str, q: Union[str, None] = None, short: bool = False):
    item = {"item_id": item_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item

# Multiples parametros por path y query
@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int, item_id: str, q: Union[str, None] = None, short: bool = False
):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item


# request body = data que el cliente envia al servidor
# response body = data que el servidor envia al cliente
# se debe importar BaseModel de Pydantic y crear clases desde esta = request body
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

# @app.post("/items/")
# async def create_item(item: Item):
#     return item
# {
#   "name": "Camisa",
#   "description": "En manga corta, color verde",
#   "price": 25,
#   "tax": 0.12
# }
@app.post("/items/")
async def create_item(item: Item):
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict

@app.put("/items/{item_id}")
async def create_item(item_id: int, item: Item):
    return {"item_id": item_id, **item.dict()}

@app.put("/items/{item_id}")
async def create_item(item_id: int, item: Item, q: str | None = None):
    result = {"item_id": item_id, **item.dict()}
    if q:
        result.update({"q": q})
    return result


#Usar 'Query' para realizar validaciones de datos
# @app.get("/items/")
# async def read_items(q: str | None = Query(default=None, max_length=50)):
#     results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
#     if q:
#         results.update({"q": q})
#     return results

# @app.get("/items/")
# async def read_items(q: str | None = Query(default=None, min_length=3, max_length=50)):
#     results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
#     if q:
#         results.update({"q": q})
#     return results

# @app.get("/items/")
# async def read_items(
#     q: str
#     | None = Query(default=None, min_length=3, max_length=50, regex="^fixedquery$")
# ):
#     results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
#     if q:
#         results.update({"q": q})
#     return results


# recibir una lista de multiples parametros
# @app.get("/items/")
# async def read_items(q: list[str] | None = Query(default=None)):
#     query_items = {"q": q}
#     return query_items
# http://localhost:8000/items/?q=foo&q=bar
# con valores por defecto =>
# @app.get("/items/")
# async def read_items(q: list[str] = Query(default=["foo", "bar"])):
#     query_items = {"q": q}
#     return query_items
# agregando MetaData
@app.get("/items/")
async def read_items(
    q: str
    | None = Query(
        default=None,
        alias="item-query",
        title="Query string",
        description="Query string for the items to search in the database that have a good match",
        min_length=3,
        max_length=50,
        regex="^fixedquery$",
        deprecated=True,
    )
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results