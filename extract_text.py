import os
from dotenv import load_dotenv
import PIL.Image
from flask import jsonify
import google.generativeai as genai


# Configure API and load the model
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("API key not found. Set the GOOGLE_API_KEY in env variable")
genai.configure(api_key = API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


def extract_text(file_path):
    try:
        image = PIL.Image.open(file_path)
        image.verify()
    except Exception:
        return jsonify({'error': 'Uploaded file is not a valid iamge'})

    # Define the prompt
    prompt = "Convert the handwriting to text - if requried make correction based on the context of extracted text (only give extracted text in respone nothing else)"

    # Call the Generative Model
    try:
        response = model.generate_content([prompt, image])
        text_output = response.text
    except Exception as e:
        return jsonify({'error': f"AI processing failed: {str(e)}"}), 400

    return text_output
