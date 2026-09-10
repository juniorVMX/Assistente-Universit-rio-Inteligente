# 🤖 Assistente Universitário Inteligente

Sistema de Inteligência Artificial Generativa desenvolvido como projeto prático da disciplina de **Sistemas Inteligentes**.

A aplicação permite que o usuário interaja com um assistente baseado em **Llama 3**, utilizando uma API própria desenvolvida em **FastAPI** e uma interface web desenvolvida em **Streamlit**.

O sistema integra diferentes fontes de dados, permitindo trabalhar com:

* 📄 Arquivos PDF utilizando RAG;
* 📊 Planilhas Excel;
* 🗄️ Banco de dados MySQL;
* 💬 Histórico de conversas utilizando PostgreSQL;
* 🧠 Inteligência Artificial Generativa local;
* 🔎 Busca semântica em documentos;
* 🐳 Containerização com Docker e Docker Compose.

O projeto foi desenvolvido priorizando o uso de ferramentas locais e de código aberto, sem dependência de APIs pagas de modelos de Inteligência Artificial.

---

## 📌 Objetivo

O objetivo do projeto é desenvolver uma aplicação capaz de utilizar Inteligência Artificial Generativa para interagir com diferentes fontes de conhecimento.

O usuário pode enviar documentos, consultar informações estruturadas e realizar perguntas em linguagem natural.

A aplicação identifica o tipo de informação necessária para responder à pergunta e direciona a solicitação para o mecanismo apropriado.

### Principais possibilidades

```text
Pergunta do usuário
        │
        ▼
Classificação da pergunta
        │
 ┌──────┼────────┬────────┐
 ▼      ▼        ▼        ▼
PDF   MySQL    Excel    Geral
 │      │        │        │
 ▼      ▼        ▼        ▼
RAG   SQL      Dados    Llama 3
 │      │        │        │
 └──────┴────────┴────────┘
              │
              ▼
          Resposta
```

---

# 🏗️ Arquitetura

A aplicação utiliza uma arquitetura baseada em serviços.

```text
┌─────────────────────────────────────────────────────┐
│                    USUÁRIO                          │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│                 STREAMLIT                           │
│                 Container agente                    │
│                 Porta 8501                          │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│                    FASTAPI                          │
│                 API própria                         │
│                 Porta 8000                          │
└───────────────┬───────────────┬─────────────────────┘
                │               │
                │               │
        ┌───────▼───────┐ ┌─────▼─────────┐
        │     MySQL     │ │  PostgreSQL   │
        │  Dados SQL    │ │   Histórico   │
        └───────────────┘ └───────────────┘
                │
                │
        ┌───────▼────────────────────────┐
        │             RAG                │
        │                                │
        │ PDF → Chunks → Embeddings      │
        │              ↓                 │
        │           ChromaDB             │
        │              ↓                 │
        │      Busca semântica           │
        └───────────────┬────────────────┘
                        │
                        ▼
              ┌──────────────────┐
              │      Ollama      │
              │     Llama 3      │
              │    all-minilm    │
              └──────────────────┘
```

---

# 🧰 Tecnologias utilizadas

## Linguagem

* **Python 3.12**

## Interface

* **Streamlit**

## API

* **FastAPI**
* **Uvicorn**

## Inteligência Artificial

* **Ollama**
* **Llama 3**
* **all-MiniLM**
* **LangChain**

## RAG

* **LangChain Text Splitters**
* **Ollama Embeddings**
* **ChromaDB**
* **Busca semântica por similaridade**

## Documentos

* **PyPDF**
* **PyPDFLoader**
* **Pandas**
* **OpenPyXL**

## Bancos de dados

* **MySQL 8.4**
* **PostgreSQL 16**
* **ChromaDB**

## Infraestrutura

* **Docker**
* **Docker Compose**

---

# ✨ Funcionalidades

## 💬 Chat com Inteligência Artificial

O usuário pode realizar perguntas em linguagem natural através da interface Streamlit.

As respostas são produzidas pelo modelo **Llama 3**, executado localmente através do Ollama.

---

## 📄 Processamento de PDF

O usuário pode enviar um arquivo PDF pela interface.

O sistema:

1. Recebe o arquivo;
2. Processa o documento;
3. Extrai o texto;
4. Divide o conteúdo em partes menores;
5. Gera embeddings;
6. Armazena os vetores no ChromaDB;
7. Permite realizar perguntas sobre o conteúdo.

---

# 🔎 RAG — Retrieval-Augmented Generation

O sistema utiliza **RAG (Retrieval-Augmented Generation)** para responder perguntas relacionadas aos documentos enviados.

O RAG evita que o sistema precise enviar todo o conteúdo do PDF ao modelo de linguagem.

Em vez disso, o documento é processado e transformado em representações vetoriais.

### Fluxo do RAG

```text
                 PDF
                  │
                  ▼
            PyPDFLoader
                  │
                  ▼
          Extração do texto
                  │
                  ▼
       Divisão em pequenos chunks
                  │
                  ▼
         Modelo de embeddings
            all-MiniLM
                  │
                  ▼
             ChromaDB
                  │
                  │
          Usuário faz pergunta
                  │
                  ▼
        Busca por similaridade
                  │
                  ▼
       Trechos mais relevantes
                  │
                  ▼
              Llama 3
                  │
                  ▼
              Resposta
```

### Por que utilizar RAG?

O RAG permite que o modelo utilize informações específicas presentes nos documentos fornecidos pelo usuário.

Isso reduz a necessidade de colocar documentos inteiros no prompt e permite trabalhar melhor com documentos maiores.

Além disso, o modelo não precisa ser treinado novamente para cada documento.

---

# 🧠 Modelo de Inteligência Artificial

O projeto utiliza o **Llama 3**, executado localmente através do **Ollama**.

O Ollama não é executado dentro dos containers Docker. Ele permanece instalado no sistema operacional e disponibiliza o modelo para a API através da rede.

A comunicação ocorre utilizando:

```text
http://host.docker.internal:11434
```

Essa decisão permite manter o modelo de IA separado dos containers da aplicação.

### Modelos utilizados

```text
llama3
all-minilm
```

O `llama3` é responsável pela geração das respostas.

O `all-minilm` é utilizado para gerar os embeddings necessários ao mecanismo RAG.

---

# 🗄️ MySQL

O sistema possui integração com um banco de dados MySQL.

Banco utilizado:

```text
meu_banco
```

Usuário:

```text
agente
```

O projeto utiliza uma tabela de exemplo chamada:

```text
alunos
```

com as seguintes colunas:

```text
id
nome
curso
idade
```

A Inteligência Artificial pode transformar perguntas feitas em linguagem natural em consultas SQL.

### Exemplo

Pergunta:

```text
Quais alunos fazem Engenharia da Computação?
```

Fluxo:

```text
Pergunta
   ↓
Llama 3
   ↓
Geração de SELECT
   ↓
Validação da consulta
   ↓
MySQL
   ↓
Resultado
   ↓
Llama 3
   ↓
Resposta em linguagem natural
```

---

# 🔐 Segurança das consultas SQL

Para evitar alterações indevidas no banco de dados, o sistema possui uma função de validação das consultas SQL.

A consulta precisa começar com:

```sql
SELECT
```

Além disso, comandos de alteração são bloqueados.

Entre os comandos proibidos estão:

```text
INSERT
UPDATE
DELETE
DROP
ALTER
TRUNCATE
CREATE
RENAME
GRANT
REVOKE
```

Dessa forma, o assistente utiliza o MySQL prioritariamente para consultas de leitura.

---

# 📊 Excel

O sistema também permite o envio de arquivos Excel.

Os dados da planilha são processados utilizando:

* Pandas;
* OpenPyXL.

Os dados são convertidos para uma representação que pode ser enviada à API e utilizada pelo modelo para responder perguntas relacionadas à planilha.

### Exemplo

```text
Usuário envia Excel
        ↓
Pandas
        ↓
Leitura dos dados
        ↓
Conversão dos dados
        ↓
FastAPI
        ↓
Llama 3
        ↓
Resposta
```

---

# 💾 PostgreSQL

O PostgreSQL é utilizado para armazenar o histórico das conversas.

A aplicação registra:

* sessão;
* usuário;
* resposta do assistente;
* data e hora.

A tabela principal utilizada é:

```text
mensagens
```

Estrutura:

```sql
CREATE TABLE IF NOT EXISTS mensagens (
    id SERIAL PRIMARY KEY,
    sessao VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL,
    conteudo TEXT NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Isso permite manter diferentes sessões de conversa.

---

# 🐳 Docker

Os principais componentes da aplicação são executados utilizando Docker.

Containers utilizados:

```text
agente
api
mysql
postgres
```

### Containers

| Container  | Função               | Porta |
| ---------- | -------------------- | ----: |
| `agente`   | Interface Streamlit  |  8501 |
| `api`      | API FastAPI          |  8000 |
| `mysql`    | Banco de dados MySQL |  3306 |
| `postgres` | Banco de histórico   |  5432 |

O ChromaDB utiliza um volume Docker chamado:

```text
rag_data
```

montado no container da API em:

```text
/app/chroma_db
```

Dessa forma, os dados vetoriais possuem persistência através do volume Docker.

---

# 📁 Estrutura do projeto

```text
agente-de-ia/
│
├── api.py
├── app.py
├── compose.yml
├── Dockerfile
├── .gitignore
└── README.md
```

### `app.py`

Responsável pela interface do sistema utilizando Streamlit.

### `api.py`

Responsável pela API FastAPI e pela lógica principal do sistema, incluindo:

* comunicação com o Llama;
* RAG;
* processamento de PDF;
* integração com MySQL;
* integração com PostgreSQL;
* classificação das perguntas;
* processamento das respostas.

### `compose.yml`

Define os serviços Docker utilizados pelo projeto.

### `Dockerfile`

Define a imagem utilizada pelos serviços Python.

### `.gitignore`

Evita que arquivos temporários, caches e dados locais sejam enviados ao repositório.

---

# ⚙️ Requisitos

Para executar o projeto, é necessário possuir:

* Linux, Windows ou macOS;
* Docker;
* Docker Compose;
* Ollama;
* modelo Llama 3;
* modelo de embeddings `all-minilm`.

É recomendado possuir pelo menos **16 GB de RAM** para uma utilização confortável dos modelos locais.

---

# 🧠 Instalação do Ollama

O Ollama deve ser instalado no sistema operacional e não dentro do Docker.

Depois da instalação, baixe os modelos:

```bash
ollama pull llama3
```

```bash
ollama pull all-minilm
```

Verifique os modelos instalados:

```bash
ollama list
```

O resultado deverá apresentar os modelos utilizados pelo projeto.

---

# 🚀 Executando o projeto

Clone o repositório:

```bash
git clone <URL_DO_REPOSITORIO>
```

Entre na pasta:

```bash
cd agente-de-ia
```

Construa e inicialize os containers:

```bash
docker compose -f compose.yml up -d --build
```

Verifique os containers:

```bash
docker compose -f compose.yml ps
```

Todos os serviços principais deverão estar em execução.

---

# 🌐 Acessando a aplicação

Depois de iniciar os containers, a interface pode ser acessada em:

```text
http://localhost:8501
```

A API FastAPI pode ser acessada em:

```text
http://localhost:8000
```

A documentação interativa da API está disponível em:

```text
http://localhost:8000/docs
```

O endpoint de verificação da API:

```text
http://localhost:8000/health
```

---

# 🔌 Endpoints da API

## `GET /health`

Verifica se a API está funcionando.

Resposta esperada:

```json
{
  "status": "online",
  "servico": "API Assistente Universitário",
  "versao": "1.0.0"
}
```

---

## `GET /conversas`

Retorna as conversas existentes.

---

## `GET /conversas/{sessao}`

Retorna o histórico de uma sessão específica.

---

## `POST /chat`

Processa uma mensagem enviada pelo usuário.

A API identifica o tipo da pergunta e direciona o processamento para:

```text
MYSQL
PDF
EXCEL
GERAL
```

---

## `POST /upload/pdf`

Recebe um arquivo PDF e realiza o processamento necessário para disponibilizá-lo no sistema RAG.

---

# 🔄 Classificação das perguntas

Antes de processar determinadas perguntas, o sistema identifica a categoria da solicitação.

As categorias utilizadas são:

```text
MYSQL
PDF
EXCEL
GERAL
```

### MYSQL

Utilizada quando a pergunta depende dos dados armazenados no banco MySQL.

### PDF

Utilizada quando a resposta depende do conteúdo do documento enviado.

Nesse caso, o sistema utiliza o RAG.

### EXCEL

Utilizada quando a pergunta depende dos dados da planilha enviada.

### GERAL

Utilizada para perguntas que não dependem de uma fonte de dados específica.

---

# 🧪 Exemplos de utilização

## Pergunta geral

```text
O que é Inteligência Artificial Generativa?
```

Processamento:

```text
GERAL → Llama 3
```

---

## Pergunta sobre PDF

Depois de enviar um documento:

```text
Qual é o objetivo apresentado no documento?
```

Processamento:

```text
PDF
 ↓
ChromaDB
 ↓
Busca semântica
 ↓
Trechos relevantes
 ↓
Llama 3
```

---

## Pergunta sobre MySQL

```text
Quais alunos possuem mais de 20 anos?
```

Processamento:

```text
MYSQL
 ↓
Llama 3
 ↓
SELECT
 ↓
Validação
 ↓
MySQL
 ↓
Resultado
 ↓
Llama 3
```

---

## Pergunta sobre Excel

```text
Qual é o maior valor apresentado na planilha?
```

Processamento:

```text
EXCEL
 ↓
Dados da planilha
 ↓
Llama 3
 ↓
Resposta
```

---

# 🔄 Persistência

O projeto utiliza volumes Docker para manter os dados dos bancos.

Volumes:

```text
postgres_data
mysql_data
rag_data
```

Eles são utilizados respectivamente para:

```text
postgres_data → histórico das conversas
mysql_data    → banco MySQL
rag_data      → banco vetorial ChromaDB
```

Isso permite que os dados continuem disponíveis mesmo após a recriação dos containers, desde que os volumes não sejam removidos.

---

# 🛑 Parando a aplicação

Para parar os containers:

```bash
docker compose -f compose.yml down
```

Para iniciar novamente sem reconstruir:

```bash
docker compose -f compose.yml up -d
```

Para reconstruir a aplicação após alterações no código:

```bash
docker compose -f compose.yml up -d --build
```

---

# 🧹 Removendo os containers e volumes

⚠️ O comando abaixo também remove os volumes e, consequentemente, os dados persistidos:

```bash
docker compose -f compose.yml down -v
```

Utilize somente quando for necessário recriar completamente o ambiente.

---

# 🔒 Observações de segurança

As credenciais presentes no `compose.yml` são destinadas ao ambiente local de desenvolvimento e demonstração acadêmica.

Em um ambiente de produção, recomenda-se:

* utilizar variáveis de ambiente;
* não versionar credenciais reais;
* utilizar senhas fortes;
* restringir acesso aos bancos;
* aplicar autenticação e autorização adequadas na API.

---

# 📚 Conceitos demonstrados

O projeto demonstra a aplicação prática de diversos conceitos relacionados à Inteligência Artificial e Engenharia de Software:

* Inteligência Artificial Generativa;
* Large Language Models (LLM);
* Retrieval-Augmented Generation (RAG);
* Embeddings;
* Busca semântica;
* Bancos vetoriais;
* Processamento de documentos;
* APIs REST;
* FastAPI;
* Streamlit;
* Integração com bancos relacionais;
* Persistência de dados;
* Containerização;
* Docker Compose;
* Processamento de dados com Python;
* Geração e validação de consultas SQL.

---

# 🎓 Contexto acadêmico

Projeto desenvolvido para a disciplina de **Sistemas Inteligentes**, com foco na aplicação prática de Inteligência Artificial Generativa, integração de dados e construção de uma aplicação capaz de utilizar documentos e bancos de dados como fontes de conhecimento.

---

# 👨‍💻 Autor

**Francisco Adriano Costa de Morais Júnior**

Engenharia da Computação — CEUMA

---

# 📄 Licença

Projeto desenvolvido para fins acadêmicos e educacionais.
