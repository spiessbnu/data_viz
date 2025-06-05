import streamlit as st
import pandas as pd
import plotly.express as px

# ==============================================
# 1) Configuração da página e header
# ==============================================
st.set_page_config(
    page_title="Dashboard SC (Multianual)",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("Dashboard Interativo: Municípios de SC")
st.markdown(
    """
    Este aplicativo explora as seguintes variáveis disponíveis no arquivo:
    
    - **Municipio** (object)  
    - **cod_IBGE** (int64)  
    - **IDH-M_2010** (float64)  
    - **Populacao_2010** (int64)  
    - **Densidade_2010** (float64)  
    - **Populacao_2022** (int64)  
    - **Densidade_2022** (float64)  
    - **PIBcapita_2019** (float64)  
    - **PIBcapita_2021** (float64)  
    - **Crescimento_populacional_abs** (int64)  
    - **Crescimento_populacional_pct** (float64)  
    - **Crescimento_PIBcapita_abs** (float64)  
    - **Crescimento_PIBcapita_pct** (float64)  
    """
)

# ==============================================
# 2) Função para carregar e validar dados
# ==============================================
@st.cache_data
def load_data():
    df = pd.read_excel("municipios_2025_atualizado.xlsx")
    
    # Lista exata de colunas esperadas
    colunas_esperadas = [
        "Municipio",
        "cod_IBGE",
        "IDH-M_2010",
        "Populacao_2010",
        "Densidade_2010",
        "Populacao_2022",
        "Densidade_2022",
        "PIBcapita_2019",
        "PIBcapita_2021",
        "Crescimento_populacional_abs",
        "Crescimento_populacional_pct",
        "Crescimento_PIBcapita_abs",
        "Crescimento_PIBcapita_pct"
    ]
    faltando = [c for c in colunas_esperadas if c not in df.columns]
    if faltando:
        raise KeyError(
            f"Colunas obrigatórias não encontradas: {faltando}. "
            "Verifique os cabeçalhos no Excel."
        )
    
    # Conversão para tipos numéricos (se já não estiver em tipo adequado)
    df["Populacao_2010"] = pd.to_numeric(df["Populacao_2010"], errors="coerce")
    df["Densidade_2010"] = pd.to_numeric(df["Densidade_2010"], errors="coerce")
    df["IDH-M_2010"]    = pd.to_numeric(df["IDH-M_2010"],    errors="coerce")
    df["Populacao_2022"] = pd.to_numeric(df["Populacao_2022"], errors="coerce")
    df["Densidade_2022"] = pd.to_numeric(df["Densidade_2022"], errors="coerce")
    df["PIBcapita_2019"] = pd.to_numeric(df["PIBcapita_2019"], errors="coerce")
    df["PIBcapita_2021"] = pd.to_numeric(df["PIBcapita_2021"], errors="coerce")
    df["Crescimento_populacional_abs"] = pd.to_numeric(
        df["Crescimento_populacional_abs"], errors="coerce"
    )
    df["Crescimento_populacional_pct"] = pd.to_numeric(
        df["Crescimento_populacional_pct"], errors="coerce"
    )
    df["Crescimento_PIBcapita_abs"] = pd.to_numeric(
        df["Crescimento_PIBcapita_abs"], errors="coerce"
    )
    df["Crescimento_PIBcapita_pct"] = pd.to_numeric(
        df["Crescimento_PIBcapita_pct"], errors="coerce"
    )
    
    # Remover linhas sem valores essenciais (pelo menos Município e População 2022)
    df = df.dropna(subset=["Municipio", "Populacao_2022"])
    return df

df = load_data()

# ==============================================
# 3) Sidebar: seleção de visualização
# ==============================================
st.sidebar.header("Escolha a visualização")
vis_options = [
    "1) Top 10 Municípios por População (2022)",
    "2) Top 10 Municípios por Densidade (2022)",
    "3) Histograma: PIB per capita 2019",
    "4) Histograma: PIB per capita 2021",
    "5) Scatter: PIB2021 vs Densidade2022 (bolhas por Pop2022)",
    "6) Scatter: Crescimento Pop (%) vs Crescimento PIB (%)",
    "7) Boxplot: IDH-M (2010)",
    "8) Treemap: População 2022 por Faixas de IDH-M 2010"
]
choice = st.sidebar.selectbox("Opção:", vis_options)
st.sidebar.markdown("---")
st.sidebar.write("Fonte: IBGE e Cálculos Internos")

# ==============================================
# 4) Funções de plotagem (Plotly Express)
# ==============================================
def plot_top10_pop2022(df):
    top10 = df.nlargest(10, "Populacao_2022")
    fig = px.bar(
        top10.sort_values("Populacao_2022"),
        x="Populacao_2022",
        y="Municipio",
        orientation="h",
        title="Top 10 Municípios por População (2022)",
        labels={"Populacao_2022": "População (2022)", "Municipio": "Município"},
        hover_data={
            "cod_IBGE": True,
            "Populacao_2010": True,
            "Densidade_2022": True
        }
    )
    fig.update_layout(margin=dict(l=100, r=20, t=50, b=20))
    return fig

def plot_top10_dens2022(df):
    top10 = df.nlargest(10, "Densidade_2022")
    fig = px.bar(
        top10.sort_values("Densidade_2022"),
        x="Densidade_2022",
        y="Municipio",
        orientation="h",
        title="Top 10 Municípios por Densidade (2022)",
        labels={"Densidade_2022": "Densidade (hab/km²) – 2022", "Municipio": "Município"},
        hover_data={
            "cod_IBGE": True,
            "Populacao_2022": True,
            "IDH-M_2010": True
        },
        color="Densidade_2022",
        color_continuous_scale="Reds"
    )
    fig.update_layout(
        margin=dict(l=100, r=20, t=50, b=20),
        coloraxis_colorbar=dict(title="Densidade")
    )
    return fig

def plot_hist_pib2019(df):
    fig = px.histogram(
        df,
        x="PIBcapita_2019",
        nbins=30,
        title="Distribuição de PIB per capita 2019",
        labels={"PIBcapita_2019": "PIB per capita (R$) – 2019"},
        marginal="box",
        opacity=0.8
    )
    fig.update_layout(margin=dict(l=40, r=20, t=50, b=40))
    return fig

def plot_hist_pib2021(df):
    fig = px.histogram(
        df,
        x="PIBcapita_2021",
        nbins=30,
        title="Distribuição de PIB per capita 2021",
        labels={"PIBcapita_2021": "PIB per capita (R$) – 2021"},
        marginal="box",
        opacity=0.8
    )
    fig.update_layout(margin=dict(l=40, r=20, t=50, b=40))
    return fig

def plot_scatter_pib21_dens22(df):
    fig = px.scatter(
        df,
        x="PIBcapita_2021",
        y="Densidade_2022",
        size="Populacao_2022",
        color="Densidade_2022",
        color_continuous_scale="Viridis",
        hover_name="Municipio",
        title="PIB per capita (2021) vs Densidade (2022)",
        labels={
            "PIBcapita_2021": "PIB per capita (R$) – 2021",
            "Densidade_2022": "Densidade (hab/km²) – 2022"
        },
        size_max=40,
        opacity=0.7
    )
    fig.update_layout(margin=dict(l=40, r=20, t=50, b=40))
    return fig

def plot_scatter_crescimentos(df):
    fig = px.scatter(
        df,
        x="Crescimento_populacional_pct",
        y="Crescimento_PIBcapita_pct",
        size="Populacao_2022",
        color="Crescimento_PIBcapita_pct",
        color_continuous_scale="Plasma",
        hover_name="Municipio",
        title="Crescimento Populacional (%) vs Crescimento PIB per capita (%)",
        labels={
            "Crescimento_populacional_pct": "Crescimento Pop (%)",
            "Crescimento_PIBcapita_pct": "Crescimento PIBcapita (%)"
        },
        size_max=40,
        opacity=0.7
    )
    fig.update_layout(margin=dict(l=40, r=20, t=50, b=40))
    return fig

def plot_boxplot_idhm2010(df):
    fig = px.box(
        df,
        y="IDH-M_2010",
        title="Boxplot: Distribuição de IDH-M (2010)",
        labels={"IDH-M_2010": "IDH-Municipal (2010)"},
        points="all",
        color_discrete_sequence=["teal"]
    )
    fig.update_layout(margin=dict(l=40, r=20, t=50, b=40))
    return fig

def plot_treemap_pop2022_faixaidhm(df):
    # Criar faixas de IDH-M_2010: por exemplo, [<0.6, 0.6–0.7, 0.7–0.8, 0.8–0.9, ≥0.9]
    bins = [0.0, 0.6, 0.7, 0.8, 0.9, 1.0]
    labels = ["<0.6", "0.6–0.7", "0.7–0.8", "0.8–0.9", "≥0.9"]
    df["Faixa_IDH_2010"] = pd.cut(
        df["IDH-M_2010"], bins=bins, labels=labels, include_lowest=True
    )
    
    fig = px.treemap(
        df,
        path=["Faixa_IDH_2010", "Municipio"],
        values="Populacao_2022",
        color="Faixa_IDH_2010",
        color_discrete_map={
            "<0.6": "#fde0dd",
            "0.6–0.7": "#fa9fb5",
            "0.7–0.8": "#c51b8a",
            "0.8–0.9": "#7a0177",
            "≥0.9": "#49006a"
        },
        title="Treemap: População 2022 por Faixa de IDH-M 2010",
        hover_data={"Densidade_2022": True, "PIBcapita_2021": True}
    )
    fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))
    return fig

# ==============================================
# 5) Renderização condicional conforme escolha
# ==============================================
if choice == "1) Top 10 Municípios por População (2022)":
    st.markdown("### Top 10 Municípios por População (2022)")
    st.plotly_chart(plot_top10_pop2022(df), use_container_width=True)

elif choice == "2) Top 10 Municípios por Densidade (2022)":
    st.markdown("### Top 10 Municípios por Densidade (2022)")
    st.plotly_chart(plot_top10_dens2022(df), use_container_width=True)

elif choice == "3) Histograma: PIB per capita 2019":
    st.markdown("### Histograma: PIB per capita 2019")
    st.plotly_chart(plot_hist_pib2019(df), use_container_width=True)

elif choice == "4) Histograma: PIB per capita 2021":
    st.markdown("### Histograma: PIB per capita 2021")
    st.plotly_chart(plot_hist_pib2021(df), use_container_width=True)

elif choice == "5) Scatter: PIB2021 vs Densidade2022 (bolhas por Pop2022)":
    st.markdown("### Scatter: PIB per capita 2021 vs Densidade 2022")
    st.plotly_chart(plot_scatter_pib21_dens22(df), use_container_width=True)

elif choice == "6) Scatter: Crescimento Pop (%) vs Crescimento PIB (%)":
    st.markdown("### Scatter: Crescimento Pop (%) vs Crescimento PIB per capita (%)")
    st.plotly_chart(plot_scatter_crescimentos(df), use_container_width=True)

elif choice == "7) Boxplot: IDH-M (2010)":
    st.markdown("### Boxplot: Distribuição de IDH-M (2010)")
    st.plotly_chart(plot_boxplot_idhm2010(df), use_container_width=True)

elif choice == "8) Treemap: População 2022 por Faixas de IDH-M 2010":
    st.markdown("### Treemap: População 2022 por Faixa de IDH-M (2010)")
    st.plotly_chart(plot_treemap_pop2022_faixaidhm(df), use_container_width=True)

# ==============================================
# 6) Rodapé explicativo
# ==============================================
st.markdown("---")
st.write(
    """
    **Notas Finais:**  
    - Todas as visualizações acima usam as colunas EXATAMENTE correspondentes à estrutura de dados enviada.  
    - Se você tiver novas versões do Excel (por exemplo, População_2023, PIBcapita_2022, etc.), basta adicionar as colunas 
      e criar funções de plotagem adicionais, seguindo o padrão usado aqui.  
    - Para rodar localmente:  
      ```bash
      pip install -r requirements.txt
      streamlit run streamlit_app.py
      ```  
    """
)
