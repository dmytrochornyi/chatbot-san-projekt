import streamlit as st
import os
import time
import json
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

# --- KONFIGURACJA ---
st.set_page_config(page_title="SAN AI - Prosty Asystent", layout="centered")

# --- ŁADOWANIE EMBEDDINGÓW ---
@st.cache_resource
def get_embeddings():
    # Używamy standardowego modelu - najbardziej stabilny wybór
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# --- PRZETWARZANIE PDF-ÓW ---
@st.cache_resource
def load_all_pdfs():
    # Szukamy wszystkich plików PDF w głównym folderze
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    if not pdf_files:
        return None
    
    all_docs = []
    for pdf in pdf_files:
        try:
            loader = PyPDFLoader(pdf)
            all_docs.extend(loader.load())
        except Exception as e:
            st.error(f"Błąd przy pliku {pdf}: {e}")
            
    # Dzielenie na kawałki
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(all_docs)
    
    # Tworzenie bazy wektorowej
    return FAISS.from_documents(chunks, get_embeddings())

# --- BAZA JSON ---
def load_json_data():
    if os.path.exists("knowledge.json"):
        with open("knowledge.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# --- LOGIKA ODPOWIEDZI ---
def get_response(query, db, kb):
    # 1. Sprawdź JSON (najszybsze i konkretne odpowiedzi)
    q_low = query.lower()
    for key, val in kb.items():
        if key.replace("_", " ") in q_low:
            return val
            
    # 2. Sprawdź PDF-y (RAG)
    if db:
        results = db.similarity_search(query, k=2)
        if results:
            context = "\n\n".join([r.page_content for r in results])
            return f"**Informacja z dokumentów:**\n\n{context}"
            
    return "Niestety nie znalazłem odpowiedzi w moich dokumentach."

# --- INTERFEJS ---
st.title("✨ SAN AI - Asystent")
st.write("Wczytane dokumenty: regulamin.pdf, 1.pdf, 2.pdf, 3.pdf")

# Inicjalizacja bazy
with st.spinner("Ładowanie bazy wiedzy..."):
    vector_db = load_all_pdfs()
    json_kb = load_json_data()

# Historia czatu
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Wejście użytkownika
if prompt := st.chat_input("Zadaj pytanie o studia..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    with st.chat_message("assistant"):
        res = get_response(prompt, vector_db, json_kb)
        st.markdown(res)
        st.session_state.messages.append({"role": "assistant", "content": res})

# Panel boczny
with st.sidebar:
    st.header("Status")
    if vector_db: st.success("Baza PDF aktywna")
    if json_kb: st.success("Baza JSON aktywna")
    if st.button("Wyczyść czat"):
        st.session_state.messages = []
        st.rerun()
