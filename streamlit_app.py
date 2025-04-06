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

# Custom CSS for better appearance with simplified color scheme
st.markdown("""
<style>
    :root {
        --primary: #FF5722;
        --secondary: #2196F3;
        --background: #FFFFFF;
        --text: #333333;
    }
    
    .main-header {
        font-family: 'Arial', sans-serif;
        font-size: 2.5rem;
        color: var(--primary);
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        font-family: 'Arial', sans-serif;
        font-size: 1.5rem;
        color: var(--secondary);
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    .story-text {
        font-family: 'Georgia', serif;
        font-size: 1.2rem;
        line-height: 1.6;
        background-color: var(--background);
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid var(--primary);
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stButton > button {
        background-color: var(--primary);
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #E64A19;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .choice-container {
        background-color: #F5F5F5;
        padding: 15px;
        border-radius: 8px;
        margin-top: 15px;
    }
    
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 1px solid #CCCCCC;
        padding: 8px;
    }
    
    .evidence-box {
        background-color: #E3F2FD;
        border-left: 4px solid var(--secondary);
        padding: 10px;
        margin-top: 15px;
        border-radius: 5px;
    }
    
    .footer {
        text-align: center;
        margin-top: 30px;
        font-size: 0.9rem;
        color: #888888;
    }
</style>
""", unsafe_allow_html=True)

# Function to recognize speech
def recognize_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
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
def generate_story_continuation(story_so_far, user_action):
    prompt = f"""
You are an AI storyteller creating an interactive crime investigation thriller set in modern India.

Story so far:
{story_so_far}

The user (playing as the detective) has decided to: {user_action}

Continue the story based on this action. Keep it suspenseful and engaging.
Write 2-3 paragraphs only. End with a question asking what the detective wants to do next.

Important:
- Use Indian names, places, and cultural references
- Include sensory details like sounds, smells, tastes typical of Indian settings
- Keep the tone suspenseful and intriguing
"""
    try:
        response = client.text_generation(
            model="mistralai/Mistral-7B-Instruct-v0.2",
            inputs=prompt,
            parameters={
                "max_new_tokens": 350, 
                "temperature": 0.75,
                "top_p": 0.95,
                "repetition_penalty": 1.15
            }
        )
        return response
    except Exception as e:
        st.error(f"Error generating story: {e}")
        fallbacks = [
            "As you investigate further, you notice a strange odor in the room. What do you want to do next?",
            "A witness suddenly appears with new information. How do you want to proceed?",
            "You find an unexpected clue hidden in plain sight. What's your next move?"
        ]
        return random.choice(fallbacks)

# Function to generate story ending
def generate_story_ending(story_so_far, user_actions):
    prompt = f"""
Create a satisfying conclusion to the mystery that reveals the culprit. Make it distinctly Indian in setting and atmosphere.
Keep it to 3-4 paragraphs maximum.

Story so far:
{story_so_far}

The detective has taken these actions: {', '.join(user_actions)}

Important:
- Include Indian cultural elements and references
- Maintain the atmosphere of an Indian crime thriller
- Provide a satisfying resolution
"""
    try:
        response = client.text_generation(
            model="mistralai/Mistral-7B-Instruct-v0.2",
            inputs=prompt,
            parameters={
                "max_new_tokens": 450, 
                "temperature": 0.7,
                "top_p": 0.92,
                "repetition_penalty": 1.2
            }
        )
        return response
    except Exception as e:
        st.error(f"Error generating ending: {e}")
        return "The case is solved, revealing unexpected twists and turns. Justice is served, but questions linger..."

# Function to generate clues and evidence
def generate_evidence(story_stage):
    evidences = [
        {"item": "Mysterious note", "description": "A crumpled paper with cryptic symbols."},
        {"item": "Fingerprints", "description": "Unusual pattern found on the murder weapon."},
        {"item": "CCTV footage", "description": "Shows an unidentified figure entering the crime scene."},
        {"item": "Phone records", "description": "Reveal suspicious calls made on the night of the murder."},
        {"item": "Witness statement", "description": "Provides an unexpected alibi for a key suspect."}
    ]
    
    if story_stage < len(evidences):
        return evidences[story_stage]
    else:
        return {"item": "Case file", "description": "All evidence collected points to a clear suspect."}

# Main function
def main():
    # Initialize session state variables
    if 'story_so_far' not in st.session_state:
        st.session_state.story_so_far = """You're Inspector Sharma, called to investigate a murder at a luxurious mansion. 
The victim, a tech mogul, was found dead in his study. What will you do first?"""
    
    if 'story_stage' not in st.session_state:
        st.session_state.story_stage = 0
        
    if 'user_actions' not in st.session_state:
        st.session_state.user_actions = []
        
    if 'evidence_collected' not in st.session_state:
        st.session_state.evidence_collected = []
    
    # Header
    st.markdown('<p class="main-header">KukuFM VoiceChoice Tales</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Interactive Crime Thriller</p>', unsafe_allow_html=True)
    
    # Display current story
    st.markdown(f'<div class="story-text">{st.session_state.story_so_far}</div>', unsafe_allow_html=True)
    
    # Audio playback option
    if st.button("🔊 Listen"):
        try:
            with st.spinner("Generating audio..."):
                audio_file = text_to_speech(st.session_state.story_so_far)
                if audio_file:
                    st.audio(audio_file)
        except:
            st.error("Text-to-speech failed. Please try again.")
    
    # Evidence collection feature
    if st.session_state.story_stage > 0 and st.session_state.story_stage < 5:
        evidence = generate_evidence(st.session_state.story_stage - 1)
        if evidence and evidence not in st.session_state.evidence_collected:
            st.session_state.evidence_collected.append(evidence)
            
            st.markdown('<div class="evidence-box">', unsafe_allow_html=True)
            st.markdown(f"**New Evidence Collected:** {evidence['item']}")
            st.markdown(f"_{evidence['description']}_")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Voice or text input for user choice
    if st.session_state.story_stage < 5:  # Limit to 5 choices
        st.markdown('<p class="sub-header">What will you do next?</p>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🎤 Speak your choice"):
                try:
                    with st.spinner("Listening..."):
                        user_choice = recognize_speech()
                        if user_choice != "Could not understand audio":
                            st.success(f"You said: {user_choice}")
                            
                            # Store user action
                            st.session_state.user_actions.append(user_choice)
                            
                            # Generate next part of story
                            with st.spinner("Generating story..."):
                                continuation = generate_story_continuation(st.session_state.story_so_far, user_choice)
                                
                                # Update story
                                st.session_state.story_so_far = continuation
                                st.session_state.story_stage += 1
                                
                                # Rerun to update display
                                st.experimental_rerun()
                        else:
                            st.error("Could not understand audio. Please try again or use text input.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        with col2:
            user_text = st.text_input("Or type your choice:", key="user_text_input")
            if st.button("Submit", key="submit_text"):
                if user_text:
                    # Store user action
                    st.session_state.user_actions.append(user_text)
                    
                    # Generate next part of story
                    with st.spinner("Generating story..."):
                        continuation = generate_story_continuation(st.session_state.story_so_far, user_text)
                        
                        # Update story
                        st.session_state.story_so_far = continuation
                        st.session_state.story_stage += 1
                        
                        # Rerun to update display
                        st.experimental_rerun()
                else:
                    st.warning("Please enter your choice.")
    
    # Generate ending after 5 interaction points
    elif st.session_state.story_stage == 5:
        st.markdown('<div style="text-align: center; margin: 30px 0;">', unsafe_allow_html=True)
        if st.button("🕵️ Solve the Case", key="solve_case"):
            with st.spinner("Concluding the investigation..."):
                ending = generate_story_ending(st.session_state.story_so_far, st.session_state.user_actions)
                st.session_state.story_so_far += "\n\n" + ending
                st.session_state.story_stage += 1
                st.experimental_rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    # After story ends, offer restart
    elif st.session_state.story_stage > 5:
        st.markdown('<div style="text-align: center; margin: 30px 0;">', unsafe_allow_html=True)
        if st.button("🔄 Start a New Case", key="new_investigation"):
            # Reset all state
            st.session_state.story_so_far = """You're Inspector Sharma, called to investigate a murder at a luxurious mansion. 
The victim, a tech mogul, was found dead in his study. What will you do first?"""
            st.session_state.story_stage = 0
            st.session_state.user_actions = []
            st.session_state.evidence_collected = []
            st.experimental_rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Sidebar with additional features
    with st.sidebar:
        st.image("https://via.placeholder.com/280x100?text=KukuFM+Logo", use_column_width=True)
        
        # Display story progress
        st.subheader("Story Progress")
        progress = min(100, st.session_state.story_stage * 20)  # 20% per stage, max 100%
        st.progress(progress)
        
        # Display previous choices
        if st.session_state.user_actions:
            st.subheader("Your Choices")
            for i, action in enumerate(st.session_state.user_actions):
                st.write(f"{i+1}. {action}")
        
        # Evidence collection display
        if st.session_state.evidence_collected:
            st.subheader("Evidence Collected")
            for i, evidence in enumerate(st.session_state.evidence_collected):
                with st.expander(f"Evidence #{i+1}: {evidence['item']}"):
                    st.write(evidence['description'])
        
        # Help section
        with st.expander("How to Play"):
            st.markdown("""
            - Speak or type your choices to progress the story
            - Collect evidence and pay attention to details
            - Make decisions that affect the outcome
            - Solve the mystery in 5 steps
            """)

    # Footer
    st.markdown('<div class="footer">KukuFM Interactive Demo - Created for ML Engineer Application</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
