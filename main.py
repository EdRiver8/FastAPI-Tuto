# 1: Instalar fastAPI = pip install "fastapi[all]", incluye uvicorn
# Iniciar el servidor: uvicorn main:app --reload

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello cold world!"}