import streamlit as st
import time
import json
import os

# --- 1. KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="SAN AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded" # Panel boczny domyślnie otwarty
)

# --- 2. CSS - WYGLĄD GEMINI I ZABLOKOWANIE PANELU ---
st.markdown("""
    <style>
    /* Ukrycie przycisku zamykania panelu bocznego (blokada) */
    [data-testid="sidebar-close-button"] { display: none; }
    button[kind="header"] { display: none; }
    
    /* Ukrycie menu i stopki */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Styl tła */
    .main { background-color: #f0f4f9; }
    @media (prefers-color-scheme: dark) { .main { background-color: #131314; } }

    /* Gradientowy napis Gemini */
    .gemini-title {
        font-size: 3.5rem;
        font-weight: 500;
        background: linear-gradient(74deg, #4285f4 0, #9b72cb 20%, #d96570 40%, #f39264 60%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .gemini-subtitle {
        font-size: 1.6rem;
        color: #757575;
        margin-top: -10px;
        margin-bottom: 40px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. WCZYTYWANIE BAZY WIEDZY ---
@st.cache_data
def load_data():
    if os.path.exists("knowledge.json"):
        with open("knowledge.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

knowledge_base = load_data()

# --- 4. INICJALIZACJA PAMIĘCI (SESSION STATE) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 5. PANEL BOCZNY (HISTORIA - LEWA STRONA) ---
with st.sidebar:
    st.markdown("### ✨ SAN AI")
    st.caption("Asystent Akademicki")
    
    if st.button("➕ Nowa rozmowa", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    st.write("**Ostatnie pytania:**")
    
    # Wyświetlanie historii pytań użytkownika w panelu bocznym
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            # Wyświetla krótką wersję pytania
            st.markdown(f"💬 `{msg['content'][:25]}...`")

# --- 6. GŁÓWNY INTERFEJS (CZAT) ---

# A. Jeśli czat jest pusty -> Pokaż ekran powitalny
if not st.session_state.messages:
    st.write("")
    st.write("")
    st.markdown('<div class="gemini-title">Witaj, studencie</div>', unsafe_allow_html=True)
    st.markdown('<div class="gemini-subtitle">W czym mogę Ci dzisiaj pomóc?</div>', unsafe_allow_html=True)

# B. Wyświetlanie wiadomości (zawsze na początku, aby historia była widoczna)
for message in st.session_state.messages:
    avatar = "✨" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# C. Obsługa nowego pytania (Input na dole)
if prompt := st.chat_input("Wpisz pytanie do bazy SAN..."):
    
    # 1. Wyświetlamy pytanie użytkownika natychmiast
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    
    # 2. Zapisujemy do pamięci
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 3. Szukamy odpowiedzi w bazie
    with st.chat_message("assistant", avatar="✨"):
        response = "Przepraszam, nie znalazłem informacji na ten temat. Spróbuj zapytać o ECTS, regulamin, logistykę lub fizjoterapię."
        found_source = None
        
        # Proste wyszukiwanie słów kluczowych
        p_lower = prompt.lower()
        for key, value in knowledge_base.items():
            clean_key = key.replace("_", " ")
            if clean_key in p_lower or p_lower in clean_key:
                response = value
                found_source = key
                break
        
        # Animacja pisania
        placeholder = st.empty()
        full_res = ""
        for char in response:
            full_res += char
            placeholder.markdown(full_res + "▌")
            time.sleep(0.005)
        
        if found_source:
            full_res += f"\n\n*Źródło: {found_source.upper()}*"
            
        placeholder.markdown(full_res)
        
        # 4. Zapisujemy odpowiedź bota do pamięci
        st.session_state.messages.append({"role": "assistant", "content": full_res})
    
    # Wymuszamy odświeżenie panelu bocznego, by dodać tam nowe pytanie
    st.rerun()
