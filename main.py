from fastapi import FastAPI

app = FastAPI()
from auth_routes import auth_router #roteador de rotas de autenticação
from order_routes import order_router # roteador de rotas de pedidos

app.include_router(auth_router) # inclui as rotas de autenticação
app.include_router(order_router) # inclui as rotas de pedidos
