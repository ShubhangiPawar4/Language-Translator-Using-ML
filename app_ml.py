import streamlit as st
from gtts import gTTS
from io import BytesIO
from deep_translator import GoogleTranslator
import speech_recognition as sr

# ==============================
# 🌈 Custom Animated UI Styling
# ==============================
st.set_page_config(page_title="Multi-Language Translator", page_icon="🎙️", layout="centered")

st.markdown("""
<style>
/* 🌈 Background Gradient */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #a5b4fc 0%, #c7d2fe 40%, #e0f2fe 100%);
    background-attachment: fixed;
    color: #1e293b;
}

/* ✨ Glass Header */
[data-testid="stHeader"] {
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(10px);
}

/* 💎 Sidebar */
[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.6);
    backdrop-filter: blur(15px);
}

/* 🌈 Animated Gradient Title */
h1 {
    text-align: center;
    font-size: 2.8rem !important;
    font-weight: 800 !important;
    background: linear-gradient(90deg, #4f46e5, #8b5cf6, #ec4899, #f59e0b);
    background-size: 400%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: gradientShift 6s ease infinite;
}
@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* ✨ Animated Select Boxes */
.stSelectbox {
    background: rgba(255, 255, 255, 0.8) !important;
    border-radius: 12px !important;
    border: 2px solid transparent !important;
    box-shadow: 0 0 15px rgba(99, 102, 241, 0.3);
    transition: all 0.3s ease;
    cursor: pointer !important;
}
.stSelectbox:hover {
    box-shadow: 0 0 20px rgba(139, 92, 246, 0.6);
    transform: scale(1.02);
    border: 2px solid #8b5cf6 !important;
}

/* 🩵 Text Area */
textarea {
    background: rgba(255, 255, 255, 0.9) !important;
    border-radius: 15px !important;
    border: 2px solid transparent !important;
    box-shadow: 0 0 15px rgba(99, 102, 241, 0.3);
    transition: all 0.4s ease;
    font-size: 1rem !important;
}
textarea:focus {
    box-shadow: 0 0 25px rgba(139, 92, 246, 0.6);
    border: 2px solid #6366f1 !important;
    transform: scale(1.01);
}

/* 🪄 Glowing Buttons */
div.stButton > button {
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    color: white !important;
    font-weight: 600;
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(99,102,241,0.4);
    transition: all 0.3s ease;
}
div.stButton > button:hover {
    box-shadow: 0 6px 25px rgba(139,92,246,0.7);
    transform: scale(1.05);
}

/* 🎧 Info/Success Messages */
.stSuccess, .stInfo, .stWarning {
    border-radius: 10px !important;
    backdrop-filter: blur(6px);
}

/* ✨ File uploader */
.stFileUploader {
    background: rgba(255, 255, 255, 0.8) !important;
    border-radius: 15px !important;
    padding: 10px !important;
    box-shadow: 0 0 10px rgba(99,102,241,0.3);
}
</style>
""", unsafe_allow_html=True)

# ==============================
# 🎙️ Streamlit App Content
# ==============================
st.title("🎙️ Multi Language Translator")
st.markdown("Convert your **speech or text** into natural-sounding audio — in any language with real-time translation!")

# ==============================
# 🌍 Language Options
# ==============================
LANGUAGES = {
    'English': 'en', 'Hindi': 'hi', 'Marathi': 'mr', 'Gujarati': 'gu', 'Tamil': 'ta',
    'Telugu': 'te', 'Bengali': 'bn', 'Punjabi': 'pa', 'Urdu': 'ur', 'Kannada': 'kn',
    'Malayalam': 'ml', 'French': 'fr', 'Spanish': 'es', 'German': 'de', 'Italian': 'it',
    'Japanese': 'ja', 'Korean': 'ko', 'Chinese (Simplified)': 'zh-cn'
}

src_lang_name = st.selectbox("🌐 Source Language (Text Language)", options=["Auto Detect"] + list(LANGUAGES.keys()))
target_lang_name = st.selectbox("🎯 Target Language (For Speech & Translation)", options=list(LANGUAGES.keys()))

# ==============================
# 🎤 Voice Input + Text Area
# ==============================
if "recognized_text" not in st.session_state:
    st.session_state["recognized_text"] = ""

text_input = st.text_area("✍️ Enter or Speak text:", value=st.session_state["recognized_text"], height=150)

if st.button("🎤 Speak Now"):
    try:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("🎙️ Listening... please speak clearly.")
            audio = recognizer.listen(source, timeout=5)
            recognized_text = recognizer.recognize_google(audio)
            st.success("✅ Speech recognized successfully!")

            # Save recognized text into session state
            st.session_state["recognized_text"] = recognized_text
            st.rerun()  # Refresh to show in text area

    except sr.UnknownValueError:
        st.error("⚠️ Could not understand audio. Try again.")
    except sr.RequestError:
        st.error("⚠️ Speech recognition service unavailable.")
    except Exception as e:
        st.error(f"Error: {e}")

uploaded_file = st.file_uploader("📁 Or upload a text file (.txt)", type=["txt"])
if uploaded_file is not None:
    try:
        text_input = uploaded_file.read().decode("utf-8")
        st.session_state["recognized_text"] = text_input
    except Exception:
        st.error("❌ Couldn't read uploaded file. Make sure it's UTF-8 encoded.")

slow = st.checkbox("🐢 Speak slowly (slow speed)")

# ==============================
# 🎧 Translation + Speech Output
# ==============================
if "history" not in st.session_state:
    st.session_state["history"] = []

if st.button("🎧 Translate & Speak"):
    if not text_input.strip():
        st.warning("⚠️ Please enter some text or speak first.")
    else:
        try:
            src_code = "auto" if src_lang_name == "Auto Detect" else LANGUAGES[src_lang_name]
            tgt_code = LANGUAGES[target_lang_name]

            translated_text = text_input
            if src_code != tgt_code:
                translated_text = GoogleTranslator(source=src_code, target=tgt_code).translate(text_input)

            # Display results
            st.success(f"✅ Translated text ({target_lang_name}):")
            st.write(translated_text)

            # Text-to-speech
            tts = gTTS(text=translated_text, lang=tgt_code, slow=slow)
            audio_buffer = BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)

            st.audio(audio_buffer.getvalue(), format="audio/mp3")
            st.download_button(
                label="⬇️ Download Audio (MP3)",
                data=audio_buffer.getvalue(),
                file_name="translated_speech.mp3",
                mime="audio/mp3"
            )

            # Save translation history
            st.session_state["history"].append({
                "source": text_input,
                "translated": translated_text,
                "lang": target_lang_name
            })

        except Exception as e:
            st.error(f"⚠️ Error: {e}")

# ==============================
# 🧠 Translation History
# ==============================
if st.session_state["history"]:
    st.subheader("🗂️ Translation History")
    for i, record in enumerate(reversed(st.session_state["history"]), 1):
        with st.expander(f"🗣️ {i}. {record['lang']} Translation"):
            st.write("**Original:**", record["source"])
            st.write("**Translated:**", record["translated"])
