import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==============================================
# 1) Configuração da página e título
# ==============================================
st.set_page_config(
    page_title="Dashboard SC (Multianual)",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("Dashboard Interativo: Municípios de SC")
st.markdown(
    """
    Este aplicativo explora as variáveis disponíveis no arquivo Excel,
    exibindo uma visão geral em tabela e visualizações interativas.
    """
)

# ==============================================
# 2) Função para carregar e validar dados
# ==============================================
@st.cache_data
def load_data():
    df = pd.read_excel("municipios_2025_atualizado.xlsx")
    
    # Verifica existência das colunas exatas
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
    
    # Conversão para tipos numéricos
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
    
    # Remove linhas sem valores essenciais (pelo menos Município e População 2022)
    df = df.dropna(subset=["Municipio", "Populacao_2022"])
    return df

df = load_data()

# ==============================================
# 3) Exibição inicial: DataFrame completo em tabela
# ==============================================
st.markdown("## 1) Visão Geral dos Dados")
st.dataframe(df, use_container_width=True)

# ==============================================
# 4) Botões para seleção de visualização
# ==============================================
st.markdown("---")
st.markdown("## 2) Escolha a Visualização")
col1, col2, col3 = st.columns(3)

with col1:
    btn_combined = st.button("Top10 População & Densidade (2022)")
with col2:
    btn_hist_pib2021 = st.button("Histograma PIB 2021")
with col3:
    btn_scatter = st.button("Scatter IDH-M vs PIB 2021")

# ==============================================
# 5) Funções de plotagem
# ==============================================
def plot_top10_combined(df):
    """Combina os Top 10 de População 2022 e Densidade 2022 em mínimos múltiplos"""
    top10_pop = df.nlargest(10, "Populacao_2022")
    top10_den = df.nlargest(10, "Densidade_2022")
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Top 10 População (2022)", "Top 10 Densidade (2022)"),
        shared_yaxes=False, horizontal_spacing=0.15
    )
    
    # Gráfico de População
    fig.add_trace(
        go.Bar(
            x=top10_pop["Populacao_2022"],
            y=top10_pop["Municipio"],
            orientation="h",
            name="População 2022",
            marker_color="steelblue",
            hovertemplate="<b>%{y}</b><br>População: %{x}<extra></extra>"
        ),
        row=1, col=1
    )
    
    # Gráfico de Densidade
    fig.add_trace(
        go.Bar(
            x=top10_den["Densidade_2022"],
            y=top10_den["Municipio"],
            orientation="h",
            name="Densidade 2022",
            marker_color="crimson",
            hovertemplate="<b>%{y}</b><br>Densidade: %{x}<extra></extra>"
        ),
        row=1, col=2
    )
    
    # Ajustes de layout
    fig.update_layout(
        height=600,
        margin=dict(l=80, r=20, t=60, b=40),
        showlegend=False
    )
    # Inverte eixos Y para que o maior fique no topo
    fig.update_yaxes(autorange="reversed", row=1, col=1)
    fig.update_yaxes(autorange="reversed", row=1, col=2)
    
    return fig

def plot_hist_pib2021(df):
    """Histograma de PIB per capita 2021"""
    fig = px.histogram(
        df,
        x="PIBcapita_2021",
        nbins=30,
        title="Histograma: PIB per capita 2021",
        labels={"PIBcapita_2021": "PIB per capita (R$) – 2021"},
        opacity=0.8,
        color_discrete_sequence=["darkblue"]
    )
    fig.update_layout(
        margin=dict(l=50, r=20, t=50, b=40),
        yaxis_title="Contagem"
    )
    return fig

def plot_scatter_idh_vs_pib21(df):
    """Scatter: eixo Y = IDH-M_2010, eixo X = PIBcapita_2021, cor = Crescimento_populacional_pct, bolhas por Populacao_2022"""
    fig = px.scatter(
        df,
        x="PIBcapita_2021",
        y="IDH-M_2010",
        size="Populacao_2022",
        color="Crescimento_populacional_pct",
        color_continuous_scale="Viridis",
        hover_name="Municipio",
        title="Scatter: IDH-M (2010) vs PIB per capita (2021)",
        labels={
            "PIBcapita_2021": "PIB per capita (R$) – 2021",
            "IDH-M_2010": "IDH-Municipal (2010)",
            "Crescimento_populacional_pct": "Crescimento Pop (%)"
        },
        size_max=40,
        opacity=0.7
    )
    fig.update_layout(
        margin=dict(l=50, r=20, t=50, b=40),
        coloraxis_colorbar=dict(title="Crescimento Pop (%)")
    )
    return fig

# ==============================================
# 6) Renderização condicional conforme botão
# ==============================================
if btn_combined:
    st.markdown("### Top 10 Municípios por População e Densidade (2022)")
    fig_combined = plot_top10_combined(df)
    st.plotly_chart(fig_combined, use_container_width=True)

elif btn_hist_pib2021:
    st.markdown("### Histograma: PIB per capita 2021")
    fig_hist = plot_hist_pib2021(df)
    st.plotly_chart(fig_hist, use_container_width=True)

elif btn_scatter:
    st.markdown("### Scatter: IDH-M versus PIB per capita 2021")
    fig_scat = plot_scatter_idh_vs_pib21(df)
    st.plotly_chart(fig_scat, use_container_width=True)

else:
    st.info("Selecione uma visualização acima clicando em um dos botões.")

# ==============================================
# 7) Rodapé
# ==============================================
st.markdown("---")
st.write(
    """
    **Observações finais:**  
    - A tabela acima exibe os dados brutos conforme fornecidos.  
    - Use os botões para alternar entre as visualizações.  
    - Caso tenha novas colunas no Excel, adapte ou adicione novas funções de plot conforme necessário.
    """
)
