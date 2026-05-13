import streamlit as st
import time
import json
import os
from datetime import datetime

# --- 1. KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="SAN AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded" # PANEL BĘDZIE ZAWSZE WIDOCZNY
)

# --- 2. CSS DLA WYGLĄDU I STABILNOŚCI ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Gradientowy napis */
    .gemini-gradient {
        font-size: 3rem;
        font-weight: 600;
        background: linear-gradient(74deg, #4285f4 0, #9b72cb 20%, #d96570 40%, #f39264 60%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Stylizacja przycisków w panelu bocznym */
    section[data-testid="stSidebar"] .stButton button {
        background-color: transparent;
        border: 1px solid #e3e3e3;
        text-align: left;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. LOGIKA BAZY WIEDZY ---
@st.cache_data
def load_knowledge():
    if os.path.exists("knowledge.json"):
        try:
            with open("knowledge.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"błąd": "Błąd odczytu pliku JSON."}
    return {}

knowledge_base = load_knowledge()

def robust_search(query):
    query = query.lower()
    # Szukanie dopasowania w kluczach bazy danych
    for key, value in knowledge_base.items():
        # Rozbijamy klucz na pojedyncze słowa (np. "kierunek_lekarski" -> "kierunek", "lekarski")
        key_words = key.replace("_", " ").split()
        for word in key_words:
            if len(word) > 3 and word[:4] in query: # Jeśli fragment klucza jest w pytaniu
                return value, key
    return None, None

# --- 4. PANEL BOCZNY (HISTORIA - ZAWSZE WIDOCZNA) ---
with st.sidebar:
    st.markdown("### ✨ SAN AI History")
    if st.button("➕ Rozpocznij nowy czat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    st.caption("Ostatnie zapytania")
    # Wyświetlamy ostatnie pytania użytkownika jako historię
    if "messages" in st.session_state:
        user_queries = [m["content"] for m in st.session_state.messages if m["role"] == "user"]
        for q in user_queries[-5:]: # Pokaż ostatnie 5
            st.write(f"💬 {q[:25]}...")

# --- 5. GŁÓWNY EKRAN ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    st.markdown('<div class="gemini-gradient">Witaj w SAN AI</div>', unsafe_allow_html=True)
    st.write("Zadaj pytanie o kierunek studiów, ECTS lub regulamin.")
    
    # Kafelki pomocnicze
    c1, c2 = st.columns(2)
    if c1.button("🎓 Ile trwa kierunek lekarski?"): st.session_state.chat_input_val = "lekarski"
    if c2.button("📈 Ile punktów ECTS muszę mieć?"): st.session_state.chat_input_val = "ects"
else:
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=("✨" if message["role"] == "assistant" else "👤")):
            st.markdown(message["content"])

# --- 6. OBSŁUGA CZATU ---
# Mechanizm przechwytywania kliknięć w przyciski
input_text = st.chat_input("W czym mogę pomóc?")
if "chat_input_val" in st.session_state:
    input_text = st.session_state.chat_input_val
    del st.session_state.chat_input_val

if input_text:
    # Dodaj i wyświetl pytanie
    st.session_state.messages.append({"role": "user", "content": input_text})
    with st.chat_message("user", avatar="👤"):
        st.markdown(input_text)

    # Odpowiedź bota
    with st.chat_message("assistant", avatar="✨"):
        ans, source = robust_search(input_text)
        
        if ans:
            response = ans
            if source:
                response += f"\n\n*Źródło: {source.replace('_', ' ').upper()}*"
        else:
            response = "Nie znalazłem dokładnej odpowiedzi. Spróbuj zapytać o: ECTS, lekarski, fizjoterapia, logistyka lub praktyki."

        # Animacja pisania
        placeholder = st.empty()
        full_r = ""
        for char in response:
            full_r += char
            placeholder.markdown(full_r + "▌")
            time.sleep(0.005)
        placeholder.markdown(full_r)
        
    st.session_state.messages.append({"role": "assistant", "content": full_r})
    # Nie robimy st.rerun() tutaj, żeby nie "migało" i nie zwijało panelu
