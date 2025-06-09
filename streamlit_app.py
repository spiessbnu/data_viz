import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==============================================
# 1) Configuração da Página
# ==============================================
st.set_page_config(
    page_title="Dashboard de Municípios de SC",
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
    
    # Ordena o DataFrame por município para facilitar a busca nos filtros
    df = df.sort_values("Municipio").reset_index(drop=True)
    return df

# Carrega os dados e trata possíveis erros de forma elegante
df = load_data()

# ==============================================
# 3) Barra Lateral com Filtros (Sidebar)
# ==============================================
with st.sidebar:
    st.header("Filtros Interativos")
    st.markdown("Selecione um ou mais municípios para destacá-los nos gráficos.")

    # Filtro multiselect para destacar municípios
    municipios_selecionados = st.multiselect(
        label="Pesquise e selecione os municípios:",
        options=df["Municipio"].unique(),
        placeholder="Ex: Florianópolis, Blumenau..."
    )

    st.markdown("---")
    st.info(
        """
        **Sobre o App:**
        - **Dados:** Análise multianual de indicadores municipais de Santa Catarina.
        - **Fonte:** Dados fictícios baseados em fontes públicas.
        - **Desenvolvimento:** App criado com Streamlit e Plotly.
        """
    )

# ==============================================
# 4) Título Principal e Introdução
# ==============================================
st.title("📊 Dashboard Interativo: Municípios de SC")
st.markdown(
    """
    Explore indicadores demográficos e econômicos dos municípios de Santa Catarina. 
    Use as abas abaixo para navegar entre as diferentes análises e os filtros na barra lateral para destacar municípios de interesse.
    """
)

# ==============================================
# 5) Métricas de Destaque (KPIs)
# ==============================================
st.markdown("### Indicadores Gerais (2022)")

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

st.markdown("<br>", unsafe_allow_html=True) # Adiciona um espaço

# ==============================================
# 6) Funções de Plotagem (Refatoradas)
# ==============================================
def plot_top10_combined(df):
    """Gera gráficos de barras para Top 10 População e Densidade (2022)."""
    top10_pop = df.nlargest(10, "Populacao_2022").sort_values("Populacao_2022", ascending=True)
    top10_den = df.nlargest(10, "Densidade_2022").sort_values("Densidade_2022", ascending=True)
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("<b>Top 10 População (2022)</b>", "<b>Top 10 Densidade (2022)</b>"),
        horizontal_spacing=0.15
    )
    
    # Gráfico de População
    fig.add_trace(go.Bar(
        x=top10_pop["Populacao_2022"], y=top10_pop["Municipio"],
        orientation="h", name="População",
        marker_color="#1f77b4",
        hovertemplate="<b>%{y}</b><br>População: %{x:,}<extra></extra>"
    ), row=1, col=1)
    
    # Gráfico de Densidade
    fig.add_trace(go.Bar(
        x=top10_den["Densidade_2022"], y=top10_den["Municipio"],
        orientation="h", name="Densidade",
        marker_color="#ff7f0e",
        hovertemplate="<b>%{y}</b><br>Densidade: %{x:,.2f} hab/km²<extra></extra>"
    ), row=1, col=2)
    
    fig.update_layout(
        template="plotly_white", showlegend=False, height=500,
        margin=dict(l=120, r=20, t=50, b=40),
        font=dict(family="sans-serif")
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
        title_text="<b>Distribuição do PIB per capita (2021)</b>",
        yaxis_title="Número de Municípios",
        bargap=0.1,
        font=dict(family="sans-serif")
    )
    return fig

def plot_scatter_idh_vs_pib21(df, selection):
    """Gera o gráfico de dispersão IDH vs. PIB, destacando a seleção."""
    fig = px.scatter(
        df,
        x="PIBcapita_2021", y="IDH-M_2010",
        size="Populacao_2022", color="Crescimento_populacional_pct",
        color_continuous_scale=px.colors.sequential.Viridis,
        hover_name="Municipio",
        labels={
            "PIBcapita_2021": "PIB per capita (R$) – 2021",
            "IDH-M_2010": "IDH-M (2010)",
            "Populacao_2022": "População (2022)",
            "Crescimento_populacional_pct": "Cresc. Pop. (%)"
        },
        size_max=50, opacity=0.6
    )
    
    # Adiciona uma camada extra para destacar os municípios selecionados
    if selection:
        df_selected = df[df["Municipio"].isin(selection)]
        fig.add_trace(go.Scatter(
            x=df_selected["PIBcapita_2021"], y=df_selected["IDH-M_2010"],
            mode='markers',
            marker=dict(
                size=df_selected['Populacao_2022'] / (df['Populacao_2022'].max() / 50), # Escala similar ao px
                color='red',
                symbol='star',
                line=dict(width=1, color='black')
            ),
            name="Seleção",
            text=df_selected["Municipio"],
            hovertemplate="<b>%{text}</b> (Destacado)<br>PIB p/c: %{x:,.2f}<br>IDH-M: %{y:.3f}<extra></extra>"
        ))

    fig.update_layout(
        template="plotly_white", height=600,
        title_text="<b>Relação entre IDH (2010) e PIB per capita (2021)</b>",
        font=dict(family="sans-serif"),
        legend=dict(title_text='Legenda')
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
    st.header("Top 10 Municípios por População e Densidade")
    fig_combined = plot_top10_combined(df)
    st.plotly_chart(fig_combined, use_container_width=True)

with tab2:
    st.header("Análise de Renda Municipal")
    fig_hist = plot_hist_pib2021(df)
    st.plotly_chart(fig_hist, use_container_width=True)

with tab3:
    st.header("Análise Cruzada: IDH, Renda e População")
    fig_scatter = plot_scatter_idh_vs_pib21(df, municipios_selecionados)
    st.plotly_chart(fig_scatter, use_container_width=True)

with tab4:
    st.header("Explore a Base de Dados Completa")
    st.markdown("Use os cabeçalhos das colunas para ordenar os dados. O campo de busca permite filtrar por qualquer valor na tabela.")
    st.dataframe(df, use_container_width=True, height=600)

# ==============================================
# 8) Rodapé
# ==============================================
st.markdown("---")
st.write("Dashboard desenvolvido como um exemplo de refatoração de app Streamlit com foco em design e interatividade.")
