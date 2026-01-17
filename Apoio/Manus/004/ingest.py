import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv

load_dotenv()

# Configurações
KNOWLEDGE_FILE = "knowledge_base.txt"
CHROMA_PATH = "chroma_db"
# Para PGvector, as configurações seriam:
# CONNECTION_STRING = "postgresql+psycopg2://user:password@localhost:5432/rag_db"
# COLLECTION_NAME = "manus_knowledge"

def ingest_data():
    """
    Processa o arquivo de conhecimento, divide em chunks e cria o VectorStore.
    """
    print(f"Carregando documentos de {KNOWLEDGE_FILE}...")
    loader = TextLoader(KNOWLEDGE_FILE)
    documents = loader.load()

    # 1. Divisão em Chunks (Chunking)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Documentos divididos em {len(chunks)} chunks.")

    # 2. Criação dos Embeddings e VectorStore
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # Usando Chroma para demonstração local.
    # No guia final, detalharemos a substituição por PGvector.
    print(f"Criando Chroma VectorStore em {CHROMA_PATH}...")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )
    vectorstore.persist()
    print("Ingestão de dados concluída.")

if __name__ == "__main__":
    # Certifique-se de que a chave da API do OpenAI está configurada
    if not os.getenv("OPENAI_API_KEY"):
        print("ERRO: A variável de ambiente OPENAI_API_KEY não está configurada.")
    else:
        ingest_data()
