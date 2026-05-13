import streamlit as st
import time
import json
import os

# --- 1. KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="SAN AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed" # Domyślnie zwinięty pasek boczny dla minimalizmu
)

# --- 2. CSS W STYLU GEMINI ---
st.markdown("""
    <style>
    /* Ukrycie elementów Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Globalna czcionka przypominająca Google Sans */
    html, body, [class*="css"]  {
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Gradientowy tekst powitalny w stylu Gemini */
    .gemini-title {
        font-size: 3.5rem;
        font-weight: 500;
        letter-spacing: -1px;
        background: -webkit-linear-gradient(74deg, #4285f4 0, #9b72cb 9%, #d96570 20%, #d96570 24%, #9b72cb 35%, #4285f4 44%, #9b72cb 50%, #d96570 56%, #f39264 75%, #f39264 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
        line-height: 1.2;
    }
    .gemini-subtitle {
        font-size: 3.5rem;
        font-weight: 500;
        color: #c4c7c5;
        letter-spacing: -1px;
        margin-top: -10px;
        margin-bottom: 40px;
    }

    /* Kafelki z podpowiedziami (Prompt Cards) */
    .stButton>button {
        width: 100%;
        height: 100px;
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        background-color: #f8f9fa;
        color: #1f1f1f;
        text-align: left;
        padding: 15px;
        font-size: 1rem;
        transition: background-color 0.2s, box-shadow 0.2s;
        display: flex;
        align-items: flex-start;
        justify-content: flex-start;
        white-space: normal;
    }
    
    /* Tryb ciemny dla kafelków */
    @media (prefers-color-scheme: dark) {
        .stButton>button {
            background-color: #1e1e20;
            border: 1px solid #333;
            color: #e3e3e3;
        }
        .stButton>button:hover {
            background-color: #2a2a2c;
        }
        .gemini-subtitle {
            color: #444746;
        }
    }
    
    .stButton>button:hover {
        background-color: #f0f4f9;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border-color: transparent;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. BAZA WIEDZY I LOGIKA ---
@st.cache_data
def load_knowledge():
    if os.path.exists("knowledge.json"):
        with open("knowledge.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {"błąd": "Brak pliku bazy danych."}

knowledge_base = load_knowledge()

def get_san_response(user_query):
    user_query = user_query.lower()
    time.sleep(0.8) # Symulacja myślenia
        
    for key, value in knowledge_base.items():
        readable_key = key.replace("_", " ")
        if readable_key in user_query or user_query in readable_key:
            return value, key
            
    return "Przepraszam, ale nie znalazłem dokładnych informacji na ten temat w dostępnych regulaminach i sylabusach. Spróbuj zadać pytanie używając innych słów.", None

# --- 4. PANEL BOCZNY (Tylko historia, jak w Gemini) ---
with st.sidebar:
    st.write("### Ostatnie rozmowy")
    st.caption("Historia sesji (tymczasowa)")
    if st.button("➕ Nowy czat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- 5. INICJALIZACJA STANU ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 6. GŁÓWNY INTERFEJS (Ekran powitalny vs Czat) ---
if len(st.session_state.messages) == 0:
    # Ekran początkowy (Pokazuje się tylko, gdy nie ma wiadomości)
    st.markdown('<div class="gemini-title">Witaj, studencie</div>', unsafe_allow_html=True)
    st.markdown('<div class="gemini-subtitle">W czym mogę Ci dzisiaj pomóc?</div>', unsafe_allow_html=True)
    
    st.write("") # Odstęp
    
    cols = st.columns(4)
    # Kafelki pytań
    if cols[0].button("📚\n\nJakie są wymogi punktów ECTS na uczelni?"): 
        st.session_state.auto_prompt = "Ile punktów ECTS muszę zdobyć?"
    if cols[1].button("🏥\n\nIle trwają praktyki na kierunku fizjoterapia?"): 
        st.session_state.auto_prompt = "Ile godzin praktyk na fizjoterapii?"
    if cols[2].button("📝\n\nJakie są zasady poprawiania egzaminów?"): 
        st.session_state.auto_prompt = "Co to jest wpis warunkowy i jak działają poprawki?"
    if cols[3].button("🎓\n\nJak wygląda obrona pracy dyplomowej?"): 
        st.session_state.auto_prompt = "Zasady dotyczące pracy dyplomowej."

else:
    # Renderowanie historii czatu (jeśli już trwa rozmowa)
    for message in st.session_state.messages:
        # Używamy ✨ jako avatara dla bota i domyślnego dla użytkownika
        avatar = "✨" if message["role"] == "assistant" else "👤"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

# --- 7. POLE WEJŚCIOWE ---
prompt = st.chat_input("Wpisz swoje pytanie tutaj...")
    
# Przechwycenie pytania z kafelków
if "auto_prompt" in st.session_state:
    prompt = st.session_state.auto_prompt
    del st.session_state.auto_prompt

if prompt:
    # Zapisz pytanie użytkownika
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Przeładuj stronę, żeby ukryć ekran powitalny i pokazać pytanie
    if len(st.session_state.messages) == 1:
        st.rerun()
        
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Odpowiedź bota
    with st.chat_message("assistant", avatar="✨"):
        message_placeholder = st.empty()
        
        response_text, source_key = get_san_response(prompt)
        
        # Płynne generowanie tekstu
        full_res = ""
        for char in response_text:
            full_res += char
            message_placeholder.markdown(full_res + "▌")
            time.sleep(0.005) # Szybkość pisania
        
        # Wyświetlenie dyskretnego źródła (jak przypisy w Gemini)
        if source_key:
            full_res += f"\n\n<span style='color:gray; font-size: 0.8em;'>Źródło danych: {source_key.replace('_', ' ').capitalize()}</span>"
            
        message_placeholder.markdown(full_res, unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": full_res})
