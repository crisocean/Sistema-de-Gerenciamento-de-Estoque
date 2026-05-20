from fastapi import FastAPI
from auth_routes import auth_router #roteador de rotas de autenticação
from order_routes import order_router # roteador de rotas de pedidos

app = FastAPI()
#só incluindo as rotas
app.include_router(auth_router) # inclui as rotas de autenticação
app.include_router(order_router) # inclui as rotas de pedidos

@app.get("/")
async def home ():
    return {"message": "Bem-vindo à API de gerenciamento de estoque!"}