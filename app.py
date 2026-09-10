# from langchain_community.document_loaders import PyPDFLoader
# from langchain_core.messages import HumanMessage, SystemMessage
# from langchain_ollama import ChatOllama
# import pandas as pd
# import streamlit as st
# import mysql.connector
# import psycopg2

# llm = ChatOllama(
#     model="llama3",
#     temperature=0,
#     base_url="http://host.docker.internal:11434"
# )
# # Conexão com PostgreSQL
# try:
#     conexao_postgres = psycopg2.connect(
#         host="postgres",
#         port=5432,
#         database="agente",
#         user="agente",
#         password="agente123"
#     )
# except Exception as e:
#     conexao_postgres = None

# # Conexão com MySQL
# try:
#     conexao_mysql = mysql.connector.connect(
#         host="mysql",
#         port=3306,
#         database="meu_banco",
#         user="agente",
#         password="agente123"
#     )
# except Exception as e:
#     conexao_mysql = None
#     # Busca as conversas recentes no PostgreSQL
# def buscar_conversas_recentes():
#     if not conexao_postgres:
#         return []

#     try:
#         cursor = conexao_postgres.cursor()

#         cursor.execute(
#             """
#             SELECT DISTINCT ON (sessao)
#                 sessao,
#                 conteudo,
#                 criado_em
#             FROM mensagens
#             ORDER BY sessao, criado_em DESC
#             """
#         )

#         conversas = cursor.fetchall()

#         cursor.close()

#         # Ordena pela mensagem mais recente
#         conversas.sort(
#             key=lambda x: x[2],
#             reverse=True
#         )

#         return conversas

#     except Exception:
#         return []
    
#  # Função para consultar o MySQL
# def consultar_mysql(sql):
#     try:
#         cursor = conexao_mysql.cursor()

#         cursor.execute(sql)

#         resultados = cursor.fetchall()

#         colunas = [coluna[0] for coluna in cursor.description]

#         cursor.close()

#         return colunas, resultados

#     except Exception as e:
#         return None, f"Erro no MySQL: {e}"

# #     # Teste de consulta ao MySQL
# # if conexao_mysql:
# #     try:
# #         cursor_mysql = conexao_mysql.cursor()

# #         cursor_mysql.execute(
# #             "SELECT * FROM alunos"
# #         )

# #         dados_mysql = cursor_mysql.fetchall()

# #         print("DADOS DO MYSQL:")
# #         print(dados_mysql)

# #         cursor_mysql.close()

# #     except Exception as e:
# #         print("ERRO AO CONSULTAR MYSQL:")
# #         print(e)

# # Configuração da página
# st.set_page_config(
#     page_title="Assistente Universitário",
#     page_icon="🤖",
#     layout="centered"
# )

# st.title("🤖 Assistente Universitário Inteligente")

# st.caption(
#     "Converse com seus arquivos PDF, planilhas Excel e bancos de dados SQL de"
#     " forma integrada."
#     "ass:francisco adriano"
# )




# # # Barra lateral para upload de arquivos e conexões
# # with st.sidebar:

# #     st.header("📂 Fontes de Dados")

# #     # Upload de PDF
# #     pdf_file = st.file_uploader(
# #         "Enviar PDF",
# #         type=["pdf"]
# #     )

# #     texto_pdf = ""

# #     if pdf_file:

# #         with open("temp.pdf", "wb") as f:
# #             f.write(pdf_file.getbuffer())

# #         loader = PyPDFLoader("temp.pdf")

# #         docs = loader.load()

# #         texto_pdf = " ".join(
# #             [d.page_content for d in docs]
# #         )

# #         st.success(
# #             "PDF carregado com sucesso!"
# #         )


# #     # Upload de Excel
# #     excel_file = st.file_uploader(
# #         "Enviar Excel (.xlsx)",
# #         type=["xlsx"]
# #     )

# #     df = None

# #     if excel_file:

# #         df = pd.read_excel(excel_file)

# #         st.success(
# #             "Excel carregado com sucesso!"
# #         )


# #     st.divider()

# #     if st.button("Limpar Histórico do Chat"):

# #         st.session_state.messages = []

# #         st.rerun()


# # Identificador da conversa atual
# if "sessao" not in st.session_state:
#     st.session_state.sessao = "conversa_1"

# # Inicializa o histórico de mensagens na sessão do Streamlit
# if "messages" not in st.session_state:
#     st.session_state.messages = []


# # Barra lateral para upload de arquivos e conexões
# with st.sidebar:

#     st.header("📂 Fontes de Dados")

#     # Upload de PDF
#     pdf_file = st.file_uploader(
#         "Enviar PDF",
#         type=["pdf"]
#     )

#     texto_pdf = ""

#     if pdf_file:

#         with open("temp.pdf", "wb") as f:
#             f.write(pdf_file.getbuffer())

#         loader = PyPDFLoader("temp.pdf")

#         docs = loader.load()

#         texto_pdf = " ".join(
#             [d.page_content for d in docs]
#         )

#         st.success(
#             "PDF carregado com sucesso!"
#         )


#     # Upload de Excel
#     excel_file = st.file_uploader(
#         "Enviar Excel (.xlsx)",
#         type=["xlsx"]
#     )

#     df = None

#     if excel_file:

#         df = pd.read_excel(excel_file)

#         st.success(
#             "Excel carregado com sucesso!"
#         )


#     st.divider()

#     # Conversas recentes

#     st.subheader("🕘 Conversas recentes")

#     # Botão para iniciar um novo chat
#     if st.button(
#         "➕ Novo chat",
#         use_container_width=True
#     ):

#         # Cria um novo identificador
#         import uuid

#         st.session_state.sessao = f"conversa_{uuid.uuid4().hex[:8]}"

#         # Limpa apenas o chat atual
#         st.session_state.messages = []

#         st.rerun()


#     # Busca as conversas salvas no PostgreSQL
#     conversas = buscar_conversas_recentes()

#     if conversas:

#         for sessao, ultima_mensagem, criado_em in conversas:

#             titulo = ultima_mensagem[:35]

#             if len(ultima_mensagem) > 35:
#                 titulo += "..."

#             if st.button(
#                 titulo,
#                 key=f"conversa_{sessao}",
#                 use_container_width=True
#             ):

#                 st.session_state.sessao = sessao

#                 try:

#                     cursor = conexao_postgres.cursor()

#                     cursor.execute(
#                         """
#                         SELECT role, conteudo
#                         FROM mensagens
#                         WHERE sessao = %s
#                         ORDER BY criado_em ASC, id ASC
#                         """,
#                         (sessao,)
#                     )

#                     mensagens = cursor.fetchall()

#                     cursor.close()

#                     st.session_state.messages = []

#                     for role, conteudo in mensagens:

#                         st.session_state.messages.append(
#                             {
#                                 "role": role,
#                                 "content": conteudo
#                             }
#                         )

#                     st.rerun()

#                 except Exception as e:

#                     st.error(
#                         f"Erro ao carregar conversa: {e}"
#                     )

#     else:

#         st.caption("Nenhuma conversa ainda.")

#     st.divider()

#     if st.button("🗑️ Limpar Histórico do Chat"):

#         st.session_state.messages = []

#         st.rerun()


# # Exibe o histórico de mensagens na tela
# for message in st.session_state.messages:

#     with st.chat_message(
#         message["role"]
#     ):

#         st.markdown(
#             message["content"]
#         )


# # Caixa de input do chat
# if prompt := st.chat_input(
#     "Digite sua dúvida sobre os arquivos ou dados..."
# ):

#     # Adiciona mensagem do usuário ao histórico
#     st.session_state.messages.append(
#         {
#             "role": "user",
#             "content": prompt
#         }
#     )

#     # Salva pergunta do usuário no PostgreSQL
#     if conexao_postgres:
#         cursor = conexao_postgres.cursor()

#         cursor.execute(
#             """
#             INSERT INTO mensagens (sessao, role, conteudo)
#             VALUES (%s, %s, %s)
#             """,
#             (
#                 st.session_state.sessao,
#                 "user",
#                 prompt
#             )
#         )

#         conexao_postgres.commit()
#         cursor.close()

#     with st.chat_message("user"):
#         st.markdown(prompt)


#     # Resposta do Assistente
#     with st.chat_message("assistant"):

#         with st.spinner("Pensando..."):

#             # Monta o contexto
#             contexto_extra = ""


#             if texto_pdf:

#                 contexto_extra += (
#                     "\n\n"
#                     "[Conteúdo do PDF carregado]:\n"
#                     f"{texto_pdf[:3000]}"
#                 )


#             if df is not None:

#                 contexto_extra += (
#                     "\n\n"
#                     f"[Dados do Excel "
#                     f"(Colunas: {list(df.columns)})]:\n"
#                     f"{df.head(15).to_string()}"
#                 )


#             prompt_final = (
#                 f"Você é um assistente universitário prestativo e claro.\n\n"

#                 f"O sistema possui um banco de dados MySQL "
#                 f"com a seguinte tabela:\n\n"

#                 f"Tabela: alunos\n"
#                 f"Colunas:\n"
#                 f"- id: identificador do aluno\n"
#                 f"- nome: nome do aluno\n"
#                 f"- curso: curso do aluno\n"
#                 f"- idade: idade do aluno\n\n"

#                 f"Pergunta do usuário:\n"
#                 f"{prompt}\n\n"

#                 f"Se a pergunta for sobre os dados da tabela alunos, "
#                 f"gere uma consulta SQL usando apenas SELECT.\n"

#                 f"Não gere INSERT, UPDATE ou DELETE.\n\n"

#                 f"Se a pergunta não for sobre o MySQL, "
#                 f"responda normalmente.\n\n"

#                 f"{contexto_extra}"
#             )


#             # Chamada ao LLM local
#             # Chamada ao LLM local
#             try:

#                 resposta = llm.invoke(
#                     [
#                         SystemMessage(
#                             content=(
#                                 "Você é um assistente universitário. "
#                                 "Quando a pergunta for sobre a tabela alunos, "
#                                 "responda SOMENTE com uma consulta SQL SELECT. "
#                                 "Não escreva explicações."
#                             )
#                         ),
#                         HumanMessage(
#                             content=prompt_final
#                         ),
#                     ]
#                 )

#                 resposta_texto = resposta.content.strip()

#                 # Verifica se o Llama gerou uma consulta SQL
#                 if resposta_texto.upper().startswith("SELECT"):

#                     # Executa a consulta no MySQL
#                     colunas, resultados = consultar_mysql(
#                         resposta_texto
#                     )

#                     if colunas is not None:

#                         # Converte o resultado para texto
#                         dados_mysql = ""

#                         for linha in resultados:
#                             dados_mysql += str(linha) + "\n"

#                         # Pede ao Llama para transformar o resultado
#                         # em uma resposta clara para o usuário
#                         resposta_final = llm.invoke(
#                             [
#                                 SystemMessage(
#                                     content=(
#                                         "Você é um assistente "
#                                         "universitário prestativo e claro. "
#                                         "Responda à pergunta do usuário "
#                                         "usando os dados retornados pelo "
#                                         "banco de dados. "
#                                         "Não mostre SQL."
#                                     )
#                                 ),
#                                 HumanMessage(
#                                     content=(
#                                         f"Pergunta: {prompt}\n\n"
#                                         f"Resultado do MySQL:\n"
#                                         f"{dados_mysql}"
#                                     )
#                                 ),
#                             ]
#                         )

#                         resposta_texto = resposta_final.content

#                     else:

#                         resposta_texto = (
#                             f"Erro ao consultar o MySQL: "
#                             f"{resultados}"
#                         )

#                 else:

#                     # Se não for uma consulta SQL,
#                     # mantém a resposta normal do Llama
#                     resposta_texto = resposta_texto

#             except Exception as e:

#                 resposta_texto = (
#                     f"Erro ao conectar com o Ollama. "
#                     f"Verifique se o aplicativo está aberto. "
#                     f"Detalhe: {e}"
#                 )

#             st.markdown(
#                 resposta_texto
#             )

#     # Adiciona resposta ao histórico
#     st.session_state.messages.append(
#         {
#             "role": "assistant",
#             "content": resposta_texto
#         }
#     )

#     # Salva resposta no PostgreSQL
#     if conexao_postgres:
#         cursor = conexao_postgres.cursor()

#         cursor.execute(
#             """
#             INSERT INTO mensagens (sessao, role, conteudo)
#             VALUES (%s, %s, %s)
#             """,
#             (
#                 st.session_state.sessao,
#                 "assistant",
#                 resposta_texto
#             )
#         )

#         conexao_postgres.commit()
#         cursor.close()
import os
import uuid
import requests
import pandas as pd
import streamlit as st


# ============================================================
# CONFIGURAÇÃO DA API
# ============================================================

API_URL = os.getenv(
    "API_URL",
    "http://api:8000"
)


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Assistente Universitário",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Assistente Universitário Inteligente")

st.caption(
    "Converse com seus arquivos PDF, planilhas Excel e "
    "bancos de dados SQL de forma integrada. "
    "ass: francisco adriano"
)


# ============================================================
# TESTAR API
# ============================================================

def verificar_api():

    try:

        resposta = requests.get(
            f"{API_URL}/health",
            timeout=5
        )

        return resposta.status_code == 200

    except Exception:

        return False


# ============================================================
# BUSCAR CONVERSAS RECENTES
# ============================================================

def buscar_conversas_recentes():

    try:

        resposta = requests.get(
            f"{API_URL}/conversas",
            timeout=10
        )

        if resposta.status_code != 200:
            return []

        return resposta.json()

    except Exception:

        return []


# ============================================================
# CARREGAR HISTÓRICO DE UMA CONVERSA
# ============================================================

def carregar_conversa(sessao):

    try:

        resposta = requests.get(
            f"{API_URL}/conversas/{sessao}",
            timeout=10
        )

        if resposta.status_code != 200:

            st.error(
                "Não foi possível carregar a conversa."
            )

            return []

        return resposta.json()

    except Exception as e:

        st.error(
            f"Erro ao carregar conversa: {e}"
        )

        return []


# ============================================================
# ENVIAR PDF PARA A API
# ============================================================

def enviar_pdf_para_api(pdf_file):

    try:

        arquivos = {
            "file": (
                pdf_file.name,
                pdf_file.getvalue(),
                "application/pdf"
            )
        }

        resposta = requests.post(
            f"{API_URL}/upload/pdf",
            files=arquivos,
            timeout=60
        )

        if resposta.status_code != 200:

            try:

                erro = resposta.json().get(
                    "detail",
                    "Erro desconhecido."
                )

            except Exception:

                erro = resposta.text

            st.error(
                f"Erro ao processar PDF: {erro}"
            )

            return ""

        dados = resposta.json()

        return dados.get(
            "texto",
            ""
        )

    except Exception as e:

        st.error(
            f"Erro ao enviar PDF para a API: {e}"
        )

        return ""


# ============================================================
# ENVIAR PERGUNTA PARA A API
# ============================================================

def enviar_mensagem(
    sessao,
    prompt,
    texto_pdf,
    dados_excel_json
):

    try:

        dados = {
            "sessao": sessao,
            "prompt": prompt,
            "texto_pdf": texto_pdf,
            "dados_excel_json": dados_excel_json
        }

        resposta = requests.post(
            f"{API_URL}/chat",
            json=dados,
            timeout=300
        )

        if resposta.status_code != 200:

            try:

                erro = resposta.json().get(
                    "detail",
                    "Erro desconhecido."
                )

            except Exception:

                erro = resposta.text

            return (
                f"Erro ao chamar a API: {erro}"
            )

        resultado = resposta.json()

        return resultado.get(
            "resposta",
            "A API não retornou uma resposta."
        )

    except requests.exceptions.Timeout:

        return (
            "A IA demorou muito para responder. "
            "Verifique se o Ollama está funcionando."
        )

    except Exception as e:

        return (
            f"Erro ao conectar com a API: {e}"
        )


# ============================================================
# IDENTIFICADOR DA CONVERSA
# ============================================================

if "sessao" not in st.session_state:

    st.session_state.sessao = (
        "conversa_"
        + uuid.uuid4().hex[:8]
    )


# ============================================================
# HISTÓRICO LOCAL DO STREAMLIT
# ============================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


# ============================================================
# DADOS DOS ARQUIVOS
# ============================================================

if "texto_pdf" not in st.session_state:

    st.session_state.texto_pdf = ""


if "nome_pdf" not in st.session_state:

    st.session_state.nome_pdf = ""


if "dados_excel_json" not in st.session_state:

    st.session_state.dados_excel_json = ""


if "nome_excel" not in st.session_state:

    st.session_state.nome_excel = ""


# ============================================================
# BARRA LATERAL
# ============================================================

with st.sidebar:

    st.header("📂 Fontes de Dados")


    # --------------------------------------------------------
    # STATUS DA API
    # --------------------------------------------------------

    if verificar_api():

        st.success(
            "API online"
        )

    else:

        st.error(
            "API offline"
        )


    # --------------------------------------------------------
    # UPLOAD DE PDF
    # --------------------------------------------------------

    pdf_file = st.file_uploader(
        "Enviar PDF",
        type=["pdf"]
    )


    if pdf_file:

        if (
            st.session_state.nome_pdf
            != pdf_file.name
        ):

            with st.spinner(
                "Processando PDF..."
            ):

                texto_pdf = (
                    enviar_pdf_para_api(
                        pdf_file
                    )
                )

            if texto_pdf:

                st.session_state.texto_pdf = (
                    texto_pdf
                )

                st.session_state.nome_pdf = (
                    pdf_file.name
                )

                st.success(
                    "PDF carregado com sucesso!"
                )

    elif st.session_state.nome_pdf:

        st.session_state.texto_pdf = ""

        st.session_state.nome_pdf = ""


    # --------------------------------------------------------
    # UPLOAD DE EXCEL
    # --------------------------------------------------------

    excel_file = st.file_uploader(
        "Enviar Excel (.xlsx)",
        type=["xlsx"]
    )


    if excel_file:

        if (
            st.session_state.nome_excel
            != excel_file.name
        ):

            try:

                df = pd.read_excel(
                    excel_file
                )

                # Converte os dados para JSON
                # para enviar para a API

                st.session_state.dados_excel_json = (
                    df.to_json(
                        orient="records",
                        force_ascii=False
                    )
                )

                st.session_state.nome_excel = (
                    excel_file.name
                )

                st.success(
                    "Excel carregado com sucesso!"
                )

                st.caption(
                    f"{len(df)} linhas carregadas."
                )

            except Exception as e:

                st.error(
                    f"Erro ao ler Excel: {e}"
                )

    elif st.session_state.nome_excel:

        st.session_state.dados_excel_json = ""

        st.session_state.nome_excel = ""


    # --------------------------------------------------------
    # ARQUIVOS CARREGADOS
    # --------------------------------------------------------

    if st.session_state.nome_pdf:

        st.info(
            f"📄 PDF: "
            f"{st.session_state.nome_pdf}"
        )


    if st.session_state.nome_excel:

        st.info(
            f"📊 Excel: "
            f"{st.session_state.nome_excel}"
        )


    st.divider()


    # ========================================================
    # CONVERSAS RECENTES
    # ========================================================

    st.subheader(
        "🕘 Conversas recentes"
    )


    # --------------------------------------------------------
    # NOVO CHAT
    # --------------------------------------------------------

    if st.button(
        "➕ Novo chat",
        use_container_width=True
    ):

        st.session_state.sessao = (
            "conversa_"
            + uuid.uuid4().hex[:8]
        )

        st.session_state.messages = []

        st.rerun()


    # --------------------------------------------------------
    # BUSCAR CONVERSAS
    # --------------------------------------------------------

    conversas = (
        buscar_conversas_recentes()
    )


    if conversas:

        for conversa in conversas:

            sessao = conversa.get(
                "sessao",
                ""
            )

            ultima_mensagem = (
                conversa.get(
                    "ultima_mensagem",
                    "Conversa"
                )
            )

            titulo = (
                ultima_mensagem[:35]
            )

            if len(
                ultima_mensagem
            ) > 35:

                titulo += "..."


            if st.button(
                titulo,
                key=f"conversa_{sessao}",
                use_container_width=True
            ):

                st.session_state.sessao = (
                    sessao
                )

                mensagens = (
                    carregar_conversa(
                        sessao
                    )
                )

                st.session_state.messages = (
                    mensagens
                )

                st.rerun()

    else:

        st.caption(
            "Nenhuma conversa ainda."
        )


    st.divider()


    # --------------------------------------------------------
    # LIMPAR CHAT ATUAL
    # --------------------------------------------------------

    if st.button(
        "🗑️ Limpar Histórico do Chat",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()


# ============================================================
# EXIBIR HISTÓRICO
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# ============================================================
# CAIXA DE INPUT
# ============================================================

if prompt := st.chat_input(
    "Digite sua dúvida sobre os arquivos ou dados..."
):


    # --------------------------------------------------------
    # ADICIONAR PERGUNTA NA TELA
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )


    with st.chat_message("user"):

        st.markdown(
            prompt
        )


    # --------------------------------------------------------
    # RESPOSTA DO ASSISTENTE
    # --------------------------------------------------------

    with st.chat_message(
        "assistant"
    ):

        with st.spinner(
            "Pensando..."
        ):


            resposta_texto = (
                enviar_mensagem(
                    sessao=(
                        st.session_state.sessao
                    ),
                    prompt=prompt,
                    texto_pdf=(
                        st.session_state.texto_pdf
                    ),
                    dados_excel_json=(
                        st.session_state.dados_excel_json
                    )
                )
            )


            st.markdown(
                resposta_texto
            )


    # --------------------------------------------------------
    # SALVAR RESPOSTA NO HISTÓRICO LOCAL
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": resposta_texto
        }
    )