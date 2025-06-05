import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(
    page_title="Dashboard Municípios de SC 2025",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Dashboard Interativo: Municípios de SC (Dados 2025)")
st.markdown(
    """
    Aplicativo para explorar visualmente dados socioeconômicos dos municípios de Santa Catarina em 2025.
    Utilize os gráficos interativos para analisar população, PIB per capita e expectativa de vida.
    """
)

@st.cache_data
def load_data():
    # Leitura do Excel
    df = pd.read_excel("municipios_2025_atualizado.xlsx")
    
    # Exemplo de renomeação caso suas colunas estejam com sufixo de ano diferente.
    # Ajuste o dicionário abaixo conforme os nomes exatos do seu arquivo.
    mapeamento = {
        # Se a planilha tiver nome "Populacao_2010" e você queira usar 2025,
        # certifique-se de que exista "Populacao_2025". Exemplo:
        # "Populacao_2010": "Populacao_2025",
        # "PIB_per_capita_2010": "PIB_per_capita_2025",
        # "Esperanca_vida_2010": "Esperanca_vida_2025",
        # "Crescimento_populacional_pct_2010": "Crescimento_populacional_pct_2025",
    }
    df = df.rename(columns=mapeamento)
    
    # Lista de colunas esperadas para o ano de 2025
    colunas_esperadas = [
        "cod_IBGE",
        "Municipio",
        "Populacao_2025",
        "PIB_per_capita_2025",
        "Esperanca_vida_2025",
        "Crescimento_populacional_pct_2025"
    ]
    faltando = [c for c in colunas_esperadas if c not in df.columns]
    if faltando:
        raise KeyError(
            f"Colunas obrigatórias não encontradas: {faltando}. "
            "Verifique os cabeçalhos no Excel e ajuste o mapeamento."
        )
    
    # Conversão para numérico (se necessário)
    df["Populacao_2025"] = pd.to_numeric(df["Populacao_2025"], errors="coerce")
    df["PIB_per_capita_2025"] = pd.to_numeric(df["PIB_per_capita_2025"], errors="coerce")
    df["Esperanca_vida_2025"] = pd.to_numeric(df["Esperanca_vida_2025"], errors="coerce")
    df["Crescimento_populacional_pct_2025"] = pd.to_numeric(
        df["Crescimento_populacional_pct_2025"], errors="coerce"
    )
    
    # Remove linhas que não têm valores mínimos
    df = df.dropna(
        subset=[
            "Municipio",
            "Populacao_2025",
            "PIB_per_capita_2025",
            "Esperanca_vida_2025"
        ]
    )
    return df

# Carrega dados
df = load_data()

# Sidebar para seleção de visualização
st.sidebar.header("Escolha a visualização")
vis_options = [
    "1) Top 10 Municípios por População (2025)",
    "2) Top 10 Crescimento Populacional (%) (2025)",
    "3) Histograma de PIB per Capita (2025)",
    "4) Boxplot de Expectativa de Vida (2025)",
    "5) Scatter Plot: PIB vs Esperança de Vida (2025)",
    "6) Treemap: População x Faixas de PIB (2025)"
]
choice = st.sidebar.selectbox("Selecione uma opção:", vis_options)
st.sidebar.markdown("---")
st.sidebar.write("Fonte: IBGE (2023 / 2025)")

# Funções de plotagem com Plotly Express

def plot_top10_populacao(df):
    top10 = df.nlargest(10, "Populacao_2025")
    fig = px.bar(
        top10.sort_values("Populacao_2025"),
        x="Populacao_2025",
        y="Municipio",
        orientation="h",
        title="Top 10 Municípios por População (2025)",
        labels={"Populacao_2025": "População (2025)", "Municipio": "Município"},
        hover_data={"cod_IBGE": True, "PIB_per_capita_2025": True, "Esperanca_vida_2025": True},
    )
    fig.update_layout(margin=dict(l=100, r=20, t=50, b=20))
    return fig

def plot_top10_crescimento(df):
    top10 = df.nlargest(10, "Crescimento_populacional_pct_2025")
    fig = px.bar(
        top10.sort_values("Crescimento_populacional_pct_2025"),
        x="Crescimento_populacional_pct_2025",
        y="Municipio",
        orientation="h",
        title="Top 10 Municípios por Crescimento Populacional (%) (2025)",
        labels={
            "Crescimento_populacional_pct_2025": "Crescimento (%) (2025)",
            "Municipio": "Município"
        },
        hover_data={"Populacao_2025": True, "PIB_per_capita_2025": True, "Esperanca_vida_2025": True},
        color="Crescimento_populacional_pct_2025",
        color_continuous_scale="Blues"
    )
    fig.update_layout(
        margin=dict(l=100, r=20, t=50, b=20),
        coloraxis_colorbar=dict(title="% Crescimento (2025)")
    )
    return fig

def plot_histograma_pib(df):
    fig = px.histogram(
        df,
        x="PIB_per_capita_2025",
        nbins=30,
        title="Distribuição de PIB per Capita (2025)",
        labels={"PIB_per_capita_2025": "PIB per Capita (R$) – 2025"},
        marginal="box",
        opacity=0.8
    )
    fig.update_layout(margin=dict(l=40, r=20, t=50, b=40))
    return fig

def plot_boxplot_esperanca(df):
    fig = px.box(
        df,
        y="Esperanca_vida_2025",
        title="Boxplot: Distribuição de Expectativa de Vida (2025)",
        labels={"Esperanca_vida_2025": "Expectativa de Vida (anos) – 2025"},
        points="all",
        color_discrete_sequence=["teal"]
    )
    fig.update_layout(margin=dict(l=40, r=20, t=50, b=40))
    return fig

def plot_scatter_pib_esperanca(df):
    fig = px.scatter(
        df,
        x="PIB_per_capita_2025",
        y="Esperanca_vida_2025",
        size="Populacao_2025",
        color="Esperanca_vida_2025",
        color_continuous_scale="Viridis",
        hover_name="Municipio",
        title="PIB per Capita vs Expectativa de Vida (2025)",
        labels={
            "PIB_per_capita_2025": "PIB per Capita (R$) – 2025",
            "Esperanca_vida_2025": "Expectativa de Vida (anos) – 2025"
        },
        size_max=40,
        opacity=0.7
    )
    fig.update_layout(margin=dict(l=40, r=20, t=50, b=40))
    return fig

def plot_treemap_pop_pib(df):
    # Cria faixas com base em PIB per capita de 2025
    bins = [0, 20000, 30000, 40000, 50000, df["PIB_per_capita_2025"].max()]
    labels = ["<20k", "20k-30k", "30k-40k", "40k-50k", ">50k"]
    df["Faixa_PIB_2025"] = pd.cut(
        df["PIB_per_capita_2025"], bins=bins, labels=labels, include_lowest=True
    )
    fig = px.treemap(
        df,
        path=["Faixa_PIB_2025", "Municipio"],
        values="Populacao_2025",
        color="Faixa_PIB_2025",
        color_discrete_map={
            "<20k": "#d4b9da",
            "20k-30k": "#c994c7",
            "30k-40k": "#df65b0",
            "40k-50k": "#e7298a",
            ">50k": "#ce1256"
        },
        title="Treemap: População por Faixa de PIB per Capita (2025)",
        hover_data={"PIB_per_capita_2025": True, "Esperanca_vida_2025": True}
    )
    fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))
    return fig

# Renderização dos gráficos conforme escolha do usuário
if choice == "1) Top 10 Municípios por População (2025)":
    st.markdown("### Top 10 Municípios por População (2025)")
    st.plotly_chart(plot_top10_populacao(df), use_container_width=True)

elif choice == "2) Top 10 Crescimento Populacional (%) (2025)":
    st.markdown("### Top 10 Crescimento Populacional (%) (2025)")
    st.plotly_chart(plot_top10_crescimento(df), use_container_width=True)

elif choice == "3) Histograma de PIB per Capita (2025)":
    st.markdown("### Histograma de PIB per Capita (2025)")
    st.plotly_chart(plot_histograma_pib(df), use_container_width=True)

elif choice == "4) Boxplot de Expectativa de Vida (2025)":
    st.markdown("### Boxplot de Expectativa de Vida (2025)")
    st.plotly_chart(plot_boxplot_esperanca(df), use_container_width=True)

elif choice == "5) Scatter Plot: PIB vs Esperança de Vida (2025)":
    st.markdown("### Scatter Plot: PIB per Capita vs Expectativa de Vida (2025)")
    st.plotly_chart(plot_scatter_pib_esperanca(df), use_container_width=True)

elif choice == "6) Treemap: População x Faixas de PIB (2025)":
    st.markdown("### Treemap: População por Faixa de PIB per Capita (2025)")
    st.plotly_chart(plot_treemap_pop_pib(df), use_container_width=True)

# Rodapé
st.markdown("---")
st.write(
    """
    **Observação:**  
    - Caso os nomes das colunas no Excel sejam diferentes (por exemplo, sem o sufixo "_2025"), 
      ajuste o dicionário `mapeamento` para renomear as colunas originais para os nomes esperados acima.  
    - Se desejar adicionar métricas de anos anteriores (2010, 2020), basta replicar a lógica de renomeação 
      e criar novas funções de plot para cada ano.
    """
)
