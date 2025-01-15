import json
import requests
from flask import Flask, render_template, jsonify, request
import os
from extract_text import extract_text

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route("/upload", methods = ['POST'])
def upload_image():
    if 'question_image' not in request.files or 'answer_image' not in request.files:
        return jsonify({"error": "Missing files"}), 400

    # Save the uploaded file
    file_paths = {}

    #Check for empty filename
    for file_key, file in request.files.items():
        if file is None or file.filename == '':
            return jsonify({'errpr': f"No fiel selected for {file_key}"}), 420

        # Save the file and store the path
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        file_paths[file_key] = file_path

    # Extract text from the saved files
    question_text = extract_text(file_paths['question_image'])
    answer_text = extract_text(file_paths['answer_image'])

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
