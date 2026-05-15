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
    page_title="SAN AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS (STYL GEMINI) ---
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

# --- 3. LOGIKA RAG I BAZY WIEDZY ---
@st.cache_resource
def load_embeddings():
    # Używamy mniejszego, szybszego modelu
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

@st.cache_resource
def init_rag():
    """Automatyczne ładowanie PDF z GitHuba jeśli istnieje"""
    pdf_name = "regulamin.pdf"  # Tak nazwij swój plik na GitHubie
    if os.path.exists(pdf_name):
        loader = PyPDFLoader(pdf_name)
        pages = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
        chunks = text_splitter.split_documents(pages)
        embeddings = load_embeddings()
        return FAISS.from_documents(chunks, embeddings)
    return None

def load_knowledge_json():
    if os.path.exists("knowledge.json"):
        with open("knowledge.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def get_answer(query, vector_db):
    # 1. Najpierw szukamy w PDF (RAG)
    if vector_db:
        results = vector_db.similarity_search(query, k=2)
        if results:
            context = "\n\n".join([doc.page_content for doc in results])
            return f"**Znalazłem w dokumentach uczelni:**\n\n{context}"

    # 2. Jeśli nie ma w PDF, szukamy w knowledge.json
    kb = load_knowledge_json()
    q_low = query.lower()
    for key, content in kb.items():
        if key.replace("_", " ") in q_low:
            return content
            
    return "Przepraszam, nie znalazłem informacji na ten temat w moich bazach danych."

# --- 4. URUCHOMIENIE BAZY ---
v_db = init_rag()

# --- 5. INTERFEJS CZATU ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Ekran powitalny
if not st.session_state.messages:
    st.markdown('<h1 class="gemini-title">Cześć,</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Jestem inteligentnym asystentem SAN. O co chcesz zapytać?</p>', unsafe_allow_html=True)

# Wyświetlanie historii
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "✨"):
        st.markdown(msg["content"])

# Obsługa pytania
if prompt := st.chat_input("Zadaj pytanie dotyczące studiów..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="✨"):
        full_text = get_answer(prompt, v_db)
        placeholder = st.empty()
        curr = ""
        for char in full_text:
            curr += char
            placeholder.markdown(curr + "▌")
            time.sleep(0.005)
        placeholder.markdown(curr)
        st.session_state.messages.append({"role": "assistant", "content": curr})

# Panel boczny (tylko informacyjny)
with st.sidebar:
    st.markdown("<h1 style='color: white;'>SAN AI</h1>", unsafe_allow_html=True)
    st.write("Status bazy wiedzy:")
    if v_db:
        st.success("✅ Regulamin PDF załadowany")
    else:
        st.warning("⚠️ Brak pliku regulamin.pdf na GitHubie")
    
    if os.path.exists("knowledge.json"):
        st.success("✅ knowledge.json załadowany")
    else:
        st.warning("⚠️ Brak pliku knowledge.json")
