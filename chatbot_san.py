import streamlit as st
import time
import json
import os

# --- KONFIGURACJA INTERFEJSU ---
st.set_page_config(page_title="Chatbot SAN", page_icon="🏫")
st.title("🏫 Chatbot SAN")

# --- FUNKCJA ŁADOWANIA WIEDZY ---
def load_knowledge():
    if os.path.exists("knowledge.json"):
        with open("knowledge.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# --- PROSTY SILNIK RAG (Wyszukiwanie słów kluczowych) ---
def get_san_response(user_query):
    knowledge = load_knowledge()
    user_query = user_query.lower()
    
    # Przeszukiwanie bazy pod kątem słów kluczowych
    for key in knowledge:
        if key.replace("_", " ") in user_query or user_query in key:
            return f"Znaleziono w dokumentacji: {knowledge[key]}"
    
    return "Niestety nie znalazłem dokładnych informacji na ten temat w bazie SAN. Spróbuj zapytać o: regulamin, ECTS, plan zajęć lub stypendia."

# --- LOGIKA CZATU (Streamlit) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Zadaj pytanie..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = get_san_response(prompt)
        # Efekt pisania
        placeholder = st.empty()
        full_res = ""
        for char in response:
            full_res += char
            placeholder.markdown(full_res + "▌")
            time.sleep(0.01)
        placeholder.markdown(full_res)
        st.session_state.messages.append({"role": "assistant", "content": full_res})
