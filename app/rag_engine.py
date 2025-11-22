import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAI, GoogleGenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from typing import List
from langchain_core.documents import Document

PERSIST_DIRECTORY = "chroma_db"
DATA_DIR = "../data/attachments"
COLLECTION_NAME = "bus_policy_info"


if not os.environ.get("GEMINI_API_KEY"):
    print("WARNING: GEMINI_API_KEY environment variable is not set. RAG will fail.")
    os.environ["GEMINI_API_KEY"] = "DUMMY_KEY_FOR_SETUP" 

try:
    EMBEDDING_MODEL = GoogleGenAIEmbeddings(model="text-embedding-004")
    LLM = GoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)
except Exception as e:
    print(f"Error initializing Gemini models: {e}")
    EMBEDDING_MODEL = None
    LLM = None


def get_vector_store():
    """Initializes the ChromaDB Vector Store."""
    if EMBEDDING_MODEL is None:
        raise ConnectionError("Embedding model failed to initialize. Cannot access vector store.")
        
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=EMBEDDING_MODEL,
        persist_directory=PERSIST_DIRECTORY
    )

def create_vector_store():
    """Loads documents, splits them, and creates/updates the ChromaDB Vector Store."""
    if os.path.exists(PERSIST_DIRECTORY):
        print("✅ Vector store directory exists. Assuming policies are ingested.")
        
        try:
             store = get_vector_store()
             if store._collection.count() > 0:
                 print(f"✅ ChromaDB collection '{COLLECTION_NAME}' loaded with {store._collection.count()} documents.")
                 return
        except Exception:
             print("⚠️ Could not load existing vector store. Re-ingesting...")

    print("--- Starting RAG Ingestion Pipeline ---")
    
    
    loader = DirectoryLoader(
        DATA_DIR, 
        glob="*.txt", 
        loader_cls=TextLoader, 
        loader_kwargs={'encoding': 'utf8'}
    )
    try:
        documents: List[Document] = loader.load()
    except FileNotFoundError:
        print(f"⚠️ Policy file directory not found at {DATA_DIR}. RAG will not function.")
        return
        
    print(f"Loaded {len(documents)} policy documents.")

    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=512, 
        chunk_overlap=50
    )
    docs = text_splitter.split_documents(documents)
    print(f"Split documents into {len(docs)} chunks.")

    
    Chroma.from_documents(
        documents=docs,
        embedding=EMBEDDING_MODEL,
        persist_directory=PERSIST_DIRECTORY,
        collection_name=COLLECTION_NAME
    )
    print("--- RAG Ingestion Complete. Vector Store Ready. ---")




def get_rag_chain():
    """Defines the RAG execution chain using LangChain."""
    
    vectorstore = get_vector_store()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    
    # Define the template for the LLM
    template = """
    You are an expert bus ticket service assistant. Use ONLY the following retrieved context
    to answer the user's question about bus provider policies, contact details, or specific
    rules. If the information is not found in the context, politely state that you cannot
    answer based on the available provider data.

    CONTEXT:
    {context}

    USER QUESTION: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)
    
    
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()} 
        | prompt
        | LLM
        | str 
    )
    return rag_chain

async def process_rag_query(query: str) -> str:
    """Execute the RAG pipeline for a given user query."""
    if LLM is None or EMBEDDING_MODEL is None:
        return "RAG engine is unavailable. Check API key and dependencies."
    
    
    rag_chain = get_rag_chain()
    return rag_chain.invoke(query)