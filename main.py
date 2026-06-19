from fastapi import FastAPI
from auth_routes import auth_router #roteador de rotas de autenticação
from order_routes import order_router # roteador de rotas de pedidos
from lojas_router import loja_router # roteador de rotas de lojas
app = FastAPI()
#só incluindo as rotas
app.include_router(auth_router) # inclui as rotas de autenticação
app.include_router(order_router) # inclui as rotas de pedidos
app.include_router(loja_router) # inclui as rotas de lojas

@app.get("/")
async def home ():
    return {"message": "Bem-vindo à API de gerenciamento de estoque!"}