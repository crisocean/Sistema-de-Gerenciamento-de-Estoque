from fastapi import APIRouter

auth_router = APIRouter(prefix="/auth", tags=["login"])

@auth_router.get("/")

async def login():
    """Rota de login"""
    return {"message" : "Você está na rota de login"}