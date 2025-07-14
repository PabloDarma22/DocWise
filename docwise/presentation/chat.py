import streamlit as st
from urllib3 import response
from service.rag import RAGService

def show():
    st.header("💬 Chat de Documentos")

    if not st.session_state.collection:
        st.info("Selecione uma coleção primeiro na seção de Scraping")
        return

    st.success(f"📂 coleção ativa: {st.session_state.collection}")

    if "rag_service" not in st.session_state:
        st.session_state.rag_service = RAGService()

    if "current_collection" not in st.session_state or st.session_state.current_collection != st.session_state.collection:
        with st.spinner("Carregando documentos..."):
            success = st.session_state.rag_service.load_collection(st.session_state.collection)
            if success:
                st.session_state.current_collection = st.session_state.collection
                st.success("Documentos carregados com sucesso")
            else:
                st.error("Erro ao carregar documentos")
                return 

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if prompt := st.chat_input("Faça uma pergunta sobre os documentos..."):
        st.chat_message("user").write(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                response = st.session_state.rag_service.ask_question(prompt)
                st.write(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

    if st.button("🗑️ Limpar Chat"):
        st.session_state.messages = []
        st.rerun()


