import os
from firecrawl import FirecrawlApp


class ScrapingService:
    def __init__(self):
        self.api_key = os.getenv("FIRECRAWL_API_KEY")  #chave de acesso para usar o firecrawl (gratuito)
        self.api_url = os.getenv("FIRECRAWL_API_URL") #o firecrawl por ser open source, vamos baixar a aplicacao e executar com o docker

        self.app = FirecrawlApp(api_key=self.api_key, api_url=self.api_url)

    def scrap_website(self, url, collection_name):
        try:
            map_result = self.app.map_url(url) #pega todos os sublinks

            # 💡 Dica adicional: visualizar o conteúdo do map_result
            # print("🛠️ map_result:", map_result)
            # try:
            #     import streamlit as st
            #     st.write("🛠️ Resultado da varredura:", map_result)
            # except ImportError:
            #     pass  

            data = getattr(map_result, 'data', None)  # garante que data sempre existe

            if hasattr(map_result, 'links'):
                links = map_result.links
            elif data and hasattr(data, 'links'):
                links = data.links
            else:
                links = getattr(map_result, 'links', [])

            if not links:
                raise Exception("Nenhum link encontrado!")

            print(f"Encontrados {len(links)} links")

            scrape_result = self.app.batch_scrape_urls(links)

            if hasattr(scrape_result, 'data'):
                scraped_data = scrape_result.data
            else:
                scraped_data = []

            collection_path = f"data/collections/{collection_name}"
            os.makedirs(collection_path, exist_ok=True)

            saved_count = 0 

            for i, page in enumerate(scraped_data, 1):
                markdown_content = None  # inicializa como None
                origem = "nenhuma"

                print(f"\n📄 Página {i}: tipo {type(page)}")

                if hasattr(page, 'markdown') and page.markdown:
                    markdown_content = page.markdown
                    origem = "direto"

                else:
                    data = getattr(page, 'data', None)
                    if data and hasattr(data, 'markdown') and data.markdown:
                        markdown_content = data.markdown
                        origem = "via data"
                    elif isinstance(page, dict) and page.get("markdown"):
                        markdown_content = page["markdown"]
                        origem = "dict"
                if markdown_content:
                    with open(f"{collection_path}/{i}.md", "w", encoding="utf-8") as f:
                        f.write(markdown_content)
                    print(f"✅ Arquivo salvo: {i}.md (origem: {origem})")
                    saved_count += 1
                else:
                    # Salva para inspeção se desejar
                    with open(f"{collection_path}/vazio_{i}.txt", "w", encoding="utf-8") as f:
                        f.write(str(page))
                    print(f"⚠️ Nenhum markdown encontrado na página {i}. Conteúdo salvo como vazio_{i}.txt")

            return {"success": True, "files": saved_count}

        except Exception as e:
            print(f"Erro no scraping: {str(e)}")
            return {"success": False, "error": str(e)}  

            