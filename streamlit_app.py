import streamlit as st
import random
import time
import speech_recognition as sr
from gtts import gTTS
import os
from huggingface_hub import InferenceClient

# Initialize Hugging Face client - replace with your actual API key
client = InferenceClient(token="HUGGINGFACE_API_KEY")

# Set page configuration
st.set_page_config(
    page_title="KukuFM VoiceChoice Tales",
    page_icon="🎙️",
    layout="wide"
)

# Custom CSS for better appearance
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #FF5722;
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
    }
</style>
""", unsafe_allow_html=True)

# Function to recognize speech
def recognize_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening... Speak your choice.")
        audio = r.listen(source, timeout=5)
    try:
        text = r.recognize_google(audio)
        return text.lower()
    except:
        return "Could not understand audio"

# Function to generate text to speech
def text_to_speech(text):
    tts = gTTS(text=text, lang='en', slow=False)
    filename = "story_audio.mp3"
    tts.save(filename)
    return filename

# Function to generate story continuation using Hugging Face API
def generate_story_continuation(story_so_far, user_action):
    prompt = f"""
You are an AI storyteller creating an interactive crime investigation thriller.

Story so far:
{story_so_far}

The user has decided to: {user_action}

Continue the story based on this action. Keep it suspenseful and engaging.
Write 2-3 paragraphs only. End with a question asking what the detective wants to do next.
"""
    try:
        response = client.text_generation(
            model="tiiuae/falcon-7b-instruct",
            inputs=prompt,
            parameters={"max_new_tokens": 250, "temperature": 0.7}
        )
        return response
    except Exception as e:
        st.error(f"Error generating story: {e}")
        # Fallback to predefined responses
        fallbacks = [
            """You examine the victim's body closely. The medical examiner points out unusual blue discoloration around the lips - a sign of cyanide poisoning. On the desk, you notice a half-empty teacup with a strange residue at the bottom.

The butler hovers nearby, seemingly anxious. "He was alive when I brought his evening tea at 8 PM," he offers without being asked.

What do you want to investigate next?""",
            
            """You interview the family members in the drawing room. Eleanor, the widow, appears composed but her hands tremble slightly. Victoria, the daughter, interrupts with tears in her eyes. "Father was changing his will tomorrow."

James, the business partner, scoffs. "Charles was always dramatic. Our company is going public next week - worth billions."

Who do you want to question more thoroughly?"""
        ]
        return random.choice(fallbacks)

# Function to generate story ending
def generate_story_ending(story_so_far, user_actions):
    prompt = f"""
You are an AI storyteller creating the conclusion to an interactive crime investigation thriller.

Story so far:
{story_so_far}

The detective has taken these actions: {', '.join(user_actions)}

Create a satisfying conclusion to the mystery that reveals the culprit.
Keep it to 3-4 paragraphs maximum.
"""
    try:
        response = client.text_generation(
            model="tiiuae/falcon-7b-instruct",
            inputs=prompt,
            parameters={"max_new_tokens": 300, "temperature": 0.7}
        )
        return response
    except Exception as e:
        st.error(f"Error generating ending: {e}")
        # Fallback ending
        return """After connecting all the evidence, you confront the killer - it was James, the business partner. "Charles discovered I've been embezzling funds," he confesses.

As the officers take James away, you reflect on how greed can corrupt even the closest relationships.

Case closed. Another mystery solved by Detective Stone."""

# Main function
def main():
    # Header
    st.markdown('<p class="main-header">KukuFM VoiceChoice Tales</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Interactive Voice-Driven Crime Investigation</p>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'story_so_far' not in st.session_state:
        st.session_state.story_so_far = """You're Detective Alex Stone, called to investigate a murder at the luxurious Blackwood Manor. 
The victim, billionaire Charles Blackwood, was found dead in his study. The initial examination suggests poison, but there are no obvious signs of forced entry.

As you arrive, the mansion's occupants - Charles's wife Eleanor, his daughter Victoria, his business partner James, and the butler Thompson - all eye you suspiciously.

What will you do first?"""
    
    if 'story_stage' not in st.session_state:
        st.session_state.story_stage = 0
        
    if 'user_actions' not in st.session_state:
        st.session_state.user_actions = []
    
    # Display current story
    st.markdown('<p class="sub-header">The Story</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="story-text">{st.session_state.story_so_far}</div>', unsafe_allow_html=True)
    
    # Audio playback option
    if st.button("🔊 Listen to Story"):
        try:
            audio_file = text_to_speech(st.session_state.story_so_far)
            st.audio(audio_file)
        except:
            st.error("Text-to-speech failed. Please try again.")
    
    # Voice input for user choice
    if st.session_state.story_stage < 3:  # Limit to 3 choices before ending
        st.markdown('<p class="sub-header">What will Detective Stone do next?</p>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎤 Speak Your Choice"):
                try:
                    with st.spinner("Listening..."):
                        user_choice = recognize_speech()
                        st.success(f"You said: {user_choice}")
                        
                        # Store user action
                        st.session_state.user_actions.append(user_choice)
                        
                        # Generate next part of story
                        with st.spinner("The AI is crafting the next part of your story..."):
                            continuation = generate_story_continuation(st.session_state.story_so_far, user_choice)
                            
                            # Update story
                            st.session_state.story_so_far = continuation
                            st.session_state.story_stage += 1
                            
                            # Rerun to update display
                            st.experimental_rerun()
                except:
                    st.error("Voice recognition failed. Please try text input instead.")
        
        with col2:
            # Text input as fallback
            user_text = st.text_input("Or type your action:")
            if st.button("Submit"):
                # Store user action
                st.session_state.user_actions.append(user_text)
                
                # Generate next part of story
                with st.spinner("The AI is crafting the next part of your story..."):
                    continuation = generate_story_continuation(st.session_state.story_so_far, user_text)
                    
                    # Update story
                    st.session_state.story_so_far = continuation
                    st.session_state.story_stage += 1
                    
                    # Rerun to update display
                    st.experimental_rerun()
    
    # Generate ending after 3 choices
    elif st.session_state.story_stage == 3:
        if st.button("🔍 Solve the Case"):
            with st.spinner("Detective Stone is connecting the dots..."):
                ending = generate_story_ending(st.session_state.story_so_far, st.session_state.user_actions)
                st.session_state.story_so_far += "\n\n" + ending
                st.session_state.story_stage += 1
                st.experimental_rerun()
    
    # Display story progress
    st.sidebar.subheader("Investigation Progress")
    progress = min(100, st.session_state.story_stage * 25)  # 25% per stage, max 100%
    st.sidebar.progress(progress)
    
    # Display previous choices
    if st.session_state.user_actions:
        st.sidebar.subheader("Your Investigation Path")
        for i, action in enumerate(st.session_state.user_actions):
            st.sidebar.write(f"{i+1}. {action}")
    
    # Explain the AI technology
    with st.sidebar.expander("How the AI Works"):
        st.write("""
        1. **Voice Recognition**: Converts your spoken choices to text
        2. **Narrative Generation**: Hugging Face AI model generates contextually appropriate story continuations
        3. **Text-to-Speech**: Converts story text to spoken narration
        4. **Dynamic Branching**: Each choice creates a unique story path
        
        In the full implementation for Kuku FM, this would be expanded to:
        - Support multiple Indian languages
        - Use voice cloning to match original narrators
        - Personalize stories based on user preferences
        """)
    
    # Reset button
    if st.sidebar.button("Start New Investigation"):
        st.session_state.story_so_far = """You're Detective Alex Stone, called to investigate a murder at the luxurious Blackwood Manor. 
The victim, billionaire Charles Blackwood, was found dead in his study. The initial examination suggests poison, but there are no obvious signs of forced entry.

As you arrive, the mansion's occupants - Charles's wife Eleanor, his daughter Victoria, his business partner James, and the butler Thompson - all eye you suspiciously.

What will you do first?"""
        st.session_state.story_stage = 0
        st.session_state.user_actions = []
        st.experimental_rerun()

if __name__ == "__main__":
    main()
