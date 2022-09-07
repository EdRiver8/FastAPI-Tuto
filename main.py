# 1: Instalar fastAPI = pip install "fastapi[all]", incluye uvicorn
# Iniciar el servidor: uvicorn main:app --reload

from typing_extensions import Required
from fastapi import FastAPI, Query, Path, Body, status, Form, File, UploadFile
from enum import Enum
from typing import Union
from pydantic import BaseModel, Field, HttpUrl, EmailStr

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
# @app.get("/items/{item_id}")
# async def read_item(item_id: str, q: Union[str, None] = None, short: bool = False):
#     item = {"item_id": item_id}
#     if q:
#         item.update({"q": q})
#     if not short:
#         item.update(
#             {"description": "This is an amazing item that has a long description"}
#         )
#     return item

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
# @app.post("/items/")
# async def create_item(item: Item):
#     item_dict = item.dict()
#     if item.tax:
#         price_with_tax = item.price + item.tax
#         item_dict.update({"price_with_tax": price_with_tax})
#     return item_dict

@app.put("/items/{item_id}")
async def create_item(item_id: int, item: Item):
    return {"item_id": item_id, **item.dict()}

# @app.put("/items/{item_id}")
# async def create_item(item_id: int, item: Item, q: str | None = None):
#     result = {"item_id": item_id, **item.dict()}
#     if q:
#         result.update({"q": q})
#     return result


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


# Validaciones para los path params =>
@app.get("/items/{item_id}")
async def read_items(
    item_id: int = Path(default= Required, title="The ID of the item to get"),
    q: str | None = Query(default=None, alias="item-query"),
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results

@app.put("/items/{item_id}")
async def update_item(
    *,
    item_id: int = Path(default=Required, title="The ID of the item to get", ge=0, le=1000),
    q: str | None = None,
    item: Item | None = None,
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    if item:
        results.update({"item": item})
    return results

class User(BaseModel):
    username: str
    full_name: str | None = None
    
# @app.put("/items/{item_id}")
# async def update_item(item_id: int, item: Item, user: User):
#     results = {"item_id": item_id, "item": item, "user": user}
#     return results
# {
#     "item": {
#         "name": "Foo",
#         "description": "The pretender",
#         "price": 42.0,
#         "tax": 3.2
#     },
#     "user": {
#         "username": "dave",
#         "full_name": "Dave Grohl"
#     }
# }

# si requiere un parametro adicional que no esta definido en una clase usa 'Body()'
# @app.put("/items/{item_id}")
# async def update_item(item_id: int, item: Item, user: User, importance: int = Body()):
#     results = {"item_id": item_id, "item": item, "user": user, "importance": importance}
#     return results
# {
#     "item": {
#         "name": "Foo",
#         "description": "The pretender",
#         "price": 42.0,
#         "tax": 3.2
#     },
#     "user": {
#         "username": "dave",
#         "full_name": "Dave Grohl"
#     },
#     "importance": 5
# }


# Validacion por medio de las clases con Pyudantic y BaseModel =>
# class Item2(BaseModel):
#     name: str
#     description: str | None = Field(
#         default=None, title="The description of the item", max_length=300
#     )
#     price: float = Field(gt=0, description="The price must be greater than zero")
#     tax: float | None = None
#     tags: list[str] = []


# @app.put("/items/{item_id}")
# async def update_item(item_id: int, item: Item2):
#     results = {"item_id": item_id, "item": item}
#     return results


# usando un subModelo como tipo de atributo de otro modelo
# class Image(BaseModel):
#     url: str
#     name: str

# class Item3(BaseModel):
#     name: str
#     description: str | None = None
#     price: float
#     tax: float | None = None
#     tags: set[str] = set()
#     image: Image | None = None

# @app.put("/items/{item_id}")
# async def update_item(item_id: int, item: Item3):
#     results = {"item_id": item_id, "item": item}
#     return results
# {
#     "name": "Foo",
#     "description": "The pretender",
#     "price": 42.0,
#     "tax": 3.2,
#     "tags": ["rock", "metal", "bar"],
#     "image": {
#         "url": "http://example.com/baz.jpg",
#         "name": "The Foo live"
#     }
# }

class Image(BaseModel):
    url: HttpUrl # tipo dato exotico de pydantic
    name: str


class Item4(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()
    images: list[Image] | None = None


# @app.put("/items/{item_id}")
# async def update_item(item_id: int, item: Item4):
#     results = {"item_id": item_id, "item": item}
#     return results
# {
#     "name": "Foo",
#     "description": "The pretender",
#     "price": 42.0,
#     "tax": 3.2,
#     "tags": [
#         "rock",
#         "metal",
#         "bar"
#     ],
#     "images": [
#         {
#             "url": "http://example.com/baz.jpg",
#             "name": "The Foo live"
#         },
#         {
#             "url": "http://example.com/dave.jpg",
#             "name": "The Baz"
#         }
#     ]
# }

class Offer(BaseModel):
    name: str
    description: str | None = None
    price: float
    items: list[Item]
    
@app.post("/offers/")
async def create_offer(offer: Offer):
    return offer

# Definir el ejemplo de los datos =>
# class Item5(BaseModel):
#     name: str
#     description: str | None = None
#     price: float
#     tax: float | None = None

#     class Config:
#         schema_extra = {
#             "example": {
#                 "name": "Foo",
#                 "description": "A very nice Item",
#                 "price": 35.4,
#                 "tax": 3.2,
#             }
#         }

# o de otra manera =>
class Item5(BaseModel):
    name: str = Field(example="Foo")
    description: str | None = Field(default=None, example="A very nice Item")
    price: float = Field(example=35.4)
    tax: float | None = Field(default=None, example=3.2)

# @app.put("/items/{item_id}")
# async def update_item(item_id: int, item: Item5):
#     results = {"item_id": item_id, "item": item}
#     return results


# response model =>
class Item6(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: list[str] = []


@app.post("/items6/", response_model=Item6)
async def create_item(item: Item):
    return item

class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr
    full_name: str | None = None
    
class UserOut(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None
    
# # Don't do this in production!
# @app.post("/user/", response_model=UserIn)
# async def create_user(user: UserIn):
#     return user
# se retorna un usuario de salida sin la clave
@app.post("/user/", response_model=UserOut)
async def create_user(user: UserIn):
    return user


class Item7(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float = 10.5
    tags: list[str] = []


items7 = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2},
    "baz": {"name": "Baz", "description": None, "price": 50.2, "tax": 10.5, "tags": []},
}

# con 'response_model_exclude_unset' los datos default no se envian a db ni response
@app.get("/items7/{item_id}", response_model=Item7, response_model_exclude_unset=True)
async def read_item(item_id: str):
    return items7[item_id]

class Item8(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float = 10.5


items8 = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The Bar fighters", "price": 62, "tax": 20.2},
    "baz": {
        "name": "Baz",
        "description": "There goes my baz",
        "price": 50.2,
        "tax": 10.5,
    },
}

@app.get(
    "/items8/{item_id}/name",
    response_model=Item8,
    response_model_include={"name", "description"},
)
async def read_item_name(item_id: str):
    return items8[item_id]


@app.get("/items8/{item_id}/public", response_model=Item8, response_model_exclude={"tax"})
async def read_item_public_data(item_id: str):
    return items8[item_id]


# manejor de form y codigos de status, los atributos name del html deben llamarse igual
# que los argumentos de funcion del metodo http
@app.post("/login/", status_code=status.HTTP_201_CREATED)
async def login(username: str = Form(default=None), password: str = Form(default=None)):
    return {"username": username}

@app.post("/files/")
async def create_file(file: bytes | None = File(default=None)):
    return {"file_size": len(file)}

# preferiblemente usar 'UploadFile' tiene mas ventajas sonbre el otro https://fastapi.tiangolo.com/es/tutorial/request-files/
@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile | None = None):
    return {"filename": file.filename}