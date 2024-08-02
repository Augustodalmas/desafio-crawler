"""
Este script realiza conexão, criação, visualização do banco e a inserção de dados.

Funcionalidades:
- Conecta ao banco de dados PostgreSQL.
- Criação da tabela no banco PostgreSQL.
- Armazena os dados extraídos em um banco de dados PostgreSQL.
- Visualiza os dados do banco juntamente a biblioteca Pandas.

Requisitos:
- pandas
- psycopg2

Uso:
- Script para fazer conexões e interagir com banco de dados.

Autor: Augusto Rodolpho Dalmas
Data: 01/08/2024
"""
import logging
import time
import os
import pandas as pd
import psycopg2


logging.basicConfig(  # Configuração do Logging
    level=logging.INFO,  # Dizendo que todos os niveis de logging devem ser mostrados
    filename='logs.log',  # Nome do arquivo de logs
    format='%(asctime)s - %(filename)s - %(levelname)s - %(message)s',  # Formato dos registros de log
    datefmt='%Y-%m-%d %H:%M:%S'  # Formato da data que será armazenada
)


def get_connection():
    """
    Faz a conexão com o banco de dados utilizando os dados fornecidos no arquivo .env

    Returns:
        connection: objeto de conexão do psycopg2 para o banco de dados PostgreSQL.
    """
    return psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )


def create_table():
    """
    Cria a tabela 'citacoes' no banco de dados PostgreSQL, se ela não existir.

    A tabela contém três colunas: id (chave primária), texto (para o conteúdo da citação) e autor (para o autor da citação).
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS citacoes(
            id SERIAL PRIMARY KEY,
            texto TEXT,
            autor TEXT
            )
            """
        )
        conn.commit()
        logging.info('Banco de dados criado com sucesso!')
    except Exception as e:
        logging.error(f'O banco de dados não conseguiu ser criado com sucesso: {e}')
    finally:
        cursor.close()
        conn.close()


def insert_citacoes(dados):
    """
    Insere uma lista de citações na tabela 'citacoes' do banco de dados PostgreSQL.

    Args:
        dados (list): Lista de dicionários, onde cada dicionário contém uma citação com as chaves 'texto' e 'autor'.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        for citacao in dados:
            cursor.execute(
                """
                INSERT INTO citacoes (texto, autor)
                VALUES (%s, %s);
                """,
                (citacao['texto'], citacao['autor'])
            )
        conn.commit()
        logging.info('Dados inseridos com sucesso no banco de dados!')
    except Exception as e:
        logging.error(f'Ocorreu um erro ao inserir os dados: {e}')
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def view_pandas():
    """
    Consulta e exibe os dados da tabela 'citacoes' do banco de dados PostgreSQL usando a biblioteca Pandas.

    A função também registra a visualização no log.
    """
    conn = get_connection()

    requisição = "SELECT * FROM citacoes LIMIT 100"
    dataframe = pd.read_sql_query(requisição, conn)
    conn.close()
    print(dataframe)
    logging.info('Vizualizacao do Dataframe.')


time.sleep(1)
create_table()