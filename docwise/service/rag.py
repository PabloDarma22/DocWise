import os
from pydantic import SecretStr
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain.prompts import PromptTemplate


class RAGService:
    def __init__(self):
        self.embeddings = HuggingFaceBgeEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        self.llm = ChatGroq(
            api_key=SecretStr(api_key),
            model="llama3-8b-8192"
        )

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

        self.vector_store = None
        self.qa_chain = None


    def load_collection(self, collection_name):

        collection_path = f"data/collections/{collection_name}"

        loader = DirectoryLoader(
            collection_path,
            glob="**/*.md",
            loader_cls=TextLoader,
            loader_kwargs={'encoding': 'utf-8'}
        )

        documents = loader.load()

        if not documents:
            return False

        texts = self.text_splitter.split_documents(documents)

        self.vector_store = FAISS.from_documents(texts, self.embeddings)

        template = """
            Você é um assistente técnico especializado. Sua função é responder perguntas com base exclusiva nos documentos fornecidos.
            Não utilize conhecimento externo. Não suponha, não invente e não generalize.
            Baseie sua resposta apenas nas informações presentes no contexto abaixo.

            Se a resposta não estiver nos documentos, diga de forma clara:
            "A documentação fornecida não contém essa informação."

            Se aplicável, fundamente sua resposta com trechos relevantes do conteúdo.

            Documentação: {context}

            Pergunta: {question}
        """

        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )

        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(search_kwargs={"k": 3}),
            chain_type_kwargs={"prompt": prompt}
        )

        return True

    def ask_question(self, question):

        if not self.qa_chain:
            return "Nenhuma coleção carregada."

        try:
            result = self.qa_chain.invoke({"query": question})
            return result

        except Exception as e:
            return f"Erro ao processar a pergunta: {str(e)}"