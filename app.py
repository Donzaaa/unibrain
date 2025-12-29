import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import os

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="UniBrain - Sbobinatore & Tutor AI", layout="wide")

st.title("🎓 UniBrain: Il tuo Assistente di Studio")
st.markdown("Carica lezioni audio o slide PDF e lascia che l'AI crei appunti e schemi per te.")

# --- SIDEBAR: CHIAVE API ---
with st.sidebar:
    st.header("⚙️ Configurazione")
    api_key = st.text_input("Inserisci la tua Google Gemini API Key", type="password")
    st.markdown("[Ottieni la chiave gratis qui](https://aistudio.google.com/app/apikey)")
    
    st.divider()
    st.info("💡 Suggerimento: Usa Gemini 1.5 Flash per velocità o Pro per precisione.")

# --- FUNZIONI DI UTILITÀ ---
def get_pdf_text(pdf_file):
    text = ""
    pdf_reader = PdfReader(pdf_file)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def process_with_gemini(prompt, content, mime_type="text/plain"):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Se è testo semplice (dal PDF)
        if mime_type == "text/plain":
            response = model.generate_content([prompt, content])
        # Se è un file audio (caricato temporaneamente)
        else:
             # Nota: Per l'audio via API serve caricare il file su File API di Google
             # Per semplicità in questo script usiamo il testo, ma Gemini supporta audio nativo.
             # Qui simuliamo la trascrizione passando l'audio al modello (versione avanzata).
             # Per ora, manteniamo la logica testo per stabilità del codice base.
             response = model.generate_content([prompt, content])
             
        return response.text
    except Exception as e:
        return f"❌ Errore: {e}. Controlla la tua API Key."

# --- INTERFACCIA PRINCIPALE ---
tab1, tab2 = st.tabs(["📄 Analisi PDF & Slide", "🎙️ Sbobinatore Audio"])

# === TAB 1: PDF ===
with tab1:
    st.header("Da PDF ad Appunti")
    uploaded_pdf = st.file_uploader("Carica le tue slide o dispense (PDF)", type="pdf")
    
    if uploaded_pdf is not None and api_key:
        if st.button("Genera Materiale di Studio"):
            with st.spinner("L'AI sta leggendo il PDF..."):
                # 1. Estrai testo
                raw_text = get_pdf_text(uploaded_pdf)
                
                # 2. Definisci i prompt
                prompt_schema = "Sei un tutor universitario esperto. Analizza questo testo e crea uno SCHEMA concettuale strutturato per punti elenco, evidenziando le definizioni chiave e le formule se presenti."
                prompt_quiz = "Basandoti sul testo, crea 5 domande a risposta aperta per simulare l'esame."
                
                # 3. Chiama AI
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📝 Schemi & Appunti")
                    summary = process_with_gemini(prompt_schema, raw_text)
                    st.markdown(summary)
                
                with col2:
                    st.subheader("❓ Quiz di Ripasso")
                    quiz = process_with_gemini(prompt_quiz, raw_text)
                    st.markdown(quiz)

# === TAB 2: AUDIO ===
with tab2:
    st.header("Sbobinatore Intelligente")
    st.warning("⚠️ Nota: Per file audio grandi (>20MB) serve l'upload diretto su Google AI Studio. Qui mostriamo la logica.")
    uploaded_audio = st.file_uploader("Carica la registrazione della lezione (MP3/WAV)", type=["mp3", "wav"])
    
    if uploaded_audio is not None and api_key:
        st.audio(uploaded_audio)
        if st.button("Sbobina e Riassumi"):
            # PER ORA: Simuliamo la logica perché l'upload audio diretto via codice
            # richiede un passaggio in più (File API). 
            # Per un MVP gratis, consiglio di dire all'utente di usare file piccoli 
            # o implementare Whisper locale (ma è pesante per il cloud gratis).
            
            st.info("💡 Per l'audio, in questa versione 'Lite', l'AI proverà a processare il file. Se è troppo lungo, potrebbe dare errore.")
            
            # Qui inviamo il file audio grezzo a Gemini (Funziona con Gemini 1.5!)
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Salviamo temporaneamente il file
                with open("temp_audio.mp3", "wb") as f:
                    f.write(uploaded_audio.getbuffer())
                
                # Carichiamo su Gemini
                myfile = genai.upload_file("temp_audio.mp3")
                
                with st.spinner("Sto ascoltando e sbobinando... (può volerci un po')"):
                    result = model.generate_content(["Trascrivi questa lezione universitaria e poi fanne un riassunto dettagliato diviso per argomenti.", myfile])
                    st.markdown(result.text)
                    
            except Exception as e:
                st.error(f"Errore: {e}")

if not api_key:
    st.warning("👈 Inserisci la tua API Key nella barra laterale per iniziare!")
