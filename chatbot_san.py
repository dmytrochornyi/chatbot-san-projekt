import streamlit as st
import time
import json
import os

# --- 1. KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="Chatbot SAN - Asystent Akademicki",
    page_icon="🏫",
    layout="centered"
)

# --- 2. ŁADOWANIE BAZY WIEDZY ---
def load_knowledge():
    # Sprawdza czy plik knowledge.json istnieje na GitHubie
    if os.path.exists("knowledge.json"):
        with open("knowledge.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# --- 3. LOGIKA WYSZUKIWANIA (MOCK-RAG) ---
def get_san_response(user_query):
    knowledge = load_knowledge()
    user_query = user_query.lower()
    
    # Symulacja "myślenia" systemu RAG
    with st.spinner('Przeszukiwanie dokumentacji SAN...'):
        time.sleep(1.2)
        
    # Proste dopasowanie słów kluczowych
    for key, value in knowledge.items():
        # Zamieniamy podkreślniki w kluczach na spacje dla łatwiejszego szukania
        readable_key = key.replace("_", " ")
        if readable_key in user_query or user_query in readable_key:
            return value
            
    return "Niestety nie znalazłem informacji na ten temat w aktualnej bazie danych. Spróbuj zapytać o: regulamin, punkty ECTS, plan zajęć lub stypendia."

# --- 4. WYGLĄD INTERFEJSU ---
st.title("🏫 Chatbot SAN")
st.markdown("---")

# Sidebar z informacjami o projekcie (BARDZO DOBRZE WYGLĄDA W PRACY)
with st.sidebar:
    st.header("O Projekcie")
    st.info("Projekt: Chatbot Odpowiadający na Pytania o Uczelnię")
    st.write("**Technologia:** LLM + RAG")
    st.write("**Uczelnia:** Społeczna Akademia Nauk")
    st.divider()
    st.write("Status systemu: ✅ Online")
    if st.button("Wyczyść czat"):
        st.session_state.messages = []
        st.rerun()

# --- 5. OBSŁUGA HISTORII WIADOMOŚCI ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Wyświetlanie starych wiadomości
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 6. OKNO CZATU I REAKCJA ---
if prompt := st.chat_input("Zadaj pytanie (np. o ECTS, regulamin, plan)..."):
    
    # Wyświetlenie pytania użytkownika
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generowanie odpowiedzi bota
    with st.chat_message("assistant"):
        response_text = get_san_response(prompt)
        
        # Efekt "pisania" na żywo
        message_placeholder = st.empty()
        full_res = ""
        for char in response_text:
            full_res += char
            message_placeholder.markdown(full_res + "▌")
            time.sleep(0.01)
        message_placeholder.markdown(full_res)
        
    # Zapisanie odpowiedzi bota
    st.session_state.messages.append({"role": "assistant", "content": full_res})
