import streamlit as st
from gtts import gTTS
import tempfile
import os
import requests
import re
from tenacity import retry, stop_after_attempt, wait_exponential

# --- Page Setup ---
st.set_page_config(page_title="Kuku VoiceChoice: Indian Murder Mystery", page_icon="🕵️‍♂️")

# --- Disclaimer ---
st.markdown("""
**Disclaimer:** This is a demo for Kuku FM by Shanthanu Hemanth (Email: shaanhem@gmail.com, Registration Number: 21BCE2990 from VIT Vellore). It is an interactive story experience where the user can actively participate in the progression of the story.
""")

# --- Text-to-Speech ---
def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    fp = os.path.join(tempfile.gettempdir(), "audio.mp3")
    tts.save(fp)
    return fp

# --- Story Generation via Groq + LLaMA 3 70B ---
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def generate_story_continuation(story_so_far, user_input):
    prompt = f"""
Continue this Indian murder mystery set in Darjeeling. Write immersive and vivid prose like a gripping detective thriller. Continue the story in strictly 1 paragraph (not more) based on the user's decision. End with a question asking what the user wants to do next. DO NOT include any text like "User decides:" or similar - only provide the narrative continuation. Make sure that you don't end in between sentences; always end a paragraph with a question for the user. After the user answers, continue from there, generate about 50 words of continuation, and then give a question for the user again.

Case notes so far:
{story_so_far}

User chose:
{user_input}

Now continue:
"""

    GROQ_API_KEY = "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"
    API_URL = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {
                "role": "system",
                "content": "You are a storytelling AI helping with an Indian detective mystery. Be vivid, immersive, and always end with a question."
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.85,
        "max_tokens": 250
    }

    try:
        with st.spinner('Generating the next part of the story...'):
            response = requests.post(API_URL, headers=headers, json=payload)
        
        st.write("DEBUG: Response Status", response.status_code)
        st.write("DEBUG: Response Text", response.text)

        if response.status_code == 200:
            output = response.json()
            generated = output['choices'][0]['message']['content'].strip()

            generated = re.sub(r'User decides:.*', '', generated, flags=re.DOTALL)
            generated = re.sub(r'User chose:.*', '', generated, flags=re.DOTALL)
            generated = re.sub(r'What will you do\?.*', 'What will you do?', generated, flags=re.DOTALL)

            if not generated or len(generated.split()) < 10:
                return "The AI couldn't generate enough detail this time. What will you do next?"
            return generated

        return "The AI didn't return a valid continuation. What will you do next?"

    except Exception as e:
        st.error(f"An error occurred while generating the story: {e}")
        return "An error occurred while generating the story. Please try again later."

# --- Session State Init ---
if 'story' not in st.session_state:
    st.session_state.story = (
        "It was a misty morning in the old colonial town of Darjeeling. The police had cordoned off the elegant yet eerie Bose Mansion, "
        "where socialite Reema Bose was found dead in her study. Her vintage gramophone was still playing a classical raga. You are Inspector Aryan Mehta, "
        "known for your unconventional ways. As you walk into the room, you spot a half-burnt letter on the floor and a broken glass of whisky beside it. "
        "What do you do first?"
    )
    st.session_state.history = []
    st.session_state.story_waiting_for_input = True

# --- UI Layout ---
st.title("🕵️‍♂️ Kuku VoiceChoice: Indian Murder Mystery: Shanthanu Hemanth")
st.markdown("Step into the shoes of Inspector Aryan Mehta and unravel the mystery.")
st.info("🎤 Voice input coming soon! For now, please use text input.")

# Display current story
st.text_area("Case File:", value=st.session_state.story, height=300, disabled=True)

# --- Interaction Logic ---
if st.session_state.story_waiting_for_input:
    user_input = st.text_input("🗣️ What will you do next?")
    if st.button("Submit") and user_input:
        st.session_state.history.append(user_input)
        next_part = generate_story_continuation(st.session_state.story, user_input)
        st.session_state.story += f"\n\n🧑‍💼 You: {user_input}\n\n🕵️ Inspector's Log: {next_part}"
        st.session_state.story_waiting_for_input = False
        st.rerun()
else:
    st.success("✅ The story continues. Ready for your next move?")
    if st.button("▶️ Continue Story"):
        st.session_state.story_waiting_for_input = True
        st.rerun()

# --- Optional Audio ---
if st.button("🔊 Listen to Case"):
    audio_file = text_to_speech(st.session_state.story)
    st.audio(audio_file)

# --- Reset Case ---
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
