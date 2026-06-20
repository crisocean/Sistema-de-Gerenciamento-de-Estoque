from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from database import execute_query  # Importa o seu executor de banco

# Aqui está o segredo: um prefixo limpo e exclusivo para as lojas
loja_router = APIRouter(prefix="/lojas", tags=["lojas"])

class LojaNova(BaseModel):
    id_empresa: int
    nome_loja: str
    endereco_loja: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    telefone: Optional[str] = None
    status_loja: str = "ativa"

@loja_router.post("/")
def criar_loja(loja: LojaNova):
    sql = """
        INSERT INTO lojas (
            id_empresa, nome_loja, endereco_loja, cidade, estado, telefone, status_loja
        ) VALUES (%s, %s, %s, %s, %s, %s, %s);
    """
    valores = (
        loja.id_empresa, 
        loja.nome_loja, 
        loja.endereco_loja, 
        loja.cidade, 
        loja.estado, 
        loja.telefone, 
        loja.status_loja
    )
    execute_query(sql, valores)
    return {"status": "sucesso", "mensagem": f"Loja {loja.nome_loja} cadastrada!"}

@loja_router.get("/")
def listar_lojas():
    sql = "SELECT id_loja, nome_loja, cidade, status_loja FROM lojas WHERE status_loja = 'ativa';"
    lojas_listadas = execute_query(sql)
    return {"status": "sucesso", "lojas": lojas_listadas}

@loja_router.put("/{id_loja}")
def atualizar_loja(id_loja: int, loja: LojaNova):
    sql = """
        UPDATE lojas
        SET id_empresa = %s, nome_loja = %s, endereco_loja = %s,
        cidade = %s, estado = %s, telefone = %s, status_loja = %s
        WHERE id_loja = %s;
    """
    valores = (
        loja.id_empresa, loja.nome_loja, loja.endereco_loja,
        loja.cidade, loja.estado, loja.telefone, loja.status_loja,
        id_loja
    )
    execute_query(sql, valores)
    return {"status": "sucesso", "mensagem": f"Loja {loja.nome_loja} atualizada com sucesso"}
    
@loja_router.delete("/{id_loja}")
def inativar_loja(id_loja: int):
    sql = "UPDATE lojas SET status_loja = 'inativa' WHERE id_loja = %s;"
    execute_query(sql, (id_loja,))
    return {"status": "sucesso", "mensagem": f"Loja com ID {id_loja} foi inativada com sucesso"}
    