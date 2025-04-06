import streamlit as st
from gtts import gTTS
import tempfile
import os
import requests

# --- Page Setup ---
st.set_page_config(page_title="Kuku VoiceChoice: Indian Murder Mystery", page_icon="🕵️‍♂️")

# --- Functions ---
def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    fp = os.path.join(tempfile.gettempdir(), "audio.mp3")
    tts.save(fp)
    return fp

def generate_story_continuation(story_so_far, user_input):
    prompt = f"""
Continue this Indian murder mystery set in Darjeeling. Write immersive and vivid prose like a gripping detective thriller. Continue the story in 1 paragraph and end with a suspenseful question to prompt user input.

Case notes so far:
{story_so_far}

User chose:
{user_input}

Now continue:
"""

    # Replace with secure method: API_KEY = st.secrets["HUGGINGFACE_API_KEY"]
    API_KEY = "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"
    API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 300,
            "temperature": 0.85,
            "do_sample": True
        }
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            output = response.json()
            if isinstance(output, list) and "generated_text" in output[0]:
                generated = output[0]["generated_text"]
                # Remove the prompt text from the generated text:
                return generated.replace(prompt.strip(), "").strip()
        return "Something's off. A chill runs down your spine... What will you do next?"
    except Exception as e:
        return "An error occurred while generating the story. Please try again later."

# --- Session State Initialization ---
if 'story' not in st.session_state:
    st.session_state.story = (
        "It was a misty morning in the old colonial town of Darjeeling. The police had cordoned off the elegant yet eerie Bose Mansion, "
        "where socialite Reema Bose was found dead in her study. Her vintage gramophone was still playing a classical raga. You are Inspector Aryan Mehta, "
        "known for your unconventional ways. As you walk into the room, you spot a half-burnt letter on the floor and a broken glass of whisky beside it. "
        "What do you do first?"
    )
    st.session_state.history = []
    st.session_state.story_waiting_for_input = True  # When True, show input box

# --- UI Layout ---
st.title("🕵️‍♂️ Kuku VoiceChoice: Indian Murder Mystery")
st.markdown("Step into the shoes of Inspector Aryan Mehta and unravel the mystery.")
st.info("🎤 Voice input coming soon! For now, please use text input.")

# Display the current story with preserved line breaks.
st.text_area("Case File:", value=st.session_state.story, height=300, disabled=True)

# --- Interaction Flow ---
if st.session_state.story_waiting_for_input:
    # Show text input box for the next decision.
    user_input = st.text_input("🗣️ What will you do next?")
    if st.button("Submit") and user_input:
        st.session_state.history.append(user_input)
        next_part = generate_story_continuation(st.session_state.story, user_input)
        st.session_state.story += f"\n\n🧑‍💼 You: {user_input}\n\n🤖 AI: {next_part}"
        st.session_state.story_waiting_for_input = False  # Disable input until user chooses to continue
        st.rerun()
else:
    # When waiting for the user to review AI output, show a continue button.
    st.success("✅ AI has responded. Ready for your next move?")
    if st.button("▶️ Continue Story"):
        st.session_state.story_waiting_for_input = True
        st.rerun()

# --- Optional Audio Playback ---
if st.button("🔊 Listen to Case"):
    audio_file = text_to_speech(st.session_state.story)
    st.audio(audio_file)

# --- Reset / New Case ---
if st.button("🔁 Start New Case"):
    st.session_state.story = (
        "It was a misty morning in the old colonial town of Darjeeling. The police had cordoned off the elegant yet eerie Bose Mansion, "
        "where socialite Reema Bose was found dead in her study. Her vintage gramophone was still playing a classical raga. You are Inspector Aryan Mehta, "
        "known for your unconventional ways. As you walk into the room, you spot a half-burnt letter on the floor and a broken glass of whisky beside it. "
        "What do you do first?"
    )
    st.session_state.history = []
    st.session_state.story_waiting_for_input = True
    st.rerun()
