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

# Custom CSS for better appearance with Indian color palette and modern aesthetics
st.markdown("""
<style>
    /* Indian-inspired color scheme */
    :root {
        --primary: #FF7722;       /* Deep Saffron */
        --secondary: #138808;     /* India Green */
        --accent: #800080;        /* Deep Purple */
        --background: #FFF3E0;    /* Cream */
        --text-dark: #22223B;     /* Dark Indigo */
        --highlight: #F4C430;     /* Indian Yellow */
    }
    
    .main-header {
        font-family: 'Arial', sans-serif;
        font-size: 2.8rem;
        color: var(--primary);
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    .sub-header {
        font-family: 'Arial', sans-serif;
        font-size: 1.7rem;
        color: var(--accent);
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    .story-text {
        font-family: 'Georgia', serif;
        font-size: 1.3rem;
        line-height: 1.7;
        background-color: var(--background);
        padding: 25px;
        border-radius: 12px;
        border-left: 5px solid var(--primary);
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .stButton > button {
        background-color: var(--primary);
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        border: none;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #E85A0D;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        transform: translateY(-2px);
    }
    
    .choice-container {
        background-color: rgba(255, 255, 255, 0.8);
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }
    
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #CCCCCC;
        padding: 10px;
    }
    
    .story-stage-indicator {
        display: flex;
        justify-content: space-between;
        margin: 20px 0;
    }
    
    .stage-dot {
        width: 18%;
        height: 10px;
        background-color: #DDDDDD;
        border-radius: 5px;
    }
    
    .stage-dot.active {
        background-color: var(--primary);
    }
    
    /* Custom progress bar */
    .progress-container {
        width: 100%;
        height: 15px;
        background-color: #e0e0e0;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    
    .progress-bar {
        height: 100%;
        border-radius: 10px;
        background-image: linear-gradient(to right, var(--primary), var(--accent));
    }
    
    /* Character portraits */
    .character-portraits {
        display: flex;
        justify-content: space-around;
        margin: 20px 0;
    }
    
    .character {
        text-align: center;
        width: 18%;
    }
    
    .character-img {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        background-color: var(--highlight);
        margin: 0 auto;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.5rem;
        color: var(--text-dark);
        border: 3px solid white;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    .character-name {
        margin-top: 10px;
        font-weight: bold;
        color: var(--text-dark);
    }
    
    /* Animation for the listening button */
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .listening {
        animation: pulse 1.5s infinite;
        background-color: #FF4500 !important;
    }
    
    .evidence-box {
        background-color: rgba(255, 245, 224, 0.9);
        border-left: 4px solid var(--secondary);
        padding: 12px;
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
        # Create a temporary file for the audio
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, "story_audio.mp3")
        
        # Generate the speech
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(temp_file)
        
        # Return the path to the audio file
        return temp_file
    except Exception as e:
        st.error(f"Error generating speech: {str(e)}")
        return None

# Function to generate story continuation using Hugging Face API
def generate_story_continuation(story_so_far, user_action):
    # Prepare the prompt with Indian context
    prompt = f"""
You are an AI storyteller creating an interactive crime investigation thriller set in modern India.

Story so far:
{story_so_far}

The user (playing as the detective) has decided to: {user_action}

Continue the story based on this action. Keep it suspenseful and engaging with vivid Indian cultural elements and settings.
Write 2-3 paragraphs only. End with a question asking what the detective wants to do next.

Important:
- Use Indian names, places, and cultural references
- Include sensory details like sounds, smells, tastes typical of Indian settings
- Reference Indian foods, clothing, or customs when appropriate
- Keep the tone suspenseful and intriguing
"""
    try:
        response = client.text_generation(
            model="mistralai/Mistral-7B-Instruct-v0.2",  # More stable model option
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
        # Fallback to predefined Indian-themed responses
        fallbacks = [
            """You examine Kapoor sahab's body closely. Dr. Mehta points out unusual bluish discoloration around the lips - a sign of cyanide poisoning. On the ornate rosewood desk, you notice a half-empty cup of masala chai with strange residue at the bottom.

Ramu kaka, the elderly house help, hovers nearby, twisting his kurta nervously. "Sahab was fine when I brought his evening chai at 8 PM," he offers without being asked. The scent of cardamom and cloves still lingers in the air.

What do you want to investigate next, Inspector Sharma?""",
            
            """You interview the family members in the drawing room adorned with traditional Rajasthani paintings. Sunita, the widow, sits composed in her cream silk saree, but her hennaed hands tremble slightly. Priya, the daughter, interrupts with tears streaming down her face. "Papa was changing his will tomorrow. He told me last night after puja."

Vikram, the business partner, adjusts his designer glasses and scoffs. "Rajesh was always dramatic. Our tech company is going public next week - worth thousands of crores."

The ceiling fan whirs softly overhead as tension fills the room. Who do you want to question more thoroughly, Inspector?"""
        ]
        return random.choice(fallbacks)

# Function to generate story ending
def generate_story_ending(story_so_far, user_actions):
    prompt = f"""
You are an AI storyteller creating the conclusion to an interactive crime investigation thriller set in modern India.

Story so far:
{story_so_far}

The detective has taken these actions: {', '.join(user_actions)}

Create a satisfying conclusion to the mystery that reveals the culprit. Make it distinctly Indian in setting and atmosphere.
Keep it to 3-4 paragraphs maximum.

Important:
- Include Indian cultural elements and references
- Maintain the atmosphere of an Indian crime thriller
- Provide a satisfying resolution with a touch of Indian philosophy or wisdom
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
        # Fallback ending with Indian context
        return """After connecting all the evidence, you confront the killer in the garden among the marigold and jasmine plants. It was Vikram, the business partner. "Rajesh discovered I've been diverting company funds to foreign accounts," he confesses as the evening azan sounds in the distance.

As the officers lead Vikram away in handcuffs, Sunita touches your arm gently. "Inspector Sharma, my husband always said truth is like the sun - it can be hidden for some time, but never forever."

The monsoon rain begins to fall softly outside as you close your notebook. Another case solved by Mumbai Police's finest detective. As your driver starts the Ambassador car, you reflect on how even in modern India, the age-old motives of greed and power continue to corrupt.

Case closed."""

# Function to generate clues and evidence
def generate_evidence(story_stage):
    evidences = [
        {
            "item": "Cup of masala chai",
            "description": "Traces of cyanide detected. Fingerprints match the house help, Ramu kaka."
        },
        {
            "item": "Business documents",
            "description": "Shows company valuation of ₹2,500 crores. Notes in margin suggest Kapoor sahab suspected financial irregularities."
        },
        {
            "item": "Will document",
            "description": "Draft of new will found in home office. Major changes redirect assets away from Vikram and toward charitable foundations."
        },
        {
            "item": "Sunita's phone",
            "description": "Contains deleted messages to an unknown number discussing 'solving the problem permanently.'"
        },
        {
            "item": "CCTV footage",
            "description": "Shows an unidentified figure entering through the garden during evening aarti time."
        }
    ]
    
    if story_stage < len(evidences):
        return evidences[story_stage]
    else:
        return {"item": "Case file", "description": "All evidence collected points to a clear suspect."}

# Main function
def main():
    # Initialize session state variables
    if 'story_so_far' not in st.session_state:
        st.session_state.story_so_far = """You're Inspector Vikram Sharma, a senior detective with the Mumbai Crime Branch, called to investigate a murder at the luxurious Kapoor Mansion in Juhu Beach. 
The victim, tech mogul Rajesh Kapoor, was found dead in his study. Initial examination suggests poison, but there are no obvious signs of forced entry.

As you arrive, the scent of incense lingers in the air, and the household staff is preparing for the evening puja despite the tragedy. The mansion's occupants - Rajesh's wife Sunita, his daughter Priya, his business partner Vikram Malhotra, and the loyal house help Ramu kaka - all watch you with worried eyes.

The sound of Mumbai traffic fades as you step into the opulent mansion. What will you do first, Inspector Sharma?"""
    
    if 'story_stage' not in st.session_state:
        st.session_state.story_stage = 0
        
    if 'user_actions' not in st.session_state:
        st.session_state.user_actions = []
        
    if 'listening' not in st.session_state:
        st.session_state.listening = False
        
    if 'evidence_collected' not in st.session_state:
        st.session_state.evidence_collected = []
    
    # Header with Indian-themed title
    st.markdown('<p class="main-header">KukuFM आवाज़ कहानियाँ</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">इंटरैक्टिव वॉयस-ड्रिवन क्राइम इन्वेस्टिगेशन</p>', unsafe_allow_html=True)
    
    # Story progress indicator - visual representation of 5 stages
    st.markdown('<div class="story-stage-indicator">', unsafe_allow_html=True)
    for i in range(5):
        if i <= st.session_state.story_stage:
            st.markdown(f'<div class="stage-dot active"></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="stage-dot"></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Characters display
    if st.session_state.story_stage == 0:
        st.markdown('<div class="character-portraits">', unsafe_allow_html=True)
        characters = [
            {"name": "Inspector Sharma", "initial": "IS", "bg": "#FF7722"},
            {"name": "Sunita Kapoor", "initial": "SK", "bg": "#FF9E72"},
            {"name": "Priya Kapoor", "initial": "PK", "bg": "#FFB592"},
            {"name": "Vikram Malhotra", "initial": "VM", "bg": "#FFCBB2"},
            {"name": "Ramu Kaka", "initial": "RK", "bg": "#FFE0D2"}
        ]
        
        for char in characters:
            st.markdown(f'''
            <div class="character">
                <div class="character-img" style="background-color: {char['bg']};">{char['initial']}</div>
                <div class="character-name">{char['name']}</div>
            </div>
            ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display current story
    st.markdown('<p class="sub-header">अब तक की कहानी</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="story-text">{st.session_state.story_so_far}</div>', unsafe_allow_html=True)
    
    # Audio playback option with Hindi and English options
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🔊 Listen in English"):
            try:
                with st.spinner("Generating audio..."):
                    audio_file = text_to_speech(st.session_state.story_so_far, 'en')
                    if audio_file:
                        st.audio(audio_file)
            except:
                st.error("Text-to-speech failed. Please try again.")
    
    with col2:
        if st.button("🔊 हिंदी में सुनें"):
            try:
                # For demo purposes, we'll use English but in production would use Hindi
                with st.spinner("ऑडियो जनरेट हो रहा है..."):
                    audio_file = text_to_speech(st.session_state.story_so_far, 'hi')
                    if audio_file:
                        st.audio(audio_file)
            except:
                st.error("वॉइस जनरेशन में समस्या। कृपया दोबारा प्रयास करें।")
    
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
        st.markdown('<p class="sub-header">इंस्पेक्टर शर्मा अब क्या करेंगे?</p>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            listen_button_text = "🎤 बोलकर बताएं" if not st.session_state.listening else "🎙️ सुन रहा हूँ..."
            listen_button_class = "listening" if st.session_state.listening else ""
            
            if st.button(listen_button_text, key="listen_button"):
                try:
                    st.session_state.listening = True
                    st.experimental_rerun()
                except:
                    st.session_state.listening = False
                    st.error("वॉइस रिकग्निशन विफल रहा। कृपया टेक्स्ट इनपुट का उपयोग करें।")
            
            if st.session_state.listening:
                try:
                    with st.spinner("आपकी आवाज़ सुन रहा हूँ..."):
                        user_choice = recognize_speech()
                        st.session_state.listening = False
                        if user_choice != "Could not understand audio":
                            st.success(f"आपने कहा: {user_choice}")
                            
                            # Store user action
                            st.session_state.user_actions.append(user_choice)
                            
                            # Generate next part of story
                            with st.spinner("कहानी का अगला भाग तैयार हो रहा है..."):
                                continuation = generate_story_continuation(st.session_state.story_so_far, user_choice)
                                
                                # Update story
                                st.session_state.story_so_far = continuation
                                st.session_state.story_stage += 1
                                
                                # Rerun to update display
                                st.experimental_rerun()
                        else:
                            st.error("आपकी आवाज़ समझ नहीं आई। कृपया फिर से प्रयास करें या टेक्स्ट इनपुट का उपयोग करें।")
                except Exception as e:
                    st.session_state.listening = False
                    st.error(f"Error: {str(e)}")
        
        with col2:
            # Text input as fallback with improved styling
            user_text = st.text_input("या यहां टाइप करें:", key="user_text_input")
            if st.button("भेजें", key="submit_text"):
                if user_text:
                    # Store user action
                    st.session_state.user_actions.append(user_text)
                    
                    # Generate next part of story
                    with st.spinner("कहानी का अगला भाग तैयार हो रहा है..."):
                        continuation = generate_story_continuation(st.session_state.story_so_far, user_text)
                        
                        # Update story
                        st.session_state.story_so_far = continuation
                        st.session_state.story_stage += 1
                        
                        # Rerun to update display
                        st.experimental_rerun()
                else:
                    st.warning("कृपया अपनी कार्रवाई दर्ज करें।")
    
    # Generate ending after 5 interaction points
    elif st.session_state.story_stage == 5:
        st.markdown('<div style="text-align: center; margin: 30px 0;">', unsafe_allow_html=True)
        if st.button("🔍 मामले को सुलझाएं", key="solve_case"):
            with st.spinner("इंस्पेक्टर शर्मा सुराग जोड़ रहे हैं..."):
                ending = generate_story_ending(st.session_state.story_so_far, st.session_state.user_actions)
                st.session_state.story_so_far += "\n\n" + ending
                st.session_state.story_stage += 1
                st.experimental_rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    # After story ends, offer restart
    elif st.session_state.story_stage > 5:
        st.markdown('<div style="text-align: center; margin: 30px 0;">', unsafe_allow_html=True)
        if st.button("🔄 नई जांच शुरू करें", key="new_investigation"):
            # Reset all state
            st.session_state.story_so_far = """You're Inspector Vikram Sharma, a senior detective with the Mumbai Crime Branch, called to investigate a murder at the luxurious Kapoor Mansion in Juhu Beach. 
The victim, tech mogul Rajesh Kapoor, was found dead in his study. Initial examination suggests poison, but there are no obvious signs of forced entry.

As you arrive, the scent of incense lingers in the air, and the household staff is preparing for the evening puja despite the tragedy. The mansion's occupants - Rajesh's wife Sunita, his daughter Priya, his business partner Vikram Malhotra, and the loyal house help Ramu kaka - all watch you with worried eyes.

The sound of Mumbai traffic fades as you step into the opulent mansion. What will you do first, Inspector Sharma?"""
            st.session_state.story_stage = 0
            st.session_state.user_actions = []
            st.session_state.evidence_collected = []
            st.experimental_rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Sidebar with additional features
    with st.sidebar:
        st.image("https://via.placeholder.com/280x100?text=KukuFM+Logo", use_column_width=True)
        
        # Display story progress
        st.subheader("जांच की प्रगति")
        progress = min(100, st.session_state.story_stage * 20)  # 20% per stage, max 100%
        st.markdown(f"""
        <div class="progress-container">
            <div class="progress-bar" style="width: {progress}%;"></div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display previous choices
        if st.session_state.user_actions:
            st.subheader("आपके निर्णय")
            for i, action in enumerate(st.session_state.user_actions):
                st.write(f"{i+1}. {action}")
        
        # Evidence collection display
        if st.session_state.evidence_collected:
            st.subheader("एकत्रित सबूत")
            for i, evidence in enumerate(st.session_state.evidence_collected):
                with st.expander(f"सबूत #{i+1}: {evidence['item']}"):
                    st.write(evidence['description'])
        
        # Explain the AI technology
        with st.expander("यह तकनीक कैसे काम करती है"):
            st.write("""
            1. **वॉइस रिकग्निशन**: आपके बोले गए विकल्पों को टेक्स्ट में बदलता है
            2. **कहानी जनरेशन**: हगिंग फेस के AI मॉडल से संदर्भ-उपयुक्त कहानी का निर्माण
            3. **टेक्स्ट-टू-स्पीच**: कहानी के टेक्स्ट को वाचन में बदलना
            4. **डायनामिक ब्रांचिंग**: हर चुनाव एक अनूठा कहानी रास्ता बनाता है
            
            कुकू FM के पूर्ण कार्यान्वयन में इसे विस्तारित किया जाएगा:
            - कई भारतीय भाषाओं का समर्थन
            - मूल वाचकों से मेल खाने के लिए वॉइस क्लोनिंग
            - उपयोगकर्ता की पसंद के आधार पर कहानियों का व्यक्तिगतकरण
            - भारतीय संस्कृति और परिवेश का समावेश
            """)

        # Help section
        with st.expander("सहायता"):
            st.markdown("""
            **वॉइस कमांड्स हेतु सुझाव:**
            - "मैं विक्रम से पूछताछ करना चाहता हूँ"
            - "मैं कमरे की तलाशी लेना चाहता हूँ"
            - "मैं चाय के कप का परीक्षण करना चाहता हूँ"
            
            स्पष्ट रूप से और धीरे-धीरे बोलें। आप कभी भी टेक्स्ट का उपयोग कर सकते हैं।
            """)
        
        # Sample stories
        with st.expander("अन्य कहानियाँ"):
            st.markdown("""
            **जल्द आ रही हैं:**
            - हॉन्टेड हवेली का रहस्य
            - मुंबई डायमंड हाइस्ट
            - द मिसिंग स्क्रॉल ऑफ़ अजंता
            - कोलकाता किलर
            """)

    # Footer
    st.markdown('<div class="footer">KukuFM Interactive Demo - Created for ML Engineer Application</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
