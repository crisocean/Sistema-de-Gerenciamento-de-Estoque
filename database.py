import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import os
from dotenv import load_dotenv

load_dotenv()  # precisa vir antes de ler qualquer variável com os.getenv()

#configurando o logs
if not os.path.exists('logs'):
    os.makedirs('logs')
    
logging.basicConfig(filename='logs/database.log', 
level=logging.ERROR,
format='%(asctime)s - %(levelname)s - %(message)s',
datefmt='%Y-%m-%d %H:%M:%S')

#credenciais do banco postgres, agora vindas do .env (nunca commitado)
db_config = {
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD")
}

def execute_query(query: str, params: tuple = None):
    conn = None
    try:
        conn = psycopg2.connect(**db_config)
        
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            comando = query.strip().upper()
            modifica_dados = any(palavra in comando for palavra in ("INSERT", "UPDATE", "DELETE"))

            # cur.description só vem preenchido quando o comando devolve
            # linhas (SELECT puro, ou um INSERT/UPDATE/DELETE com RETURNING
            # — inclusive dentro de um WITH, como nas rotas de estoque).
            # É mais confiável que adivinhar pela primeira palavra da query.
            if cur.description is not None:
                resultado = cur.fetchall()
            else:
                resultado = {"status": "sucesso"}

            if modifica_dados:
                conn.commit()

            return resultado


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