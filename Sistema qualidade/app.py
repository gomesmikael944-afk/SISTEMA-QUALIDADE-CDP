import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import datetime, date
import uuid
import html
import json
import hashlib
import secrets

# =====================================================
# CONFIGURAÇÕES
# =====================================================

PASTA = Path(__file__).parent
PASTA_DADOS = PASTA / "dados"
PASTA_UPLOADS = PASTA / "uploads"
ARQUIVO_DADOS = PASTA_DADOS / "ocorrencias.csv"

PASTA_DADOS.mkdir(exist_ok=True)
PASTA_UPLOADS.mkdir(exist_ok=True)

st.set_page_config(
    page_title="Casa do Padeiro | Gestão da Qualidade",
    page_icon="🥖",
    layout="wide"
)

# =====================================================
# LOGIN INDIVIDUAL - CASA DO PADEIRO
# =====================================================

ARQUIVO_USUARIOS = PASTA_DADOS / "usuarios.json"


def carregar_usuarios():
    if not ARQUIVO_USUARIOS.exists():
        return {}

    try:
        with open(ARQUIVO_USUARIOS, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)

    except (json.JSONDecodeError, OSError):
        st.error("Não foi possível ler o arquivo de usuários.")
        st.stop()


def salvar_usuarios(usuarios):
    with open(ARQUIVO_USUARIOS, "w", encoding="utf-8") as arquivo:
        json.dump(
            usuarios,
            arquivo,
            ensure_ascii=False,
            indent=4
        )


def criar_hash(senha, salt=None):
    salt = salt or secrets.token_hex(16)

    senha_hash = hashlib.pbkdf2_hmac(
        "sha256",
        senha.encode("utf-8"),
        salt.encode("utf-8"),
        300000
    ).hex()

    return salt, senha_hash


def validar_senha(senha, salt, senha_hash):
    _, hash_digitado = criar_hash(senha, salt)

    return secrets.compare_digest(
        hash_digitado,
        senha_hash
    )


def tela_login():
    usuarios = carregar_usuarios()

    
    st.markdown("""
    <style>
    /* FUNDO DA TELA DE LOGIN */
    .stApp,
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #100D0A, #302014) !important;
        color: #FFFFFF !important;
    }

    /* ÁREA CENTRAL */
    [data-testid="stMainBlockContainer"] {
        max-width: 850px;
        padding-top: 4rem;
    }

    /* FORMULÁRIOS */
    [data-testid="stForm"] {
        background: #211811 !important;
        border: 1px solid #B8793D !important;
        border-radius: 18px !important;
        padding: 25px !important;
    }

    /* CAMPOS */
    [data-testid="stTextInput"] input {
        background: #30251D !important;
        color: #FFFFFF !important;
        border: 1px solid #B8793D !important;
        border-radius: 10px !important;
    }

    /* BOTÃO DE LOGIN */
    [data-testid="stFormSubmitButton"] button {
        background: linear-gradient(110deg, #B8793D, #E0A45E) !important;
        color: #17100B !important;
        font-weight: 900 !important;
        border-radius: 10px !important;
        border: none !important;
        min-height: 48px;
    }

    [data-testid="stFormSubmitButton"] button:hover {
        background: #E8B16E !important;
        transform: translateY(-1px);
    }
    </style>
    """, unsafe_allow_html=True)



    st.subheader("Acesso ao sistema")

    if not usuarios:

        st.info(
            "Primeiro acesso: cadastre o administrador do sistema."
        )

        with st.form("primeiro_acesso_login"):

            nome = st.text_input("Nome do administrador")
            usuario = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            confirmar = st.text_input(
                "Confirmar senha",
                type="password"
            )

            criar = st.form_submit_button(
                "Criar administrador",
                use_container_width=True
            )

        if criar:

            chave = usuario.strip().lower()

            if not nome.strip() or not chave:
                st.error("Preencha o nome e o usuário.")

            elif len(senha) < 8:
                st.error(
                    "A senha precisa ter pelo menos 8 caracteres."
                )

            elif senha != confirmar:
                st.error("As senhas não conferem.")

            else:

                salt, senha_hash = criar_hash(senha)

                usuarios[chave] = {
                    "nome": nome.strip(),
                    "salt": salt,
                    "senha_hash": senha_hash,
                    "perfil": "Administrador",
                    "ativo": True
                }

                salvar_usuarios(usuarios)

                st.success(
                    "Administrador criado! Agora faça login."
                )

                st.rerun()

    else:

        with st.form("form_login_individual"):

            usuario = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")

            entrar = st.form_submit_button(
                "Entrar",
                use_container_width=True
            )

        if entrar:

            chave = usuario.strip().lower()
            conta = usuarios.get(chave)

            if (
                conta
                and conta.get("ativo", True)
                and validar_senha(
                    senha,
                    conta["salt"],
                    conta["senha_hash"]
                )
            ):

                st.session_state["autenticado"] = True
                st.session_state["usuario"] = conta["nome"]
                st.session_state["perfil"] = conta.get(
                    "perfil",
                    "Usuário"
                )

                st.rerun()

            else:
                st.error("Usuário ou senha incorretos.")


# =====================================================
# VERIFICAÇÃO DE ACESSO
# =====================================================

if not st.session_state.get("autenticado", False):
    tela_login()
    st.stop()
   
STATUS = ["Sem resposta", "Em análise", "Resolvido"]

STATUS_ANTIGOS = {
    "Tudo certo": "Resolvido",
    "Resolvida": "Resolvido",
    "Resolvidas": "Resolvido"
}

PROBLEMAS = [
    "Produto amassado",
    "Produto quebrado",
    "Problema de validade",
    "Problema de embalagem",
    "Diferença de peso/tamanho",
    "Problema de textura",
    "Problema de sabor/odor",
    "Produto faltante",
    "Produto incorreto",
    "Outro"
]

PRODUTOS = {
    "Hambúrgueres e pães especiais": [
        "202 - PÃO TRADICIONAL SEM PINCEL (48 unid)",
        "104 - PÃO BRIOCHE DE BATATA BURGER TOUR PINCELADO (72 unid)",
        "106 - PÃO BRIOCHE DE BATATA BURGER TOUR GERGELIM MESCLADO (72 unid)",
        "107 - PÃO VEGAN SEM PINCEL (72 unid)",
        "182 - BRIOCHE SEM PINCEL BASE FUNDA (72 unid)",
        "108 - PÃO BRIOCHE PINCELADO 8.5-9.5CM (72 unid)",
        "183 - BRIOCHE PINCELADO BASE FUNDA (72 unid)",
        "200 - PÃO BRIOCHE LEVEMENTE PINCELADO (72 unid)",
        "184 - BRIOCHE PINCELADO GERGELIM BRANCO BASE FUNDA (72 unid)",
        "185 - BRIOCHE PINCELADO GERGELIM MESCLADO BASE FUNDA (72 unid)",
        "120 - PÃO BRIOCHE CARAMELO X (72 unid)",
        "123 - PÃO DE BATATA PINCELADO (72 unid)",
        "125 - PÃO DE BATATA PINCELADO GERGELIM MESCLADO (72 unid)",
        "129 - PÃO PRETO (72 unid)",
        "130 - PÃO PRETO COM GERGELIM BRANCO (72 unid)",
        "100 - BOSSA NOVA (72 unid)",
        "101 - MACIABATTA REDONDA (72 unid)"
    ],
    "Dog e baguetes": [
        "136 - BAGUETE CROCANTE (60 unid)",
        "133 - PÃO DE HOT DOG BRIOCHE (80 unid)",
        "134 - BAGUETE CROCANTE COM PARMESÃO (60 unid)",
        "1006 - CIABATTA (60 unid)"
    ],
    "Mini": [
        "142 - MINI BURGER BRIOCHE PINCEL (180 unid)",
        "1040 - MINI ROLL (144 unid)"
    ],
    "Couvert": [
        "1031 - KIT COUVERT (75 unid)"
    ],
    "Forma": [
        "1060 - BRIOCHE FORMA (20 unid)"
    ],
    "Sourdough": [
        "1010 - SOURDOUGH OVAL (10 unid)",
        "1038 - SOURDOUGH FILÃO GIGANTE (4 unid)",
        "1011 - SOURDOUGH REDONDO P (18 unid)"
    ],
    "Focaccia e pizza": [
        "1013 - FOCCACCIA TRADICIONAL (2 unid)"
    ],
    "Bagel": [
        "1047 - PLAIN BAGEL (64 unid)",
        "1048 - EVERYTHING BAGEL (64 unid)"
    ]
}

DIAS_VALIDADE_HAMBURGUER = 21
DIAS_VALIDADE_BOSSA = 15

COLUNAS = [
    "id", "data_registro", "cliente", "documento", "pedido",
    "produto", "lote", "fabricacao", "data_reclamacao",
    "quantidade", "tipo_problema", "descricao", "status",
    "responsavel", "anexos", "historico", "tipo_resolucao",
    "valor_cupom", "valor_lalamove", "descricao_resolucao",
    "data_resolucao"
]

# =====================================================
# IDENTIDADE VISUAL
# =====================================================

st.markdown("""
<style>

/* FUNDO GERAL */

.stApp, [data-testid="stAppViewContainer"] {
    background: #090909;
    color: #F4F0EA;
}

.block-container {
    max-width: 1450px;
    padding: 2rem 3rem 4rem;
}

/* MENU LATERAL */

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #17100B 0%, #090909 100%);
    border-right: 1px solid #6B472B;
}

section[data-testid="stSidebar"] > div {
    padding: 1.5rem 0.8rem 2rem;
}

section[data-testid="stSidebar"] h2 {
    color: #E8B16E !important;
    font-size: 22px !important;
    font-weight: 900 !important;
    letter-spacing: 1px;
}

section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
    color: #A99B8E !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    letter-spacing: 1px;
}

section[data-testid="stSidebar"] [data-testid="stButton"] {
    margin-bottom: 10px;
}

section[data-testid="stSidebar"] [data-testid="stButton"] button {
    width: 100%;
    min-height: 58px;
    border-radius: 13px;
    border: 1px solid #62452F !important;
    background: linear-gradient(110deg, #21170F, #17110D) !important;
    color: #F5E9DA !important;
    font-size: 16px !important;
    font-weight: 900 !important;
    text-align: left !important;
    padding: 8px 14px !important;
    transition: all 0.2s ease;
}

section[data-testid="stSidebar"] [data-testid="stButton"] button p {
    font-weight: 900 !important;
    font-size: 16px !important;
}

section[data-testid="stSidebar"] [data-testid="stButton"] button:hover {
    background: linear-gradient(110deg, #684322, #3A2819) !important;
    border-color: #E0A45E !important;
    color: #FFFFFF !important;
    transform: translateX(3px);
}

section[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"] {
    background: linear-gradient(110deg, #B8793D, #E0A45E) !important;
    border: 1px solid #F2C486 !important;
    color: #17100B !important;
    box-shadow: 0 4px 15px rgba(190, 125, 62, .28);
}

section[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"] p {
    color: #17100B !important;
    font-weight: 900 !important;
}

/* CABEÇALHO */

.cabecalho-cdp {
    display: flex;
    align-items: center;
    gap: 18px;
    padding: 25px 30px;
    background: linear-gradient(110deg, #21160F, #11100F 70%);
    border: 1px solid #49311F;
    border-radius: 18px;
    margin-bottom: 28px;
}

.logo-cdp {
    font-size: 42px;
}

.nome-cdp {
    color: #F7EBDD;
    font-size: 25px;
    font-weight: 850;
    letter-spacing: 1px;
}

.subtitulo-cdp {
    color: #C28A4E;
    font-size: 10px;
    letter-spacing: 3px;
    margin-top: 5px;
}

/* TÍTULOS */

h1 {
    color: #F5E9DA !important;
    font-size: 36px !important;
    font-weight: 800 !important;
}

h2 {
    color: #E9C49A !important;
}

h3 {
    color: #D69B5C !important;
}

p, label, .stMarkdown {
    color: #E8E0D7;
}

[data-testid="stCaptionContainer"] {
    color: #A99B8E;
}

/* CARTÕES */

.cartao {
    background: linear-gradient(145deg, #211811, #15110E);
    border: 1px solid #49321F;
    border-radius: 17px;
    padding: 23px;
    min-height: 115px;
}

.cartao-titulo {
    color: #B9A797;
    font-size: 13px;
    font-weight: 600;
}

.cartao-numero {
    color: #E8B16E;
    font-size: 32px;
    font-weight: 850;
    margin-top: 10px;
}

/* ETAPAS */

.etapa {
    color: #D99D5B;
    font-size: 16px;
    font-weight: 800;
    padding: 12px 16px;
    margin: 20px 0 15px;
    background: #211811;
    border-left: 4px solid #B77A3D;
    border-radius: 8px;
}

/* CAMPOS */

.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
    background: #1B1511 !important;
    color: #F6EEE6 !important;
    border: 1px solid #59402D !important;
    border-radius: 11px !important;
}

.stSelectbox [data-baseweb="select"] > div {
    background: #1B1511 !important;
    border: 1px solid #59402D !important;
    border-radius: 11px !important;
    color: #F6EEE6 !important;
}

.stSelectbox [data-baseweb="select"] span {
    color: #F6EEE6 !important;
}

.stDateInput input {
    background: #1B1511 !important;
    color: #F6EEE6 !important;
    border: 1px solid #59402D !important;
    border-radius: 11px !important;
}

/* BOTÕES GERAIS */

.stButton button,
.stFormSubmitButton button {
    background: linear-gradient(110deg, #9A6032, #C18A4C) !important;
    color: #FFFFFF !important;
    border: 1px solid #D19A5D !important;
    border-radius: 11px !important;
    min-height: 45px;
    font-weight: 750 !important;
}

/* TABELAS E FORMULÁRIOS */

[data-testid="stDataFrame"] {
    border: 1px solid #49321F;
    border-radius: 13px;
}

[data-testid="stForm"] {
    background: #110E0C;
    border: 1px solid #39291D;
    border-radius: 17px;
    padding: 22px;
}

[data-testid="stMetric"] {
    background: #17120F;
    border: 1px solid #49321F;
    border-radius: 14px;
    padding: 17px;
}

footer {
    visibility: hidden;
}

[data-testid="stHeader"] {
    background: transparent;
}

</style>

<div class="cabecalho-cdp">
    <div class="logo-cdp">🥖</div>
    <div>
        <div class="nome-cdp">CASA DO PADEIRO</div>
        <div class="subtitulo-cdp">GESTÃO DA QUALIDADE</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.caption(
    "Sistema de gestão da qualidade para acompanhamento de reclamações, produtos e lotes."
)

# =====================================================
# FUNÇÕES
# =====================================================

def preparar_dataframe(df):
    for coluna in COLUNAS:
        if coluna not in df.columns:
            df[coluna] = ""

    df = df[COLUNAS].copy()

    for coluna in COLUNAS:
        df[coluna] = df[coluna].fillna("").astype(str).str.strip()

    df["status"] = df["status"].replace(STATUS_ANTIGOS)

    return df


def carregar_dados():
    if not ARQUIVO_DADOS.exists():
        vazio = pd.DataFrame(columns=COLUNAS)
        vazio.to_csv(
            ARQUIVO_DADOS,
            index=False,
            encoding="utf-8-sig"
        )
        return vazio

    try:
        dados = pd.read_csv(
            ARQUIVO_DADOS,
            dtype=str,
            encoding="utf-8-sig",
            sep=None,
            engine="python"
        )
    except UnicodeDecodeError:
        dados = pd.read_csv(
            ARQUIVO_DADOS,
            dtype=str,
            encoding="latin-1",
            sep=None,
            engine="python"
        )

    dados.columns = dados.columns.str.strip().str.lower()

    dados = preparar_dataframe(dados)

    # IMPORTAÇÃO DO HISTÓRICO SAC
    arquivo_historico = ARQUIVO_DADOS.parent / "historico_SAC_importacao.csv"

    if arquivo_historico.exists():
        try:
            historico_sac = pd.read_csv(
                arquivo_historico,
                dtype=str,
                encoding="utf-8-sig",
                sep=None,
                engine="python"
            ).fillna("")

            novos = pd.DataFrame()

            # Relaciona as colunas do histórico com as do sistema
            novos["data_registro"] = historico_sac.get("data_registro", "")
            novos["cliente"] = historico_sac.get("cliente", "")
            novos["documento"] = ""
            novos["pedido"] = historico_sac.get("codigo_pedido", "")
            novos["produto"] = historico_sac.get("produto", "")
            novos["lote"] = historico_sac.get("lote", "")
            novos["fabricacao"] = historico_sac.get("data_fabricacao", "")
            novos["data_reclamacao"] = historico_sac.get("data_registro", "")
            novos["quantidade"] = ""
            novos["tipo_problema"] = historico_sac.get("tipo_reclamacao", "")
            novos["descricao"] = historico_sac.get("descricao_atendimento", "")
            novos["status"] = "Sem resposta"
            novos["responsavel"] = ""
            novos["anexos"] = ""
            novos["historico"] = "Sim"
            novos["tipo_resolucao"] = ""
            novos["valor_cupom"] = ""
            novos["valor_lalamove"] = ""
            novos["descricao_resolucao"] = ""
            novos["data_resolucao"] = ""

            # Cria identificadores únicos para os registros importados
            import hashlib

            campos_chave = [
                "data_registro", "cliente", "pedido",
                "produto", "lote", "descricao"
            ]

            novos["id"] = novos[campos_chave].astype(str).agg(
                "|".join, axis=1
            ).apply(
                lambda valor: "SAC-" + hashlib.md5(
                    valor.encode("utf-8")
                ).hexdigest()[:12]
            )

            novos = preparar_dataframe(novos)

            # Evita importar novamente registros já existentes
            ids_existentes = set(dados["id"].astype(str))
            novos = novos[~novos["id"].astype(str).isin(ids_existentes)]

            if not novos.empty:
                dados = pd.concat(
                    [dados, novos],
                    ignore_index=True
                )

                dados = preparar_dataframe(dados)

                dados.to_csv(
                    ARQUIVO_DADOS,
                    index=False,
                    encoding="utf-8-sig"
                )

                print(
                    f"Histórico SAC importado: {len(novos)} registros."
                )

        except Exception as erro:
            print(f"Erro ao importar histórico SAC: {erro}")

    return dados


def salvar_dados(df):
    preparar_dataframe(df).to_csv(
        ARQUIVO_DADOS,
        index=False,
        encoding="utf-8-sig"
    )


def proximo_id(df):
    if df.empty:
        return 1

    ids = pd.to_numeric(df["id"], errors="coerce")

    if ids.notna().any():
        return int(ids.max()) + 1

    return 1


def buscar_registro(df, identificador):
    resultado = df[
        df["id"].astype(str).str.strip()
        == str(identificador).strip()
    ]

    if resultado.empty:
        return None

    return resultado.iloc[0]


def indice_por_id(df, identificador):
    indices = df.index[
        df["id"].astype(str).str.strip()
        == str(identificador).strip()
    ].tolist()

    if len(indices) != 1:
        return None

    return indices[0]


def salvar_anexo(arquivo):
    nome = uuid.uuid4().hex + Path(arquivo.name).suffix.lower()

    (PASTA_UPLOADS / nome).write_bytes(
        arquivo.getbuffer()
    )

    return nome


def formatar_data(valor):
    if not valor:
        return "Não informada"

    try:
        return datetime.strptime(
            str(valor)[:10],
            "%Y-%m-%d"
        ).strftime("%d/%m/%Y")
    except ValueError:
        return str(valor)


def obter_prazo_validade(produto):
    codigo = str(produto).split(" - ")[0].strip()

    if codigo == "100":
        return DIAS_VALIDADE_BOSSA

    codigos = [
        str(item).split(" - ")[0]
        for item in PRODUTOS["Hambúrgueres e pães especiais"]
    ]

    if codigo in codigos:
        return DIAS_VALIDADE_HAMBURGUER

    return None


def dias_ate_reclamacao(produto, fabricacao, reclamacao):
    if not fabricacao or not reclamacao:
        return None

    prazo = obter_prazo_validade(produto)

    if prazo is None:
        return None

    return (reclamacao - fabricacao).days


def registrar_evento(df, identificador, mensagem):
    indice = indice_por_id(df, identificador)

    if indice is None:
        return False

    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    antigo = str(df.at[indice, "historico"]).strip()

    df.at[indice, "historico"] = (
        (antigo + "\n") if antigo else ""
    ) + f"{agora} | {mensagem}"

    return True


def exibir_status(status):
    cores = {
        "Sem resposta": "#c9443c",
        "Em análise": "#bd8046",
        "Resolvido": "#43865b"
    }

    cor = cores.get(status, "#777777")

    st.markdown(
        f'<span style="background:{cor};color:white;'
        f'padding:6px 13px;border-radius:8px;font-weight:700">'
        f'{html.escape(str(status))}</span>',
        unsafe_allow_html=True
    )


def exibir_anexos(reg, chave):
    anexos = [
        x for x in str(reg["anexos"]).split("|") if x
    ]

    st.subheader("Fotos e documentos")

    if not anexos:
        st.caption("Nenhum anexo cadastrado nesta ocorrência.")
        return

    for nome in anexos:
        caminho = PASTA_UPLOADS / nome

        if caminho.exists():
            st.download_button(
                f"Baixar anexo {nome[:12]}",
                caminho.read_bytes(),
                file_name=nome,
                key=f"{chave}_{nome}"
            )


def dinheiro(valor):
    try:
        numero = float(valor or 0)

        return (
            f"R$ {numero:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )
    except (ValueError, TypeError):
        return "R$ 0,00"


def converter_valor(valor):
    try:
        return float(valor or 0)
    except (ValueError, TypeError):
        return 0.0


# =====================================================
# CARREGAMENTO E MENU
# =====================================================

df = carregar_dados()

# Identificadores internos: não dependem dos emojis dos títulos.

PAGINAS = {
    "dashboard": "📊 Dashboard",
    "nova": "📝 Nova ocorrência",
    "consulta": "🔍 Consultar ocorrências",
    "resolucao": "🛠️ Resolução de problemas",
    "analise": "📈 Análise por produto/lote",
    "exportar": "📤 Exportar dados"
}

if (
    "pagina_atual" not in st.session_state
    or st.session_state.pagina_atual not in PAGINAS
):
    st.session_state.pagina_atual = "dashboard"

st.sidebar.markdown("## NAVEGAÇÃO")
st.sidebar.caption("CASA DO PADEIRO | QUALIDADE")

for chave, rotulo in PAGINAS.items():

    selecionado = st.session_state.pagina_atual == chave

    if st.sidebar.button(
        rotulo,
        key=f"menu_{chave}",
        use_container_width=True,
        type="primary" if selecionado else "secondary"
    ):
        st.session_state.pagina_atual = chave
        st.rerun()

pagina = st.session_state.pagina_atual


# =====================================================
# DASHBOARD COMPLETO
# =====================================================

if pagina == "dashboard":

    st.title("Dashboard de qualidade")
    st.caption("Visão geral das ocorrências, desempenho e custos da qualidade.")

    total = len(df)

    sem = int((df["status"] == "Sem resposta").sum())
    analise = int((df["status"] == "Em análise").sum())
    resolvidas = int((df["status"] == "Resolvido").sum())

    # ================================================
    # INDICADORES OPERACIONAIS
    # ================================================

    st.subheader("Indicadores operacionais")

    c1, c2, c3, c4 = st.columns(4)

    indicadores = [
        (c1, "Total de ocorrências", total, "#d9a323"),
        (c2, "Sem resposta", sem, "#ff5252"),
        (c3, "Em análise", analise, "#f5b82e"),
        (c4, "Resolvidas", resolvidas, "#20c879")
    ]

    for col, titulo, valor, cor in indicadores:
        with col:
            st.markdown(
                f'<div class="cartao">'
                f'<div class="cartao-titulo">{titulo}</div>'
                f'<div class="cartao-numero" style="color:{cor}">{valor}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

    percentual_resolvido = (
        (resolvidas / total) * 100 if total else 0
    )

    st.write("")
    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Taxa de resolução",
        f"{percentual_resolvido:.1f}%"
    )

    c2.metric(
        "Clientes envolvidos",
        df["cliente"].replace("", pd.NA).dropna().nunique()
    )

    c3.metric(
        "Lotes identificados",
        df["lote"].replace("", pd.NA).dropna().nunique()
    )

    st.divider()

    # ================================================
    # INDICADORES FINANCEIROS
    # ================================================

    st.subheader("Indicadores financeiros")

    gasto_cupons = (
        pd.to_numeric(df["valor_cupom"], errors="coerce")
        .fillna(0)
        .sum()
    )

    gasto_lalamove = (
        pd.to_numeric(df["valor_lalamove"], errors="coerce")
        .fillna(0)
        .sum()
    )

    custo_total = gasto_cupons + gasto_lalamove

    ocorrencias_com_custo = int(
        (
            (pd.to_numeric(df["valor_cupom"], errors="coerce").fillna(0) > 0)
            |
            (pd.to_numeric(df["valor_lalamove"], errors="coerce").fillna(0) > 0)
        ).sum()
    )

    custo_medio = custo_total / total if total else 0

    custo_medio_com_custo = (
        custo_total / ocorrencias_com_custo
        if ocorrencias_com_custo else 0
    )

    def formatar_reais(valor):
        return (
            f"R$ {valor:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

    c1, c2, c3, c4 = st.columns(4)

    financeiros = [
        (c1, "Total em cupons", gasto_cupons, "#f5c451"),
        (c2, "Total em Lalamove", gasto_lalamove, "#f5c451"),
        (c3, "Custo total", custo_total, "#ff5252"),
        (c4, "Custo médio por ocorrência", custo_medio, "#20c879")
    ]

    for col, titulo, valor, cor in financeiros:
        with col:
            st.markdown(
                f'<div class="cartao">'
                f'<div class="cartao-titulo">{titulo}</div>'
                f'<div class="cartao-numero" style="color:{cor};font-size:24px">'
                f'{formatar_reais(valor)}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

    st.write("")

    c1, c2 = st.columns(2)

    c1.metric(
        "Ocorrências com custo registrado",
        ocorrencias_com_custo
    )

    c2.metric(
        "Custo médio por ocorrência com custo",
        formatar_reais(custo_medio_com_custo)
    )

    st.caption(
        "O custo médio por ocorrência considera todos os registros. "
        "O segundo indicador considera somente ocorrências com algum custo registrado."
    )

    st.divider()

    # ================================================
    # GRÁFICOS FINANCEIROS
    # ================================================

    st.subheader("Análise dos custos")

    a, b = st.columns(2)

    with a:

        custos = pd.DataFrame({
            "Tipo de custo": ["Cupons", "Lalamove"],
            "Valor": [gasto_cupons, gasto_lalamove]
        })

        custos = custos[custos["Valor"] > 0]

        if not custos.empty:

            fig = px.pie(
                custos,
                names="Tipo de custo",
                values="Valor",
                hole=0.55,
                title="Distribuição dos custos",
                color="Tipo de custo",
                color_discrete_map={
                    "Cupons": "#d9a323",
                    "Lalamove": "#64748b"
                }
            )

            fig.update_traces(
                texttemplate="%{label}<br>R$ %{value:,.2f}"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:
            st.info("Ainda não existem custos registrados.")

    with b:

        st.markdown("**Resumo financeiro**")

        st.write("Total em cupons:", formatar_reais(gasto_cupons))
        st.write("Total em Lalamove:", formatar_reais(gasto_lalamove))

        st.divider()

        st.markdown("**Custo total registrado**")

        st.markdown(
            f'<div style="font-size:32px;font-weight:800;color:#ff5252">'
            f'{formatar_reais(custo_total)}</div>',
            unsafe_allow_html=True
        )

    # ================================================
    # EVOLUÇÃO MENSAL DOS CUSTOS
    # ================================================

    st.subheader("Evolução mensal dos custos")

    if not df.empty:

        financeiro_mensal = df.copy()

        financeiro_mensal["custo_cupom"] = (
            pd.to_numeric(
                financeiro_mensal["valor_cupom"],
                errors="coerce"
            ).fillna(0)
        )

        financeiro_mensal["custo_lalamove"] = (
            pd.to_numeric(
                financeiro_mensal["valor_lalamove"],
                errors="coerce"
            ).fillna(0)
        )

        financeiro_mensal["custo_total"] = (
            financeiro_mensal["custo_cupom"]
            + financeiro_mensal["custo_lalamove"]
        )

        financeiro_mensal["data_base"] = pd.to_datetime(
            financeiro_mensal["data_resolucao"],
            format="%d/%m/%Y %H:%M",
            errors="coerce"
        )

        financeiro_mensal["data_base"] = (
            financeiro_mensal["data_base"].fillna(
                pd.to_datetime(
                    financeiro_mensal["data_registro"],
                    format="%d/%m/%Y %H:%M",
                    errors="coerce"
                )
            )
        )

        financeiro_mensal = financeiro_mensal.dropna(
            subset=["data_base"]
        )

        if not financeiro_mensal.empty:

            financeiro_mensal["Mês"] = (
                financeiro_mensal["data_base"]
                .dt.to_period("M")
                .astype(str)
            )

            mensal = (
                financeiro_mensal
                .groupby("Mês")[
                    ["custo_cupom", "custo_lalamove", "custo_total"]
                ]
                .sum()
                .reset_index()
            )

            mensal = mensal.rename(columns={
                "custo_cupom": "Cupons",
                "custo_lalamove": "Lalamove",
                "custo_total": "Custo total"
            })

            fig = px.bar(
                mensal,
                x="Mês",
                y=["Cupons", "Lalamove"],
                title="Custos registrados por mês",
                barmode="stack"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:
            st.info("Não foi possível identificar as datas dos registros.")

    st.divider()

    # ================================================
    # OCORRÊNCIAS POR STATUS E PROBLEMA
    # ================================================

    st.subheader("Análise das ocorrências")

    a, b = st.columns(2)

    with a:

        dados_status = (
            df["status"]
            .value_counts()
            .rename_axis("Status")
            .reset_index(name="Quantidade")
        )

        if not dados_status.empty:

            fig = px.pie(
                dados_status,
                names="Status",
                values="Quantidade",
                color="Status",
                color_discrete_map={
                    "Sem resposta": "#e53935",
                    "Em análise": "#d99a00",
                    "Resolvido": "#159447"
                },
                title="Ocorrências por status"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    with b:

        dados_problemas = (
            df["tipo_problema"]
            .value_counts()
            .rename_axis("Problema")
            .reset_index(name="Quantidade")
        )

        if not dados_problemas.empty:

            fig = px.bar(
                dados_problemas,
                x="Problema",
                y="Quantidade",
                title="Ocorrências por tipo de problema"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    st.divider()

    # ================================================
    # RANKING DE CLIENTES
    # ================================================

    st.subheader("Ranking de clientes com mais reclamações")

    ranking_clientes = (
        df["cliente"]
        .replace("", pd.NA)
        .dropna()
        .value_counts()
        .head(10)
        .rename_axis("Cliente")
        .reset_index(name="Quantidade de reclamações")
    )

    if not ranking_clientes.empty:

        fig = px.bar(
            ranking_clientes.sort_values(
                "Quantidade de reclamações",
                ascending=True
            ),
            x="Quantidade de reclamações",
            y="Cliente",
            orientation="h",
            text="Quantidade de reclamações",
            title="Top 10 clientes"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:
        st.info("Ainda não existem clientes cadastrados.")

    # ================================================
    # RANKING DE PRODUTOS
    # ================================================

    st.subheader("Produtos com mais ocorrências")

    ranking_produtos = (
        df["produto"]
        .replace("", pd.NA)
        .dropna()
        .value_counts()
        .head(10)
        .rename_axis("Produto")
        .reset_index(name="Ocorrências")
    )

    if not ranking_produtos.empty:

        fig = px.bar(
            ranking_produtos.sort_values(
                "Ocorrências",
                ascending=True
            ),
            x="Ocorrências",
            y="Produto",
            orientation="h",
            text="Ocorrências",
            title="Top 10 produtos"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:
        st.info("Ainda não existem produtos cadastrados.")

    st.divider()

    # ================================================
    # ÚLTIMAS OCORRÊNCIAS
    # ================================================

    st.subheader("Últimas ocorrências")

    if not df.empty:

        st.dataframe(
            df[
                [
                    "id",
                    "data_registro",
                    "cliente",
                    "pedido",
                    "produto",
                    "lote",
                    "tipo_problema",
                    "status",
                    "valor_cupom",
                    "valor_lalamove"
                ]
            ].tail(10).iloc[::-1],
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("Nenhuma ocorrência cadastrada até o momento.")


# =====================================================
# NOVA OCORRÊNCIA
# =====================================================

elif pagina == "nova":

    st.title("Cadastrar ocorrência")
    st.caption("Registre os dados do cliente, produto e problema identificado.")

    st.markdown(
        '<div class="etapa">Identificação do produto</div>',
        unsafe_allow_html=True
    )

    c1, c2 = st.columns([1, 2])

    categoria = c1.selectbox(
        "Categoria",
        list(PRODUTOS.keys()),
        key="nova_categoria"
    )

    produto = c2.selectbox(
        "Produto e código",
        PRODUTOS[categoria],
        key="novo_produto"
    )

    with st.form("form_ocorrencia", clear_on_submit=True):

        st.markdown(
            '<div class="etapa">Dados do cliente</div>',
            unsafe_allow_html=True
        )

        c1, c2 = st.columns(2)

        cliente = c1.text_input("Nome do cliente *")
        documento = c2.text_input("CNPJ ou CPF")

        c1, c2 = st.columns(2)

        pedido = c1.text_input("Número do pedido")

        data_reclamacao = c2.date_input(
            "Data da reclamação",
            value=date.today(),
            format="DD/MM/YYYY"
        )

        st.markdown(
            '<div class="etapa">Dados do lote</div>',
            unsafe_allow_html=True
        )

        c1, c2 = st.columns(2)

        lote = c1.text_input("Lote de fabricação")
        quantidade = c2.text_input("Quantidade afetada")

        fabricacao = st.date_input(
            "Data de fabricação",
            value=date.today(),
            format="DD/MM/YYYY",
            key="data_fabricacao_nova"
        )

        st.markdown(
            '<div class="etapa">Detalhes da ocorrência</div>',
            unsafe_allow_html=True
        )

        c1, c2 = st.columns(2)

        tipo_problema = c1.selectbox(
            "Tipo de problema",
            PROBLEMAS
        )

        responsavel = c2.text_input(
            "Responsável pelo acompanhamento"
        )

        descricao = st.text_area(
            "Descrição detalhada",
            placeholder="Descreva o relato do cliente, as condições do produto e o que foi observado...",
            height=130
        )

        st.markdown(
            '<div class="etapa">Fotos e evidências</div>',
            unsafe_allow_html=True
        )

        arquivos = st.file_uploader(
            "Anexar fotos e documentos",
            accept_multiple_files=True
        )

        enviar = st.form_submit_button(
            "CADASTRAR OCORRÊNCIA",
            type="primary",
            use_container_width=True
        )

    if enviar:

        if not cliente.strip():
            st.error("Preencha o nome do cliente.")

        elif not descricao.strip():
            st.error("Preencha a descrição da ocorrência.")

        elif fabricacao > data_reclamacao:
            st.error("A fabricação não pode ser posterior à reclamação.")

        else:

            anexos = [
                salvar_anexo(arq)
                for arq in (arquivos or [])
            ]

            novo_id = proximo_id(df)
            agora = datetime.now().strftime("%d/%m/%Y %H:%M")

            linha = {
                "id": str(novo_id),
                "data_registro": agora,
                "cliente": cliente.strip(),
                "documento": documento.strip(),
                "pedido": pedido.strip(),
                "produto": produto,
                "lote": lote.strip(),
                "fabricacao": fabricacao.strftime("%Y-%m-%d"),
                "data_reclamacao": data_reclamacao.strftime("%Y-%m-%d"),
                "quantidade": quantidade.strip(),
                "tipo_problema": tipo_problema,
                "descricao": descricao.strip(),
                "status": "Sem resposta",
                "responsavel": responsavel.strip(),
                "anexos": "|".join(anexos),
                "historico": (
                    f"{agora} | Ocorrência cadastrada | Status: Sem resposta"
                ),
                "tipo_resolucao": "",
                "valor_cupom": "",
                "valor_lalamove": "",
                "descricao_resolucao": "",
                "data_resolucao": ""
            }

            df = pd.concat(
                [df, pd.DataFrame([linha])],
                ignore_index=True
            )

            salvar_dados(df)

            st.success(f"Ocorrência #{novo_id} cadastrada com sucesso!")

            dias = dias_ate_reclamacao(
                produto,
                fabricacao,
                data_reclamacao
            )

            prazo = obter_prazo_validade(produto)

            if dias is not None and prazo is not None:

                if dias > prazo:
                    st.warning(
                        f"A reclamação ocorreu {dias} dias após a fabricação. "
                        f"O prazo de referência para este produto é de {prazo} dias."
                    )

                else:
                    st.success(
                        f"Reclamação dentro do prazo de referência: "
                        f"{dias} dia(s). Prazo: {prazo} dias."
                    )

            st.rerun()

# =====================================================
# CONSULTAR OCORRÊNCIAS
# =====================================================

# =====================================================
# CONSULTAR OCORRÊNCIAS
# =====================================================

elif pagina == "consulta":

    st.title("Consultar ocorrências")
    st.caption("Pesquise, filtre e acompanhe os registros.")

    if df.empty:

        st.info("Nenhuma ocorrência cadastrada.")

    else:

        st.markdown(
            '<div class="etapa">Filtros de pesquisa</div>',
            unsafe_allow_html=True
        )

        # LISTAS DOS FILTROS

        problemas = sorted([
            p for p in df["tipo_problema"].dropna().unique().tolist()
            if str(p).strip()
        ])

        # CAMPOS DE PESQUISA

        c1, c2, c3 = st.columns([2, 1, 1])

        busca = c1.text_input(
            "Pesquisar cliente, pedido, produto ou lote",
            placeholder="Digite sua pesquisa...",
            key="busca_consulta"
        )

        status_opcoes = ["Todos"] + STATUS

        status_filtro = c2.selectbox(
            "Status",
            status_opcoes,
            index=0,
            key="status_consulta"
        )

        problema_opcoes = ["Todos"] + problemas

        problema_filtro = c3.selectbox(
            "Tipo de problema",
            problema_opcoes,
            index=0,
            key="problema_consulta"
        )

        st.divider()

        # APLICAR FILTROS

        filtrado = df.copy()

        if busca.strip():

            mascara = filtrado[
                ["cliente", "pedido", "produto", "lote"]
            ].apply(
                lambda coluna: coluna.str.contains(
                    busca.strip(),
                    case=False,
                    na=False,
                    regex=False
                )
            ).any(axis=1)

            filtrado = filtrado[mascara]

        if status_filtro != "Todos":

            filtrado = filtrado[
                filtrado["status"] == status_filtro
            ]

        if problema_filtro != "Todos":

            filtrado = filtrado[
                filtrado["tipo_problema"] == problema_filtro
            ]

        # INDICADORES DA PESQUISA

        total_filtrado = len(filtrado)

        pendentes_filtrados = int(
            filtrado["status"].isin(
                ["Sem resposta", "Em análise"]
            ).sum()
        )

        resolvidos_filtrados = int(
            (filtrado["status"] == "Resolvido").sum()
        )

        st.markdown("### Resultado da pesquisa")

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Ocorrências encontradas",
            total_filtrado
        )

        c2.metric(
            "Pendentes",
            pendentes_filtrados
        )

        c3.metric(
            "Resolvidas",
            resolvidos_filtrados
        )

        # TABELA COM STATUS COLORIDOS

        if filtrado.empty:

            st.warning(
                "Nenhuma ocorrência encontrada com os filtros selecionados."
            )

        else:

            tabela = filtrado[
                [
                    "id",
                    "data_registro",
                    "cliente",
                    "pedido",
                    "produto",
                    "lote",
                    "tipo_problema",
                    "status"
                ]
            ].copy()

            tabela.columns = [
                "ID",
                "Data do registro",
                "Cliente",
                "Pedido",
                "Produto",
                "Lote",
                "Tipo de problema",
                "Status"
            ]

            def colorir_status(valor):

                estilos = {
                    "Sem resposta": (
                        "background-color: #542522;"
                        "color: #FF938B;"
                        "font-weight: bold;"
                    ),
                    "Em análise": (
                        "background-color: #49351F;"
                        "color: #F2BD78;"
                        "font-weight: bold;"
                    ),
                    "Resolvido": (
                        "background-color: #203D2A;"
                        "color: #8BD6A0;"
                        "font-weight: bold;"
                    )
                }

                return estilos.get(valor, "")

            tabela_formatada = tabela.style.map(
                colorir_status,
                subset=["Status"]
            )

            st.dataframe(
                tabela_formatada,
                use_container_width=True,
                hide_index=True
            )

            # SELECIONAR OCORRÊNCIA

            st.markdown(
                '<div class="etapa">Visualizar ocorrência</div>',
                unsafe_allow_html=True
            )

            escolhido = st.selectbox(
                "Selecione uma ocorrência",
                filtrado["id"].astype(str).tolist(),
                format_func=lambda x: (
                    f"#{x} | "
                    f"{buscar_registro(filtrado, x)['cliente'] or 'Cliente não informado'} | "
                    f"{buscar_registro(filtrado, x)['produto'] or 'Produto não informado'}"
                ),
                key="ocorrencia_visualizacao"
            )

            reg = buscar_registro(df, escolhido)

            if reg is not None:

                st.subheader(f"Ocorrência #{escolhido}")

                c1, c2 = st.columns(2)

                with c1:

                    st.write(
                        "**Cliente:**",
                        reg["cliente"] or "Não informado"
                    )

                    st.write(
                        "**Documento:**",
                        reg["documento"] or "Não informado"
                    )

                    st.write(
                        "**Pedido:**",
                        reg["pedido"] or "Não informado"
                    )

                    st.write(
                        "**Produto:**",
                        reg["produto"] or "Não informado"
                    )

                with c2:

                    st.write(
                        "**Lote:**",
                        reg["lote"] or "Não informado"
                    )

                    st.write(
                        "**Quantidade:**",
                        reg["quantidade"] or "Não informada"
                    )

                    st.write(
                        "**Problema:**",
                        reg["tipo_problema"] or "Não informado"
                    )

                    st.write(
                        "**Responsável:**",
                        reg["responsavel"] or "Não informado"
                    )

                c1, c2 = st.columns(2)

                c1.write(
                    "**Data de fabricação:** "
                    + formatar_data(reg["fabricacao"])
                )

                c2.write(
                    "**Data da reclamação:** "
                    + formatar_data(reg["data_reclamacao"])
                )

                st.write("**Descrição da ocorrência**")

                st.info(
                    reg["descricao"] or "Nenhuma descrição cadastrada."
                )

                st.write("**Status atual**")
                exibir_status(reg["status"])

                exibir_anexos(
                    reg,
                    f"consulta_{escolhido}"
                )

                st.divider()

                st.subheader("Atualizar acompanhamento")

                with st.form(f"form_atualizar_{escolhido}"):

                    novo_status = st.selectbox(
                        "Status",
                        STATUS,
                        index=(
                            STATUS.index(reg["status"])
                            if reg["status"] in STATUS else 0
                        ),
                        key=f"novo_status_{escolhido}"
                    )

                    novo_responsavel = st.text_input(
                        "Responsável",
                        value=reg["responsavel"],
                        key=f"novo_responsavel_{escolhido}"
                    )

                    observacao = st.text_area(
                        "Observação da atualização",
                        placeholder="Registre o andamento ou a informação recebida...",
                        key=f"observacao_{escolhido}"
                    )

                    atualizar = st.form_submit_button(
                        "SALVAR ATUALIZAÇÃO",
                        use_container_width=True
                    )

                if atualizar:

                    indice = indice_por_id(df, escolhido)

                    if indice is None:

                        st.error(
                            "Não foi possível identificar uma única ocorrência."
                        )

                    else:

                        status_anterior = df.at[indice, "status"]

                        df.at[indice, "status"] = novo_status

                        df.at[indice, "responsavel"] = (
                            novo_responsavel.strip()
                        )

                        registrar_evento(
                            df,
                            escolhido,
                            (
                                f"Status: {status_anterior} para {novo_status} "
                                f"| Responsável: {novo_responsavel.strip()} "
                                f"| Observação: {observacao.strip()}"
                            )
                        )

                        salvar_dados(df)

                        st.success(
                            "Acompanhamento atualizado com sucesso!"
                        )

                        st.rerun()

                # HISTÓRICO

                st.subheader("Histórico da ocorrência")

                historico = str(reg["historico"]).split("\n")

                if any(evento.strip() for evento in historico):

                    for evento in historico:

                        if evento.strip():
                            st.info(evento)

                else:

                    st.caption(
                        "Nenhum evento registrado."
                    )

                # SOLUÇÃO REGISTRADA

                if str(reg["tipo_resolucao"]).strip():

                    st.subheader("Solução registrada")

                    st.write(
                        "**Tipo:**",
                        reg["tipo_resolucao"]
                    )

                    if reg["tipo_resolucao"] == "Cupom":

                        st.write(
                            "**Valor do cupom:**",
                            dinheiro(reg["valor_cupom"])
                        )

                    elif reg["tipo_resolucao"] == "Troca de caixa":

                        st.write(
                            "**Valor do Lalamove:**",
                            dinheiro(reg["valor_lalamove"])
                        )

                    st.write(
                        "**Descrição:**",
                        reg["descricao_resolucao"]
                    )

                    st.write(
                        "**Data da resolução:**",
                        reg["data_resolucao"] or "Não informada"
                    )


# =====================================================
# RESOLUÇÃO DE PROBLEMAS
# =====================================================

elif pagina == "resolucao":

    st.title("Resolução de problemas")
    st.caption("Registre a solução aplicada e os valores envolvidos.")

    if df.empty:

        st.info("Nenhuma ocorrência cadastrada.")

    else:

        pendentes = df[
            df["status"] != "Resolvido"
        ].copy()

        if pendentes.empty:

            st.success("Todas as ocorrências estão resolvidas.")

        else:

            escolhido = st.selectbox(
                "Selecione a ocorrência",
                pendentes["id"].astype(str).tolist(),
                format_func=lambda x: (
                    f"#{x} | "
                    f"{buscar_registro(pendentes, x)['cliente'] or 'Cliente não informado'} | "
                    f"{buscar_registro(pendentes, x)['produto'] or 'Produto não informado'}"
                ),
                key="selecao_resolucao"
            )

            reg = buscar_registro(df, escolhido)

            if reg is not None:

                st.subheader("Informações da ocorrência")

                c1, c2 = st.columns(2)

                with c1:
                    st.write("**Cliente:**", reg["cliente"] or "Não informado")
                    st.write("**Documento:**", reg["documento"] or "Não informado")
                    st.write("**Pedido:**", reg["pedido"] or "Não informado")
                    st.write("**Produto:**", reg["produto"] or "Não informado")

                with c2:
                    st.write("**Lote:**", reg["lote"] or "Não informado")
                    st.write("**Problema:**", reg["tipo_problema"] or "Não informado")
                    st.write("**Status:**", reg["status"] or "Não informado")
                    st.write("**Quantidade:**", reg["quantidade"] or "Não informada")

                c1, c2 = st.columns(2)

                c1.write(
                    "**Data da reclamação:** "
                    + formatar_data(reg["data_reclamacao"])
                )

                c2.write(
                    "**Data de fabricação:** "
                    + formatar_data(reg["fabricacao"])
                )

                st.write("**Descrição da ocorrência**")
                st.info(reg["descricao"] or "Nenhuma descrição cadastrada.")

                exibir_anexos(reg, f"resolucao_{escolhido}")

                st.divider()

                st.subheader("Registrar resolução")

                with st.form(f"form_resolucao_{escolhido}"):

                    tipos_resolucao = ["Cupom", "Troca de caixa"]

                    tipo_atual = (
                        reg["tipo_resolucao"]
                        if reg["tipo_resolucao"] in tipos_resolucao
                        else "Cupom"
                    )

                    tipo = st.selectbox(
                        "Forma de resolução",
                        tipos_resolucao,
                        index=tipos_resolucao.index(tipo_atual),
                        key=f"tipo_resolucao_{escolhido}"
                    )

                    valor_cupom = 0.0
                    valor_lalamove = 0.0

                    if tipo == "Cupom":

                        valor_cupom = st.number_input(
                            "Valor do cupom (R$)",
                            min_value=0.0,
                            value=converter_valor(reg["valor_cupom"]),
                            step=1.0,
                            format="%.2f",
                            key=f"valor_cupom_{escolhido}"
                        )

                    else:

                        valor_lalamove = st.number_input(
                            "Valor do Lalamove (R$)",
                            min_value=0.0,
                            value=converter_valor(reg["valor_lalamove"]),
                            step=1.0,
                            format="%.2f",
                            key=f"valor_lalamove_{escolhido}"
                        )

                    descricao_solucao = st.text_area(
                        "Descreva como o problema foi resolvido",
                        value=reg["descricao_resolucao"],
                        height=120,
                        key=f"descricao_solucao_{escolhido}"
                    )

                    responsavel_solucao = st.text_input(
                        "Responsável pela resolução",
                        value=reg["responsavel"],
                        key=f"responsavel_solucao_{escolhido}"
                    )

                    concluir = st.form_submit_button(
                        "SALVAR RESOLUÇÃO E CONCLUIR",
                        type="primary",
                        use_container_width=True
                    )

                if concluir:

                    if not descricao_solucao.strip():

                        st.error("Descreva como a ocorrência foi resolvida.")

                    else:

                        indice = indice_por_id(df, escolhido)

                        if indice is None:

                            st.error(
                                "Não foi possível identificar uma única ocorrência. "
                                "Verifique os IDs dos registros."
                            )

                        else:

                            # Salva a solução somente na ocorrência selecionada.
                            df.at[indice, "tipo_resolucao"] = tipo

                            df.at[indice, "valor_cupom"] = (
                                f"{valor_cupom:.2f}"
                                if tipo == "Cupom" else ""
                            )

                            df.at[indice, "valor_lalamove"] = (
                                f"{valor_lalamove:.2f}"
                                if tipo == "Troca de caixa" else ""
                            )

                            df.at[indice, "descricao_resolucao"] = (
                                descricao_solucao.strip()
                            )

                            df.at[indice, "data_resolucao"] = (
                                datetime.now().strftime("%d/%m/%Y %H:%M")
                            )

                            df.at[indice, "responsavel"] = (
                                responsavel_solucao.strip()
                            )

                            df.at[indice, "status"] = "Resolvido"

                            registrar_evento(
                                df,
                                escolhido,
                                (
                                    f"Resolução registrada: {tipo} "
                                    f"| Cupom: {dinheiro(valor_cupom)} "
                                    f"| Lalamove: {dinheiro(valor_lalamove)} "
                                    f"| Responsável: {responsavel_solucao.strip()} "
                                    f"| Descrição: {descricao_solucao.strip()}"
                                )
                            )

                            salvar_dados(df)

                            st.success(
                                f"Ocorrência #{escolhido} resolvida com sucesso!"
                            )

                            st.rerun()

# =====================================================
# ANÁLISE POR PRODUTO E LOTE
# =====================================================

elif pagina == "analise":

    st.title("Análise por produto e lote")
    st.caption("Identifique produtos, lotes e problemas recorrentes.")

    if df.empty:

        st.info("Ainda não existem dados para análise.")

    else:

        c1, c2 = st.columns(2)

        produto_filtro = c1.selectbox(
            "Produto",
            ["Todos"] + sorted(df["produto"].dropna().unique().tolist())
        )

        lote_busca = c2.text_input("Pesquisar lote")

        analise_df = df.copy()

        if produto_filtro != "Todos":
            analise_df = analise_df[
                analise_df["produto"] == produto_filtro
            ]

        if lote_busca:
            analise_df = analise_df[
                analise_df["lote"].str.contains(
                    lote_busca,
                    case=False,
                    na=False,
                    regex=False
                )
            ]

        c1, c2, c3 = st.columns(3)

        c1.metric("Ocorrências", len(analise_df))
        c2.metric("Clientes envolvidos", analise_df["cliente"].nunique())

        c3.metric(
            "Lotes identificados",
            analise_df["lote"].replace("", pd.NA).nunique()
        )

        resumo = (
            analise_df
            .groupby(["produto", "lote"], dropna=False)
            .size()
            .reset_index(name="Ocorrências")
            .sort_values("Ocorrências", ascending=False)
        )

        st.subheader("Resumo por produto e lote")

        st.dataframe(
            resumo,
            use_container_width=True,
            hide_index=True
        )

        if not analise_df.empty:

            problemas_df = (
                analise_df["tipo_problema"]
                .value_counts()
                .rename_axis("Problema")
                .reset_index(name="Quantidade")
            )

            fig = px.bar(
                problemas_df,
                x="Problema",
                y="Quantidade",
                title="Problemas encontrados"
            )

            fig.update_layout(
                paper_bgcolor="#15100d",
                plot_bgcolor="#15100d",
                font_color="#f4eee8"
            )

            st.plotly_chart(fig, use_container_width=True)

# =====================================================
# EXPORTAR DADOS
# =====================================================

elif pagina == "exportar":

    st.title("Exportar dados")
    st.caption("Exporte os registros e acompanhe os valores de resolução.")

    if df.empty:

        st.info("Não existem dados para exportar.")

    else:

        csv = df.to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            "BAIXAR RELATÓRIO CSV",
            csv,
            "relatorio_qualidade.csv",
            "text/csv",
            type="primary"
        )

        st.caption("O arquivo pode ser aberto no Excel.")

        st.write(
            f"Total de ocorrências disponíveis: {len(df)}"
        )

        gasto_cupons = (
            pd.to_numeric(df["valor_cupom"], errors="coerce")
            .fillna(0)
            .sum()
        )

        gasto_lalamove = (
            pd.to_numeric(df["valor_lalamove"], errors="coerce")
            .fillna(0)
            .sum()
        )

        c1, c2 = st.columns(2)

        c1.metric(
            "Total em cupons",
            dinheiro(gasto_cupons)
        )

        c2.metric(
            "Total em Lalamove",
            dinheiro(gasto_lalamove)
        )
