import streamlit as st
from gtts import gTTS
import tempfile
import os
import requests

# --- Config ---
st.set_page_config(page_title="Kuku VoiceChoice: Interactive Story Experience", page_icon="📖")

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

    API_KEY = "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"  # Replace this
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
                generated = output[0]["generated_text"]
                return generated.replace(prompt.strip(), "").strip()
        return "The forest whispers back, but nothing new unfolds. What do you want to do next?"
    except Exception as e:
        return "An error occurred while generating the story. Please try again later."

# --- App State ---
if 'story' not in st.session_state:
    st.session_state.story = """You find yourself at the edge of a mysterious forest. The trees sway gently, as if inviting you in. A path stretches out before you."""
    st.session_state.history = []

# --- UI ---
st.title("📖 Interactive AI Story")
st.markdown("Type what you'd like to do next and continue the story!")
st.info("🎤 Voice input coming soon! For now, please use text input.")

# Show current story
st.text_area("Story so far:", value=st.session_state.story, height=250, disabled=True)

# Text input
user_input = st.text_input("What will you do next?")

if st.button("Submit") and user_input:
    st.session_state.history.append(user_input)
    next_part = generate_story_continuation(st.session_state.story, user_input)
    st.session_state.story += f"\n\nYou: {user_input}\n\nAI: {next_part}"
    st.rerun()

# Optional listen to story
if st.button("🔊 Listen to Story"):
    audio_file = text_to_speech(st.session_state.story)
    st.audio(audio_file)

# Reset
if st.button("🔁 Start Over"):
    st.session_state.story = """You find yourself at the edge of a mysterious forest. The trees sway gently, as if inviting you in. A path stretches out before you."""
    st.session_state.history = []
    st.rerun()
