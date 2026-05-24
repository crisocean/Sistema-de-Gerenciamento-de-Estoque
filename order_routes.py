from fastapi import APIRouter
from database import execute_query
from pydantic import BaseModel
order_router = APIRouter(prefix="/orders", tags=["produtos"])
class ProdutoNovo (BaseModel):
    nome_produto : str
    descricao : str
    categoria : str
    marca : str
    preco_venda : float
    preco_produto : float
    status_produto : str
    data_cadastro : str
    
@order_router.get("/")  
def listar_produtos():
    """Rota de produtos"""
    sql = "SELECT id_produto, nome_produto, preco_venda FROM produtos"
    produtos_listados = execute_query(sql)
    return {"status" : "sucesso",
            "produtos" : produtos_listados}

@order_router.get("/{id_produto}")
def BuscarProduto_PorId(id_produto : int):
    """
    Rota dinâmica que busca um único produto baseado no ID enviado na URL.
    """
    sql = "SELECT id_produto, nome_produto, preco_venda FROM produtos WHERE id_produto = %s;"
    produto_encontrado = execute_query(sql,(id_produto,))
    
    return{
        "status" : "sucessso",
        "produto" : produto_encontrado
    }
    

@order_router.post("/")
def criar_produtos(produto : ProdutoNovo):
    sql = "INSERT INTO produtos (nome_produto,descricao,categoria,marca,preco_venda, preco_produto,status_produto,data_cadastro ) VALUES (%s, %s, %s, %s, %s, %s, %s);"
    
    valores = (produto.nome_produto, produto.descricao, produto.categoria, produto.marca, produto.preco_venda, produto.preco_produto, produto.status_produto, produto.data_cadastro)
    execute_query(sql,valores)
    
    return{
        "status" : "sucesso",
        "mensagem" : "Produto cadastrado com sucesso"
    }
    
    