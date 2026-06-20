from fastapi import FastAPI
from auth_routes import auth_router #roteador de rotas de autenticação
from order_routes import order_router # roteador de rotas de pedidos
from lojas_router import loja_router # roteador de rotas de lojas
from estoque_router import estoque_router # roteador de rotas de estoque
from usuario_routes import usuario_router # roteador de rotas de usuarios (cadastro/login)
app = FastAPI()
#só incluindo as rotas
app.include_router(auth_router) # inclui as rotas de autenticação
app.include_router(order_router) # inclui as rotas de pedidos
app.include_router(loja_router) # inclui as rotas de lojas
app.include_router(estoque_router) # inclui as rotas de estoque
app.include_router(usuario_router) # inclui as rotas de usuarios

@app.get("/")
async def home ():
    return {"message": "Bem-vindo à API de gerenciamento de estoque!"}