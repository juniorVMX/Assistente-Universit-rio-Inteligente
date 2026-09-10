# FROM python:3.12-slim

# WORKDIR /app

# RUN apt-get update && apt-get install -y \
#     build-essential \
#     && rm -rf /var/lib/apt/lists/*

# COPY app.py .

# RUN pip install --no-cache-dir \
#     streamlit \
#     pandas \
#     openpyxl \
#     pypdf \
#     langchain \
#     langchain-community \
#     langchain-core \
#     langchain-ollama \
#     psycopg2-binary \
#     mysql-connector-python

# EXPOSE 8501

# CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY app.py api.py ./

RUN pip install --no-cache-dir \
    streamlit \
    fastapi \
    uvicorn \
    python-multipart \
    requests \
    pandas \
    openpyxl \
    pypdf \
    langchain \
    langchain-community \
    langchain-core \
    langchain-ollama \
    langchain-text-splitters \
    langchain-chroma \
    chromadb \
    psycopg2-binary \
    mysql-connector-python
# Ollama NÃO será instalado no Docker.
# O projeto utiliza o Ollama instalado no sistema operacional.
# Para instalar Ollama dentro do Docker, seria necessário:
# RUN curl -fsSL https://ollama.com/install.sh | sh

EXPOSE 8501 8000

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]