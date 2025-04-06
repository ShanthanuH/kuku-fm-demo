import streamlit as st
from gtts import gTTS
import tempfile
import os
import requests
import re

# --- Page Setup ---
st.set_page_config(page_title="Kuku VoiceChoice: Indian Murder Mystery", page_icon="🕵️‍♂️")

# --- Functions ---
def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    fp = os.path.join(tempfile.gettempdir(), "audio.mp3")
    tts.save(fp)
    return fp

def generate_story_continuation(story_so_far, user_input):
    # Extract only the most recent part of the story to avoid token limits
    story_parts = story_so_far.split("\n\n")
    recent_story = "\n\n".join(story_parts[-4:]) if len(story_parts) > 4 else story_so_far
    
    prompt = f"""
Continue this Indian murder mystery set in Darjeeling. Write a vivid, immersive continuation based on the user's choice.

Guidelines:
1. Write 2-3 paragraphs of rich, atmospheric prose
2. Include sensory details and tension
3. End with an open question about what to do next
4. Do NOT offer multiple choice options
5. Do NOT include text like "User decides:" or numbered options
6. Focus on developing the mystery with clues and atmosphere

Recent story context:
{recent_story}

User chose:
{user_input}

Now continue the story:
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
            "max_new_tokens": 350,  # Increased token limit
            "temperature": 0.75,    # Slightly reduced for more coherent output
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
                result = generated.replace(prompt.strip(), "").strip()
                
                # Clean up any problematic patterns
                result = re.sub(r'User decides:.*', '', result, flags=re.DOTALL)
                result = re.sub(r'User chose:.*', '', result, flags=re.DOTALL)
                result = re.sub(r'Options:.*', '', result, flags=re.DOTALL)
                result = re.sub(r'\d+\.\s.*', '', result, flags=re.DOTALL)  # Remove numbered options
                
                # Ensure the response is substantial
                if len(result.split()) < 20:
                    return "Your investigation leads to a surprising revelation. The air feels thick with tension as you process this new information. What will you do next, Inspector?"
                
                return result
            
        # Handle API issues with a fallback response
        return "As you delve deeper into the mystery, new connections begin to emerge. The pieces of the puzzle are starting to fit together, but something still feels off. What's your next move, Inspector?"
    
    except Exception as e:
        return f"The case takes an unexpected turn. Your instincts tell you there's more to this than meets the eye. What will you do next, Inspector?"

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

# --- Debug Information (optional) ---
# Uncomment this to see debugging info
# if 'history' in st.session_state:
#     st.write(f"Story history entries: {len(st.session_state.history)}")

# --- Interaction Flow ---
if st.session_state.story_waiting_for_input:
    # Show text input box for the next decision.
    user_input = st.text_input("🗣️ What will you do next?")
    if st.button("Submit") and user_input:
        st.session_state.history.append(user_input)
        next_part = generate_story_continuation(st.session_state.story, user_input)
        st.session_state.story += f"\n\n🧑‍💼 You: {user_input}\n\n🕵️ Inspector's Log: {next_part}"
        st.session_state.story_waiting_for_input = False  # Disable input until user chooses to continue
        st.rerun()
else:
    # When waiting for the user to review AI output, show a continue button.
    st.success("✅ The story continues. Ready for your next move?")
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
