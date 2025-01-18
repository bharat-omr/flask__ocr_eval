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
    if 'answer_image' not in request.files:
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
    answer_text = extract_text(file_paths['answer_image'])
    max_marks = request.form['max_marks']

    new_entry = {
        "user_answer": answer_text,
        "max_marks": max_marks
    }

    # Debug Print
    print(f"Payload\n{new_entry}")

    try:
        # Send rewuest
        url = 'http://192.168.1.24:9000/evaluate'
        evaluation_response = requests.post(
            url,
            json = new_entry,
            headers = {'Content-Type': 'application/json'}
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
            return jsonify({'error':'Failed to send request to external API', 'details':evaluation_response.text}), 500

        # Include the external API response in the final output
        feedback = evaluation_response.json().get("Feedback")
        score = evaluation_response.json().get("Marks")
        print(f"\nFeedback: {feedback}\nScore: {score}\n")

        # Return the extracated text and Evaluation Resposne
        return jsonify({
            "Feedback": feedback,
            "Score": score,
            "ExtractedText": answer_text
        })

    except Exception as e:
        print(f"unexpection has occurred {str(e)}")
        return jsonify({'error': f"An unexpected error occurred: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host = "0.0.0.0", port = 9000, debug=True)
