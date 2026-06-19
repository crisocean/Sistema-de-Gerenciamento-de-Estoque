from fastapi import APIRouter
from database import execute_query
from pydantic import BaseModel
from fastapi import HTTPException
from typing import Optional

order_router = APIRouter(prefix="/orders", tags=["produtos"])

class ProdutoNovo (BaseModel):
    id_categoria: int
    nome_produto: str
    descricao: str
    marca: str
    preco_venda: float
    preco_produto: float
    status_produto: str
    
    
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
    if not produto_encontrado:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    return{
        "status" : "sucesso",
        "produto" : produto_encontrado
    }

@order_router.post("/")
def criar_produtos(produto : ProdutoNovo):
    sql = """
        INSERT INTO produtos (
            id_categoria, nome_produto, descricao, marca, 
            preco_venda, preco_produto, status_produto
        ) VALUES (%s, %s, %s, %s, %s, %s, %s);
    """
    
    valores = (
        produto.id_categoria, 
        produto.nome_produto, 
        produto.descricao, 
        produto.marca, 
        produto.preco_venda, 
        produto.preco_produto, 
        produto.status_produto
    )
    
    execute_query(sql,valores)
    
    return{
        "status" : "sucesso",
        "mensagem" : f"Produto {produto.nome_produto} cadastrado com sucesso"
    }
#rota de atualização de produto
@order_router.put("/{id_produto}") #recebe o id do produto para a alteração
def atualizar_produto(id_produto : int, produto : ProdutoNovo): #define os parametros, id do produto e os atributos do produto na classe
    sql = """
        UPDATE produtos 
        SET id_categoria = %s, nome_produto = %s, descricao = %s, 
        marca = %s, preco_venda = %s, preco_produto = %s, status_produto = %s
        WHERE id_produto = %s;
    """
    
    valores = (
        produto.id_categoria, 
        produto.nome_produto, 
        produto.descricao, 
        produto.marca, 
        produto.preco_venda, 
        produto.preco_produto, 
        produto.status_produto,
        id_produto 
    )
    
    execute_query(sql,valores)

    return{
        "status" : "sucesso",
        "mensagem" : f"Produto {produto.nome_produto} foi atualizado com sucesso"
    }
    
@order_router.delete("/{id_produto}")
def deletar_produto (id_produto : int):
    sql = """ 
    UPDATE produtos 
    SET status_produto = 'indisponivel' 
    WHERE id_produto = %s;
    """
    # Apenas o id_produto da URL é necessário.
    valores = (id_produto,)
    
    execute_query(sql,valores)
    return{
        "status" : "sucesso",
        "mensagem" : f"Produto com ID {id_produto} foi desativado com sucesso"
    }
    

