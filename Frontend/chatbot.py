import os
import streamlit as st
from google import genai
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

CHROMA_DB_PATH = "../data/bus_db"
COLLECTION_NAME ="bus_infomation"

if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)
    LLM_MODEL = 'gemini-2.5-flash-lite'
else:
    st.error("GEMINI_API_KEY not found. Please set the environment variable.")
    st.stop()

@st.cache_resource
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
        st.error(f"Error loading ChromaDB collection: {e}")
        st.info(f"Make sure the directory '{path}' and collection '{collection_name}' exist.")
        return None

def get_rag_answer(user_query: str, collection) -> str:
    
    results = collection.similarity_search(user_query)
    
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
        response = client.models.generate_content(
            model=LLM_MODEL,
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"An error occurred during generation: {e}"
    


st.title("Ask Questions about ticket")

collection = get_chroma_client_and_collection(CHROMA_DB_PATH, COLLECTION_NAME)

if collection is None:
    st.stop()
    
if "messages" not in st.session_state:
    st.session_state.messages = []
    
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a question about ticket / bus information"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Searching and generating response..."):
        answer = get_rag_answer(prompt, collection)

    with st.chat_message("assistant"):
        st.markdown(answer)
        
    st.session_state.messages.append({"role": "assistant", "content": answer})