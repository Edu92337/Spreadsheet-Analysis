import os
import streamlit as st
import pandas as pd
from pandasai import SmartDataframe
from pandasai.llm import OpenAI
from pandasai.responses.response_parser import ResponseParser


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


# Interface do Streamlit
st.title("Análise e Manipulação de Planilhas com PandasAI")

# Verificar se o DataFrame foi carregado e armazenado
if 'df' not in st.session_state:
    st.session_state.df = None

# Upload do arquivo pelo usuário
uploaded_file = st.file_uploader("Faça upload de um arquivo CSV para análise", type=["csv"])

if uploaded_file:
    # Ler o arquivo enviado pelo usuário
    original_df = pd.read_csv(uploaded_file)

    # Armazenar o DataFrame original no session_state, caso não exista
    if st.session_state.df is None:
        st.session_state.df = original_df.copy()

    # Mostrar prévia do DataFrame
    with st.expander("🔎 Prévia do DataFrame"):
        st.write(st.session_state.df.head())

# Se o DataFrame já foi carregado, seguir com as interações
if st.session_state.df is not None:
    # Entrada do usuário para comandos
    query = st.text_area("🗣️ O que deseja fazer com os dados?")
    container = st.container()

    if query:
        # Configurar o LLM (OpenAI)
        llm = OpenAI(api_token = st.secrets["openai"]["api_key"])

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
                b = st.button("📥 Salvar DataFrame Modificado")

                if b:
                    # Salva o DataFrame modificado no session_state
                    st.session_state.df = st.session_state.df.copy()
                    # Mostrar uma mensagem de sucesso
                    st.success("DataFrame modificado salvo com sucesso!")

                # Botão para baixar o CSV do DataFrame modificado
                csv = st.session_state.df.to_csv(index=False)
                st.download_button(
                    label="📥 Baixar DataFrame Modificado",
                    data=csv,
                    file_name="dataframe_modificado.csv",
                    mime="text/csv"
                )

            except Exception as e:
                st.error(f"⚠️ Ocorreu um erro: {e}")
else:
    st.info("Por favor, faça upload de um arquivo CSV para continuar.")
