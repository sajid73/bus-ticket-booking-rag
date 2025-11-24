import os
# import chromadb
import streamlit as st
from google import genai
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
# from google.generativeai import types

# Load environment variables from .env file
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

CHROMA_DB_PATH = "../data/bus_db" 
COLLECTION_NAME = "bus_infomation"

if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)
    LLM_MODEL = 'gemini-2.5-flash'
else:
    st.error("GEMINI_API_KEY not found. Please set the environment variable.")
    st.stop()

# --- ChromaDB and Embedding Setup (Singleton Pattern) ---
@st.cache_resource
def get_chroma_client_and_collection(path: str, collection_name: str):
    """Initializes the persistent ChromaDB client and collection."""
    try:
        # 1. Initialize the embedding function (must match the one used for ingestion)
        embedding_function = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        
        # 2. Initialize the persistent client
        # client = chromadb.PersistentClient(path=path)
        
        # 3. Get the existing collection
        collection = Chroma(
            collection_name,
            embedding_function=embedding_function,
            persist_directory=path
        )
        return collection
        
    except Exception as e:
        st.error(f"Error loading ChromaDB collection: {e}")
        st.info(f"Make sure the directory '{path}' and collection '{collection_name}' exist.")
        return None

# --- RAG Function ---
def get_rag_answer(user_query: str, collection) -> str:
    """Performs retrieval and generation."""
    
    # 1. Retrieval (Search the DB)
    results = collection.similarity_search(
        user_query,
        # k=1, # Retrieve top 3 relevant chunks
        # include=['documents']
    )
    
    # Extract the retrieved text chunks
    # print(results)
    results = [doc.page_content for doc in results]
    retrieved_context = " ".join(results)
    
    # 2. Generation (Prompt the LLM)
    prompt = f"""
    You are a helpful assistant. Use the following context in your response:
    
    CONTEXT: {retrieved_context}
    
    QUESTION: {user_query}
    
    ANSWER:
    """

    try:
        response = client.models.generate_content(
            model=LLM_MODEL,
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"An error occurred during generation: {e}"

# --- Streamlit Interface ---
def main():
    st.title("📚 ChromaDB RAG Chatbot with Gemini")
    
    # Load the collection once and cache it
    collection = get_chroma_client_and_collection(CHROMA_DB_PATH, COLLECTION_NAME)
    
    if collection is None:
        st.stop()
        
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Display user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate and display assistant response
        with st.spinner("Searching and generating response..."):
            answer = get_rag_answer(prompt, collection)

        with st.chat_message("assistant"):
            st.markdown(answer)
            
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": answer})

if __name__ == "__main__":
    main()