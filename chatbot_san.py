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
    initial_sidebar_state="expanded"
)

# --- 2. ZAAWANSOWANY CSS (STYL GEMINI PREMIUM) ---
st.markdown("""
    <style>
    /* Usunięcie elementów systemowych */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Tło i czcionki */
    .main {
        background-color: #f0f4f9;
    }
    @media (prefers-color-scheme: dark) {
        .main { background-color: #131314; }
    }

    /* Gradientowy napis Gemini */
    .gemini-gradient {
        font-size: 3.5rem;
        font-weight: 500;
        background: linear-gradient(74deg, #4285f4 0, #9b72cb 20%, #d96570 40%, #f39264 60%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .gemini-subtitle {
        font-size: 3.5rem;
        font-weight: 500;
        color: #c4c7c5;
        margin-top: -15px;
        margin-bottom: 40px;
    }

    /* Stylizacja lewego panelu (Historia) */
    [data-testid="stSidebar"] {
        background-color: #f0f4f9;
        border-right: 1px solid #e3e3e3;
    }
    @media (prefers-color-scheme: dark) {
        [data-testid="stSidebar"] {
            background-color: #1e1e20;
            border-right: 1px solid #333;
        }
    }

    /* Kafelki sugestii (Cards) */
    .stButton>button {
        width: 100%;
        border-radius: 16px;
        border: none;
        background-color: #ffffff;
        padding: 20px;
        text-align: left;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    @media (prefers-color-scheme: dark) {
        .stButton>button { background-color: #1e1e20; color: white; box-shadow: none; border: 1px solid #333; }
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        background-color: #f8f9fa;
    }

    /* Wyśrodkowanie promptu na dole */
    .stChatInputContainer {
        padding-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. LOGIKA BAZY WIEDZY ---
@st.cache_data
def load_knowledge():
    if os.path.exists("knowledge.json"):
        with open("knowledge.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {"błąd": "Baza wiedzy nie została załadowana."}

knowledge_base = load_knowledge()

def search_knowledge(query):
    query = query.lower()
    time.sleep(1.0) # Realistyczne opóźnienie AI
    for key, value in knowledge_base.items():
        if key.replace("_", " ") in query or query in key:
            return value, key
    return "Przepraszam, nie znalazłem informacji na ten temat w dokumentacji SAN. Spróbuj zapytać o konkretny kierunek, punkty ECTS lub regulamin.", None

# --- 4. ZARZĄDZANIE HISTORIĄ (LEWY PANEL) ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [] # Lista tytułów rozmów
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.write("") 
    if st.button("➕ Nowy czat", use_container_width=True, type="primary"):
        if len(st.session_state.messages) > 0:
            # Zapisz obecny czat do historii przed czyszczeniem
            title = st.session_state.messages[0]["content"][:30] + "..."
            st.session_state.chat_history.insert(0, {"title": title, "date": datetime.now().strftime("%H:%M")})
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption("Niedawne")
    for chat in st.session_state.chat_history:
        st.button(f"💬 {chat['title']}", key=f"hist_{chat['title']}", use_container_width=True)

# --- 5. GŁÓWNY INTERFEJS (PRAWY PANEL) ---
if len(st.session_state.messages) == 0:
    # EKRAN POWITALNY (Gdy czat jest pusty)
    st.write("")
    st.write("")
    st.markdown('<div class="gemini-gradient">Witaj, studencie SAN</div>', unsafe_allow_html=True)
    st.markdown('<div class="gemini-subtitle">W czym mogę Ci dzisiaj pomóc?</div>', unsafe_allow_html=True)

    # KAFELKI SUGESTII
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("📚\n\nSprawdź wymogi ECTS"): st.session_state.temp_prompt = "Ile punktów ECTS muszę zdobyć na semestr?"
    with col2:
        if st.button("🏥\n\nPraktyki Fizjoterapia"): st.session_state.temp_prompt = "Ile godzin praktyk zawodowych jest na fizjoterapii?"
    with col3:
        if st.button("⚖️\n\nRegulamin poprawkowy"): st.session_state.temp_prompt = "Jak działają terminy poprawkowe i wpis warunkowy?"
    with col4:
        if st.button("🎓\n\nObrona magisterska"): st.session_state.temp_prompt = "Jak wygląda proces obrony pracy dyplomowej?"

else:
    # WYŚWIETLANIE ROZMOWY
    for message in st.session_state.messages:
        avatar = "✨" if message["role"] == "assistant" else "👤"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

# --- 6. OBSŁUGA WEJŚCIA (CHAT INPUT) ---
prompt = st.chat_input("Wpisz pytanie...")

# Obsługa kliknięcia w kafelki
if "temp_prompt" in st.session_state:
    prompt = st.session_state.temp_prompt
    del st.session_state.temp_prompt

if prompt:
    # Dodaj pytanie użytkownika
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Odśwież, aby pokazać czat zamiast ekranu powitalnego
    if len(st.session_state.messages) == 1:
        st.rerun()

    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="✨"):
        placeholder = st.empty()
        full_res = ""
        
        # Logika wyszukiwania
        answer, source = search_knowledge(prompt)
        
        # Animacja pisania
        for char in answer:
            full_res += char
            placeholder.markdown(full_res + "▌")
            time.sleep(0.005)
        
        if source:
            full_res += f"\n\n<span style='color:gray; font-size: 0.85em;'>Informacja na podstawie: **{source.replace('_', ' ').upper()}**</span>"
        
        placeholder.markdown(full_res, unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": full_res})
