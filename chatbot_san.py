import streamlit as st
import time
import json
import os

# --- 1. TWARDA KONFIGURACJA STRONY ---
# Ustawienie "expanded" wymusza otwarcie panelu bocznego na komputerach.
st.set_page_config(
    page_title="SAN AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded" 
)

# --- 2. CSS - STYLIZACJA NA GEMINI ---
st.markdown("""
    <style>
    /* Ukrycie menu i stopki Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Wygląd głównego tła i czcionki */
    .main { background-color: #f0f4f9; }
    @media (prefers-color-scheme: dark) { .main { background-color: #131314; } }

    /* Gradientowy napis tytułowy - styl Gemini */
    .gemini-title {
        font-size: 3.5rem;
        font-weight: 500;
        background: linear-gradient(74deg, #4285f4 0, #9b72cb 20%, #d96570 40%, #f39264 60%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
    .gemini-subtitle {
        font-size: 1.5rem;
        color: #666;
        margin-bottom: 30px;
    }
    
    /* Zablokowanie szerokości panelu bocznego */
    [data-testid="stSidebar"] {
        min-width: 300px;
        max-width: 300px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. BAZA WIEDZY (WCZYTYWANIE) ---
@st.cache_data
def load_knowledge():
    # Pobiera dane z Twojego pliku knowledge.json
    if os.path.exists("knowledge.json"):
        with open("knowledge.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

knowledge_base = load_knowledge()

# --- 4. ZARZĄDZANIE STANEM (PAMIĘĆ) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 5. PANEL BOCZNY (LEWA STRONA) ---
with st.sidebar:
    st.markdown("### ✨ Historia Rozmów")
    
    # Przycisk do czyszczenia (jedyny moment, gdy strona się przeładowuje)
    if st.button("➕ Nowy czat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
        
    st.divider()
    
    # Wyświetlanie ostatnich pytań w panelu bocznym
    st.caption("Twoje pytania:")
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.write(f"💬 {msg['content'][:25]}...") # Wyświetla pierwsze 25 znaków pytania

# --- 6. GŁÓWNY INTERFEJS (PRAWA STRONA) ---
# Jeśli nie ma wiadomości - pokaż ekran startowy (ale bez kafelków podpowiedzi)
if len(st.session_state.messages) == 0:
    st.markdown('<div class="gemini-title">Witaj, studencie</div>', unsafe_allow_html=True)
    st.markdown('<div class="gemini-subtitle">Jestem asystentem uczelnianym. O co chcesz zapytać?</div>', unsafe_allow_html=True)
else:
    # Jeśli są wiadomości - wyświetl historię na środku ekranu
    for msg in st.session_state.messages:
        avatar = "✨" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

# --- 7. LOGIKA CZATU I WYSZUKIWANIA ---
if prompt := st.chat_input("Wpisz swoje zapytanie tutaj..."):
    
    # 1. Zapisz i wyświetl pytanie użytkownika
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # 2. Przygotuj odpowiedź bota
    with st.chat_message("assistant", avatar="✨"):
        response = "Przepraszam, nie odnalazłem tej informacji w bazie. Spróbuj użyć kluczowych słów, takich jak: ECTS, regulamin, logistyka, fizjoterapia czy medycyna."
        source_found = ""
        prompt_lower = prompt.lower()
        
        # Pancerne wyszukiwanie (Jeśli słowo z klucza w JSON jest w pytaniu, odpowiada)
        for key, value in knowledge_base.items():
            # Rozbija klucz np. "kierunek_lekarski" na "kierunek" i "lekarski"
            keywords = key.replace("_", " ").split()
            for word in keywords:
                # Szuka słów dłuższych niż 3 znaki, żeby uniknąć pomyłek
                if len(word) > 3 and word[:4] in prompt_lower:
                    response = value
                    source_found = key
                    break
            if source_found:
                break
        
        # 3. Wyświetlenie animacji pisania
        message_placeholder = st.empty()
        full_response = ""
        for char in response:
            full_response += char
            message_placeholder.markdown(full_response + "▌")
            time.sleep(0.005) # Szybkość animacji
            
        # Dodanie przypisu ze źródłem, jeśli coś znalazł
        if source_found:
            full_response += f"\n\n<span style='color:gray; font-size: 0.8em;'>Źródło: {source_found.upper()}</span>"
            
        message_placeholder.markdown(full_response, unsafe_allow_html=True)
        
    # 4. Zapisz odpowiedź do historii
    st.session_state.messages.append({"role": "assistant", "content": full_response})
