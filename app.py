import json
import requests
from flask import Flask, render_template, jsonify, request
import os
import PIL.Image
import google.generativeai as genai
from dotenv import load_dotenv
from typing import cast

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# Configure the Google Generative AI API
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("API key not found. Set the 'GOOGLE_API_KEY' environment variable.")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


def extract_text(image):
    # Process the image and generate text
    prompt = "Convert the handwriting to text - make correction based on the context of extracted text (only give extracted text in respone nothing else)"

    # Call the Generative AI model
    try:
        response = model.generate_content([prompt, image])
        text_output = response.text
    except Exception as e:
        return jsonify({'error': f"AI processing failed: {str(e)}"}), 500

    return text_output


@app.route('/')
def index():
    return render_template('index.html')


@app.route("/upload", methods = ['POST'])
def upload_image():
    if 'question_image' not in request.files or 'answer_image' not in request.files:
        return jsonify({"error": "Missing files"}), 400

    # Save the uploaded file
    file_q = request.files['question_image']
    file_a = request.files['answer_image']
    if file_q.filename == '' or file_q.filename == '':
        return jsonify({'error': 'No file is selected'}), 400

    file_path_question = os.path.join(app.config['UPLOAD_FOLDER'], file_q.filename)
    file_path_answer = os.path.join(app.config['UPLOAD_FOLDER'], file_a.filename)
    file_q.save(file_path_question)
    file_a.save(file_path_answer)

    # Validate the image
    try:
        image_q = PIL.Image.open(file_path_question)
        image_a = PIL.Image.open(file_path_answer)
        image_q.verify()
        image_a.verify()
    except Exception:
        return jsonify({'error': 'Uploaded file is not a valid image'}), 400

    question_text = extract_text(image_q)
    answer_text = extract_text(image_a)

    # Get the evaluation parameter
    question_type = request.form.get('question_type')
    class_level = request.form.get('class')
    board = request.form.get("board")

    # Define word limit
    word_count_range = {
        "1 Marker": "15-25 words",
        "3 Marker": "30-80 words",
        "4 Marker": "80-120 words",
        "6 Marker": "150-200 words",
        "10 Marker": "200-300 words",
    }

    # Get the word count
    if question_type in word_count_range:
        word_count = word_count_range[question_type]
    else:
        word_count = "80-120 words"

    new_entry = {
        "Class": class_level,
        "Board": board,
        "word_count": word_count,
        "questions":[
            {"ID": "S1_Q1", "Text": question_text}
        ],
        "answers":[
            {"ID":"S1_Q1", "Text": answer_text}
        ]
    }

    # Debug Print
    print(f"Payload\n{new_entry}")

    try:
        # Send rewuest
        url = 'http://192.168.1.28:9000/evaluate'
        evaluation_response = requests.post(
            url,
            json=new_entry,  # Use 'json' for automatic JSON serialization
            headers={'Content-Type': 'application/json'}  # Correct header format
        )

        # Outpur dir exist
        output_dir = './output'
        os.makedirs(output_dir, exist_ok = True)

        # Save the respone in  JSON format
        output_file_path = os.path.join(output_dir, "output_file.json")

        # Load existing data if the file exists
        if os.path.exists(output_file_path):
            try:
                with open(output_file_path, 'r') as json_file:
                    existing_data = json.load(json_file)
                    if not isinstance(existing_data, list):
                        existing_data = [existing_data]
            except json.JSONDecodeError:
                print("Error reading existing JSON file. Creating a new one")
                existing_data  =[]

        else:
            existing_data = []

        # Append the new entry
        existing_data.append(new_entry)

        # Save and Update the JSON file
        with open(output_file_path, 'w', encoding = 'utf-8') as json_file:
            json.dump(existing_data, json_file, ensure_ascii=False, indent = 4)

        if evaluation_response.status_code != 200:
            return jsonify({'error':'Failed to send request to external API',
                            'details':evaluation_response.text}), 500

        # Include the external API response in the final output
        evaluation_result = evaluation_response.json()
        evaluations = evaluation_result.get("evaluations", [])
        for evaluation in evaluations:
            feedback = evaluation["Evaluation"].get("Feedback")
            score = evaluation["Evaluation"].get("Score")
            print(f"\nFeedback: {feedback}\nScore: {score}\n")

        return jsonify({"Feedback": feedback, "Score": score})

    except Exception as e:
        return jsonify({'error': f"An unexpected error occurred: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host = "0.0.0.0", port = 9000, debug=True)
