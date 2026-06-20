from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os

# HTTPBearer já sabe ler o cabeçalho "Authorization: Bearer <token>".
# Se o cabeçalho não vier, ele mesmo devolve 401 antes de chegar aqui.
security = HTTPBearer()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")


def get_usuario_atual(credenciais: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    O "porteiro": roda antes da rota que o usa.
    Pega o token do cabeçalho, confirma que foi assinado com a mesma
    SECRET_KEY (ou seja, foi gerado pelo nosso /usuarios/login) e que
    ainda não expirou. Se passar, devolve o payload do token (sub e
    nivel_acesso) para a rota usar, se precisar saber quem é o usuário.
    """
    token = credenciais.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado, faça login novamente.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido.")

    return payload