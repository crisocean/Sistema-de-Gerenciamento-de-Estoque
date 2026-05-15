from fastapi import APIRouter

order_router = APIRouter(prefix="/orders", tags=["produtos"])

@order_router.get("/")

async def produtos():
    """Rota de produtos"""
    return {"message": "Você acessou a rota de produtos", "autenticado": False}