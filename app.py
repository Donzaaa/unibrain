import streamlit as st
import google.generativeai as genai

st.title("🕵️‍♂️ Diagnostica UniBrain")

# 1. Input API Key
api_key = st.text_input("Inserisci API Key", type="password")

if api_key:
    genai.configure(api_key=api_key)
    
    st.divider()
    
    # 2. CONTROLLO VERSIONE (Il colpevole probabile)
    try:
        version = genai.__version__
        st.info(f"📦 Versione libreria installata: **{version}**")
        
        # Se la versione è inferiore a 0.7.0, Gemini Flash NON funzionerà
        if version < "0.7.0":
            st.error("❌ LA VERSIONE È TROPPO VECCHIA! Serve almeno la 0.7.0")
        else:
            st.success("✅ La versione è corretta.")
    except:
        st.warning("⚠️ Impossibile leggere la versione della libreria.")

    st.divider()

    # 3. LISTA MODELLI DISPONIBILI
    st.write("### 🤖 Modelli disponibili per la tua Chiave:")
    try:
        models_found = False
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                st.write(f"- `{m.name}`")
                models_found = True
        
        if not models_found:
            st.warning("Nessun modello trovato. La chiave potrebbe essere errata?")
            
    except Exception as e:
        st.error(f"Errore nel recupero modelli: {e}")
