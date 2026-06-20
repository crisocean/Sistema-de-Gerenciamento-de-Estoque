from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from database import execute_query

# Cria a gaveta de rotas exclusiva para os usuários
usuario_router = APIRouter(prefix="/usuarios", tags=["usuarios"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

secret_key = "adminsab1105"

class LoginData(BaseModel):
    email: str
    senha: str
    
# ---------------------------------------------------------
# A ROTA DE LOGIN
# ---------------------------------------------------------
@usuario_router.post("/login")
def fazer_login(login_data: LoginData):
    # 1. Pede a identidade (Busca o usuário no banco pelo email)
    sql = "SELECT id_usuario, senha_usuario, nivel_acesso FROM usuarios WHERE email = %s"
    resultado = execute_query(sql, (login_data.email,))
    if not resultado:
        # Se o email não existir, barra logo de cara.
        # Dica de segurança: Nunca diga "Email não existe", diga "Email ou senha incorretos". 
        # Assim o hacker não sabe qual dos dois ele errou.
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")
    usuario = resultado[0]
    # 2. Verifica a senha (O Python bate a senha digitada no liquidificador 
    # e compara com a maçaroca salva no banco)
    senha_correta = pwd_context.verify(login_data.senha, usuario["senha_usuario"])
    if not senha_correta:
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")
    
    # 3. A SENHA BATEU! Fabrica o Crachá (JWT)
    # Aqui definimos o Payload (os dados que vão no crachá)
    dados_cracha = {
        "sub": str(usuario["id_usuario"]),        # De quem é o crachá
        "nivel_acesso": usuario["nivel_acesso"],  # O que ele pode fazer
        "exp": datetime.utcnow() + timedelta(hours=8) # O crachá se autodestrói em 8 horas
    }
    
    # O servidor assina o crachá usando a Chave Mestra
    token = jwt.encode(dados_cracha, secret_key, algorithm="HS256")
    
    # 4. Entrega o crachá para o client
    return {
        "status": "sucesso", 
        "mensagem": "Login aprovado",
        "access_token": token
    }