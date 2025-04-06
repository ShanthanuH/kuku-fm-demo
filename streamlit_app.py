import streamlit as st
from gtts import gTTS
import tempfile
import os
import requests

# --- Page Setup ---
st.set_page_config(page_title="Kuku VoiceChoice: Murder Mystery", page_icon="🕵️‍♂️")

# --- Functions ---
def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    fp = os.path.join(tempfile.gettempdir(), "audio.mp3")
    tts.save(fp)
    return fp

def generate_story_continuation(story_so_far, user_input):
    prompt = f"""
Continue this Indian murder mystery in Darjeeling. Write immersive and vivid prose, like a gripping detective thriller. Use a storytelling tone and end with a suspenseful question to prompt user input.

Case notes so far:
{story_so_far}

User chose:
{user_input}

Now continue:
"""

    API_KEY = "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"  # 🔐 Replace with st.secrets later
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
                return generated.replace(prompt.strip(), "").strip()
        return "Something's off. You feel a chill in the air... What will you do next?"
    except:
        return "An error occurred while generating the story. Please try again later."


# --- Session State Init ---
if 'story' not in st.session_state:
    st.session_state.story = """It was a misty morning in the old colonial town of Darjeeling. The police had cordoned off the elegant yet eerie Bose Mansion, where socialite Reema Bose was found dead in her study. Her vintage gramophone was still playing a classical raga. You are Inspector Aryan Mehta, known for your unconventional ways. As you walk into the room, you spot a half-burnt letter on the floor and a broken glass of whisky beside it. What do you do first?"""
    st.session_state.history = []
    st.session_state.story_waiting_for_input = True

# --- UI Layout ---
st.title("🕵️‍♂️ Kuku VoiceChoice: Indian Murder Mystery")
st.markdown("Step into the shoes of Inspector Aryan Mehta and solve the case.")
st.info("🎤 Voice input coming soon. Stay tuned!")

# --- Story Display ---
st.text_area("Case File:", value=st.session_state.story, height=300, disabled=True)

# --- Interaction Flow ---
if st.session_state.story_waiting_for_input:
    user_input = st.text_input("🗣️ What will you do next?")

    if st.button("Submit") and user_input:
        st.session_state.history.append(user_input)
        next_part = generate_story_continuation(st.session_state.story, user_input)
        st.session_state.story += f"\n\n🧑‍💼 You: {user_input}\n\n🤖 AI: {next_part}"
        st.session_state.story_waiting_for_input = False
        st.rerun()
else:
    st.success("✅ AI has responded. Ready for your next move?")
    if st.button("▶️ Continue Story"):
        st.session_state.story_waiting_for_input = True
        st.rerun()

# --- Audio Option ---
if st.button("🔊 Listen to Story"):
    audio_file = text_to_speech(st.session_state.story)
    st.audio(audio_file)

# --- Reset Story ---
if st.button("🔁 Start New Case"):
    st.session_state.story = """It was a misty morning in the old colonial town of Darjeeling. The police had cordoned off the elegant yet eerie Bose Mansion, where socialite Reema Bose was found dead in her study. Her vintage gramophone was still playing a classical raga. You are Inspector Aryan Mehta, known for your unconventional ways. As you walk into the room, you spot a half-burnt letter on the floor and a broken glass of whisky beside it. What do you do first?"""
    st.session_state.history = []
    st.session_state.story_waiting_for_input = True
    st.rerun()
