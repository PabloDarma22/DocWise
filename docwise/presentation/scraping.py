import streamlit as st
import os 
from service.scraping import ScrapingService

def show():
    st.header("🔎 Web Scraping")

    scraper = ScrapingService()

    with st.form('scraping_form'):
        url = st.text_input("URL do site:", placeholder="https://exemplo.com")
        collection_name = st.text_input("Nome da coleção:", placeholder="minha-colecao")
        submited = st.form_submit_button("Iniciar scraping")

        if submited and url and collection_name:
            with st.spinner("Extraindo conteúdo..."):
                result = scraper.scrap_website(url, collection_name)

            if result["success"]:
                st.success(f"✅ {result['files']} arquivos salvos.")
            else:
                st.error(f"❌ Erro:{result['error']}")