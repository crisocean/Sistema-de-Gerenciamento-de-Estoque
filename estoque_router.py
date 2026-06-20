from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from database import execute_query

# Mesmo padrão de prefixo isolado já usado em lojas_router.py
estoque_router = APIRouter(prefix="/estoque", tags=["estoque"])


class EstoqueNovo(BaseModel):
    """Vincula um produto a uma loja, com saldo inicial."""
    id_loja: int
    id_produto: int
    quantidade: int = 0
    quantidade_minima: int = 0


class MovimentoEstoque(BaseModel):
    """Usado nas rotas de entrada/saída. O valor é sempre positivo;
    quem decide se soma ou subtrai é a rota chamada, não o payload."""
    quantidade: int = Field(gt=0, description="Quantidade a movimentar, sempre positiva")


@estoque_router.post("/")
def criar_estoque(estoque: EstoqueNovo):
    """
    Cria o vínculo inicial entre um produto e uma loja.
    A constraint UNIQUE (id_loja, id_produto) do banco impede duplicidade;
    convertendo isso para um 409 em vez de deixar o erro cru subir.
    """
    sql = """
        INSERT INTO estoque (id_loja, id_produto, quantidade, quantidade_minima)
        VALUES (%s, %s, %s, %s);
    """
    valores = (estoque.id_loja, estoque.id_produto, estoque.quantidade, estoque.quantidade_minima)

    try:
        execute_query(sql, valores)
    except Exception as erro:
        codigo = getattr(erro, "pgcode", None)
        if codigo == "23505":
            raise HTTPException(status_code=409, detail="Este produto já está cadastrado nesta loja.")
        if codigo == "23503":
            raise HTTPException(status_code=404, detail="Loja ou produto informado não existe.")
        raise HTTPException(status_code=500, detail="Erro ao registrar estoque.")

    return {
        "status": "sucesso",
        "mensagem": f"Produto {estoque.id_produto} vinculado à loja {estoque.id_loja}."
    }


@estoque_router.get("/loja/{id_loja}")
def listar_estoque_por_loja(id_loja: int):
    """Lista todos os produtos e saldos disponíveis numa loja específica."""
    sql = """
        SELECT e.id_estoque, e.id_produto, p.nome_produto,
               e.quantidade, e.quantidade_minima, e.ultima_atualizacao
        FROM estoque e
        JOIN produtos p ON p.id_produto = e.id_produto
        WHERE e.id_loja = %s
        ORDER BY p.nome_produto;
    """
    resultado = execute_query(sql, (id_loja,))
    return {"status": "sucesso", "estoque": resultado}


@estoque_router.get("/produto/{id_produto}")
def listar_estoque_por_produto(id_produto: int):
    """Lista em quais lojas um produto está disponível e em qual quantidade."""
    sql = """
        SELECT e.id_estoque, e.id_loja, l.nome_loja,
               e.quantidade, e.quantidade_minima, e.ultima_atualizacao
        FROM estoque e
        JOIN lojas l ON l.id_loja = e.id_loja
        WHERE e.id_produto = %s
        ORDER BY l.nome_loja;
    """
    resultado = execute_query(sql, (id_produto,))
    return {"status": "sucesso", "estoque": resultado}


@estoque_router.put("/{id_estoque}/entrada")
def registrar_entrada(id_estoque: int, movimento: MovimentoEstoque):
    """
    Entrada de mercadoria: soma a quantidade recebida ao saldo atual e
    grava o histórico na MESMA instrução (CTE de escrita). Assim, saldo
    e log nunca ficam dessincronizados — ou os dois são salvos, ou nenhum.
    """
    sql = """
        WITH atualizacao AS (
            UPDATE estoque
            SET quantidade = quantidade + %s, ultima_atualizacao = CURRENT_TIMESTAMP
            WHERE id_estoque = %s
            RETURNING id_estoque, quantidade AS saldo_novo
        )
        INSERT INTO movimentacoes_estoque (id_estoque, tipo_movimento, quantidade, saldo_anterior, saldo_novo)
        SELECT id_estoque, 'entrada', %s, saldo_novo - %s, saldo_novo
        FROM atualizacao
        RETURNING id_estoque, saldo_anterior, saldo_novo;
    """
    valores = (movimento.quantidade, id_estoque, movimento.quantidade, movimento.quantidade)
    resultado = execute_query(sql, valores)

    if not resultado:
        raise HTTPException(status_code=404, detail="Registro de estoque não encontrado.")

    return {
        "status": "sucesso",
        "mensagem": "Entrada registrada com sucesso.",
        "saldo_atual": resultado[0]["saldo_novo"],
    }


@estoque_router.put("/{id_estoque}/saida")
def registrar_saida(id_estoque: int, movimento: MovimentoEstoque):
    """
    Saída de mercadoria: subtrai do saldo atual e grava o histórico na
    mesma instrução. A trava de saldo continua na cláusula WHERE do
    UPDATE ("quantidade >= %s"): se ela não encontrar linha, o CTE não
    produz resultado, e o INSERT do histórico (que depende dele) também
    não executa — update e log vivem ou morrem juntos.
    """
    sql = """
        WITH atualizacao AS (
            UPDATE estoque
            SET quantidade = quantidade - %s, ultima_atualizacao = CURRENT_TIMESTAMP
            WHERE id_estoque = %s AND quantidade >= %s
            RETURNING id_estoque, quantidade AS saldo_novo
        )
        INSERT INTO movimentacoes_estoque (id_estoque, tipo_movimento, quantidade, saldo_anterior, saldo_novo)
        SELECT id_estoque, 'saida', %s, saldo_novo + %s, saldo_novo
        FROM atualizacao
        RETURNING id_estoque, saldo_anterior, saldo_novo;
    """
    valores = (movimento.quantidade, id_estoque, movimento.quantidade, movimento.quantidade, movimento.quantidade)
    resultado = execute_query(sql, valores)

    if not resultado:
        # Pode ser ID inexistente OU saldo insuficiente — checamos qual dos
        # dois casos é, só para devolver uma mensagem de erro mais precisa.
        existe = execute_query("SELECT quantidade FROM estoque WHERE id_estoque = %s;", (id_estoque,))
        if not existe:
            raise HTTPException(status_code=404, detail="Registro de estoque não encontrado.")
        raise HTTPException(
            status_code=400,
            detail=f"Saldo insuficiente. Disponível: {existe[0]['quantidade']}, solicitado: {movimento.quantidade}."
        )

    return {
        "status": "sucesso",
        "mensagem": "Saída registrada com sucesso.",
        "saldo_atual": resultado[0]["saldo_novo"],
    }