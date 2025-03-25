import streamlit as st

def display_welcome_message():
    """Display an engaging welcome message for PsicoChat."""
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <h1 style="color: #3498db;">🧠 Bienvenido a PsicoChat</h1>
        <p style="color: #2c3e50; font-size: 1.1em;">
            Tu compañero de IA para apoyo en salud mental
        </p>
    </div>
    """, unsafe_allow_html=True)

def display_help_resources(language):
    """Display help resources based on selected language."""
    resources = {
        "es": {
            "title": "Recursos de Ayuda",
            "hotlines": [
                "Línea de Prevención del Suicidio: 988",
                "Cruz Roja Española: 913 101 024"
            ]
        },
        "en": {
            "title": "Help Resources",
            "hotlines": [
                "National Suicide Prevention Lifeline: 988",
                "Crisis Text Line: Text HOME to 741741"
            ]
        },
        "fr": {
            "title": "Ressources d'Aide",
            "hotlines": [
                "Ligne de Prévention du Suicide: 01 45 39 40 00",
                "SOS Amitié: 09 72 39 40 50"
            ]
        }
    }
    
    current_resources = resources.get(language, resources["es"])
    
    st.sidebar.header(current_resources["title"])
    for hotline in current_resources["hotlines"]:
        st.sidebar.text(hotline)

def show_disclaimer():
    """Show a prominent disclaimer about AI assistance."""
    st.warning(
        "⚠️ Importante: PsicoChat proporciona apoyo informativo. "
        "No sustituye la atención profesional de salud mental. "
        "Busca ayuda profesional para problemas serios."
    )

def reset_chat():
    """Reset the chat session."""
    st.session_state.messages = []
    st.experimental_rerun()