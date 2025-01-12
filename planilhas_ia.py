import os
import streamlit as st
import pandas as pd
from pandasai import SmartDataframe
from pandasai.llm import OpenAI
from pandasai.responses.response_parser import ResponseParser


st.set_page_config(layout="wide", page_title="Análise de Planilhas com PandasAI")
class CustomResponse(ResponseParser):
    """Classe para personalizar a exibição das respostas no Streamlit."""

    def __init__(self, context) -> None:
        super().__init__(context)

    def format_dataframe(self, result):
        st.dataframe(result["value"])
        return

    def format_plot(self, result):
        st.image(result["value"])
        return

    def format_other(self, result):
        st.write(result["value"])
        return

col1, col3 = st.columns([4, 3])
# Interface do Streamlit
st.title("Análise e Manipulação de Planilhas com PandasAI")

# Verificar se o DataFrame foi carregado e armazenado
if 'df' not in st.session_state:
    st.session_state.df = None

# Criando colunas na proporção 4:3
col1, col3 = st.columns([4, 3])

with col1:
    # Upload do arquivo pelo usuário
    uploaded_file = st.file_uploader("📂 Faça upload de um arquivo CSV para análise", type=["csv"])

    if uploaded_file:
        # Ler o arquivo enviado pelo usuário
        original_df = pd.read_csv(uploaded_file)

        # Armazenar o DataFrame original no session_state, caso não exista
        if st.session_state.df is None:
            st.session_state.df = original_df.copy()


    # Se o DataFrame já foi carregado, seguir com as interações
    if st.session_state.df is not None:
        # Entrada do usuário para comandos
        query = st.text_area("🗣️ O que deseja fazer com os dados?")

        if query:
            # Configurar o LLM (OpenAI)
            api_key = st.secrets["openai"]["api_key"]
            llm = OpenAI(api_token=api_key)

            # Configurar o SmartDataframe com respostas personalizadas
            query_engine = SmartDataframe(
                st.session_state.df,  # Usar o DataFrame armazenado
                config={
                    "llm": llm,
                    "response_parser": CustomResponse,
                    "disable_safety": True
                },
            )

            # Gerar resposta com base na consulta do usuário
            with st.spinner("Gerando resposta..."):
                try:
                    answer = query_engine.chat(query)
                    st.write("✅ Resposta do modelo:")
                    st.write(answer)

                    # Mostrar o DataFrame atualizado após a modificação
                    with st.expander("🔄 DataFrame atualizado"):
                        st.write(st.session_state.df)

                    # Botão para salvar o DataFrame modificado
                    if st.button("📥 Salvar DataFrame Modificado"):
                        st.session_state.df = st.session_state.df.copy()
                        st.success("DataFrame modificado salvo com sucesso!")

                except Exception as e:
                    st.error(f"⚠️ Ocorreu um erro: {e}")

with col3:
    st.header("📊 Visualização do DataFrame")
    if st.session_state.df is not None:
        st.dataframe(st.session_state.df)
    else:
        st.info("Carregue um arquivo CSV para visualizar o DataFrame.")
