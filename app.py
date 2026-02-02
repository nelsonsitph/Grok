import streamlit as st
from openai import OpenAI
from streamlit_mic_recorder import speech_to_text
from gtts import gTTS
import io

# --- 1. Page Setup ---
st.set_page_config(page_title="Grok-only Voice Assistant", page_icon="🎙️")
st.title("Nelson Trial: Voice Only")

# --- 2. Grok Connection ---
# You only need the GROK_API_KEY in your Streamlit Secrets now
XAI_API_KEY = st.secrets["GROK_API_KEY"]
client = OpenAI(api_key=XAI_API_KEY, base_url="https://api.x.ai/v1")

st.write("Click the button and start talking. I will use your xAI credits for the reply.")

# --- 3. The Microphone Component ---
# This converts your voice to text using the browser's built-in engine (Free)
text_input = speech_to_text(
    language='en', 
    start_prompt="Click to Speak 🎙️", 
    stop_prompt="Stop Recording ⏹️", 
    just_once=True, 
    key='STT'
)

if text_input:
    st.info(f"You said: {text_input}")

    # --- 4. Send to Grok-3-Mini ---
    with st.spinner("Grok is thinking..."):
        try:
            response = client.chat.completions.create(
                model="grok-3-mini",
                messages=[
                    {"role": "system", "content": "Answer in 1-2 short sentences for a primary student."},
                    {"role": "user", "content": text_input}
                ],
                extra_body={"reasoning_effort": "low"}
            )
            grok_answer = response.choices[0].message.content
            st.success(f"Grok: {grok_answer}")

            # --- 5. Free Text-to-Speech ---
            tts = gTTS(text=grok_answer, lang='en')
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            st.audio(audio_fp, format="audio/mp3", autoplay=True)
            
        except Exception as e:
            st.error(f"Error: {e}")