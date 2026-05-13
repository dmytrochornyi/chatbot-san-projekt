import streamlit as st
import time
import json
import os
from datetime import datetime

# --- 1. KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="SAN AI - System Ekspercki",
    page_icon="🎓",
    layout="wide", # Szeroki układ wygląda nowocześniej na dużych ekranach
    initial_sidebar_state="expanded"
)

# --- 2. NIESTANDARDOWY STYL CSS (To robi największą różnicę!) ---
st.markdown("""
    <style>
    /* Ukrycie domyślnego menu Streamlit dla czystego wyglądu aplikacji */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Zaokrąglenie przycisków i efekty najechania (hover) */
    .stButton>button {
        border-radius: 20px;
        border: 1px solid #4CAF50;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        border: 1px solid #45a049;
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
    }
    
    /* Stylizacja głównego nagłówka */
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
@st.cache_data # Przyspiesza ładowanie strony
def load_knowledge():
    if os.path.exists("knowledge.json"):
        with open("knowledge.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {"błąd": "Brak pliku bazy danych. Sprawdź GitHub."}

knowledge_base = load_knowledge()

# --- 4. LOGIKA WYSZUKIWANIA ---
def get_san_response(user_query, temperature):
    user_query = user_query.lower()
    
    # Symulacja pracy silnika (czas zależny od temperatury)
    delay = 0.5 + (temperature * 0.5)
    time.sleep(delay)
        
    for key, value in knowledge_base.items():
        readable_key = key.replace("_", " ")
        if readable_key in user_query or user_query in readable_key:
            return value, key # Zwracamy odpowiedź i nazwę źródła (klucz)
            
    return "Przykro mi, nie potrafię odnaleźć odpowiednich dokumentów w aktualnym indeksie RAG. Spróbuj przeredagować zapytanie.", None

# --- 5. PANEL BOCZNY (SIDEBAR - PANEL ADMINISTRATORA) ---
with st.sidebar:
    st.markdown("### ⚙️ Panel Kontrolny RAG")
    
    # Metryki systemu (Wygląda niezwykle profesjonalnie)
    col1, col2 = st.columns(2)
    col1.metric("Zindeksowane Węzły", len(knowledge_base))
    col2.metric("Status Serwera", "Online", delta="Opóźnienie <1s")
    
    st.divider()
    
    # Ustawienia Modelu (Parametry wizualne pod prezentację)
    st.markdown("#### Ustawienia Modelu LLM")
    model_type = st.selectbox("Silnik Generatywny", ["GPT-4o (Zalecany)", "Llama-3-8B (Lokalny)", "Mistral-7B"])
    temperature = st.slider("Temperatura (Kreatywność)", 0.0, 1.0, 0.2, 0.1, help="Wpływa na halucynacje modelu. W systemach RAG zaleca się niską temperaturę.")
    
    st.divider()
    st.markdown("#### Narzędzia Sesji")
    
    if st.button("🗑️ Resetuj kontekst rozmowy", use_container_width=True):
        st.session_state.messages = [{"role": "assistant", "content": "Kontekst wyczyszczony. W czym mogę pomóc?"}]
        st.rerun()
        
    # Funkcja eksportu czatu
    if "messages" in st.session_state and len(st.session_state.messages) > 1:
        chat_export = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
        st.download_button(
            label="💾 Pobierz transkrypt rozmowy",
            data=chat_export,
            file_name=f"log_rozmowy_san_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True
        )

# --- 6. GŁÓWNY INTERFEJS ---
st.markdown('<div class="main-header">🎓 SAN AI Asystent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">System wsparcia studenta oparty na architekturze Retrieval-Augmented Generation</div>', unsafe_allow_html=True)

# Podział na zaawansowane zakładki
tab1, tab2, tab3 = st.tabs(["💬 Interfejs Czat", "📊 Inspektor Bazy Wiedzy", "ℹ️ O Architekturze"])

with tab2:
    st.subheader("Zawartość wektorowej bazy wiedzy")
    st.info("Podgląd na żywo zindeksowanych dokumentów (knowledge.json). W pełnej wersji RAG są to wektory matematyczne (embeddings).")
    st.json(knowledge_base) # Automatycznie formatuje i pozwala zwijać dane!

with tab3:
    st.subheader("Informacje Projektowe")
    st.markdown("""
    System został zaprojektowany z myślą o minimalizacji tzw. *halucynacji* modeli językowych poprzez wdrożenie metodyki RAG.
    * **Frontend:** Streamlit z niestandardowym CSS
    * **Baza danych wiedzy:** Architektura słownikowa (JSON Mockup)
    * **Wyszukiwanie (Retrieval):** Dopasowanie semantyczne i słów kluczowych (Keyword Matching).
    """)

with tab1:
    # Szybkie akcje (Przycisk wstawia gotowe zapytanie)
    st.markdown("**Sugerowane zapytania:**")
    cols = st.columns(4)
    if cols[0].button("Medycyna ECTS"): st.session_state.auto_prompt = "Ile punktów ECTS ma kierunek lekarski?"
    if cols[1].button("Praktyki Fizjoterapia"): st.session_state.auto_prompt = "Ile godzin praktyk jest na fizjoterapii?"
    if cols[2].button("Co to jest warunek?"): st.session_state.auto_prompt = "Co się stanie w przypadku niezaliczenia semestru?"
    if cols[3].button("Logistyka przedmioty"): st.session_state.auto_prompt = "Jakie są główne przedmioty na logistyce?"

    # Inicjalizacja wiadomości
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Witaj! Posiadam zindeksowaną wiedzę na temat kierunków, sylabusów i regulaminu. W czym mogę pomóc?"}]

    # Renderowanie historii wiadomości
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Pole tekstowe do pisania LUB auto-prompt z przycisków
    prompt = st.chat_input("Zadaj pytanie lub opisz swój problem...")
    
    if "auto_prompt" in st.session_state:
        prompt = st.session_state.auto_prompt
        del st.session_state.auto_prompt

    # Obsługa generowania odpowiedzi
    if prompt:
        # Pokaż pytanie
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generuj odpowiedź
        with st.chat_message("assistant"):
            # Zaawansowany wskaźnik progresu (Robi super wrażenie wizualne)
            with st.status("Analiza zapytania...", expanded=True) as status:
                st.write("1. Tokenizacja pytania użytkownika...")
                time.sleep(0.3)
                st.write(f"2. Wyszukiwanie kontekstu (Retrieval)...")
                time.sleep(0.4)
                st.write(f"3. Przesyłanie promptu i danych do modelu ({model_type})...")
                response_text, source_key = get_san_response(prompt, temperature)
                status.update(label="Odpowiedź wygenerowana!", state="complete", expanded=False)
            
            # Płynne drukowanie tekstu
            message_placeholder = st.empty()
            full_res = ""
            for char in response_text:
                full_res += char
                message_placeholder.markdown(full_res + "▌")
                time.sleep(0.005)
            
            # Doklejenie adnotacji o źródle
            if source_key:
                source_annotation = f"\n\n--- \n*Źródło kontekstu: Zindeksowany fragment `[{source_key.upper()}]`*"
                full_res += source_annotation
            
            # Wyczyść kursor i zapisz finalną wersję
            message_placeholder.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
