import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

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
    st.info("💡 Suggerimento: Stiamo usando il modello Gemini 2.0 Flash.")

# --- FUNZIONI DI UTILITÀ ---
def get_pdf_text(pdf_file):
    text = ""
    pdf_reader = PdfReader(pdf_file)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def process_with_gemini(prompt, content):
    try:
        genai.configure(api_key=api_key)
        
        # --- MODIFICA FONDAMENTALE: Usiamo il modello 2.0 presente nella tua lista ---
        model = genai.GenerativeModel('gemini-2.0-flash') 
        
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
    st.info("Per ora supportiamo l'analisi testuale. L'upload audio diretto richiede una configurazione cloud più avanzata.")
    st.markdown("Carica qui sotto la trascrizione o appunti grezzi presi a lezione.")
    
    raw_notes = st.text_area("Incolla qui il testo della lezione:", height=200)
    
    if raw_notes and api_key:
        if st.button("Riorganizza Appunti"):
             with st.spinner("Sto riorganizzando..."):
                prompt = "Riscrivi questi appunti grezzi in modo ordinato, accademico e strutturato in capitoli. Correggi eventuali errori grammaticali."
                result = process_with_gemini(prompt, raw_notes)
                st.markdown(result)

if not api_key:
    st.warning("👈 Inserisci la tua API Key nella barra laterale per iniziare!")
