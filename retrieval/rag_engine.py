import os
import getpass

from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.embeddings import GoogleGenAIEmbeddings
from langchain_chroma import Chroma

loader = DirectoryLoader("../data/attachment", glob="*.txt")

text_document = loader.load()
for doc in text_document:
    print(doc.page_content[:])


text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)

documents = text_splitter.split_documents(text_document)

# vector embedding and vector storage

if not os.getenv("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google API key: ")

db = Chroma.from_documents(documents, GoogleGenAIEmbeddings(model="models/text-embedding-004"), persist_directory="../data/vectorstore")



# # rag_engine.py
# import os
# from langchain_community.vectorstores import Chroma
# from langchain_google_genai import GoogleGenAIEmbeddings
# from langchain.chains.retrieval_qa.base import RetrievalQA
# from langchain.embeddings import GoogleGenAIEmbeddings
# from langchain_text_splitters import RecursiveCharacterTextSplitter

# VECTORSTORE_DIR = "../data/vectorstore"

# def create_vector_store(data_folder="../data/attachment"):
#     """Load text files, split, embed, and store in Chroma vector DB."""
#     # 1. Load text files
#     documents = []
#     for filename in os.listdir(data_folder):
#         if filename.endswith(".txt"):
#             with open(os.path.join(data_folder, filename), "r", encoding="utf-8") as f:
#                 content = f.read()
#                 documents.append({"text": content, "metadata": {"source": filename}})
    
#     # 2. Split text into chunks
#     splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
#     docs_split = []
#     for doc in documents:
#         chunks = splitter.split_text(doc["text"])
#         for chunk in chunks:
#             docs_split.append({"text": chunk, "metadata": doc["metadata"]})
    
#     # 3. Initialize embeddings
#     embeddings = GoogleGenAIEmbeddings(model_name="models/gemini-embedding-001", api_key=os.environ["GEMINI_API_KEY"])
    
#     # 4. Create or load Chroma vectorstore
#     vectordb = Chroma(
#         collection_name="bus_providers_policies",
#         persist_directory=VECTORSTORE_DIR,
#         embedding_function=embeddings
#     )
    
#     vectordb.add_texts([d["text"] for d in docs_split], metadatas=[d["metadata"] for d in docs_split])
#     vectordb.persist()
#     return vectordb


# async def process_rag_query(query: str):
#     """Given a user query, use the RAG pipeline to return an answer."""
#     embeddings = GoogleGenAIEmbeddings(model_name="text-bison-001", api_key=os.environ["GEMINI_API_KEY"])
#     vectordb = Chroma(persist_directory=VECTORSTORE_DIR, embedding_function=embeddings)
#     retriever = vectordb.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    
#     llm = ChatGoogleGemini(model="chat-bison-001", api_key=os.environ["GEMINI_API_KEY"])
#     qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
    
#     result = qa.run(query)
#     return result

# create_vector_store()