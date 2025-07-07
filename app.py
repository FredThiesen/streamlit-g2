import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import importlib.util
import sys
import os

# --- Animação de carregamento ao importar e preparar os dados tratados ---
with st.spinner('Carregando dados e preparando visualização...'):
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

# --- NAVEGAÇÃO POR ABAS NO TOPO (st.tabs) ---
tab_labels = [
    "Página Inicial",
    "Análises por Sexo",
    "Análises por Idade",
    "Especialidades",
    "Municípios",
    "Tendências Temporais"
]
tabs = st.tabs(tab_labels)

# --- Filtros continuam na sidebar, agora com tooltips (help) explicativos ---
st.sidebar.title("Filtros")
sexos = df['Sexo'].dropna().unique().tolist()
especialidades = df['Especialidade'].dropna().unique().tolist()
municipios = df['Município'].dropna().unique().tolist()
min_idade, max_idade = int(df['Idade'].min()), int(df['Idade'].max())
min_ano = df['Data/Hora_ Consulta Ambulatorial'].dt.year.min()
max_ano = df['Data/Hora_ Consulta Ambulatorial'].dt.year.max()

# --- Lista fixa dos meses em português para ordenação ---
MESES_PT = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]

# --- Filtros organizados em um expander na sidebar, com componentes mais amigáveis ---
with st.sidebar.expander("Filtros Avançados", expanded=True):
    sexo_sel = st.multiselect(
        "Sexo", options=sexos, default=sexos,
        help="Filtra os atendimentos pelo sexo do paciente.",
        placeholder="Selecione um ou mais sexos"
    )
    esp_sel = st.multiselect(
        "Especialidade", options=especialidades, default=especialidades,
        help="Filtra os atendimentos pela especialidade médica.",
        placeholder="Selecione especialidades"
    )
    # Município como selectbox para seleção única
    municipio_sel = st.selectbox(
        "Município", options=["Todos"] + municipios,
        help="Filtra os atendimentos por município. Selecione 'Todos' para não filtrar."
    )
    mun_sel = municipios if municipio_sel == "Todos" else [municipio_sel]
    idade_sel = st.slider(
        "Faixa Etária", min_value=min_idade, max_value=max_idade, value=(min_idade, max_idade),
        help="Filtra os atendimentos pela idade dos pacientes."
    )
    meses = [m for m in MESES_PT if m in df['Mes'].unique()]
    mes_sel = st.multiselect(
        "Mês da Consulta", options=meses, default=meses,
        help="Filtra os atendimentos pelo mês de realização da consulta.",
        placeholder="Selecione meses"
    )

# --- Aplica filtros ---
df_filt = df[
    df['Sexo'].isin(sexo_sel) &
    df['Especialidade'].isin(esp_sel) &
    df['Município'].isin(mun_sel) &
    df['Idade'].between(idade_sel[0], idade_sel[1]) &
    df['Mes'].isin(mes_sel)
]

# --- Renderiza cada página na respectiva aba ---
with tabs[0]:
    # --- Página Inicial ---
    st.title("Dashboard de Consultas Ambulatoriais 2023")
    st.markdown("""
    ### Objetivo
    Este dashboard interativo permite explorar e analisar os atendimentos ambulatoriais realizados em 2023. Utilize os filtros na barra lateral para refinar os dados e navegue pelas páginas para diferentes perspectivas.

    **Como navegar:**
    - Use as abas no topo para acessar diferentes análises.
    - Os filtros afetam todos os gráficos e tabelas.
    - Passe o mouse sobre os gráficos interativos para detalhes.
    """)
    st.info("Os dados exibidos já foram tratados e organizados previamente.")

    # --- Cards de Métricas de Destaque (KPIs) ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total de Atendimentos", int(df_filt.shape[0]))
    with col2:
        st.metric("Municípios Distintos", int(df_filt['Município'].nunique()))
    with col3:
        st.metric("Especialidades Distintas", int(df_filt['Especialidade'].nunique()))
    with col4:
        idade_media = df_filt['Idade'].mean()
        st.metric("Idade Média dos Pacientes", f"{idade_media:.1f}")

    st.subheader("Distribuição de Pacientes por Sexo")
    # Pie chart (gráfico de pizza) usando Plotly Express
    sexo_counts = df_filt['Sexo'].value_counts()
    fig_pie = px.pie(
        names=sexo_counts.index,
        values=sexo_counts.values,
        color=sexo_counts.index,
        color_discrete_map={"FEMININO": "pink", "MASCULINO": "skyblue"},
        title="Distribuição de Pacientes por Sexo"
    )
    fig_pie.update_traces(textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)

with tabs[1]:
    # --- Análises por Sexo ---
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

with tabs[2]:
    # --- Análises por Idade ---
    st.header("Análises por Idade")
    st.subheader("Distribuição Geral de Atendimentos por Idade")
    fig_idade = px.histogram(df_filt, x='Idade', nbins=30, title='Distribuição Geral de Atendimentos por Idade', color_discrete_sequence=['mediumseagreen'])
    st.plotly_chart(fig_idade, use_container_width=True)
    st.subheader("Boxplot de Idade por Especialidade (Top 5)")
    top_especialidades = df_filt['Especialidade'].value_counts().head(5).index
    fig_box = px.box(df_filt[df_filt['Especialidade'].isin(top_especialidades)], x='Especialidade', y='Idade', points='all', color='Especialidade', title='Idade por Especialidade (Top 5)')
    st.plotly_chart(fig_box, use_container_width=True)

with tabs[3]:
    # --- Especialidades ---
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

with tabs[4]:
    # --- Municípios ---
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

with tabs[5]:
    # --- Tendências Temporais ---
    st.header("Tendências Temporais")
    st.subheader("Tendência de Atendimentos na Semana")
    consultas_por_data = df_filt.groupby('Dia_Semana').size().reindex(['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'], fill_value=0)
    fig_semana = px.line(x=consultas_por_data.index, y=consultas_por_data.values, markers=True, labels={'x':'Dia da Semana','y':'Número de Atendimentos'}, title='Tendência de Atendimentos na Semana')
    st.plotly_chart(fig_semana, use_container_width=True)
    st.subheader("Tendência de Atendimentos por Mês")
    # Ordena os meses conforme a lista fixa
    consultas_por_mes = df_filt['Mes'].value_counts().reindex(MESES_PT, fill_value=0)
    fig_mes = px.line(x=consultas_por_mes.index, y=consultas_por_mes.values, markers=True, labels={'x':'Mês','y':'Consultas'}, title='Tendência de Atendimentos por Mês')
    st.plotly_chart(fig_mes, use_container_width=True)
