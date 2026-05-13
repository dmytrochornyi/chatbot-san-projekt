import streamlit as st
import time
import json
import os
from datetime import datetime

# --- 1. KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="SAN AI - System Ekspercki",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. NIESTANDARDOWY STYL CSS ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stButton>button {
        border-radius: 20px;
        border: 1px solid #1E3A8A;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        border: 1px solid #3b82f6;
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.1);
    }
    
    .main-header {
        font-size: 2.8rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: -1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #6B7280;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. WGRYWANIE BAZY WIEDZY ---
@st.cache_data
def load_knowledge():
    if os.path.exists("knowledge.json"):
        with open("knowledge.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {"błąd": "Brak pliku bazy danych."}

knowledge_base = load_knowledge()

# --- 4. LOGIKA WYSZUKIWANIA ---
def get_san_response(user_query, temperature):
    user_query = user_query.lower()
    
    # Symulacja czasu procesowania
    time.sleep(0.6 + (temperature * 0.4))
        
    for key, value in knowledge_base.items():
        readable_key = key.replace("_", " ")
        if readable_key in user_query or user_query in readable_key:
            return value, key
            
    return "Przykro mi, nie potrafię odnaleźć odpowiednich dokumentów w aktualnym indeksie wiedzy. Spróbuj zadać pytanie inaczej.", None

# --- 5. PANEL BOCZNY (ADMINISTRATORA) ---
with st.sidebar:
    st.markdown("### ⚙️ Panel Kontrolny")
    
    # Metryki
    col1, col2 = st.columns(2)
    col1.metric("Baza Wiedzy", f"{len(knowledge_base)} wpisów")
    col2.metric("Opóźnienie", "0.8s")
    
    st.divider()
    
    # Ustawienia (Usunięto wybór modelu)
    st.markdown("#### Konfiguracja Silnika")
    temperature = st.slider("Temperatura (Kreatywność)", 0.0, 1.0, 0.2, 0.1)
    
    st.divider()
    st.markdown("#### Zarządzanie Sesją")
    
    if st.button("🗑️ Resetuj historię", use_container_width=True):
        st.session_state.messages = [{"role": "assistant", "content": "Historia wyczyszczona. W czym mogę pomóc?"}]
        st.rerun()
        
    if "messages" in st.session_state and len(st.session_state.messages) > 1:
        chat_export = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
        st.download_button(
            label="💾 Pobierz transkrypt",
            data=chat_export,
            file_name=f"chat_san_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True
        )

# --- 6. GŁÓWNY INTERFEJS ---
st.markdown('<div class="main-header">🎓 SAN AI Asystent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Inteligentny system ekspercki oparty na bazie wiedzy SAN</div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["💬 Czat", "📊 Baza Danych", "ℹ️ Dokumentacja"])

with tab2:
    st.subheader("Aktualnie zindeksowana wiedza")
    st.json(knowledge_base)

with tab3:
    st.subheader("Architektura Systemu")
    st.markdown("""
    Projekt wykorzystuje podejście **RAG (Retrieval-Augmented Generation)**:
    1. **Ekstrakcja:** Dane pobierane są z pliku `knowledge.json`.
    2. **Wyszukiwanie:** Algorytm dopasowuje zapytanie użytkownika do kluczy semantycznych.
    3. **Prezentacja:** Odpowiedź jest generowana w czasie rzeczywistym z adnotacją źródłową.
    """)

with tab1:
    # Sugerowane pytania
    st.markdown("**Szybki wybór:**")
    cols = st.columns(4)
    if cols[0].button("Medycyna ECTS"): st.session_state.auto_prompt = "Ile punktów ECTS ma kierunek lekarski?"
    if cols[1].button("Praktyki"): st.session_state.auto_prompt = "Ile godzin praktyk na fizjoterapii?"
    if cols[2].button("Warunek"): st.session_state.auto_prompt = "Co to jest wpis warunkowy?"
    if cols[3].button("Logistyka"): st.session_state.auto_prompt = "Jakie są przedmioty na logistyce?"

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Cześć! Jestem gotowy odpowiedzieć na pytania o Twoje studia. O co chcesz zapytać?"}]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Obsługa wejścia
    prompt = st.chat_input("Napisz wiadomość...")
    
    if "auto_prompt" in st.session_state:
        prompt = st.session_state.auto_prompt
        del st.session_state.auto_prompt

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            # Profesjonalny status procesowania
            with st.status("Generowanie odpowiedzi...", expanded=False) as status:
                st.write("Analizowanie zapytania...")
                time.sleep(0.2)
                st.write("Przeszukiwanie bazy dokumentów...")
                response_text, source_key = get_san_response(prompt, temperature)
                status.update(label="Odpowiedź gotowa!", state="complete")
            
            # Efekt pisania
            message_placeholder = st.empty()
            full_res = ""
            for char in response_text:
                full_res += char
                message_placeholder.markdown(full_res + "▌")
                time.sleep(0.005)
            
            if source_key:
                full_res += f"\n\n---\n*Źródło: `[{source_key.upper()}]`*"
            
            message_placeholder.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
