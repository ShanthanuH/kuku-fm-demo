import streamlit as st
from gtts import gTTS
import tempfile
import os
import requests
import time

# --- Config ---
st.set_page_config(
    page_title="KukuFM VoiceChoice Tales", 
    page_icon="🎙️",
    layout="wide"
)

# --- Custom CSS ---
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #FF5722;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #FF8A65;
    }
    .story-text {
        font-size: 1.2rem;
        line-height: 1.6;
        background-color: #FFF3E0;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #FF5722;
    }
    .stButton>button {
        background-color: #FF5722;
        color: white;
        border: none;
        border-radius: 20px;
        padding: 10px 20px;
    }
    .stButton>button:hover {
        background-color: #E64A19;
    }
    .stTextInput>div>div>input {
        border-radius: 20px;
        border: 2px solid #FF8A65;
        padding: 10px 15px;
    }
    .user-choice {
        background-color: #E8F5E9;
        padding: 10px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 3px solid #4CAF50;
    }
    .ai-response {
        background-color: #FFF3E0;
        padding: 10px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 3px solid #FF5722;
    }
</style>
""", unsafe_allow_html=True)

# --- Functions ---
def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    fp = os.path.join(tempfile.gettempdir(), "audio.mp3")
    tts.save(fp)
    return fp

def generate_story_continuation(story_so_far, user_input):
    prompt = f"""
Continue this crime investigation thriller story. The storytelling style should be immersive and vivid. Continue the story in 2 paragraphs and end with a question to the user to prompt next action.

Story so far:
{story_so_far}

User chose:
{user_input}

Now continue:
"""

    API_KEY = st.secrets["HUGGINGFACE_API_KEY"]
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
        return "The investigation continues, but no new leads appear. What's your next move, Detective?"
    except Exception as e:
        return "An error occurred while generating the story. Please try again later."

# --- App State ---
if 'story' not in st.session_state:
    st.session_state.story = """You're Detective Alex Stone, called to investigate a murder at the luxurious Blackwood Manor. 
The victim, billionaire Charles Blackwood, was found dead in his study. The initial examination suggests poison, but there are no obvious signs of forced entry.

As you arrive, the mansion's occupants - Charles's wife Eleanor, his daughter Victoria, his business partner James, and the butler Thompson - all eye you suspiciously."""
    st.session_state.history = []
    st.session_state.story_stage = 0

# --- UI ---
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<p class="main-header">KukuFM VoiceChoice Tales</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Interactive Voice-Driven Crime Investigation</p>', unsafe_allow_html=True)
    
    # Show current story with formatting
    st.markdown('<p class="sub-header">The Story</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="story-text">{st.session_state.story}</div>', unsafe_allow_html=True)
    
    # Text input
    st.markdown('<p class="sub-header">What will Detective Stone do next?</p>', unsafe_allow_html=True)
    user_input = st.text_input("", placeholder="Type your next action here...")
    
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("🎤 Speak Your Choice"):
            with st.spinner("Listening..."):
                # Simulate voice recognition for demo
                time.sleep(2)
                choices = ["Examine the body more closely", "Question the business partner", 
                          "Search for hidden evidence", "Check the security cameras"]
                user_input = choices[st.session_state.story_stage % len(choices)]
                st.success(f"You said: {user_input}")
                
                st.session_state.history.append(user_input)
                with st.spinner("Detective Stone is investigating..."):
                    next_part = generate_story_continuation(st.session_state.story, user_input)
                    st.session_state.story += f"\n\n**You decided to:** {user_input}\n\n{next_part}"
                    st.session_state.story_stage += 1
                    st.experimental_rerun()
    
    with col_btn2:
        if st.button("🔍 Submit") and user_input:
            st.session_state.history.append(user_input)
            with st.spinner("Detective Stone is investigating..."):
                next_part = generate_story_continuation(st.session_state.story, user_input)
                st.session_state.story += f"\n\n**You decided to:** {user_input}\n\n{next_part}"
                st.session_state.story_stage += 1
                st.experimental_rerun()
    
    # Optional listen to story
    if st.button("🔊 Listen to Story"):
        with st.spinner("Generating audio..."):
            audio_file = text_to_speech(st.session_state.story)
            st.audio(audio_file)

with col2:
    # Sidebar content
    st.markdown('<p class="sub-header">Investigation Progress</p>', unsafe_allow_html=True)
    progress = min(100, st.session_state.story_stage * 20)  # 20% per stage, max 100%
    st.progress(progress)
    
    # Display previous choices
    if st.session_state.history:
        st.markdown('<p class="sub-header">Your Investigation Path</p>', unsafe_allow_html=True)
        for i, action in enumerate(st.session_state.history):
            st.markdown(f"**Step {i+1}:** {action}")
    
    # Explain the AI technology
    with st.expander("How the AI Works"):
        st.write("""
        This demo showcases the KukuFM VoiceChoice Tales experience:
        
        1. **Voice Recognition**: Converts your spoken choices to text
        2. **Narrative Generation**: AI analyzes your input to determine story direction
        3. **Text-to-Speech**: Converts story text to spoken narration
        4. **Dynamic Branching**: Your choices influence the story outcome
        
        In the full implementation for Kuku FM, this would be expanded to:
        - Support multiple Indian languages
        - Use voice cloning to match original narrators
        - Personalize stories based on user preferences
        """)
    
    # Reset button
    if st.button("🔁 Start New Investigation"):
        st.session_state.story = """You're Detective Alex Stone, called to investigate a murder at the luxurious Blackwood Manor. 
The victim, billionaire Charles Blackwood, was found dead in his study. The initial examination suggests poison, but there are no obvious signs of forced entry.

As you arrive, the mansion's occupants - Charles's wife Eleanor, his daughter Victoria, his business partner James, and the butler Thompson - all eye you suspiciously."""
        st.session_state.history = []
        st.session_state.story_stage = 0
        st.experimental_rerun()
