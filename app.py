import os
import io
import tempfile
import streamlit as st
from modules.text_extraction import extract_text_from_pdf, extract_text_from_audio, extract_text_from_image, extract_text_from_video
from modules.translation import translate_text
from modules.chat_logic import generate_response
from modules.settings import client
from modules.ui_components import display_welcome_message, display_help_resources, show_disclaimer, reset_chat

# Configurar la aplicación
st.set_page_config(
    page_title="PsicoChat - Asistente de Psicología", 
    page_icon="🧠", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
    :root {
        --primary-color: #3498db;
        --secondary-color: #2ecc71;
        --background-color: #f4f6f7;
        --text-color: #2c3e50;
    }
    
    .stApp {
        background-color: var(--background-color);
        font-family: 'Inter', 'Roboto', sans-serif;
    }
    
    .stMarkdown h1 {
        color: var(--primary-color);
        text-align: center;
        font-weight: 700;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    # Mostrar mensaje de bienvenida
    display_welcome_message()

    # Sidebar con opciones
    with st.sidebar:
        st.header("Acerca de PsicoChat")
        st.write("PsicoChat es un asistente virtual diseñado para ofrecer apoyo e información sobre psicología y salud mental.")
        
        # Botón de reiniciar chat
        if st.button("🔄 Reiniciar Chat"):
            st.session_state.messages = []
            st.experimental_rerun()
        
        language = st.selectbox("Selecciona el idioma", ["Español (es)", "English (en)", "Français (fr)"])
        language_code = language.split("(")[1].strip(")")

        # Mostrar recursos de ayuda
        display_help_resources(language_code)

        # Uploaders de archivos
        uploaded_pdf = st.file_uploader("Sube un PDF", type=["pdf"])
        pdf_context = extract_text_from_pdf(uploaded_pdf) if uploaded_pdf else ''

        uploaded_audio = st.file_uploader("Sube un archivo de audio", type=["mp3", "wav"])
        audio_context = process_audio_upload(uploaded_audio, language_code) if uploaded_audio else ''
        
        uploaded_image = st.file_uploader("Sube una imagen para proporcionar contexto adicional", type=["png", "jpg", "jpeg"])
        image_context = extract_text_from_image(uploaded_image, lang="spa") if uploaded_image else ''

        uploaded_video = st.file_uploader("Sube un video para proporcionar contexto adicional", type=["mp4", "mov", "avi", "mkv"])
        video_context = process_video_upload(uploaded_video, language_code) if uploaded_video else ''

    # Chat principal
    chat_interface(language_code, pdf_context, audio_context, image_context, video_context)

def process_audio_upload(uploaded_audio, language_code):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_mp3:
        temp_mp3.write(uploaded_audio.read())
        temp_mp3_path = temp_mp3.name

    try:
        audio_context = extract_text_from_audio(temp_mp3_path, language=language_code)
        st.sidebar.subheader("Texto extraído del audio:")
        st.sidebar.write(audio_context)
    except Exception as e:
        st.sidebar.error(f"Error procesando audio: {e}")
        audio_context = ''
    finally:
        os.remove(temp_mp3_path)
    
    return audio_context

def process_video_upload(uploaded_video, language_code):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
        temp_video.write(uploaded_video.read())
        temp_video_path = temp_video.name

    try:
        video_context = extract_text_from_video(open(temp_video_path, 'rb'), audio_language=language_code)
        st.sidebar.subheader("Texto extraído del video:")
        st.sidebar.write(video_context)
    except Exception as e:
        st.sidebar.error(f"Error procesando video: {e}")
        video_context = ''
    finally:
        os.remove(temp_video_path)
    
    return video_context

def chat_interface(language_code, pdf_context, audio_context, image_context, video_context):
    # Inicializa el chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mostrar mensajes previos
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="👤" if message["role"] == "Usuario" else "🧠"):
            st.markdown(message["content"])
            
    # Entrada del usuario
    prompt = st.chat_input("Escribe tu pregunta aquí...")

    if prompt:
        st.session_state.messages.append({"role": "Usuario", "content": prompt})
        with st.chat_message("Usuario", avatar="👤"):
            st.markdown(prompt)

        # Preparar el historial completo
        history = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in st.session_state.messages])
        
        # Crear el prompt completo con contexto
        full_prompt = generate_response(
            prompt,
            history,
            pdf_context,
            audio_context,
            image_context,
            video_context,
            language_code
        )
        
        # Obtener respuesta del modelo
        with st.chat_message("PsicoChat", avatar="🧠"):
            message_placeholder = st.empty()
            full_response = ""
            
            with st.spinner("Elaborando respuesta..."):
                try:
                    response = client.text_generation(
                        full_prompt,
                        max_new_tokens=1000,
                        stream=True,
                        temperature=0.7,
                        repetition_penalty=1.2
                    )
                    for chunk in response:
                        full_response += chunk
                    full_response_translated = translate_text(full_response, target_lang=language_code)
                    message_placeholder.markdown(full_response_translated)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    full_response = "Lo siento, hubo un problema. Intenta de nuevo."
                    message_placeholder.markdown(full_response)
            
            # Mostrar advertencia en caso de crisis
            if any(word in prompt.lower() for word in ["crisis", "suicid", "autolesion", "suicide", "self-harm"]):
                show_disclaimer()
        
        st.session_state.messages.append({"role": "🤖 PsicoChat", "content": full_response})

if __name__ == "__main__":
    main()