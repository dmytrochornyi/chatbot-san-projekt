import streamlit as st
import time
import json
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

# --- 1. KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="SAN AI - System RAG",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS - STYL GEMINI ---
st.markdown("""
    <style>
    [data-testid="sidebar-close-button"] { display: none; }
    button[kind="header"] { display: none; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .main { background-color: #131314; color: #e3e3e3; }
    .gemini-title {
        font-size: 3rem;
        font-weight: 500;
        background: linear-gradient(74deg, #4285f4 0, #9b72cb 20%, #d96570 40%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .subtitle { color: #8e918f; font-size: 1.5rem; margin-bottom: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIKA RAG (PDF + JSON) ---
@st.cache_resource
def load_embeddings():
    # Pobieranie i ładowanie prawdziwego modelu wielojęzycznego do embeddingów
    return HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

def load_knowledge_json():
    if os.path.exists("knowledge.json"):
        with open("knowledge.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

@st.cache_resource
def process_pdf(_uploaded_file):
    # Podkreślnik przed uploaded_file chroni przed błędem hashowania w Streamlit Cache
    with open("temp_upload.pdf", "wb") as f:
        f.write(_uploaded_file.getbuffer())
    
    loader = PyPDFLoader("temp_upload.pdf")
    pages = loader.load()
    
    # Podział tekstu na optymalne kawałki
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
    chunks = text_splitter.split_documents(pages)
    
    # Tworzenie bazy wektorowej FAISS z prawdziwymi embeddingami
    embeddings = load_embeddings()
    vector_db = FAISS.from_documents(chunks, embeddings)
    return vector_db

def get_answer(query, vector_db=None):
    # 1. RAG - szukanie we wgranym PDF
    if vector_db:
        # Wyszukujemy 2 najbardziej podobne fragmenty z dokumentu
        search_results = vector_db.similarity_search(query, k=2)
        if search_results:
            context = "\n\n".join([doc.page_content for doc in search_results])
            return f"**Znalazłem w przesłanym dokumencie:**\n\n{context}"

    # 2. Awaryjne szukanie w knowledge.json
    kb = load_knowledge_json()
    q_low = query.lower()
    for key, content in kb.items():
        if key.replace("_", " ") in q_low:
            return content
            
    return "Niestety nie znalazłem informacji na ten temat w bazie wiedzy ani w przesłanym pliku."

# --- 4. PANEL BOCZNY ---
with st.sidebar:
    st.markdown("<h1 style='color: white;'>SAN AI</h1>", unsafe_allow_html=True)
    st.divider()
    
    st.subheader("📁 Baza Wiedzy PDF")
    pdf_file = st.file_uploader("Wgraj regulamin (PDF)", type="pdf")
    
    v_db = None
    if pdf_file:
        with st.spinner("Indeksowanie dokumentu i generowanie wektorów..."):
            v_db = process_pdf(pdf_file)
        st.success("PDF załadowany i wektoryzacja zakończona!")
    
    st.divider()
    if st.button("Wyczyść czat"):
        st.session_state.messages = []
        st.rerun()

# --- 5. GŁÓWNY CZAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    st.markdown('<h1 class="gemini-title">Cześć,</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Jestem Twoim asystentem SAN. Wgraj PDF w panelu bocznym lub zadaj pytanie.</p>', unsafe_allow_html=True)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "✨"):
        st.markdown(msg["content"])

if prompt := st.chat_input("O co chcesz zapytać?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="✨"):
        full_text = get_answer(prompt, v_db)
        placeholder = st.empty()
        curr = ""
        # Animacja pisania
        for char in full_text:
            curr += char
            placeholder.markdown(curr + "▌")
            time.sleep(0.005)
        placeholder.markdown(curr)
        st.session_state.messages.append({"role": "assistant", "content": curr})
