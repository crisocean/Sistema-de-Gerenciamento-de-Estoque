from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import os
import bcrypt
import jwt
from database import execute_query

usuario_router = APIRouter(prefix="/usuarios", tags=["usuarios"])

SECRET_KEY = os.getenv("JWT_SECRET_KEY")


class UsuarioNovo(BaseModel):
    nome_usuario: str
    email: str
    senha_usuario: str
    id_lojas: Optional[int] = None
    nivel_acesso: int = 1


class LoginData(BaseModel):
    email: str
    senha: str


# ---------------------------------------------------------
# CADASTRO
# ---------------------------------------------------------
@usuario_router.post("/cadastro")
def cadastrar_usuario(usuario: UsuarioNovo):
    """Cadastra um usuário, guardando só o hash bcrypt da senha."""
    senha_hash = bcrypt.hashpw(usuario.senha_usuario.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    sql = """
        INSERT INTO usuarios (nome_usuario, email, senha_usuario, id_lojas, nivel_acesso)
        VALUES (%s, %s, %s, %s, %s);
    """
    valores = (usuario.nome_usuario, usuario.email, senha_hash, usuario.id_lojas, usuario.nivel_acesso)

    try:
        execute_query(sql, valores)
    except Exception as erro:
        if getattr(erro, "pgcode", None) == "23505":
            raise HTTPException(status_code=409, detail="Este e-mail já está cadastrado.")
        raise HTTPException(status_code=500, detail="Erro ao cadastrar usuário.")

    return {"status": "sucesso", "mensagem": f"Usuário {usuario.nome_usuario} cadastrado com sucesso."}


# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------
@usuario_router.post("/login")
def fazer_login(login_data: LoginData):
    # 1. Busca o usuário pelo email
    sql = "SELECT id_usuario, senha_usuario, nivel_acesso FROM usuarios WHERE email = %s"
    resultado = execute_query(sql, (login_data.email,))
    if not resultado:
        # Nunca diga "email não existe" — diga sempre a mesma mensagem genérica,
        # senão um atacante descobre quais emails estão cadastrados por tentativa.
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")
    usuario = resultado[0]

    # 2. Verifica a senha usando bcrypt diretamente (mesma lib do cadastro,
    # evitando o conflito de versão entre passlib e bcrypt)
    senha_correta = bcrypt.checkpw(
        login_data.senha.encode("utf-8"),
        usuario["senha_usuario"].encode("utf-8")
    )
    if not senha_correta:
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")

    # 3. Senha bateu — gera o JWT
    dados_cracha = {
        "sub": str(usuario["id_usuario"]),
        "nivel_acesso": usuario["nivel_acesso"],
        "exp": datetime.utcnow() + timedelta(hours=8)
    }
    token = jwt.encode(dados_cracha, SECRET_KEY, algorithm="HS256")

    return {
        "status": "sucesso",
        "mensagem": "Login aprovado",
        "access_token": token
    }