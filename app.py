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

@app.route("/upload", methods=['POST'])
def upload_image():
    if 'answer_image' not in request.files:
        return jsonify({"error": "Missing files"}), 400

    file_paths = {}

    for file_key, file in request.files.items():
        if file is None or file.filename == '':
            return jsonify({'error': f"No file selected for {file_key}"}), 420

        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        file_paths[file_key] = file_path

    answer_text = extract_text(file_paths['answer_image'])
    
    new_entry = {"user_answer": answer_text}
    
    print(f"Payload\n{new_entry}")
    
    try:
        url = 'http://192.168.1.35:9000/evaluate'
        evaluation_response = requests.post(
            url,
            json=new_entry,
            headers={'Content-Type': 'application/json'}
        )
        
        output_dir = './output'
        os.makedirs(output_dir, exist_ok=True)
        output_file_path = os.path.join(output_dir, "output_file.json")

        if os.path.exists(output_file_path):
            try:
                with open(output_file_path, 'r') as json_file:
                    existing_data = json.load(json_file)
                    if not isinstance(existing_data, list):
                        existing_data = [existing_data]
            except json.JSONDecodeError:
                print("Error reading existing JSON file. Creating a new one")
                existing_data = []
        else:
            existing_data = []

        existing_data.append(new_entry)

        with open(output_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(existing_data, json_file, ensure_ascii=False, indent=4)

        if evaluation_response.status_code != 200:
            return jsonify({'error': 'Failed to send request to external API', 'details': evaluation_response.text}), 500

        feedback = evaluation_response.json().get("Feedback")
        score = evaluation_response.json().get("Marks")
        print(f"\nFeedback: {feedback}\nScore: {score}\n")

        return jsonify({
            "Feedback": feedback,
            "Score": score,
            "ExtractedText": answer_text
        })
    
    except Exception as e:
        print(f"Unexpected error occurred: {str(e)}")
        return jsonify({'error': f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)