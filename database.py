import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import os

#configurando o logs
if not os.path.exists('logs'):
    os.makedirs('logs')
    
logging.basicConfig(filename='logs/database.log', 
level=logging.ERROR,
format='%(asctime)s - %(levelname)s - %(message)s',
datefmt='%Y-%m-%d %H:%M:%S')

#credenciais do banco postgres
db_config = {
    "host": "localhost",
    "database": "postgres",
    "user": "postgres",
    "password": "12344321"
}

def consulta_produtos():
    conn = None
    try:
        conn = psycopg2.connect(**db_config)
        
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            query_sql = "SELECT id_produto, nome_produto, preco_venda FROM produtos;"
            cur.execute(query_sql)
            resultados = cur.fetchall()
            print("Resultados da consulta:")
            for linha in resultados:
                return resultados

    except Exception as erro:
        logging.error(f"Erro ao acessar o banco de dados: {erro}", exc_info=True)
        if conn:
            conn.rollback()
    
        print("\n[!] Ocorreu um erro no banco de dados.")
        print("Os detalhes técnicos foram salvos em 'logs/database.log'.")
        raise erro
    
    finally:
        if conn:
            conn.close()   
            print("\nConexão com o banco de dados encerrada.")