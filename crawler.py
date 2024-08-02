"""
Este script realiza o scraping de dados do site http://quotes.toscrape.com criando assim um arquivos
Json, CSV e armazenando os dados dentro de um banco PostgresSQL, os arquivos vão para a pasta Dados_Gerados
Caso não tenha, o script já cria para o usuário.
Rodando o script é gerado uma prova de consulta dentro da pasta Screenshots.

Funcionalidades:
-Extração de dados da URL selecionada utilizando a biblioteca beautifulsoup4, criando as pastas caso necessário
com o OS, gerando provas de consulta em pdf com PDFKIT e criando os logs com o logging
-Salva os arquivos em Json
-Salva os arquivos em CSV
-Sistema de agendamento de execução do script, configurado dentro do arquivo .env

Requisitos:
-pandas
-requests
-schedule
-beautifulsoup4
-python-dotenv
-pdfkit

Uso:
- Script utilizado para realização de web scraping do site quotes.toscrape.com e armazenando os dados para analise

Autor: Augusto Rodolpho Dalmas
Data: 01/08/2024
"""
import json
import logging
import os
import time
from datetime import datetime
import requests
import pandas as pd
from bs4 import BeautifulSoup
import schedule
from dotenv import load_dotenv
import pdfkit
from database import insert_citacoes, view_pandas


load_dotenv()  # Carregar variáveis do arquivo .env

logging.basicConfig(  # Configuração do Logging
    level=logging.INFO,  # Dizendo que todos os niveis de logging devem ser mostrados
    filename='logs_do_sistema.log',  # Nome do arquivo de logs
    format='%(asctime)s - %(filename)s - %(levelname)s - %(message)s',  # Formato dos registros de log
    datefmt='%Y-%m-%d %H:%M:%S')  # Formato da data que será armazenada


def extrair_dados_citacoes(base_url, total_paginas):
    """
    Extrai dados de citações do site quotes.toscrape.com e salva provas de consulta em PDF.

    Args:
        base_url (str): URL base do site para scraping.
        total_paginas (int): Número total de páginas para raspar.

    Returns:
        list: Lista de dicionários contendo as citações.
    """
    total_citacao = []  # Inicializa a lista para armazenar todas as citações
    for pagina in range(1, total_paginas + 1):
        url = f"{base_url}/page/{pagina}"
        resposta = requests.get(url)
        resposta.raise_for_status()  # Garante que a requisição foi bem-sucedida
        soup = BeautifulSoup(resposta.text, 'html.parser')

        if not os.path.exists('Screenshots'):  # Caso não exista a pasta Screenshots
            os.makedirs('Screenshots')  # Será criada
            logging.info("Diretorio de Screenshots foi criado com sucesso!")

        logging.info(f'Conteudo da pagina {pagina} salvo para a url {url}')
        pdfkit.from_url(url, f'Screenshots/prova_consulta_page_{pagina}.pdf')  # Transforma a URL em PDF

        tempo_inicial = time.time()  # Inicia o tempo do scraping

        citacoes = soup.find_all(class_='quote')  # Encontra todas as citações na página
        dados = []
        for citacao in citacoes:
            texto = citacao.find(class_='text').get_text(strip=True)
            autor = citacao.find(class_='author').get_text(strip=True)
            tags = [tag.get_text(strip=True) for tag in citacao.find_all(class_='tag')]
            dados.append({
                'texto': texto,
                'autor': autor,
                'tags': tags
            })

        tempo_final = time.time()  # Finaliza o tempo de scraping
        duracao = tempo_final - tempo_inicial
        duracao_final = round(duracao, 4)
        logging.info(f'A raspagem da pagina {pagina} demorou {duracao_final} segundos')
        total_citacao.extend(dados)

    logging.info('Raspagem concluida')
    return total_citacao


def salvar_em_json(dados):
    """
    Salva os dados extraídos em um arquivo JSON.

    Args:
        dados (list): Lista de dicionários contendo as citações.
    """
    dados_json = json.dumps(dados, ensure_ascii=False, indent=4)  # Transforma total_citacao em uma string Json
    try:
        if not os.path.exists('Dados_gerados'):  # Caso não exista a pasta Dados_gerados
            os.makedirs('Dados_gerados')  # Será criado
            logging.info("Diretorio de Dados_gerados foi criado com sucesso!")
        with open("Dados_gerados/citacoes_json.json", "w", encoding="utf-8") as f:  # Abre o arquivo JSON
            f.write(dados_json)  # Escreve os dados em formato JSON dentro do arquivo.
        logging.info('Arquivo Json gerado com sucesso!')
    except Exception as e:
        logging.error(f'Arquivo Json não foi gerado conforme esperado. {e}')


def salvar_em_csv(dados):
    """
    Salva os dados extraídos em um arquivo CSV.

    Args:
        dados (list): Lista de dicionários contendo as citações.
    """
    try:
        lista_citacoes = []  # Cria uma lista para armazenar as citações
        for citacao in dados:
            lista_citacoes.append({  # Adiciona cada citação como um dicionário à lista
                "Citacao": citacao["texto"],
                "Autor": citacao["autor"],
                "Tags": ", ".join(citacao["tags"])  # Converte a lista de tags em uma string separada por vírgulas
            })

        tabela = pd.DataFrame(lista_citacoes)  # Converte a lista de dicionários em um DataFrame
        tabela.to_csv("Dados_gerados/citacoes_csv.csv", index=False)   # Escreve o DataFrame para um arquivo CSV
        logging.info('Arquivo Csv gerado com sucesso!')
    except Exception as e:
        logging.error(f'O arquivo Json não foi gerado conforme esperado! {e}')


def executar_script():
    """
    Função principal para executar o script de scraping, salvar os dados em JSON e CSV, e armazenar no banco de dados.
    """
    base_url = "http://quotes.toscrape.com"
    total_paginas = 10  # Define o número total de páginas que você deseja raspar
    total_citacao = extrair_dados_citacoes(base_url, total_paginas)
    salvar_em_json(total_citacao)
    salvar_em_csv(total_citacao)
    insert_citacoes(total_citacao)
    view_pandas()


def agendar_script(hora):
    """
    Agenda a execução do script para um horário específico.

    Args:
        hora (str): Horário no formato HH:MM para executar o script.
    """
    schedule.every().day.at(hora).do(executar_script)


def rodar_agendamento():
    """
    Mantém o agendamento rodando continuamente.
    """
    while True:
        schedule.run_pending()
        time.sleep(1)


def main():
    """
    Função principal que verifica se deve agendar o script ou executá-lo imediatamente.
    """
    # Verificar se deve agendar o script
    verifica_agendamento = os.getenv('VERIFICA_AGENDAMENTO', 'False') == 'True'
    if verifica_agendamento:
        hoje = datetime.now().strftime('%d/%m/%Y')
        data = os.getenv('DIA_AGENDAMENTO')
        hora = os.getenv('HORA_AGENDAMENTO')
        if hoje == data:
            agendar_script(hora)
            print(f"Script agendado para rodar no dia {data} às {hora}.")
            rodar_agendamento()

        else:
            print("A data selecionado está no passado, troque a data no arquivo .env e suba novamente o docker.")
    else:
        print("Execução automática.")
        executar_script()


if __name__ == "__main__":
    main()
