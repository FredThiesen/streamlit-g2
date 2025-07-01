import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import importlib.util
import sys
import os

# --- Importa o script de tratamento de dados como módulo ---
TRATAMENTO_PATH = os.path.join(os.path.dirname(__file__), 'trata-dados-e-cria-graficos.py')
spec = importlib.util.spec_from_file_location("trata_dados", TRATAMENTO_PATH)
trata_dados = importlib.util.module_from_spec(spec)
sys.modules["trata_dados"] = trata_dados
spec.loader.exec_module(trata_dados)

df = trata_dados.df  # DataFrame já tratado

# --- Configuração da página ---
st.set_page_config(
    page_title="Dashboard Consultas Ambulatoriais 2023",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Sidebar: Filtros ---
st.sidebar.title("Filtros")
sexos = df['Sexo'].dropna().unique().tolist()
especialidades = df['Especialidade'].dropna().unique().tolist()
municipios = df['Município'].dropna().unique().tolist()
min_idade, max_idade = int(df['Idade'].min()), int(df['Idade'].max())
min_ano = df['Data/Hora_ Consulta Ambulatorial'].dt.year.min()
max_ano = df['Data/Hora_ Consulta Ambulatorial'].dt.year.max()

sexo_sel = st.sidebar.multiselect("Sexo", options=sexos, default=sexos)
esp_sel = st.sidebar.multiselect("Especialidade", options=especialidades, default=especialidades)
mun_sel = st.sidebar.multiselect("Município", options=municipios, default=municipios)
idade_sel = st.sidebar.slider("Faixa Etária", min_value=min_idade, max_value=max_idade, value=(min_idade, max_idade))
meses = df['Mes'].sort_values().unique().tolist()
mes_sel = st.sidebar.multiselect("Mês da Consulta", options=meses, default=meses)

# --- Aplica filtros ---
df_filt = df[
    df['Sexo'].isin(sexo_sel) &
    df['Especialidade'].isin(esp_sel) &
    df['Município'].isin(mun_sel) &
    df['Idade'].between(idade_sel[0], idade_sel[1]) &
    df['Mes'].isin(mes_sel)
]

# --- Páginas ---
paginas = [
    "Página Inicial",
    "Análises por Sexo",
    "Análises por Idade",
    "Especialidades",
    "Municípios",
    "Tendências Temporais"
]
pagina = st.sidebar.radio("Navegue pelas páginas:", paginas)

# --- Página Inicial ---
if pagina == "Página Inicial":
    st.title("Dashboard de Consultas Ambulatoriais 2023")
    st.markdown("""
    ### Objetivo
    Este dashboard interativo permite explorar e analisar os atendimentos ambulatoriais realizados em 2023. Utilize os filtros na barra lateral para refinar os dados e navegue pelas páginas para diferentes perspectivas.

    **Como navegar:**
    - Use o menu lateral para acessar diferentes análises.
    - Os filtros afetam todos os gráficos e tabelas.
    - Passe o mouse sobre os gráficos interativos para detalhes.
    """)
    st.info("Os dados exibidos já foram tratados e organizados previamente.")
    st.subheader("Distribuição de Pacientes por Sexo")
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.countplot(data=df_filt, x='Sexo', palette='pastel', ax=ax)
    ax.set_title('Distribuição de Pacientes por Sexo')
    st.pyplot(fig)

# --- Análises por Sexo ---
elif pagina == "Análises por Sexo":
    st.header("Análises por Sexo")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Distribuição de Idade - Feminino")
        fig_fem = px.histogram(df_filt[df_filt['Sexo'] == 'FEMININO'], x='Idade', nbins=30, title='Idade das Pacientes (Feminino)', color_discrete_sequence=['pink'])
        st.plotly_chart(fig_fem, use_container_width=True)
    with col2:
        st.subheader("Distribuição de Idade - Masculino")
        fig_masc = px.histogram(df_filt[df_filt['Sexo'] == 'MASCULINO'], x='Idade', nbins=30, title='Idade dos Pacientes (Masculino)', color_discrete_sequence=['skyblue'])
        st.plotly_chart(fig_masc, use_container_width=True)

# --- Análises por Idade ---
elif pagina == "Análises por Idade":
    st.header("Análises por Idade")
    st.subheader("Distribuição Geral de Atendimentos por Idade")
    fig_idade = px.histogram(df_filt, x='Idade', nbins=30, title='Distribuição Geral de Atendimentos por Idade', color_discrete_sequence=['mediumseagreen'])
    st.plotly_chart(fig_idade, use_container_width=True)
    st.subheader("Boxplot de Idade por Especialidade (Top 5)")
    top_especialidades = df_filt['Especialidade'].value_counts().head(5).index
    fig_box = px.box(df_filt[df_filt['Especialidade'].isin(top_especialidades)], x='Especialidade', y='Idade', points='all', color='Especialidade', title='Idade por Especialidade (Top 5)')
    st.plotly_chart(fig_box, use_container_width=True)

# --- Especialidades ---
elif pagina == "Especialidades":
    st.header("Especialidades")
    st.subheader("Distribuição de Especialidades por Sexo (Top 5)")
    top_especialidades = df_filt['Especialidade'].value_counts().head(5).index
    fig_esp = px.histogram(df_filt[df_filt['Especialidade'].isin(top_especialidades)], x='Especialidade', color='Sexo', barmode='group', title='Especialidades por Sexo (Top 5)')
    st.plotly_chart(fig_esp, use_container_width=True)
    st.subheader("Heatmap: Atendimentos por Especialidade e Dia da Semana (Top 10)")
    top10_esp = df_filt['Especialidade'].value_counts().head(10).index
    pivot_top10 = df_filt[df_filt['Especialidade'].isin(top10_esp)].pivot_table(
        index='Especialidade', columns='Dia_Semana', aggfunc='size', fill_value=0
    )
    fig, ax = plt.subplots(figsize=(8, 8))
    sns.heatmap(pivot_top10, cmap='YlGnBu', annot=True, fmt='d', annot_kws={"size": 7}, cbar_kws={'shrink': 0.6}, ax=ax)
    ax.set_title('Volume de Atendimentos por Especialidade e Dia da Semana')
    st.pyplot(fig)

# --- Municípios ---
elif pagina == "Municípios":
    st.header("Municípios")
    st.subheader("Top 10 Municípios com Mais Atendimentos")
    df_mun = df_filt[df_filt['Município'] != 'Não informado']
    top_municipios = df_mun['Município'].value_counts().head(10)
    fig_mun = px.bar(x=top_municipios.values, y=top_municipios.index, orientation='h', color=top_municipios.values, color_continuous_scale='Blues', labels={'x':'Contagem','y':'Município'}, title='Top 10 Municípios com Mais Atendimentos')
    st.plotly_chart(fig_mun, use_container_width=True)
    st.subheader("Idade Média dos Pacientes por Município (Top 5)")
    top5_municipios = df_filt['Município'].value_counts().head(5).index
    idade_media = df_filt[df_filt['Município'].isin(top5_municipios)].groupby('Município')['Idade'].mean().sort_values()
    fig_idade_mun = px.bar(x=idade_media.index, y=idade_media.values, labels={'x':'Município','y':'Idade Média'}, color=idade_media.values, color_continuous_scale='Purples', title='Idade Média por Município (Top 5)')
    st.plotly_chart(fig_idade_mun, use_container_width=True)

# --- Tendências Temporais ---
elif pagina == "Tendências Temporais":
    st.header("Tendências Temporais")
    st.subheader("Tendência de Atendimentos na Semana")
    consultas_por_data = df_filt.groupby('Dia_Semana').size().reindex(['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'], fill_value=0)
    fig_semana = px.line(x=consultas_por_data.index, y=consultas_por_data.values, markers=True, labels={'x':'Dia da Semana','y':'Número de Atendimentos'}, title='Tendência de Atendimentos na Semana')
    st.plotly_chart(fig_semana, use_container_width=True)
    st.subheader("Tendência de Atendimentos por Mês")
    consultas_por_mes = df_filt['Mes'].value_counts().sort_index()
    fig_mes = px.line(x=consultas_por_mes.index, y=consultas_por_mes.values, markers=True, labels={'x':'Mês','y':'Consultas'}, title='Tendência de Atendimentos por Mês')
    st.plotly_chart(fig_mes, use_container_width=True)
