
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import datetime, date
import uuid
import html

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

    return preparar_dataframe(dados)


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
# DASHBOARD PROFISSIONAL
# =====================================================

if pagina == "dashboard":

    st.title("Dashboard | Gestão da Qualidade")
    st.caption(
        "Acompanhe ocorrências, problemas recorrentes e custos de resolução."
    )

    dados_dashboard = df.copy()

    dados_dashboard["data_grafico"] = pd.to_datetime(
        dados_dashboard["data_registro"],
        format="%d/%m/%Y %H:%M",
        errors="coerce"
    )

    datas_validas = dados_dashboard["data_grafico"].dropna()

    st.markdown("### Filtros")

    f1, f2, f3 = st.columns([2, 1, 1])

    if not datas_validas.empty:
        data_inicial = datas_validas.min().date()
        data_final = datas_validas.max().date()
    else:
        data_inicial = date.today()
        data_final = date.today()

    periodo = f1.date_input(
        "Período de registro",
        value=(data_inicial, data_final),
        format="DD/MM/YYYY",
        key="dashboard_periodo"
    )

    status_filtro = f2.selectbox(
        "Status",
        ["Todos"] + STATUS,
        key="dashboard_status"
    )

    problemas_disponiveis = sorted([
        problema
        for problema in dados_dashboard["tipo_problema"].dropna().unique()
        if str(problema).strip()
    ])

    problema_filtro = f3.selectbox(
        "Tipo de problema",
        ["Todos"] + problemas_disponiveis,
        key="dashboard_problema"
    )

    if isinstance(periodo, (tuple, list)) and len(periodo) == 2:
        inicio, fim = periodo
    else:
        inicio = fim = periodo

    if inicio > fim:
        st.warning("A data inicial não pode ser posterior à data final.")
        inicio, fim = fim, inicio

    filtrado = dados_dashboard[
        dados_dashboard["data_grafico"].dt.date.between(inicio, fim)
    ].copy()

    if status_filtro != "Todos":
        filtrado = filtrado[
            filtrado["status"] == status_filtro
        ]

    if problema_filtro != "Todos":
        filtrado = filtrado[
            filtrado["tipo_problema"] == problema_filtro
        ]

    st.divider()

    if filtrado.empty:
        st.info("Nenhuma ocorrência encontrada para os filtros selecionados.")

    else:
        total = len(filtrado)

        sem_resposta = int(
            (filtrado["status"] == "Sem resposta").sum()
        )
        em_analise = int(
            (filtrado["status"] == "Em análise").sum()
        )
        resolvidas = int(
            (filtrado["status"] == "Resolvido").sum()
        )
        pendentes = sem_resposta + em_analise

        percentual_resolvido = (
            resolvidas / total * 100 if total else 0
        )

        custo_cupons = (
            pd.to_numeric(filtrado["valor_cupom"], errors="coerce")
            .fillna(0)
            .sum()
        )
        custo_lalamove = (
            pd.to_numeric(filtrado["valor_lalamove"], errors="coerce")
            .fillna(0)
            .sum()
        )
        custo_total = custo_cupons + custo_lalamove

        def moeda_dashboard(valor):
            return (
                f"R$ {valor:,.2f}"
                .replace(",", "X")
                .replace(".", ",")
                .replace("X", ".")
            )

        st.markdown("### Indicadores do período")

        k1, k2, k3, k4 = st.columns(4)

        k1.metric("Ocorrências", total)
        k2.metric("Pendentes", pendentes)
        k3.metric("Resolvidas", resolvidas)
        k4.metric(
            "Taxa de resolução",
            f"{percentual_resolvido:.1f}%"
        )

        c1, c2, c3 = st.columns(3)
        c1.metric("Custo em cupons", moeda_dashboard(custo_cupons))
        c2.metric("Custo em Lalamove", moeda_dashboard(custo_lalamove))
        c3.metric("Custo total", moeda_dashboard(custo_total))

        st.divider()
        grafico1, grafico2 = st.columns(2)

        with grafico1:
            dados_status = pd.DataFrame({
                "Status": [
                    "Sem resposta",
                    "Em análise",
                    "Resolvido"
                ],
                "Quantidade": [
                    sem_resposta,
                    em_analise,
                    resolvidas
                ]
            })

            dados_status = dados_status[
                dados_status["Quantidade"] > 0
            ]

            fig_status = px.pie(
                dados_status,
                names="Status",
                values="Quantidade",
                title="Ocorrências por status",
                color="Status",
                color_discrete_map={
                    "Sem resposta": "#C9443C",
                    "Em análise": "#BD8046",
                    "Resolvido": "#43865B"
                },
                hole=0.58
            )

            fig_status.update_layout(
                paper_bgcolor="#15100d",
                plot_bgcolor="#15100d",
                font_color="#f4eee8",
                legend_title_text=""
            )

            st.plotly_chart(
                fig_status,
                use_container_width=True
            )

        with grafico2:
            dados_problemas = (
                filtrado["tipo_problema"]
                .replace("", "Não informado")
                .value_counts()
                .rename_axis("Problema")
                .reset_index(name="Ocorrências")
            )

            fig_problemas = px.bar(
                dados_problemas,
                x="Ocorrências",
                y="Problema",
                orientation="h",
                text="Ocorrências",
                title="Problemas mais frequentes"
            )

            fig_problemas.update_layout(
                paper_bgcolor="#15100d",
                plot_bgcolor="#15100d",
                font_color="#f4eee8",
                yaxis={"categoryorder": "total ascending"}
            )

            st.plotly_chart(
                fig_problemas,
                use_container_width=True
            )

        grafico3, grafico4 = st.columns(2)

        with grafico3:
            dados_produtos = (
                filtrado["produto"]
                .replace("", "Não informado")
                .value_counts()
                .head(10)
                .rename_axis("Produto")
                .reset_index(name="Ocorrências")
            )

            fig_produtos = px.bar(
                dados_produtos,
                x="Ocorrências",
                y="Produto",
                orientation="h",
                text="Ocorrências",
                title="Top 10 produtos com mais ocorrências"
            )

            fig_produtos.update_layout(
                paper_bgcolor="#15100d",
                plot_bgcolor="#15100d",
                font_color="#f4eee8",
                yaxis={"categoryorder": "total ascending"}
            )

            st.plotly_chart(
                fig_produtos,
                use_container_width=True
            )

        with grafico4:
            mensal = filtrado.dropna(
                subset=["data_grafico"]
            ).copy()

            if not mensal.empty:
                mensal["Mês"] = (
                    mensal["data_grafico"]
                    .dt.to_period("M")
                    .astype(str)
                )

                mensal_resumo = (
                    mensal.groupby("Mês")
                    .size()
                    .reset_index(name="Ocorrências")
                    .sort_values("Mês")
                )

                fig_mensal = px.line(
                    mensal_resumo,
                    x="Mês",
                    y="Ocorrências",
                    markers=True,
                    text="Ocorrências",
                    title="Evolução mensal"
                )

                fig_mensal.update_layout(
                    paper_bgcolor="#15100d",
                    plot_bgcolor="#15100d",
                    font_color="#f4eee8"
                )

                st.plotly_chart(
                    fig_mensal,
                    use_container_width=True
                )
            else:
                st.info("Não há datas válidas para exibir a evolução mensal.")

        st.subheader("Ocorrências recentes")

        ultimas = (
            filtrado.sort_values(
                "data_grafico",
                ascending=False,
                na_position="last"
            )
            .head(10)
        )

        st.dataframe(
            ultimas[
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
            ],
            use_container_width=True,
            hide_index=True
        )

    # ---------------------------------------------
    # TRATAMENTO DOS DADOS
    # ---------------------------------------------

    total = len(df)

    sem_resposta = int(
        (df["status"] == "Sem resposta").sum()
    )

    em_analise = int(
        (df["status"] == "Em análise").sum()
    )

    resolvidas = int(
        (df["status"] == "Resolvido").sum()
    )

    pendentes = sem_resposta + em_analise

    custo_cupons = (
        pd.to_numeric(df["valor_cupom"], errors="coerce")
        .fillna(0)
        .sum()
    )

    custo_lalamove = (
        pd.to_numeric(df["valor_lalamove"], errors="coerce")
        .fillna(0)
        .sum()
    )

    custo_total = custo_cupons + custo_lalamove

    def moeda_dashboard(valor):
        return (
            f"R$ {valor:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

    # ---------------------------------------------
    # INDICADORES PRINCIPAIS
    # ---------------------------------------------

    st.markdown("### Indicadores gerais")

    c1, c2, c3, c4 = st.columns(4)

    indicadores = [
        (c1, "TOTAL DE OCORRÊNCIAS", total, "#E8B16E"),
        (c2, "PENDENTES", pendentes, "#D65A50"),
        (c3, "RESOLVIDAS", resolvidas, "#5A9B6B"),
        (c4, "CUSTO TOTAL", moeda_dashboard(custo_total), "#E8B16E")
    ]

    for coluna, titulo, valor, cor in indicadores:

        with coluna:

            st.markdown(
                f"""
                <div class="cartao" style="min-height:145px;">
                    <div class="cartao-titulo">
                        {titulo}
                    </div>
                    <div class="cartao-numero"
                         style="color:{cor}; font-size:30px;">
                        {valor}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("")

    # ---------------------------------------------
    # DETALHAMENTO DOS CUSTOS
    # ---------------------------------------------

    st.markdown("### Controle financeiro")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Total em cupons",
        moeda_dashboard(custo_cupons)
    )

    c2.metric(
        "Total em Lalamove",
        moeda_dashboard(custo_lalamove)
    )

    c3.metric(
        "Custo total das resoluções",
        moeda_dashboard(custo_total)
    )

    st.divider()

    # ---------------------------------------------
    # GRÁFICOS
    # ---------------------------------------------

    if total > 0:

        col1, col2 = st.columns(2)

        with col1:

            dados_status = pd.DataFrame({
                "Status": [
                    "Sem resposta",
                    "Em análise",
                    "Resolvido"
                ],
                "Quantidade": [
                    sem_resposta,
                    em_analise,
                    resolvidas
                ]
            })

            dados_status = dados_status[
                dados_status["Quantidade"] > 0
            ]

            fig = px.pie(
                dados_status,
                names="Status",
                values="Quantidade",
                title="Distribuição das ocorrências",
                color="Status",
                color_discrete_map={
                    "Sem resposta": "#C9443C",
                    "Em análise": "#BD8046",
                    "Resolvido": "#43865B"
                },
                hole=0.58
            )

            fig.update_layout(
                paper_bgcolor="#15100d",
                plot_bgcolor="#15100d",
                font_color="#f4eee8",
                legend_title_text=""
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        with col2:

            dados_problemas = (
                df["tipo_problema"]
                .replace("", "Não informado")
                .value_counts()
                .reset_index()
            )

            dados_problemas.columns = [
                "Problema",
                "Quantidade"
            ]

            fig = px.bar(
                dados_problemas,
                x="Quantidade",
                y="Problema",
                orientation="h",
                title="Principais tipos de problemas",
                text="Quantidade"
            )

            fig.update_layout(
                paper_bgcolor="#15100d",
                plot_bgcolor="#15100d",
                font_color="#f4eee8",
                yaxis={"categoryorder": "total ascending"}
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        # -----------------------------------------
        # PRODUTOS COM MAIS OCORRÊNCIAS
        # -----------------------------------------

        st.subheader("Produtos com mais ocorrências")

        produtos_df = (
            df["produto"]
            .replace("", "Não informado")
            .value_counts()
            .head(10)
            .reset_index()
        )

        produtos_df.columns = [
            "Produto",
            "Ocorrências"
        ]

        fig = px.bar(
            produtos_df,
            x="Produto",
            y="Ocorrências",
            text="Ocorrências",
            title="Ranking dos 10 produtos"
        )

        fig.update_layout(
            paper_bgcolor="#15100d",
            plot_bgcolor="#15100d",
            font_color="#f4eee8",
            xaxis_tickangle=-35
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # -----------------------------------------
        # EVOLUÇÃO MENSAL
        # -----------------------------------------

        st.subheader("Evolução mensal das ocorrências")

        mensal = df.copy()

        mensal["data_grafico"] = pd.to_datetime(
            mensal["data_registro"],
            format="%d/%m/%Y %H:%M",
            errors="coerce"
        )

        mensal = mensal.dropna(
            subset=["data_grafico"]
        )

        if not mensal.empty:

            mensal["Mês"] = (
                mensal["data_grafico"]
                .dt.to_period("M")
                .astype(str)
            )

            mensal_resumo = (
                mensal.groupby("Mês")
                .size()
                .reset_index(name="Ocorrências")
            )

            fig = px.line(
                mensal_resumo,
                x="Mês",
                y="Ocorrências",
                markers=True,
                title="Quantidade de reclamações por mês"
            )

            fig.update_layout(
                paper_bgcolor="#15100d",
                plot_bgcolor="#15100d",
                font_color="#f4eee8"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        # -----------------------------------------
        # ÚLTIMAS OCORRÊNCIAS
        # -----------------------------------------

        st.subheader("Últimas ocorrências registradas")

        ultimas = df.tail(10).iloc[::-1]

        st.dataframe(
            ultimas[
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
            ],
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "Ainda não existem ocorrências cadastradas para gerar os gráficos."
        )

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
