from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
import psycopg2
import mysql.connector
import os
import uuid


# ============================================================
# CONFIGURAÇÃO DA API
# ============================================================

app = FastAPI(
    title="API Assistente Universitário",
    description="API própria para IA generativa com Llama 3, PDF, Excel, MySQL e PostgreSQL.",
    version="1.0.0"
)


# ============================================================
# MODELO DE IA
# ============================================================

llm = ChatOllama(
    model="llama3",
    temperature=0,
    base_url="http://host.docker.internal:11434"
)
# ============================================================
# CONFIGURAÇÃO DO RAG
# ============================================================

embeddings = OllamaEmbeddings(
    model="all-minilm",
    base_url="http://host.docker.internal:11434"
)

CAMINHO_CHROMA = "/app/chroma_db"

vectorstore = Chroma(
    collection_name="documentos_pdf",
    persist_directory=CAMINHO_CHROMA,
    embedding_function=embeddings
)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150
)

# ============================================================
# CONEXÃO COM POSTGRESQL
# ============================================================

def get_postgres_connection():
    try:
        return psycopg2.connect(
            host="postgres",
            port=5432,
            database="agente",
            user="agente",
            password="agente123"
        )

    except Exception:
        return None


# ============================================================
# CONEXÃO COM MYSQL
# ============================================================

def get_mysql_connection():
    try:
        return mysql.connector.connect(
            host="mysql",
            port=3306,
            database="meu_banco",
            user="agente",
            password="agente123"
        )

    except Exception:
        return None


# ============================================================
# VALIDAÇÃO DE SQL
# ============================================================

def validar_sql(sql: str) -> bool:

    sql = sql.strip()

    if not sql:
        return False

    sql_upper = sql.upper()

    # A consulta precisa começar com SELECT
    if not sql_upper.startswith("SELECT"):
        return False

    # Não permitir múltiplas instruções
    if ";" in sql[:-1]:
        return False

    # Comandos proibidos
    comandos_proibidos = [
        "INSERT",
        "UPDATE",
        "DELETE",
        "DROP",
        "ALTER",
        "TRUNCATE",
        "CREATE",
        "RENAME",
        "GRANT",
        "REVOKE"
    ]

    for comando in comandos_proibidos:

        if comando in sql_upper:
            return False

    return True


# ============================================================
# SCHEMAS
# ============================================================

class MensagemCreate(BaseModel):

    sessao: str

    prompt: str

    texto_pdf: Optional[str] = ""

    dados_excel_json: Optional[str] = ""


class ConversaSchema(BaseModel):

    sessao: str

    ultima_mensagem: str

    criado_em: str


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "online",
        "servico": "API Assistente Universitário",
        "versao": "1.0.0"
    }


# ============================================================
# LISTAR CONVERSAS
# ============================================================

@app.get(
    "/conversas",
    response_model=List[ConversaSchema]
)
def listar_conversas():

    conn = get_postgres_connection()

    if not conn:
        raise HTTPException(
            status_code=500,
            detail="Não foi possível conectar ao PostgreSQL."
        )

    try:

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT DISTINCT ON (sessao)
                sessao,
                conteudo,
                criado_em::text
            FROM mensagens
            ORDER BY sessao, criado_em DESC
            """
        )

        conversas = cursor.fetchall()

        cursor.close()
        conn.close()

        conversas.sort(
            key=lambda x: x[2],
            reverse=True
        )

        return [
            {
                "sessao": conversa[0],
                "ultima_mensagem": conversa[1],
                "criado_em": conversa[2]
            }
            for conversa in conversas
        ]

    except Exception as e:

        conn.close()

        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar conversas: {e}"
        )


# ============================================================
# OBTER HISTÓRICO DE UMA CONVERSA
# ============================================================

@app.get("/conversas/{sessao}")
def obter_historico_conversa(sessao: str):

    conn = get_postgres_connection()

    if not conn:

        raise HTTPException(
            status_code=500,
            detail="Não foi possível conectar ao PostgreSQL."
        )

    try:

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT role, conteudo
            FROM mensagens
            WHERE sessao = %s
            ORDER BY criado_em ASC, id ASC
            """,
            (sessao,)
        )

        mensagens = cursor.fetchall()

        cursor.close()
        conn.close()

        return [
            {
                "role": mensagem[0],
                "content": mensagem[1]
            }
            for mensagem in mensagens
        ]

    except Exception as e:

        conn.close()

        raise HTTPException(
            status_code=500,
            detail=f"Erro ao carregar conversa: {e}"
        )


# ============================================================
# PROCESSAMENTO DO CHAT
# ============================================================

@app.post("/chat")
def processar_chat(dados: MensagemCreate):

    conn_pg = get_postgres_connection()

    # --------------------------------------------------------
    # SALVAR PERGUNTA DO USUÁRIO
    # --------------------------------------------------------

    if conn_pg:

        try:

            cursor = conn_pg.cursor()

            cursor.execute(
                """
                INSERT INTO mensagens
                    (sessao, role, conteudo)
                VALUES
                    (%s, %s, %s)
                """,
                (
                    dados.sessao,
                    "user",
                    dados.prompt
                )
            )

            conn_pg.commit()

            cursor.close()

        except Exception as e:

            conn_pg.rollback()

            print(
                f"Erro ao salvar pergunta no PostgreSQL: {e}"
            )

    # --------------------------------------------------------
    # MONTAR CONTEXTO
    # --------------------------------------------------------

        contexto_extra = ""

    if dados.dados_excel_json:

        contexto_extra += (
            "\n\n"
            "[DADOS DO EXCEL]\n"
            f"{dados.dados_excel_json}"
        )

    # --------------------------------------------------------
    # PROMPT
    # --------------------------------------------------------

    # ========================================================
    # IDENTIFICAR O TIPO DA PERGUNTA
    # ========================================================

    try:

        classificacao = llm.invoke(
            [
                SystemMessage(
                    content=(
                        "Classifique a pergunta do usuário em "
                        "APENAS uma destas categorias:\n\n"
                        "MYSQL\n"
                        "PDF\n"
                        "EXCEL\n"
                        "GERAL\n\n"

                        "MYSQL: perguntas sobre alunos, nomes, "
                        "cursos, idades ou dados da tabela alunos.\n"

                        "PDF: perguntas que dependem do conteúdo "
                        "do PDF enviado.\n"

                        "EXCEL: perguntas que dependem dos dados "
                        "da planilha enviada.\n"

                        "GERAL: qualquer outra pergunta.\n\n"

                        "Responda SOMENTE com uma categoria."
                    )
                ),
                HumanMessage(
                    content=dados.prompt
                )
            ]
        )

        tipo_pergunta = (
            classificacao.content
            .strip()
            .upper()
        )

    except Exception:

        tipo_pergunta = "GERAL"


    # ========================================================
    # PERGUNTA SOBRE MYSQL
    # ========================================================

    if tipo_pergunta == "MYSQL":

        prompt_sql = (
            "Você é um assistente que gera SQL para o banco "
            "de dados MySQL.\n\n"

            "Tabela disponível:\n"
            "alunos\n\n"

            "Colunas:\n"
            "- id\n"
            "- nome\n"
            "- curso\n"
            "- idade\n\n"

            "Gere SOMENTE uma consulta SELECT válida.\n"
            "Não utilize INSERT, UPDATE, DELETE, DROP, ALTER "
            "ou qualquer comando de alteração.\n\n"

            f"Pergunta do usuário:\n{dados.prompt}"
        )

        try:

            resposta = llm.invoke(
                [
                    SystemMessage(
                        content=(
                            "Gere somente uma consulta SQL "
                            "SELECT válida."
                        )
                    ),
                    HumanMessage(
                        content=prompt_sql
                    )
                ]
            )

            resposta_texto = (
                resposta.content.strip()
            )

        except Exception as e:

            resposta_texto = (
                f"Erro ao gerar SQL: {e}"
            )


       # ========================================================
    # PERGUNTA GERAL / PDF / EXCEL
    # ========================================================

    else:

        # ====================================================
        # PERGUNTA SOBRE PDF - RAG
        # ====================================================

        if tipo_pergunta == "PDF":

            try:

                # --------------------------------------------
                # BUSCAR OS TRECHOS MAIS RELEVANTES NO CHROMA
                # --------------------------------------------

                documentos_relevantes = vectorstore.similarity_search(
                    dados.prompt,
                    k=4
                )

                # --------------------------------------------
                # VERIFICAR SE ENCONTROU INFORMAÇÕES
                # --------------------------------------------

                if not documentos_relevantes:

                    resposta_texto = (
                        "Não encontrei informações relevantes "
                        "no PDF enviado."
                    )

                else:

                    # ----------------------------------------
                    # MONTAR CONTEXTO COM OS CHUNKS RECUPERADOS
                    # ----------------------------------------

                    contexto_rag = "\n\n".join(
                        documento.page_content
                        for documento in documentos_relevantes
                    )

                    # ----------------------------------------
                    # PROMPT DO RAG
                    # ----------------------------------------

                    prompt_rag = (
                        "Você é um assistente universitário "
                        "prestativo, claro e objetivo.\n\n"

                        "Responda à pergunta utilizando "
                        "somente as informações presentes "
                        "nos trechos recuperados do PDF.\n\n"

                        "Se a resposta não estiver presente "
                        "nos trechos recuperados, informe que "
                        "não encontrou essa informação no PDF.\n\n"

                        "Não invente informações.\n\n"

                        "[TRECHOS RELEVANTES DO PDF]\n"
                        f"{contexto_rag}\n\n"

                        "[PERGUNTA DO USUÁRIO]\n"
                        f"{dados.prompt}"
                    )

                    # ----------------------------------------
                    # ENVIAR CONTEXTO RECUPERADO PARA O LLAMA
                    # ----------------------------------------

                    resposta = llm.invoke(
                        [
                            SystemMessage(
                                content=(
                                    "Responda utilizando "
                                    "as informações dos "
                                    "trechos fornecidos."
                                )
                            ),
                            HumanMessage(
                                content=prompt_rag
                            )
                        ]
                    )

                    resposta_texto = (
                        resposta.content.strip()
                    )

            except Exception as e:

                resposta_texto = (
                    "Erro ao consultar o RAG: "
                    f"{e}"
                )

        # ====================================================
        # PERGUNTA GERAL OU EXCEL
        # ====================================================

        else:

            contexto = ""

            # -----------------------------------------------
            # CONTEXTO DO EXCEL
            # -----------------------------------------------

            if dados.dados_excel_json:

                contexto += (
                    "\n\n[DADOS DO EXCEL]\n"
                    f"{dados.dados_excel_json}"
                )

            # -----------------------------------------------
            # PROMPT NORMAL
            # -----------------------------------------------

            prompt_normal = (
                "Você é um assistente universitário "
                "prestativo, claro e objetivo.\n\n"

                "Responda à pergunta do usuário normalmente.\n\n"

                "Se houver dados fornecidos pelo Excel, "
                "utilize essas informações para responder.\n\n"

                "Não invente informações que não estejam "
                "nos dados fornecidos quando a pergunta "
                "depender desses dados.\n\n"

                f"Pergunta do usuário:\n"
                f"{dados.prompt}\n"

                f"{contexto}"
            )

            try:

                resposta = llm.invoke(
                    [
                        SystemMessage(
                            content=(
                                "Você é um assistente universitário "
                                "prestativo e claro. "
                                "Responda normalmente à pergunta."
                            )
                        ),
                        HumanMessage(
                            content=prompt_normal
                        )
                    ]
                )

                resposta_texto = (
                    resposta.content.strip()
                )

            except Exception as e:

                resposta_texto = (
                    f"Erro ao processar a pergunta: {e}"
                )
    # ========================================================
    # VERIFICAR SE O LLAMA GEROU SQL
    # ========================================================

    sql = resposta_texto.strip()

    # Remover possíveis blocos Markdown
    if sql.startswith("```"):

        linhas = sql.splitlines()

        linhas_filtradas = []

        for linha in linhas:

            if linha.strip().startswith("```"):
                continue

            if linha.strip().lower() == "sql":
                continue

            linhas_filtradas.append(linha)

        sql = "\n".join(
            linhas_filtradas
        ).strip()

    # ========================================================
    # EXECUTAR MYSQL
    # ========================================================

    if validar_sql(sql):

        conn_mysql = get_mysql_connection()

        if conn_mysql:

            try:

                cursor_mysql = conn_mysql.cursor()

                cursor_mysql.execute(sql)

                resultados = cursor_mysql.fetchall()

                colunas = [
                    coluna[0]
                    for coluna in cursor_mysql.description
                ]

                cursor_mysql.close()
                conn_mysql.close()

                # --------------------------------------------
                # FORMATAR RESULTADO
                # --------------------------------------------

                dados_mysql = ""

                for linha in resultados:

                    dados_mysql += (
                        str(linha) + "\n"
                    )

                if not dados_mysql:

                    dados_mysql = (
                        "A consulta não retornou resultados."
                    )

                # --------------------------------------------
                # SEGUNDA CHAMADA AO LLAMA
                # --------------------------------------------

                resposta_final = llm.invoke(
                    [
                        SystemMessage(
                            content=(
                                "Você é um assistente "
                                "universitário prestativo "
                                "e claro.\n\n"

                                "Responda à pergunta do usuário "
                                "utilizando os dados retornados "
                                "pelo banco de dados.\n\n"

                                "Não mostre a consulta SQL "
                                "ao usuário."
                            )
                        ),

                        HumanMessage(
                            content=(
                                f"Pergunta: {dados.prompt}\n\n"

                                f"Colunas: {colunas}\n\n"

                                f"Resultado do MySQL:\n"
                                f"{dados_mysql}"
                            )
                        )
                    ]
                )

                resposta_texto = (
                    resposta_final.content.strip()
                )

            except Exception as e:

                resposta_texto = (
                    "Erro ao consultar o MySQL: "
                    f"{e}"
                )

                if conn_mysql:
                    conn_mysql.close()

        else:

            resposta_texto = (
                "Não foi possível conectar ao "
                "banco de dados MySQL."
            )

    # ========================================================
    # SALVAR RESPOSTA NO POSTGRESQL
    # ========================================================

    if conn_pg:

        try:

            cursor = conn_pg.cursor()

            cursor.execute(
                """
                INSERT INTO mensagens
                    (sessao, role, conteudo)
                VALUES
                    (%s, %s, %s)
                """,
                (
                    dados.sessao,
                    "assistant",
                    resposta_texto
                )
            )

            conn_pg.commit()

            cursor.close()
            conn_pg.close()

        except Exception as e:

            conn_pg.rollback()
            conn_pg.close()

            print(
                f"Erro ao salvar resposta no PostgreSQL: {e}"
            )

    # ========================================================
    # RESPOSTA DA API
    # ========================================================

    return {
        "resposta": resposta_texto,
        "sessao": dados.sessao
    }


# ============================================================
# UPLOAD E LEITURA DE PDF
# ============================================================

@app.post("/upload/pdf")
def upload_pdf(
    file: UploadFile = File(...)
):

    # Verificar extensão
    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Nenhum arquivo foi enviado."
        )

    if not file.filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="O arquivo enviado precisa ser PDF."
        )

    temp_path = (
        f"/tmp/temp_"
        f"{uuid.uuid4().hex}.pdf"
    )

    try:

        # --------------------------------------------
        # SALVAR ARQUIVO TEMPORÁRIO
        # --------------------------------------------

        with open(temp_path, "wb") as arquivo:

            arquivo.write(
                file.file.read()
            )

        # --------------------------------------------
        # LER PDF
        # --------------------------------------------

        loader = PyPDFLoader(
            temp_path
        )

        docs = loader.load()

        # --------------------------------------------
        # EXTRAIR TEXTO
        # --------------------------------------------

        texto_pdf = "\n\n".join(
            documento.page_content
            for documento in docs
        )
                # --------------------------------------------
        # DIVIDIR O PDF EM CHUNKS
        # --------------------------------------------

        chunks = text_splitter.split_documents(docs)

        # --------------------------------------------
        # LIMPAR DOCUMENTOS ANTERIORES
        # --------------------------------------------

        global vectorstore

        try:
            vectorstore.delete_collection()
        except Exception:
            pass

        vectorstore = Chroma(
            collection_name="documentos_pdf",
            persist_directory=CAMINHO_CHROMA,
            embedding_function=embeddings
        )

        # --------------------------------------------
        # GERAR EMBEDDINGS E ARMAZENAR NO CHROMA
        # --------------------------------------------

        vectorstore.add_documents(chunks)

        print(
            f"RAG: {len(chunks)} chunks armazenados."
        )

        # --------------------------------------------
        # VERIFICAR SE PDF POSSUI TEXTO
        # --------------------------------------------

        if not texto_pdf.strip():

            raise HTTPException(
                status_code=400,
                detail=(
                    "Não foi possível extrair texto "
                    "deste PDF."
                )
            )

        return {
            "arquivo": file.filename,
            "paginas": len(docs),
            "texto": texto_pdf
        }

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar PDF: {e}"
        )

    finally:

        # --------------------------------------------
        # REMOVER TEMPORÁRIO
        # --------------------------------------------

        if os.path.exists(temp_path):

            os.remove(temp_path)