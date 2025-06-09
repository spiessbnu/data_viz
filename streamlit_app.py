import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==============================================
# 1) Configuração da Página
# ==============================================
st.set_page_config(
    page_title="Dashboard Vale do Itajaí (SC)",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================
# 2) Função para Carregar e Preparar os Dados
# ==============================================
@st.cache_data
def load_data():
    """
    Carrega, valida e prepara os dados do arquivo Excel.
    A anotação @st.cache_data garante que os dados sejam carregados apenas uma vez.
    """
    try:
        df = pd.read_excel("municipios_2025_atualizado.xlsx")
    except FileNotFoundError:
        st.error("Erro: O arquivo 'municipios_2025_atualizado.xlsx' não foi encontrado. Por favor, coloque-o no mesmo diretório do seu script.")
        st.stop()

    # Validação de colunas essenciais
    colunas_esperadas = [
        "Municipio", "cod_IBGE", "IDH-M_2010", "Populacao_2010", "Densidade_2010",
        "Populacao_2022", "Densidade_2022", "PIBcapita_2019", "PIBcapita_2021",
        "Crescimento_populacional_abs", "Crescimento_populacional_pct",
        "Crescimento_PIBcapita_abs", "Crescimento_PIBcapita_pct"
    ]
    colunas_faltando = [c for c in colunas_esperadas if c not in df.columns]
    if colunas_faltando:
        st.error(f"Erro de Validação: As seguintes colunas obrigatórias não foram encontradas no arquivo Excel: {colunas_faltando}. Por favor, verifique os cabeçalhos.")
        st.stop()

    # Conversão segura para tipos numéricos
    for col in colunas_esperadas:
        if col not in ["Municipio", "cod_IBGE"]:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Remove linhas onde dados essenciais são nulos
    df = df.dropna(subset=["Municipio", "Populacao_2022", "PIBcapita_2021", "IDH-M_2010"])
    
    # Ordena o DataFrame por município
    df = df.sort_values("Municipio").reset_index(drop=True)
    return df

# Carrega os dados e trata possíveis erros
df = load_data()

# ==============================================
# 3) Barra Lateral com Informações (Sidebar)
# ==============================================
with st.sidebar:
    st.header("Sobre o App")
    st.info(
        """
        **Dados:** Análise multianual de indicadores municipais do Vale do Itajaí (SC).  
        **Fonte:** IBGE (2025)  
        **Desenvolvimento:** App criado com Streamlit e Plotly.  
        
        *Ciência de Dados 2025 - Prof. Maiko Spiess*
        """
    )

# ==============================================
# 4) Título Principal e Introdução
# ==============================================
st.title("📊 Dashboard Interativo: Vale do Itajaí (SC)")
st.markdown(
    """
    Explore indicadores demográficos e econômicos dos municípios do Vale do Itajaí. 
    Use as abas abaixo para navegar entre as diferentes análises.
    """
)

# ==============================================
# 5) Métricas de Destaque (KPIs)
# ==============================================
st.markdown("### Indicadores Gerais do Vale do Itajaí (2022)")

# Calcula as métricas
total_municipios = df["Municipio"].nunique()
populacao_total_2022 = df["Populacao_2022"].sum()
pib_medio_2021 = df["PIBcapita_2021"].mean()
idh_medio_2010 = df["IDH-M_2010"].mean()

# Exibe as métricas em colunas
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Nº de Municípios", value=f"{total_municipios}")
with col2:
    st.metric(label="População Total", value=f"{populacao_total_2022:,.0f}".replace(",", "."))
with col3:
    st.metric(label="PIB per capita Médio (2021)", value=f"R$ {pib_medio_2021:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
with col4:
    st.metric(label="IDH-M Médio (2010)", value=f"{idh_medio_2010:.3f}")

st.markdown("<br>", unsafe_allow_html=True)

# ==============================================
# 6) Funções de Plotagem (Títulos Atualizados)
# ==============================================
def plot_top10_combined(df):
    """Gera gráficos de barras para Top 10 População e Densidade."""
    top10_pop = df.nlargest(10, "Populacao_2022").sort_values("Populacao_2022", ascending=True)
    top10_den = df.nlargest(10, "Densidade_2022").sort_values("Densidade_2022", ascending=True)
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(
            "<b>Top 10 População (2022)</b>", 
            "<b>Top 10 Densidade (2022)</b>"
        ),
        horizontal_spacing=0.15
    )
    
    fig.add_trace(go.Bar(
        x=top10_pop["Populacao_2022"], y=top10_pop["Municipio"], orientation="h",
        name="População", marker_color="#1f77b4",
        hovertemplate="<b>%{y}</b><br>População: %{x:,}<extra></extra>"
    ), row=1, col=1)
    
    fig.add_trace(go.Bar(
        x=top10_den["Densidade_2022"], y=top10_den["Municipio"], orientation="h",
        name="Densidade", marker_color="#ff7f0e",
        hovertemplate="<b>%{y}</b><br>Densidade: %{x:,.2f} hab/km²<extra></extra>"
    ), row=1, col=2)
    
    fig.update_layout(
        template="plotly_white", showlegend=False, height=500,
        margin=dict(l=120, r=20, t=50, b=40), font=dict(family="sans-serif")
    )
    fig.update_xaxes(title_text="Habitantes")
    fig.update_yaxes(showticklabels=True)
    return fig

def plot_hist_pib2021(df):
    """Gera o histograma da distribuição do PIB per capita 2021."""
    fig = px.histogram(
        df, x="PIBcapita_2021", nbins=40,
        labels={"PIBcapita_2021": "PIB per capita (R$) – 2021"},
        opacity=0.8, color_discrete_sequence=["#1f77b4"]
    )
    fig.update_layout(
        template="plotly_white", height=500,
        title_text="<b>Distribuição do PIB per capita - Vale do Itajaí (2021)</b>",
        yaxis_title="Número de Municípios", bargap=0.1, font=dict(family="sans-serif")
    )
    return fig

def plot_scatter_idh_vs_pib21(df):
    """Gera o gráfico de dispersão IDH vs. PIB."""
    fig = px.scatter(
        df, x="PIBcapita_2021", y="IDH-M_2010",
        size="Populacao_2022", color="Crescimento_populacional_pct",
        color_continuous_scale=px.colors.sequential.Viridis,
        hover_name="Municipio",
        labels={
            "PIBcapita_2021": "PIB per capita (R$) – 2021",
            "IDH-M_2010": "IDH-M (2010)",
            "Populacao_2022": "População (2022)",
            "Crescimento_populacional_pct": "Cresc. Pop. (%)"
        },
        size_max=50, opacity=0.7
    )

    fig.update_layout(
        template="plotly_white", height=600,
        title_text="<b>IDH (2010) vs. PIB per capita (2021) - Vale do Itajaí</b>",
        font=dict(family="sans-serif")
    )
    return fig

# ==============================================
# 7) Conteúdo Principal com Abas (Tabs)
# ==============================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📍 Visão Geral",
    "💰 Análise de Renda",
    "🧑‍🤝‍🧑 IDH vs. Renda",
    "📄 Explorar Dados"
])

with tab1:
    st.header("Top 10 Municípios do Vale do Itajaí por População e Densidade")
    fig_combined = plot_top10_combined(df)
    st.plotly_chart(fig_combined, use_container_width=True)

with tab2:
    st.header("Análise de Renda dos Municípios do Vale do Itajaí")
    fig_hist = plot_hist_pib2021(df)
    st.plotly_chart(fig_hist, use_container_width=True)

with tab3:
    st.header("Análise Cruzada: IDH, Renda e População no Vale do Itajaí")
    fig_scatter = plot_scatter_idh_vs_pib21(df)
    st.plotly_chart(fig_scatter, use_container_width=True)

with tab4:
    st.header("Explore os Dados Completos do Vale do Itajaí")
    st.markdown("Use os cabeçalhos das colunas para ordenar os dados. O campo de busca permite filtrar por qualquer valor na tabela.")
    st.dataframe(df, use_container_width=True, height=600)

# ==============================================
# 8) Rodapé
# ==============================================
st.markdown("---")
st.write("Dashboard desenvolvido como um exemplo de refatoração de app Streamlit com foco em design e interatividade.")
