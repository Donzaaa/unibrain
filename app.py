import streamlit as st
import google.generativeai as genai
import time
import os

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="UniBrain Vision", layout="wide")
st.title("🎓 UniBrain Vision: Legge anche le Scansioni")
st.markdown("Questo script invia il PDF direttamente a Google. Funziona anche con libri scansionati/immagini.")

# --- SIDEBAR ---
with st.sidebar:
    api_key = st.text_input("Inserisci API Key", type="password")
    # Usiamo il 2.0 che sappiamo essere attivo sul tuo account
    model_name = "gemini-2.0-flash" 
    st.info(f"🚀 Motore attivo: {model_name}")

# --- FUNZIONE UPLOAD FILE A GOOGLE ---
def upload_to_gemini(path, mime_type="application/pdf"):
    file = genai.upload_file(path, mime_type=mime_type)
    return file

def wait_for_files_active(files):
    """Aspetta che il file sia processato lato Google"""
    st.write("⏳ Elaborazione file lato server Google...")
    bar = st.progress(0)
    for name in (file.name for file in files):
        file = genai.get_file(name)
        while file.state.name == "PROCESSING":
            time.sleep(2) # Aspetta 2 secondi
            file = genai.get_file(name)
            bar.progress(50)
    bar.progress(100)
    return

# --- MAIN INTERFACE ---
uploaded_file = st.file_uploader("Carica il tuo PDF (Anche scansionato)", type=['pdf'])

if uploaded_file and api_key:
    if st.button("Analizza Libro"):
        
        genai.configure(api_key=api_key)
        
        # 1. SALVATAGGIO TEMPORANEO
        # Dobbiamo salvare il file su disco per poterlo inviare alle API di Google
        temp_filename = "temp_book.pdf"
        with open(temp_filename, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        try:
            # 2. UPLOAD A GOOGLE
            with st.spinner("Caricamento del file nel cervello dell'AI..."):
                file_ref = upload_to_gemini(temp_filename, mime_type="application/pdf")
            
            # 3. ATTESA ELABORAZIONE (OCR)
            wait_for_files_active([file_ref])
            
            # 4. GENERAZIONE CONTENUTO
            with st.spinner("L'AI sta leggendo e riassumendo..."):
                model = genai.GenerativeModel(model_name)
                
                # Prompt ottimizzato per evitare blocchi
                prompt = """
                Agisci come un professore universitario. Hai accesso a questo documento PDF.
                Analizzalo e produci un riassunto dettagliato dei concetti principali trattati nel documento.
                Usa il grassetto per i termini tecnici e struttura la risposta con punti elenco.
                """
                
                # Chiamata che include il riferimento al file
                response = model.generate_content([file_ref, prompt])
                
                st.subheader("📝 Risultato Analisi")
                st.markdown(response.text)
                
                # Pulizia opzionale: cancelliamo il file dai server Google per privacy
                # genai.delete_file(file_ref.name) 
                
        except Exception as e:
            st.error(f"Errore durante l'elaborazione: {str(e)}")
            if "429" in str(e):
                st.warning("⚠️ Hai superato i limiti di velocità (Quota). Aspetta un minuto e riprova.")
        
        finally:
            # Pulizia file locale
            if os.path.exists(temp_filename):
                os.remove(temp_filename)

if not api_key:
    st.warning("👈 Inserisci la chiave API per iniziare.")
