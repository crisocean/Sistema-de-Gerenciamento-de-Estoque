from fastapi import APIRouter
from database import consulta_produtos

order_router = APIRouter(prefix="/orders", tags=["produtos"])

@order_router.get("/")

async def listar_produtos():
    produtos = consulta_produtos()
    """Rota de produtos"""
    return {"message": "Você acessou a rota de produtos", "autenticado": False, "produtos": produtos}