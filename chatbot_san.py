import streamlit as st
import time

# --- KONFIGURACJA INTERFEJSU SAN ---
st.set_page_config(
    page_title="Chatbot SAN - Asystent Akademicki", 
    page_icon="🏫",
    layout="centered"
)

# Stylizacja nagłówka nawiązująca do tematu pracy
st.title("🏫 Chatbot SAN")
st.subheader("Inteligentny system wspomagania studentów (LLM + RAG)")
st.info("System udziela odpowiedzi na podstawie regulaminów, sylabusów oraz planów zajęć.")

# --- INICJALIZACJA SYSTEMU ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- FUNKCJA LOGIKI RAG (Silnik Twojej pracy) ---
def get_san_response(user_query):
    """
    Miejsce na integrację z bazą wektorową i LLM.
    Zgodnie z zakresem projektu: Ekstrakcja -> RAG -> Odpowiedź.
    """
    # Tu w przyszłości trafi kod: 
    # context = vector_db.similarity_search(user_query)
    # response = llm.generate(context, user_query)
    
    # Symulacja działania inteligentnego systemu
    time.sleep(1) # Symulacja czasu procesowania RAG
    return f"Na podstawie dostępnej dokumentacji akademickiej informuję, że w odpowiedzi na zapytanie: '{user_query}', system odnalazł odpowiednie sekcje w regulaminie i sylabusie..."

# --- WYŚWIETLANIE HISTORII ROZMOWY ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- OBSŁUGA CZATU ---
if prompt := st.chat_input("Zadaj pytanie o regulamin, sylabus lub plan zajęć..."):
    
    # Dodanie pytania użytkownika
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Procesowanie odpowiedzi przez Chatbot SAN
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # Pobranie danych z silnika RAG
        full_response = get_san_response(prompt)
        
        # Animacja generowania odpowiedzi (wygląd LLM)
        display_text = ""
        for char in full_response:
            display_text += char
            message_placeholder.markdown(display_text + "▌")
            time.sleep(0.01)
        
        message_placeholder.markdown(full_response)
    
    # Zapisanie odpowiedzi w historii
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# --- SEKTY PROJEKTOWE (Sidebar dla komisji/prowadzącego) ---
with st.sidebar:
    st.header("Parametry Projektu")
    st.write("**Temat:** Chatbot LLM + RAG")
    st.write("**Zakres:**")
    st.write("- Regulamin uczelni")
    st.write("- Sylabusy")
    st.write("- Plan zajęć")
    st.divider()
    if st.button("Wyczyść historię sesji"):
        st.session_state.messages = []
        st.rerun()