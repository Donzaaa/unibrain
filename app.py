import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import time

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
    st.success("✅ Libreria aggiornata. Usiamo Gemini 1.5 Flash (Stabile).")

# --- FUNZIONI DI UTILITÀ ---
def get_pdf_text(pdf_file):
    text = ""
    pdf_reader = PdfReader(pdf_file)
    for page in pdf_reader.pages:
        # Aggiungiamo un controllo per evitare errori su pagine vuote
        page_text = page.extract_text()
        if page_text:
            text += page_text
    return text

def process_with_gemini(prompt, content):
    try:
        genai.configure(api_key=api_key)
        
        # --- MODIFICA: Usiamo 1.5 Flash che ora funziona ed è stabile per il Free Tier ---
        model = genai.GenerativeModel('gemini-1.5-flash') 
        
        response = model.generate_content([prompt, content])
        return response.text
    except Exception as e:
        # Se c'è un errore, restituiamo il messaggio per vederlo a video
        return f"ERRORE_API: {str(e)}"

# --- INTERFACCIA PRINCIPALE ---
tab1, tab2 = st.tabs(["📄 Analisi PDF & Slide", "🎙️ Sbobinatore Audio"])

# === TAB 1: PDF ===
with tab1:
    st.header("Da PDF ad Appunti")
    st.info("💡 Consigli: Se il PDF è un libro intero (>100 pag), l'AI potrebbe metterci un po'.")
    uploaded_pdf = st.file_uploader("Carica le tue slide o dispense (PDF)", type="pdf")
    
    if uploaded_pdf is not None and api_key:
        if st.button("Genera Materiale di Studio"):
            with st.spinner("1/3 - L'AI sta leggendo il PDF..."):
                # 1. Estrai testo
                raw_text = get_pdf_text(uploaded_pdf)
                # Calcolo approssimativo token (1 parola = ~1.3 token)
                st.caption(f"Testo estratto: circa {len(raw_text.split())} parole.")

            # 2. Definisci i prompt
            prompt_schema = "Sei un tutor universitario esperto. Analizza questo testo e crea uno SCHEMA concettuale strutturato per punti elenco, evidenziando le definizioni chiave e le formule se presenti. Usa formattazione Markdown."
            prompt_quiz = "Basandoti sul testo, crea 5 domande a risposta aperta (con soluzioni alla fine) per simulare l'esame."
            
            # 3. Esecuzione SEQUENZIALE (per evitare errore 429)
            
            # FASE A: Appunti
            with st.spinner("2/3 - Generazione Schemi in corso..."):
                summary = process_with_gemini(prompt_schema, raw_text)
                if "ERRORE_API" in summary:
                    st.error(summary)
                else:
                    st.subheader("📝 Schemi & Appunti")
                    st.markdown(summary)
            
            # Pausa tattica per far respirare l'API
            time.sleep(2) 
            
            # FASE B: Quiz
            with st.spinner("3/3 - Generazione Quiz in corso..."):
                quiz = process_with_gemini(prompt_quiz, raw_text)
                if "ERRORE_API" in quiz:
                    st.error(quiz)
                else:
                    st.divider()
                    st.subheader("❓ Quiz di Ripasso")
                    st.markdown(quiz)

# === TAB 2: AUDIO ===
with tab2:
    st.header("Sbobinatore Intelligente")
    st.markdown("Incolla qui sotto la trascrizione o appunti grezzi presi a lezione.")
    
    raw_notes = st.text_area("Incolla qui il testo della lezione:", height=200)
    
    if raw_notes and api_key:
        if st.button("Riorganizza Appunti"):
             with st.spinner("Sto riorganizzando..."):
                prompt = "Riscrivi questi appunti grezzi in modo ordinato, accademico e strutturato in capitoli. Correggi eventuali errori grammaticali."
                result = process_with_gemini(prompt, raw_notes)
                st.markdown(result)

if not api_key:
    st.warning("👈 Inserisci la tua API Key nella barra laterale per iniziare!")
