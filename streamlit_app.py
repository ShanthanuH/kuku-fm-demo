import streamlit as st
import tempfile
import os
import random
import requests
from gtts import gTTS

# --- App Config ---
st.set_page_config(page_title="Kuku VoiceChoice", page_icon="🎧", layout="centered")

# --- App Title and Branding ---
st.markdown("""
    <h1 style='text-align: center; color: #ff4b4b;'>🎧 Kuku VoiceChoice</h1>
    <p style='text-align: center; font-size: 16px;'>An Interactive Audio Tale Experience</p>
    <hr>
""", unsafe_allow_html=True)

# --- Session State ---
if 'story' not in st.session_state:
    st.session_state.story = """You find yourself at the edge of a mysterious forest. The trees sway gently, as if inviting you in. A path stretches out before you."""
    st.session_state.history = []

# --- Functions ---
def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    fp = os.path.join(tempfile.gettempdir(), "audio.mp3")
    tts.save(fp)
    return fp

def generate_story_continuation(story_so_far, user_input):
    prompt = f"""
Continue this story. The storytelling style should be immersive and vivid. Continue the story in 2 paragraphs and end with a question to the user to prompt next action.

Story so far:
{story_so_far}

User chose:
{user_input}

Now continue:
"""

    API_KEY = st.secrets["HUGGINGFACE_API_KEY"]  # Secure loading
    API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 300,
            "temperature": 0.8,
            "do_sample": True
        }
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            output = response.json()
            if isinstance(output, list) and "generated_text" in output[0]:
                return output[0]["generated_text"][len(prompt):].strip()
    except Exception as e:
        st.error(f"Error: {e}")
    
    fallback = [
        "You venture deeper into the forest, hearing whispers in the wind. Suddenly, a path splits into two—one dark, one lit. Which will you take?",
        "You follow the trail, and it leads to an ancient stone altar. Something glows beneath the moss. What do you do?",
    ]
    return random.choice(fallback)

# --- UI Layout ---
st.markdown("#### 📝 Story so far:")

formatted_story = st.session_state.story.replace('\n', '<br>')
st.markdown(f"""
<div style="background-color:#f9f9f9; padding:15px; border-radius:10px; height:250px; overflow-y:auto;">
{formatted_story}
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# --- Disclaimer for Speak Feature ---
st.warning("🎤 Voice input feature coming soon! For now, type your choices below to shape your journey.")

# --- Text Input ---
user_input = st.text_input("What do you do next?")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("✨ Continue Story"):
        if user_input:
            st.session_state.history.append(user_input)
            next_part = generate_story_continuation(st.session_state.story, user_input)
            st.session_state.story += f"\n\nYou: {user_input}\n\nAI: {next_part}"
            st.rerun()

with col2:
    if st.button("🔊 Listen"):
        audio_file = text_to_speech(st.session_state.story)
        st.audio(audio_file)

with col3:
    if st.button("🔁 Start Over"):
        st.session_state.story = """You find yourself at the edge of a mysterious forest. The trees sway gently, as if inviting you in. A path stretches out before you."""
        st.session_state.history = []
        st.rerun()

# --- Optional: View Past Choices ---
with st.expander("📜 View Past Choices"):
    if st.session_state.history:
        for i, h in enumerate(st.session_state.history, 1):
            st.markdown(f"**Choice {i}:** {h}")
    else:
        st.info("No choices yet.")
