import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import tempfile
import os
import random
import requests

# --- Config ---
st.set_page_config(page_title="AI Story", page_icon="📖")

# --- Functions ---
def recognize_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening...")
        r.adjust_for_ambient_noise(source)
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
            text = r.recognize_google(audio)
            return text.lower()
        except:
            return None

def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    fp = os.path.join(tempfile.gettempdir(), "audio.mp3")
    tts.save(fp)
    return fp

def generate_story_continuation(story_so_far, user_input):
    prompt = f"""
Continue this story:

Story so far:
{story_so_far}

The user chose: {user_input}

Continue the story in 2 paragraphs and ask what happens next.
"""
    try:
        # Replace with your Hugging Face API key
        API_KEY = "YOUR_HUGGINGFACE_API_KEY"
        API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        headers = {"Authorization": f"Bearer {API_KEY}"}

        response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
        if response.status_code == 200:
            return response.json()[0]['generated_text'].replace(prompt, "").strip()
    except:
        pass
    
    # fallback if no API or error
    fallback = [
        "You venture deeper into the forest, hearing whispers in the wind. Suddenly, a path splits into two—one dark, one lit. Which will you take?",
        "You follow the trail, and it leads to an ancient stone altar. Something glows beneath the moss. What do you do?",
    ]
    return random.choice(fallback)

# --- App State ---
if 'story' not in st.session_state:
    st.session_state.story = """You find yourself at the edge of a mysterious forest. The trees sway gently, as if inviting you in. A path stretches out before you."""
    st.session_state.history = []

# --- UI ---
st.title("🎙️ Simple AI Story")
st.markdown("Speak or type what you'd like to do next!")

# Show current story
st.text_area("Story so far:", value=st.session_state.story, height=200, disabled=True)

# Listen button
if st.button("🎤 Speak"):
    choice = recognize_speech()
    if choice:
        st.success(f"You said: {choice}")
    else:
        st.error("Sorry, I couldn't understand. Try typing instead.")
        choice = None
else:
    choice = None

# Text input
text_choice = st.text_input("Or type your action:")
if st.button("Submit") or choice:
    user_input = text_choice if text_choice else choice
    if user_input:
        st.session_state.history.append(user_input)
        next_story = generate_story_continuation(st.session_state.story, user_input)
        st.session_state.story += f"\n\nYou: {user_input}\n\nAI: {next_story}"
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
