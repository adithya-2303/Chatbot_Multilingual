import google.generativeai as genai
import gradio as gr
import speech_recognition as sr  # Voice recognition
from deep_translator import GoogleTranslator  # Translation support
import re  # Regular expressions for text cleanup
import os

# 🔹 Configure Google Gemini API
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    raise RuntimeError("GOOGLE_API_KEY environment variable is not set. Please set it before running the app.")
genai.configure(api_key=api_key)

# 🔹 Model Name (from available models for this API key)
MODEL_NAME = "gemini-2.5-flash"

# 🔹 Function to clean unnecessary Markdown formatting
def clean_markdown(text):
    """Removes unnecessary Markdown symbols like **bold**, *italic*, and ```code blocks```."""
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)  # Remove **bold**
    text = re.sub(r"\*(.*?)\*", r"\1", text)      # Remove *italic*
    text = re.sub(r"```(.*?)```", r"\1", text, flags=re.DOTALL)  # Remove ```code```
    return text.strip()

# 🔹 Speech to Text Function
def speech_to_text(audio):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            return text
    except Exception as e:
        return ""  # 🔥 FIX: Returning empty string instead of error message

# 🔹 Chat Function with AI (with Language Translation)
def chat_with_ai(user_input, language):
    try:
        # Translate input to English before sending it to the AI
        if language != "English":
            user_input = GoogleTranslator(source=language.lower(), target="english").translate(user_input)
        
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(user_input)
        
        if hasattr(response, "text"):
            ai_response = response.text  # AI-generated response
            
            # 🔥 Clean Markdown formatting (Fix for ** symbols)
            ai_response = clean_markdown(ai_response)

            # Translate AI response back to selected language
            if language != "English":
                ai_response = GoogleTranslator(source="english", target=language.lower()).translate(ai_response)
            
            return ai_response
        else:
            return "⚠ Error: AI response not found!"
    except Exception as e:
        return f"⚠ Error: {str(e)}"

# 🔹 List of Indian Languages (Shortened)
INDIAN_LANGUAGES = [
    "English", "Hindi", "Marathi", "Gujarati", "Bengali", "Tamil", "Telugu", "Kannada",
    "Malayalam", "Punjabi", "Assamese", "Urdu", "Sanskrit", "Konkani", "Maithili"
]

# 🔹 Gradio UI
with gr.Blocks(theme="soft", title="ChaturChat") as chat_ui:
    gr.Markdown(
        """
        <h1 style="text-align: center; color: #FFA500;">🤖 ChatBot - Your AI Chat Buddy! 🗣️</h1>
        <p style="text-align: center; font-size: 18px;">Chat in <b>multiple Indian languages</b> and have fun with AI!</p>
        """,
        elem_id="title"
    )

    with gr.Row():
        with gr.Column(scale=3):
            voice_input = gr.Audio(sources=["microphone"], type="filepath", label="🎙 Speak Here")  # Fixed
            user_input = gr.Textbox(
                label="🔹 Your Message", 
                placeholder="Type or use voice input...",
                lines=2
            )
            language = gr.Dropdown(
                choices=INDIAN_LANGUAGES, 
                label="🌐 Select Language", 
                value="English"
            )
            btn_submit = gr.Button("🚀 Send", variant="primary")
            btn_clear = gr.Button("🗑 Clear")

        with gr.Column(scale=4):
            output = gr.Textbox(
                label="💬 AI Response", 
                placeholder="AI's response will appear here...",
                interactive=False,
                lines=5
            )

    # 🔹 Voice Input Processing
    voice_input.change(speech_to_text, inputs=voice_input, outputs=user_input)  # Converts voice to text

    # 🔹 Button Actions
    btn_submit.click(chat_with_ai, inputs=[user_input, language], outputs=output)
    
    # 🔥 FIXED: Now clears voice input & error message in text input
    btn_clear.click(lambda: ("", "", None), inputs=[], outputs=[user_input, output, voice_input])  

# 🔹 Footer
   # gr.Markdown(
       # """
       # <hr>
       # <p style="text-align: center; font-size: 14px;">🚀 Made by AI Enthusiasts | Powered by Google Gemini</p>
      #  """
    #)

# 🔹 Run Chatbot
chat_ui.launch()