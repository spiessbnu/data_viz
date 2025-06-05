import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import geopandas as gpd

# Título da aplicação
st.title("Gráficos e Mapas de Municípios de SC")

# ========== Funções para Carregamento de Dados ==========

@st.cache_data
def load_data():
    """
    Carrega o arquivo Excel com dados dos municípios.
    Retorna um DataFrame pandas.
    """
    df = pd.read_excel("municipios_2025_atualizado.xlsx")
    return df

@st.cache_data
def load_shapefile():
    """
    Carrega o shapefile (.shp) dos municípios de Santa Catarina usando GeoPandas.
    Retorna um GeoDataFrame.
    """
    shapefile_path = "SC_Municipios_2024.shp"
    gdf_sc = gpd.read_file(shapefile_path)
    return gdf_sc

# Carrega os dados
df = load_data()

# ========== Sidebar de Seleção de Visualizações ==========

st.sidebar.header("Opções de Visualização")
vis_options = [
    "Gráfico de Barras – Top 10 Crescimento Populacional",
    "Scatter Plot Seaborn – PIB vs Expectativa de Vida",
    "Scatter Plot Plotly – PIB vs Expectativa de Vida Interativo",
    "Mapa Coroplético"
]
choice = st.sidebar.selectbox("Selecione a visualização:", vis_options)

# ========== Lógica para Cada Visualização ==========

if choice == "Gráfico de Barras – Top 10 Crescimento Populacional":
    # 1) Seleciona os 10 maiores valores de 'Crescimento_populacional_pct'
    top10 = df.sort_values("Crescimento_populacional_pct", ascending=False).head(10)
    
    # 2) Cria a figura Matplotlib/Seaborn
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        x="Crescimento_populacional_pct",
        y="Municipio", 
        data=top10, 
        ax=ax, 
        palette="Blues_d"
    )
    ax.set_xlabel("Crescimento Populacional (%)")
    ax.set_ylabel("Município")
    ax.set_title("Top 10 Municípios por Crescimento Populacional (%)")
    plt.tight_layout()
    
    # 3) Exibe a figura no Streamlit
    st.pyplot(fig)

elif choice == "Scatter Plot Seaborn – PIB vs Expectativa de Vida":
    # 1) Cria figura Seaborn
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(
        x="PIB_per_capita",
        y="Esperanca_vida",
        size="Populacao",
        data=df,
        ax=ax,
        alpha=0.7,
        sizes=(20, 200),
        legend=False
    )
    ax.set_xlabel("PIB per capita (R$)")
    ax.set_ylabel("Expectativa de Vida (anos)")
    ax.set_title("Relação PIB per capita vs Expectativa de Vida")
    plt.tight_layout()
    
    # 2) Exibe a figura no Streamlit
    st.pyplot(fig)

elif choice == "Scatter Plot Plotly – PIB vs Expectativa de Vida Interativo":
    # 1) Cria figura interativa Plotly Express
    fig = px.scatter(
        df,
        x="PIB_per_capita",
        y="Esperanca_vida",
        size="Populacao",
        hover_name="Municipio",
        title="Relação PIB per capita vs Expectativa de Vida",
        labels={
            "PIB_per_capita": "PIB per capita (R$)",
            "Esperanca_vida": "Expectativa de Vida (anos)",
            "Populacao": "População"
        }
    )
    fig.update_layout(margin={"r": 20, "t": 60, "l": 20, "b": 20})
    
    # 2) Exibe o gráfico Plotly no Streamlit
    st.plotly_chart(fig, use_container_width=True)

elif choice == "Mapa Coroplético":
    # 1) Carrega o shapefile
    gdf_sc = load_shapefile()
    
    # 2) Ajusta o tipo de dado para merge
    gdf_sc["CD_GEOCMU"] = gdf_sc["CD_GEOCMU"].astype(int)
    
    # 3) Faz merge entre GeoDataFrame e DataFrame de municípios
    merged_gdf = gdf_sc.merge(df, left_on="CD_GEOCMU", right_on="cod_IBGE", how="inner")
    
    # 4) Seleciona a variável de interesse
    variable = st.sidebar.selectbox(
        "Variável para mapear:",
        ["Crescimento_populacional_pct", "PIB_per_capita", "Esperanca_vida"]
    )
    
    # 5) Cria mapa coroplético usando Plotly Express
    fig_map = px.choropleth_mapbox(
        merged_gdf,
        geojson=merged_gdf.__geo_interface__,
        locations=merged_gdf.index,
        color=variable,
        mapbox_style="carto-positron",
        zoom=6.5,
        center={"lat": -27.2469, "lon": -50.4754},
        opacity=0.7,
        labels={variable: variable},
        hover_name="Municipio"
    )
    fig_map.update_geos(fitbounds="locations", visible=False)
    fig_map.update_layout(
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        title_text=f"{variable} por Município em SC",
        title_x=0.5,
        title_font_size=16,
        coloraxis_colorbar=dict(ticksuffix="%")
    )
    
    # 6) Exibe o mapa no Streamlit
    st.plotly_chart(fig_map, use_container_width=True)

# ========== Rodapé com Fonte ==========

st.markdown("---")
st.write("Fonte: IBGE (2023)")
