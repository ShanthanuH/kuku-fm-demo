import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import os
import tempfile
from huggingface_hub import InferenceClient

# Initialize Hugging Face client - replace with your actual API key
client = InferenceClient(token="HUGGINGFACE_API_KEY")

# Set page configuration
st.set_page_config(
    page_title="Voice Story",
    page_icon="🎙️",
    layout="wide"
)

# Basic CSS styling
st.markdown("""
<style>
    .story-text {
        font-family: 'Georgia', serif;
        font-size: 1.2rem;
        line-height: 1.6;
        background-color: #E3F2FD;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    
    .user-choice {
        font-family: 'Arial', sans-serif;
        font-size: 1.1rem;
        background-color: #FFF3E0;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: right;
    }
    
    .main-header {
        font-size: 2.2rem;
        color: #FF5722;
        text-align: center;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Function to recognize speech
def recognize_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Listening...")
        r.adjust_for_ambient_noise(source, duration=0.5)
        audio = r.listen(source, timeout=5, phrase_time_limit=5)
    
    try:
        text = r.recognize_google(audio)
        return text.lower()
    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError:
        return "Could not request results from speech recognition service"
    except Exception as e:
        return f"Error: {str(e)}"

# Function to generate text to speech
def text_to_speech(text):
    try:
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, "story_audio.mp3")
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(temp_file)
        return temp_file
    except Exception as e:
        st.error(f"Error generating speech: {str(e)}")
        return None

# Function to generate story continuation using Hugging Face API
def generate_story_continuation(story_so_far, user_action):
    prompt = f"""
Continue this interactive story based on the user's choice:

Story so far:
{story_so_far}

The user has decided to: {user_action}

Continue the story based on this action. Make it engaging and end with a question asking what the user wants to do next.
Write 2-3 paragraphs only.
"""
    try:
        response = client.text_generation(
            model="mistralai/Mistral-7B-Instruct-v0.2",
            inputs=prompt,
            parameters={
                "max_new_tokens": 250, 
                "temperature": 0.7,
                "top_p": 0.9
            }
        )
        return response
    except Exception as e:
        st.error(f"Error generating story: {e}")
        return "What would you like to do next?"

# Function to generate initial story beginning
def generate_story_beginning():
    # Using a fixed story beginning for simplicity
    return """You find yourself standing at the entrance of an ancient forest. The trees tower above you, their leaves rustling in the gentle breeze. A narrow path winds its way into the depths of the woods, and you can hear faint, mysterious sounds coming from within. 

Something about this forest calls to you, as if it holds secrets waiting to be discovered. What do you want to do?"""

# Main function
def main():
    # Initialize session state variables
    if 'story_history' not in st.session_state:
        st.session_state.story_history = []
    
    if 'story_so_far' not in st.session_state:
        st.session_state.story_so_far = ""
        
    # Header
    st.markdown('<p class="main-header">Voice Interactive Story</p>', unsafe_allow_html=True)
    
    # Display reset button
    if st.session_state.story_history:
        if st.button("Start Over"):
            st.session_state.story_history = []
            st.session_state.story_so_far = ""
            st.rerun()
    
    # Start story if it hasn't begun
    if not st.session_state.story_history:
        story_beginning = generate_story_beginning()
        st.session_state.story_history.append({"role": "ai", "content": story_beginning})
        st.session_state.story_so_far = story_beginning
    
    # Display story and user actions
    for item in st.session_state.story_history:
        if item["role"] == "ai":
            st.markdown(f'<div class="story-text">{item["content"]}</div>', unsafe_allow_html=True)
            
            # Audio button for AI parts
            if st.button("🔊 Listen", key=f"listen_{len(st.session_state.story_history)}"):
                audio_file = text_to_speech(item["content"])
                if audio_file:
                    st.audio(audio_file)
                
        elif item["role"] == "user":
            st.markdown(f'<div class="user-choice">{item["content"]}</div>', unsafe_allow_html=True)
    
    # User input section
    st.write("---")
    
    # Voice or text input for user choice
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("🎤 Speak", key="speak_button"):
            user_choice = recognize_speech()
            if user_choice != "Could not understand audio" and not user_choice.startswith("Error"):
                # Add user action to history
                st.session_state.story_history.append({"role": "user", "content": user_choice})
                
                # Generate next part of story
                with st.spinner("Continuing the story..."):
                    next_part = generate_story_continuation(st.session_state.story_so_far, user_choice)
                    st.session_state.story_history.append({"role": "ai", "content": next_part})
                    st.session_state.story_so_far += f"\n\nUser: {user_choice}\n\nStory: {next_part}"
                st.rerun()
            else:
                st.error(user_choice)
    
    with col2:
        user_text = st.text_input("Or type what you want to do:", key="user_text")
        if st.button("Submit", key="submit_text"):
            if user_text:
                # Add user action to history
                st.session_state.story_history.append({"role": "user", "content": user_text})
                
                # Generate next part of story
                with st.spinner("Continuing the story..."):
                    next_part = generate_story_continuation(st.session_state.story_so_far, user_text)
                    st.session_state.story_history.append({"role": "ai", "content": next_part})
                    st.session_state.story_so_far += f"\n\nUser: {user_text}\n\nStory: {next_part}"
                st.rerun()

if __name__ == "__main__":
    main()
