import streamlit as st
from gtts import gTTS
import tempfile
import os
import requests

# --- Config ---
st.set_page_config(page_title="Kuku VoiceChoice: Indian Murder Mystery", page_icon="🔍")

# --- Functions ---
def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    fp = os.path.join(tempfile.gettempdir(), "audio.mp3")
    tts.save(fp)
    return fp

def generate_story_continuation(story_so_far, user_input):
    prompt = f"""
Continue this interactive Indian murder mystery. The storytelling style should be immersive, suspenseful, and cinematic. The story should move ahead by one paragraph and always end with a cliffhanger or question that invites the user to respond.

Story so far:
{story_so_far}

User chose:
{user_input}

Now continue:
"""

    API_KEY = "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"  # Replace with your HuggingFace API Key
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
        return "The silence deepens... something feels off. What will you do?"
    except Exception as e:
        return "An error occurred while generating the story. Please try again later."

# --- App State ---
if 'story' not in st.session_state:
    st.session_state.story = """It was a misty morning in the old colonial town of Darjeeling. The police had cordoned off the elegant yet eerie Bose Mansion, where socialite Reema Bose was found dead in her study. Her vintage gramophone was still playing a classical raga. You are Inspector Aryan Mehta, known for your unconventional ways. As you walk into the room, you spot a half-burnt letter on the floor and a broken glass of whisky beside it. What do you do first?"""
    st.session_state.history = []

# --- UI ---
st.title("🔍 Kuku VoiceChoice: Indian Murder Mystery")
st.markdown("Uncover clues. Interrogate suspects. Solve the mystery. 🕵️‍♂️")
st.info("🎤 Voice input coming soon! For now, please use text input.")

# Show current story
st.text_area("Case File:", value=st.session_state.story, height=280, disabled=True)

# Text input
user_input = st.text_input("Your next move?")

if st.button("Submit") and user_input:
    st.session_state.history.append(user_input)
    next_part = generate_story_continuation(st.session_state.story, user_input)
    st.session_state.story += f"\n\nYou: {user_input}\n\nAI: {next_part}"
    st.rerun()

# Optional listen to story
if st.button("🔊 Listen to Case"):
    audio_file = text_to_speech(st.session_state.story)
    st.audio(audio_file)

# Reset
if st.button("🔁 Start New Case"):
    st.session_state.story = """It was a misty morning in the old colonial town of Darjeeling. The police had cordoned off the elegant yet eerie Bose Mansion, where socialite Reema Bose was found dead in her study. Her vintage gramophone was still playing a classical raga. You are Inspector Aryan Mehta, known for your unconventional ways. As you walk into the room, you spot a half-burnt letter on the floor and a broken glass of whisky beside it. What do you do first?"""
    st.session_state.history = []
    st.rerun()
