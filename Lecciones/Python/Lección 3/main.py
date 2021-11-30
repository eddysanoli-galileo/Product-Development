from enum import Enum
from typing import Optional, List
import pandas as pd
import random
import io

from fastapi import FastAPI, Response
from pydantic import BaseModel

from fastapi.responses import ORJSONResponse, UJSONResponse, RedirectResponse, \
     HTMLResponse, PlainTextResponse, StreamingResponse, FileResponse

app = FastAPI()

# =================

# NOTAS:

# Ejecutar servidor de FastAPI: uvicorn main:app --reload
# - main: Nombre del archivo py con la API
# - app: Nombre de la variable que guarda el objeto FastAPI()

# Pueden existir funciones con la misma ruta si utilizan diferentes métodos (POST y GET 
# por ejemplo)

# El orden en el que colocamos los requests abajo es importante. Si existen dos requests
# que llevan a la misma ruta, se ejecuta la primer request encontrada de arriba para abajo.

# OpenAPI: La respuesta se retorna en la forma de un JSON

# La API se autodocumenta. La documentación se puede ver de si se ingresa a:
# - localhost:8000/docs (Swagger)
# - localhost:8000/redoc (Interfaz más bonita)

# =================

# Opciones para el rol a seleccionar
class RoleName(str, Enum):
    reader = "reader"
    admin = "admin"
    writer = "writer"

# Definición de un data class:
# - Los parámetros le dicen a FastAPI el tipo de validaciones a aplicar
# - Hecho para hacer a los objetos serializables
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

# Datos de una base de datos falsa
fake_items_db = [{"item_name": "uno"}, {"item_name": "dos"}, {"item_name": "tres"}]

# =================

# Ruta Base
@app.get("/")
def root():
    return {"message": "Hello World from Eddy"}

# GET: Retorna los items de la base de datos
@app.get("/items/all", response_class=ORJSONResponse)
def read_all_items():
    return [{"item_id": "un item"}, {"item_id": "un item"}, {"item_id": "un item"}, {"item_id": "un item"},
            {"item_id": "un item"}, {"item_id": "un item"}, {"item_id": "un item"}, {"item_id": "un item"}]

# GET: Retorna los items de la base de datos
@app.get("/items/all/alternative", response_class=UJSONResponse)
def read_all_items_alternative():
    return [{"item_id": "un item"}, {"item_id": "un item"}, {"item_id": "un item"}, {"item_id": "un item"},
            {"item_id": "un item"}, {"item_id": "un item"}, {"item_id": "un item"}, {"item_id": "un item"}]


# GET: Obtiene el item 
@app.get("/items/{item_id}")
def read_item(item_id: int, query: Optional[str] = None):

    if query:
        return {"item_id": item_id, "query": query}
    else:
        return {"item_id": item_id}

# Retorna el usuario con el user ID dado
@app.get("/users/{user_id}")
def read_user(user_id: str):
    return {"user_id": user_id}

# Retorna el usuario actual
@app.get("/users/current")
def read_current_user():
    return {"user_id": "The current user"}

# GET: Retorna el rol del usuario actual
@app.get("/roles/{rolename}")
def get_role_permissions(rolename: RoleName):
    if rolename == RoleName.reader:
        return {"role": rolename, "permissions": "Read only"}
    elif rolename == RoleName.writer:
        return {"role": rolename, "permissions": "Read/Write"}
    else:
        return {"role": rolename, "permissions": "Full access"}

# GET: Obtiene un item de un usuario específico
# (Variables de Path / Parámetros de URL)
@app.get("/users/{user_id}/items/{item_id}")
def read_user_items(user_id: int, item_id: int, query: Optional[str] = None, short: Optional[bool] = False):

    item = {"item_id": item_id, "owner": user_id}

    if query:
        item.update({"query": query})

    if not short:
        item.update({"description": "Long description"})
    else:
        item.update({"description": "Short description"})

    return item

# POST: Crea un item
# (POST requests con JSON)
@app.post("/items/")
def create_item(item: Item):

    # Si no está definido el impuesto
    if not item.tax:
        item.tax = item.price * 0.12

    return {"item_id": random.randint(1,100), **item.dict()}

# PUT: Actualizar un item y mostrar sus nuevos valores
@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"msg": f"El item {item_id} fue actualizado", "item": item.dict()}


# GET: HTML
@app.get("/html", response_class = HTMLResponse)
def get_html():
    return """
    <html>
        <head>
            <title>Some title here </title>  
        </head>  
        <body>
            <h1> Look its HTML! </h1>   
        </body> 
    </html>      
    """

# GET: Response retornada en XML
@app.get("/legacy")
def get_legacy_response():
    data = """<?xml version "1.0"?>
    <shampoo>
    <Header>
        Apply shampoo here.
    </Header>
    <Body>
        You'll have to use soap here.
    </Body>
    </shampoo>
    """

    return Response(content=data, media_type="application/xml")

# GET: Plain text
@app.get("/plain", response_class = PlainTextResponse)
def get_plain_text():
    return "Hello World"

# GET: Redirigir a otro sitio web
@app.get("/redirect")
def redirect():
    return RedirectResponse("https://google.com")

# GET: Abrir un video local
@app.get("/video")
def show_video():
    video_file = open("ejemplo.mp4", mode = "rb")
    return StreamingResponse(video_file, media_type = "video/mp4")

# GET: Descargar video
# (En la práctica es igual al de abrir el video)
@app.get("/video/downloads")
def download_video():
    return FileResponse("ejemplo.mp4")

# GET: Descargar archivo CSV
@app.get("/csv")
def download_csv():
    df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})

    stream = io.StringIO()

    df.to_csv(stream, index = False)

    response = StreamingResponse(iter([stream.getvalue()]), media_type = "text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=export.csv"

    return response