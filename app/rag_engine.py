import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from google import genai
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv
from langchain_core.documents import Document

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

CHROMA_DB_PATH = "../data/bus_db" 
COLLECTION_NAME = "bus_infomation"


def check_gemini_key():
    if GEMINI_API_KEY:
        client = genai.Client(api_key=GEMINI_API_KEY)
        LLM_MODEL = 'gemini-2.5-flash'
        return client, LLM_MODEL
    else:
        return

def get_chroma_client_and_collection(path: str, collection_name: str):
    try:
        embedding_function = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        
        collection = Chroma(
            collection_name,
            embedding_function=embedding_function,
            persist_directory=path
        )
        return collection
        
    except Exception as e:
        # st.error(f"Error loading ChromaDB collection: {e}")
        # st.info(f"Make sure the directory '{path}' and collection '{collection_name}' exist.")
        return None


def get_rag_answer(user_query: str, collection) -> str:
    
    results = collection.similarity_search(
        user_query,
    )
    
    results = [doc.page_content for doc in results]
    retrieved_context = " ".join(results)
    
    prompt = f"""
    You are an expert bus ticket service assistant. Use ONLY the following retrieved context
    to answer the user's question about bus provider policies, contact details, or specific
    rules. If the information is not found in the context, politely state that you cannot
    answer based on the available provider data.
    
    CONTEXT: {retrieved_context}
    
    QUESTION: {user_query}
    
    ANSWER:
    """
    
    try:
        client, LLM_MODEL = check_gemini_key()
        response = client.models.generate_content(
            model=LLM_MODEL,
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"An error occurred during generation: {e}"

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
        | LLM_MODEL
        | str 
    )
    return rag_chain

async def process_rag_query(query: str) -> str:
    """Execute the RAG pipeline for a given user query."""
    if LLM is None or EMBEDDING_MODEL is None:
        return "RAG engine is unavailable. Check API key and dependencies."
    
    
    rag_chain = get_rag_chain()
    return rag_chain.invoke(query)