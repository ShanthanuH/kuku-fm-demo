import streamlit as st
import random
import time
import speech_recognition as sr
from gtts import gTTS
import os
import tempfile
from huggingface_hub import InferenceClient

# Initialize Hugging Face client - replace with your actual API key
client = InferenceClient(token="HUGGINGFACE_API_KEY")

# Set page configuration
st.set_page_config(
    page_title="KukuFM VoiceChoice Tales",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for a more modern, chatbot-like interface
st.markdown("""
<style>
    :root {
        --primary: #FF5722;
        --secondary: #2196F3;
        --background: #FFFFFF;
        --text: #333333;
        --light-gray: #F5F5F5;
        --chat-ai: #E3F2FD;
        --chat-user: #FFF3E0;
    }
    
    .main-header {
        font-family: 'Arial', sans-serif;
        font-size: 2.8rem;
        color: var(--primary);
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.1);
    }
    
    .sub-header {
        font-family: 'Arial', sans-serif;
        font-size: 1.5rem;
        color: var(--secondary);
        margin-bottom: 1.5rem;
        text-align: center;
        font-weight: 300;
    }
    
    .story-text {
        font-family: 'Georgia', serif;
        font-size: 1.2rem;
        line-height: 1.6;
        background-color: var(--chat-ai);
        padding: 25px;
        border-radius: 12px;
        margin-bottom: 25px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        position: relative;
        max-width: 95%;
    }
    
    .story-text::before {
        content: '';
        position: absolute;
        left: -10px;
        top: 20px;
        border-right: 15px solid var(--chat-ai);
        border-top: 10px solid transparent;
        border-bottom: 10px solid transparent;
    }
    
    .user-choice {
        font-family: 'Arial', sans-serif;
        font-size: 1.1rem;
        line-height: 1.5;
        background-color: var(--chat-user);
        padding: 15px 20px;
        border-radius: 12px;
        margin: 20px 0 20px auto;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        position: relative;
        max-width: 85%;
        display: block;
        text-align: right;
    }
    
    .user-choice::after {
        content: '';
        position: absolute;
        right: -10px;
        top: 20px;
        border-left: 15px solid var(--chat-user);
        border-top: 10px solid transparent;
        border-bottom: 10px solid transparent;
    }
    
    .stButton > button {
        background-color: var(--primary);
        color: white;
        border-radius: 25px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .stButton > button:hover {
        background-color: #E64A19;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        transform: translateY(-2px);
    }
    
    .chat-container {
        max-height: 70vh;
        overflow-y: auto;
        padding-right: 10px;
        margin-bottom: 20px;
        scroll-behavior: smooth;
    }
    
    .input-container {
        background-color: var(--light-gray);
        padding: 20px;
        border-radius: 15px;
        margin-top: 20px;
        display: flex;
        flex-direction: column;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
    }
    
    .stTextInput > div > div > input {
        border-radius: 25px;
        border: 1px solid #DDDDDD;
        padding: 12px 20px;
        font-size: 1.1rem;
    }
    
    .stTextInput > div {
        padding-bottom: 10px;
    }
    
    .avatar-ai {
        width: 40px;
        height: 40px;
        background-color: var(--secondary);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        float: left;
        margin-right: 15px;
        margin-top: -5px;
    }
    
    .avatar-user {
        width: 40px;
        height: 40px;
        background-color: var(--primary);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        float: right;
        margin-left: 15px;
        margin-top: -5px;
    }
    
    .footer {
        text-align: center;
        margin-top: 40px;
        padding-top: 20px;
        font-size: 0.9rem;
        color: #888888;
        border-top: 1px solid #EEEEEE;
    }
    
    .listening-animation {
        display: inline-block;
        margin-left: 10px;
    }
    
    .dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: var(--primary);
        animation: pulse 1.5s infinite ease-in-out;
        margin: 0 2px;
    }
    
    .dot:nth-child(2) {
        animation-delay: 0.2s;
    }
    
    .dot:nth-child(3) {
        animation-delay: 0.4s;
    }
    
    @keyframes pulse {
        0% { transform: scale(0.8); opacity: 0.5; }
        50% { transform: scale(1.2); opacity: 1; }
        100% { transform: scale(0.8); opacity: 0.5; }
    }
    
    /* Progress bar customization */
    .stProgress > div > div {
        background-color: var(--primary) !important;
    }
    
    /* Sidebar customization */
    .css-1d391kg {
        background-color: var(--light-gray);
        border-radius: 10px;
        padding: 15px;
        margin-top: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Function to recognize speech
def recognize_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        st.session_state.listening = True
        st.experimental_rerun() # To display the listening animation
        audio = r.listen(source, timeout=5, phrase_time_limit=5)
        st.session_state.listening = False
    
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
def text_to_speech(text, lang='en'):
    try:
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, "story_audio.mp3")
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(temp_file)
        return temp_file
    except Exception as e:
        st.error(f"Error generating speech: {str(e)}")
        return None

# Function to generate story continuation using Hugging Face API
def generate_story_continuation(story_so_far, user_action, genre="fantasy"):
    prompt = f"""
You are a creative AI storyteller crafting an immersive interactive story.

Genre: {genre}

Story so far:
{story_so_far}

The user has decided to: {user_action}

Continue the story based on this action. Make it engaging and rich with sensory details.
Write 2-3 paragraphs only. End with a question asking what the user wants to do next.

Important:
- Use vivid language and create an immersive atmosphere
- Include sensory details (sights, sounds, smells, etc.)
- Keep the tone consistent with the chosen genre
- Make the user feel like the protagonist
- Create meaningful choices that impact the story
"""
    try:
        response = client.text_generation(
            model="mistralai/Mistral-7B-Instruct-v0.2",
            inputs=prompt,
            parameters={
                "max_new_tokens": 350, 
                "temperature": 0.78,
                "top_p": 0.95,
                "repetition_penalty": 1.15
            }
        )
        return response
    except Exception as e:
        st.error(f"Error generating story: {e}")
        fallbacks = [
            "The path ahead splits in two directions. What do you want to do next?",
            "A mysterious figure appears before you. How do you want to proceed?",
            "You find yourself facing an unexpected challenge. What's your next move?"
        ]
        return random.choice(fallbacks)

# Function to generate story ending
def generate_story_ending(story_so_far, user_actions, genre="fantasy"):
    prompt = f"""
Create a satisfying conclusion to the story that ties together the user's choices.

Genre: {genre}

Story so far:
{story_so_far}

The user has taken these actions: {', '.join(user_actions)}

Important:
- Provide a meaningful resolution
- Reference the user's previous choices
- Keep the ending consistent with the established tone
- Make it emotionally satisfying
- Keep it to 3-4 paragraphs maximum
"""
    try:
        response = client.text_generation(
            model="mistralai/Mistral-7B-Instruct-v0.2",
            inputs=prompt,
            parameters={
                "max_new_tokens": 450, 
                "temperature": 0.72,
                "top_p": 0.92,
                "repetition_penalty": 1.2
            }
        )
        return response
    except Exception as e:
        st.error(f"Error generating ending: {e}")
        return "Your journey comes to an end, with the choices you made shaping the outcome. The adventure may be over, but the memories will remain..."

# Function to generate story beginning
def generate_story_beginning(genre="fantasy", setting="medieval kingdom", protagonist="adventurer"):
    prompt = f"""
Create an engaging opening for an interactive story that pulls the reader in immediately.

Genre: {genre}
Setting: {setting}
Protagonist: {protagonist}

Important:
- Set the scene vividly
- Introduce a compelling situation or conflict
- Position the reader as the protagonist
- Include sensory details
- End with a question asking what the user wants to do
- Keep it to 2-3 paragraphs maximum
"""
    try:
        response = client.text_generation(
            model="mistralai/Mistral-7B-Instruct-v0.2",
            inputs=prompt,
            parameters={
                "max_new_tokens": 350, 
                "temperature": 0.76,
                "top_p": 0.95,
                "repetition_penalty": 1.1
            }
        )
        return response
    except Exception as e:
        st.error(f"Error generating story beginning: {e}")
        return "You find yourself at the beginning of an adventure. The path ahead is unclear, but your choices will shape your destiny. What do you want to do first?"

# Main function
def main():
    # Initialize session state variables
    if 'story_history' not in st.session_state:
        st.session_state.story_history = []
    
    if 'user_actions' not in st.session_state:
        st.session_state.user_actions = []
        
    if 'story_stage' not in st.session_state:
        st.session_state.story_stage = 0
        
    if 'current_genre' not in st.session_state:
        st.session_state.current_genre = "fantasy"
        
    if 'listening' not in st.session_state:
        st.session_state.listening = False
        
    # Header
    st.markdown('<p class="main-header">KukuFM VoiceChoice Tales</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Interactive AI Storyteller</p>', unsafe_allow_html=True)
    
    # Sidebar with genre selection and story controls
    with st.sidebar:
        st.image("https://via.placeholder.com/280x100?text=KukuFM+Logo", use_column_width=True)
        
        # Genre selection (only before story starts)
        if st.session_state.story_stage == 0 and not st.session_state.story_history:
            st.subheader("Choose Your Adventure")
            genre = st.selectbox(
                "Story Genre",
                ["Fantasy", "Sci-Fi", "Mystery", "Horror", "Adventure", "Romance"],
                key="genre_select"
            )
            st.session_state.current_genre = genre.lower()
            
            setting = st.selectbox(
                "Story Setting",
                ["Medieval Kingdom", "Space Colony", "Modern City", "Ancient Temple", 
                 "Enchanted Forest", "Dystopian Future", "Haunted Mansion"],
                key="setting_select"
            )
            
            protagonist = st.selectbox(
                "Protagonist",
                ["Adventurer", "Detective", "Wizard", "Space Explorer", 
                 "Soldier", "Lost Traveler", "Ordinary Person"],
                key="protagonist_select"
            )
            
            if st.button("Begin Your Adventure", key="start_adventure"):
                with st.spinner("Creating your story..."):
                    starting_story = generate_story_beginning(
                        st.session_state.current_genre, 
                        setting.lower(), 
                        protagonist.lower()
                    )
                    st.session_state.story_history.append({"role": "ai", "content": starting_story})
                    st.session_state.story_stage = 1
                    st.experimental_rerun()
        
        # Display story progress
        st.subheader("Story Progress")
        progress = min(100, st.session_state.story_stage * 20)  # 20% per stage, max 100%
        st.progress(progress)
        
        # Display previous choices
        if st.session_state.user_actions:
            st.subheader("Your Choices")
            for i, action in enumerate(st.session_state.user_actions):
                st.write(f"{i+1}. {action}")
        
        # Help section
        with st.expander("How to Play"):
            st.markdown("""
            - Speak or type your choices to progress the story
            - Each choice shapes how the story unfolds
            - The adventure will conclude after 5 choices
            - Use the voice option for a hands-free experience
            - Listen to narration with the 🔊 button
            """)
            
        # Reset button
        if st.session_state.story_history:
            if st.button("🔄 Start New Story", key="reset_story"):
                st.session_state.story_history = []
                st.session_state.user_actions = []
                st.session_state.story_stage = 0
                st.experimental_rerun()
    
    # Main area - Chat container
    chat_container = st.container()
    
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # Display story and user actions as a chat interface
        for item in st.session_state.story_history:
            if item["role"] == "ai":
                st.markdown(f'<div class="avatar-ai">AI</div><div class="story-text">{item["content"]}</div>', unsafe_allow_html=True)
                
                # Audio playback option after each AI message
                audio_col, _ = st.columns([1, 9])
                with audio_col:
                    if st.button("🔊", key=f"listen_{st.session_state.story_history.index(item)}"):
                        try:
                            with st.spinner("Generating audio..."):
                                audio_file = text_to_speech(item["content"])
                                if audio_file:
                                    st.audio(audio_file)
                        except:
                            st.error("Text-to-speech failed. Please try again.")
            
            elif item["role"] == "user":
                st.markdown(f'<div class="user-choice">{item["content"]}<div class="avatar-user">YOU</div></div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Show listening animation if needed
        if st.session_state.listening:
            st.markdown("""
            <div style="text-align: center; margin: 20px 0;">
                <span>Listening</span>
                <span class="listening-animation">
                    <span class="dot"></span>
                    <span class="dot"></span>
                    <span class="dot"></span>
                </span>
            </div>
            """, unsafe_allow_html=True)
    
    # User input section - only show if story has started and not ended
    if st.session_state.story_history and st.session_state.story_stage < 6:
        st.markdown('<div class="input-container">', unsafe_allow_html=True)
        
        # Voice or text input for user choice
        col1, col2 = st.columns([1, 4])
        
        with col1:
            if st.button("🎤 Speak", key="speak_button", use_container_width=True):
                try:
                    user_choice = recognize_speech()
                    if user_choice != "Could not understand audio" and user_choice.startswith("error") is False:
                        # Add user action to history
                        st.session_state.user_actions.append(user_choice)
                        st.session_state.story_history.append({"role": "user", "content": user_choice})
                        
                        # Generate next part of story
                        with st.spinner("Generating story..."):
                            # Get the last AI message as the current story
                            current_story = next((item["content"] for item in reversed(st.session_state.story_history) 
                                                 if item["role"] == "ai"), "")
                            
                            if st.session_state.story_stage < 5:
                                # Continue the story
                                continuation = generate_story_continuation(
                                    current_story, 
                                    user_choice,
                                    st.session_state.current_genre
                                )
                                st.session_state.story_history.append({"role": "ai", "content": continuation})
                            else:
                                # Generate ending
                                ending = generate_story_ending(
                                    current_story, 
                                    st.session_state.user_actions,
                                    st.session_state.current_genre
                                )
                                st.session_state.story_history.append({"role": "ai", "content": ending})
                            
                            # Update story stage
                            st.session_state.story_stage += 1
                            
                            # Rerun to update display
                            st.experimental_rerun()
                    else:
                        st.error("Could not understand audio. Please try again or use text input.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        with col2:
            user_text = st.text_input("Type your action...", key="user_text_input", 
                                     placeholder="What do you want to do next?")
            if st.button("Send", key="submit_text", use_container_width=False):
                if user_text:
                    # Add user action to history
                    st.session_state.user_actions.append(user_text)
                    st.session_state.story_history.append({"role": "user", "content": user_text})
                    
                    # Generate next part of story
                    with st.spinner("Generating story..."):
                        # Get the last AI message as the current story
                        current_story = next((item["content"] for item in reversed(st.session_state.story_history) 
                                             if item["role"] == "ai"), "")
                        
                        if st.session_state.story_stage < 5:
                            # Continue the story
                            continuation = generate_story_continuation(
                                current_story, 
                                user_text,
                                st.session_state.current_genre
                            )
                            st.session_state.story_history.append({"role": "ai", "content": continuation})
                        else:
                            # Generate ending
                            ending = generate_story_ending(
                                current_story, 
                                st.session_state.user_actions,
                                st.session_state.current_genre
                            )
                            st.session_state.story_history.append({"role": "ai", "content": ending})
                        
                        # Update story stage
                        st.session_state.story_stage += 1
                        
                        # Rerun to update display
                        st.experimental_rerun()
                else:
                    st.warning("Please enter your action.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # After story ends (after 5 interactions), show replay button
    elif st.session_state.story_stage >= 6:
        st.markdown('<div style="text-align: center; margin: 30px 0;">', unsafe_allow_html=True)
        if st.button("🔄 Start a New Adventure", key="new_adventure", use_container_width=False):
            # Reset all state
            st.session_state.story_history = []
            st.session_state.user_actions = []
            st.session_state.story_stage = 0
            st.experimental_rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown('<div class="footer">KukuFM VoiceChoice Tales - AI-Powered Interactive Storyteller</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
