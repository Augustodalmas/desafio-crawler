FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/

ENV TZ=America/Sao_Paulo

RUN apt-get update && \
    apt-get install -y wkhtmltopdf

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

CMD ["python", "crawler.py"]