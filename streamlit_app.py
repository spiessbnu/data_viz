import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# -------------------------------------------------------------
# 1. Título e descrição geral
# -------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard Municípios de SC",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("Dashboard Interativo: Municípios de SC (2025)")
st.markdown(
    """
    Este aplicativo exibe diversas visualizações interativas para explorar dados
    socioeconômicos dos municípios de Santa Catarina.  
    **Interatividade** via Plotly para explorar tendências de PIB, população e expectativa de vida.
    """
)

# -------------------------------------------------------------
# 2. Função para carregar dados
# -------------------------------------------------------------
@st.cache_data
def load_data():
    """
    Carrega o arquivo Excel com dados dos municípios.
    - Retorna um DataFrame pandas contendo colunas principais:
      ['cod_IBGE', 'Municipio', 'Populacao', 'PIB_per_capita', 'Esperanca_vida', 'Crescimento_populacional_pct'].
    """
    df = pd.read_excel("municipios_2025_atualizado.xlsx")
    # Ajustes de possíveis tipos: garante que colunas numéricas sejam numéricas
    df["Populacao"] = pd.to_numeric(df["Populacao"], errors="coerce")
    df["PIB_per_capita"] = pd.to_numeric(df["PIB_per_capita"], errors="coerce")
    df["Esperanca_vida"] = pd.to_numeric(df["Esperanca_vida"], errors="coerce")
    df["Crescimento_populacional_pct"] = pd.to_numeric(df["Crescimento_populacional_pct"], errors="coerce")
    return df.dropna(subset=["Municipio", "Populacao", "PIB_per_capita", "Esperanca_vida"])

df = load_data()

# -------------------------------------------------------------
# 3. Sidebar: seleção de visualização
# -------------------------------------------------------------
st.sidebar.header("Escolha a visualização")
vis_options = [
    "1) Top 10 Municípios por População",
    "2) Top 10 Crescimento Populacional (%)",
    "3) Histograma de PIB per Capita",
    "4) Boxplot de Expectativa de Vida",
    "5) Scatter Plot: PIB vs Esperança de Vida",
    "6) Treemap: População x Faixas de PIB"
]
choice = st.sidebar.selectbox("Selecione uma opção:", vis_options)

st.sidebar.markdown("---")
st.sidebar.write("Fonte: IBGE (2023)")

# -------------------------------------------------------------
# 4. Funções auxiliares para criar cada gráfico
# -------------------------------------------------------------

def plot_top10_populacao(df):
    """
    Gráfico de barras interativo (Plotly) com os 10 municípios de maior população.
    """
    top10_pop = df.nlargest(10, "Populacao")
    fig = px.bar(
        top10_pop.sort_values("Populacao"),
        x="Populacao",
        y="Municipio",
        orientation="h",
        title="Top 10 Municípios por População",
        labels={"Populacao": "População", "Municipio": "Município"},
        hover_data={"cod_IBGE": True, "PIB_per_capita": True, "Esperanca_vida": True},
    )
    fig.update_layout(margin=dict(l=100, r=20, t=50, b=20))
    return fig

def plot_top10_crescimento(df):
    """
    Gráfico de barras interativo (Plotly) com os 10 municípios de maior crescimento populacional (%).
    """
    top10_cres = df.nlargest(10, "Crescimento_populacional_pct")
    fig = px.bar(
        top10_cres.sort_values("Crescimento_populacional_pct"),
        x="Crescimento_populacional_pct",
        y="Municipio",
        orientation="h",
        title="Top 10 Municípios por Crescimento Populacional (%)",
        labels={"Crescimento_populacional_pct": "Crescimento (%)", "Municipio": "Município"},
        hover_data={"Populacao": True, "PIB_per_capita": True, "Esperanca_vida": True},
        color="Crescimento_populacional_pct",
        color_continuous_scale="Blues"
    )
    fig.update_layout(margin=dict(l=100, r=20, t=50, b=20), coloraxis_colorbar=dict(title="% Crescimento"))
    return fig

def plot_histograma_pib(df):
    """
    Histograma interativo (Plotly) da distribuição de PIB per capita entre todos os municípios.
    """
    fig = px.histogram(
        df,
        x="PIB_per_capita",
        nbins=30,
        title="Distribuição de PIB per Capita entre Municípios de SC",
        labels={"PIB_per_capita": "PIB per Capita (R$)"},
        marginal="box",  # adiciona boxplot marginal para visualizar outliers
        opacity=0.8
    )
    fig.update_layout(margin=dict(l=40, r=20, t=50, b=40))
    return fig

def plot_boxplot_esperanca(df):
    """
    Boxplot interativo (Plotly) da variável 'Esperanca_vida' para todos os municípios.
    """
    fig = px.box(
        df,
        y="Esperanca_vida",
        title="Boxplot: Distribuição de Expectativa de Vida (anos)",
        labels={"Esperanca_vida": "Expectativa de Vida (anos)"},
        points="all",  # exibe todos os pontos individuais para ver dispersão
        color_discrete_sequence=["teal"]
    )
    fig.update_layout(margin=dict(l=40, r=20, t=50, b=40))
    return fig

def plot_scatter_pib_esperanca(df):
    """
    Scatter Plot interativo (Plotly) comparando PIB per capita vs Expectativa de Vida,
    com bolhas dimensionadas pela população e coloridas pela expectativa de vida.
    """
    fig = px.scatter(
        df,
        x="PIB_per_capita",
        y="Esperanca_vida",
        size="Populacao",
        color="Esperanca_vida",
        color_continuous_scale="Viridis",
        hover_name="Municipio",
        title="PIB per Capita vs Expectativa de Vida (bolhas por população)",
        labels={
            "PIB_per_capita": "PIB per Capita (R$)",
            "Esperanca_vida": "Expectativa de Vida (anos)"
        },
        size_max=40,
        opacity=0.7
    )
    fig.update_layout(margin=dict(l=40, r=20, t=50, b=40))
    return fig

def plot_treemap_pop_pib(df):
    """
    Treemap interativo (Plotly) que agrupa municípios em faixas de PIB per capita,
    e exibe área proporcional à população.
    """
    # 1) Criar uma coluna categórica de faixas de PIB, por exemplo:
    bins = [0, 20000, 30000, 40000, 50000, 100000]
    labels = ["<20k", "20k-30k", "30k-40k", "40k-50k", ">50k"]
    df["Faixa_PIB"] = pd.cut(df["PIB_per_capita"], bins=bins, labels=labels, include_lowest=True)

    # 2) Para o treemap, cada retângulo representa um município; 
    # colorido pela faixa, e valor do retângulo é a população.
    fig = px.treemap(
        df,
        path=["Faixa_PIB", "Municipio"],
        values="Populacao",
        color="Faixa_PIB",
        color_discrete_map={
            "<20k": "#d4b9da",
            "20k-30k": "#c994c7",
            "30k-40k": "#df65b0",
            "40k-50k": "#e7298a",
            ">50k": "#ce1256"
        },
        title="Treemap: População por Faixa de PIB per Capita",
        hover_data={"PIB_per_capita": True, "Esperanca_vida": True}
    )
    fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))
    return fig

# -------------------------------------------------------------
# 5. Exibe a visualização escolhida
# -------------------------------------------------------------
if choice == "1) Top 10 Municípios por População":
    st.markdown("### 1) Top 10 Municípios por População")
    fig1 = plot_top10_populacao(df)
    st.plotly_chart(fig1, use_container_width=True)

elif choice == "2) Top 10 Crescimento Populacional (%)":
    st.markdown("### 2) Top 10 Crescimento Populacional (%)")
    fig2 = plot_top10_crescimento(df)
    st.plotly_chart(fig2, use_container_width=True)

elif choice == "3) Histograma de PIB per Capita":
    st.markdown("### 3) Histograma de PIB per Capita")
    fig3 = plot_histograma_pib(df)
    st.plotly_chart(fig3, use_container_width=True)

elif choice == "4) Boxplot de Expectativa de Vida":
    st.markdown("### 4) Boxplot de Expectativa de Vida")
    fig4 = plot_boxplot_esperanca(df)
    st.plotly_chart(fig4, use_container_width=True)

elif choice == "5) Scatter Plot: PIB vs Esperança de Vida":
    st.markdown("### 5) Scatter Plot: PIB per Capita vs Expectativa de Vida")
    fig5 = plot_scatter_pib_esperanca(df)
    st.plotly_chart(fig5, use_container_width=True)

elif choice == "6) Treemap: População x Faixas de PIB":
    st.markdown("### 6) Treemap: População por Faixa de PIB per Capita")
    fig6 = plot_treemap_pop_pib(df)
    st.plotly_chart(fig6, use_container_width=True)

# -------------------------------------------------------------
# 6. Rodapé
# -------------------------------------------------------------
st.markdown("---")
st.write(
    """
    **Observação:**  
    - Todos os gráficos são interativos: você pode passar o mouse sobre os pontos/barras/retângulos para ver detalhes.  
    - Caso queira incorporar novas métricas (ex.: IDH, renda média domiciliar, etc.), basta adicionar as colunas correspondentes no Excel e adaptar as funções acima.  
    - Para rodar localmente:  
      ```bash
      pip install -r requirements.txt
      streamlit run streamlit_app.py
      ```  
    """
)
