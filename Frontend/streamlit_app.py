import os
# import chromadb
import streamlit as st
from google import genai
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

st.set_page_config(layout="wide", page_title="Ticket Booking System")

main_page = st.Page("main_page.py", title="Home", icon="🏠")
manage_booking = st.Page("manage_booking.py", title="My Booking", icon="🚌")
chatbot = st.Page("chatbot.py", title="Chatbot", icon="❄️")

pg = st.navigation([main_page, manage_booking, chatbot])

pg.run()