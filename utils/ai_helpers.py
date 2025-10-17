import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configure Gemini API
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Use current recommended model names/aliases
# The 'gemini-2.5-flash' model is multimodal, handling both vision and text.
VISION_MODEL = "gemini-2.5-flash"
TEXT_MODEL = "gemini-2.5-flash"


def analyze_image(uploaded_file):
    """Analyze an image using the Gemini Vision model."""
    try:
        image = Image.open(uploaded_file)
        # Use a model that supports vision
        model = genai.GenerativeModel(VISION_MODEL)

        prompt = (
            "Describe clearly and medically what visible injury or condition appears in this image."
        )

        # Pass both the text prompt and the image object
        response = model.generate_content([prompt, image])
        if hasattr(response, "text") and response.text:
            return response.text.strip()
        return "No description detected."

    except Exception as e:
        # Check if the error is related to a missing model and provide a helpful tip
        if "404" in str(e) and "models" in str(e):
             st.error("Error: Model not found. Please ensure you are using the latest 'google-genai' library and supported model names.")
        else:
             st.error(f"Error analyzing image: {e}")
        return "Unable to analyze the image."


def generate_first_aid_steps(injury_description):
    """Generate short, step-by-step first aid instructions."""
    try:
        # Use the same model for text generation
        model = genai.GenerativeModel(TEXT_MODEL)
        prompt = (
            f"Provide concise, safe, step-by-step first aid instructions for: {injury_description}."
        )

        response = model.generate_content(prompt)
        if hasattr(response, "text") and response.text:
            return response.text.strip()
        return "No first aid steps generated."

    except Exception as e:
        st.error(f"Error generating first aid steps: {e}")
        return "Unable to generate first aid instructions."