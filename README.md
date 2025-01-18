# OCR-Based Handwritten Answer Evaluation System

## Overview
This project is a web-based application that extracts handwritten text from uploaded images using Optical Character Recognition (OCR) and evaluates the answers against a predefined marking scheme. The evaluation process involves multiple advanced AI models, ensuring accurate text recognition and meaningful feedback for users.

### Key Features
1. **OCR for Handwritten Text Extraction**:
   - Uses the Google Gemini-1.5-Flash model for high-accuracy OCR.
   - Handles diverse handwriting styles and noisy input images.

2. **Evaluation Pipeline**:
   - Integrates with an external API that utilizes Google Text-004 embedding model.
   - Embeds marking schemes and evaluates user answers using AI models.

3. **User-Friendly Interface**:
   - Allows users to upload handwritten answer images.
   - Includes a progress bar for real-time feedback during processing.
   - Implements a modern dark-themed design for better readability.

4. **Customizable Inputs**:
   - Accepts user input for maximum marks (`max_marks`) to adjust the evaluation dynamically.

---

## Project Structure

```
project/
├── app.py                 # Main Flask application.
├── static/
│   ├── css/
│   │   └── style.css      # Frontend styling.
│   └── js/
│       └── script.js      # Client-side functionality.
├── templates/
│   └── index.html         # Main HTML page.
├── output/
│   └── output_file.json   # Stores evaluation results.
├── README.md              # Project documentation (this file).
└── requirements.txt       # Python dependencies.
```

---

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment (optional but recommended)

### Installation
1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-repository/ocr-evaluation-system.git
   cd ocr-evaluation-system
   ```

2. **Set up a virtual environment** (optional):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure upload folder**:
   Ensure that an `UPLOAD_FOLDER` is defined in `app.py` and the folder exists:
   ```python
   app.config['UPLOAD_FOLDER'] = './uploads'
   ```
   Create the folder if it does not exist:
   ```bash
   mkdir uploads
   ```

5. **Run the application**:
   ```bash
   python app.py
   ```
   The application will be available at `http://127.0.0.1:5000/`.

---

## Usage

1. Open the application in your web browser.
2. Upload a handwritten answer image.
3. Enter the maximum marks (`max_marks`) for the question.
4. Submit the form and wait for the evaluation.
5. View the extracted text, feedback, and score on the results page.

---

## API Details

### Upload Endpoint
- **URL**: `/upload`
- **Method**: `POST`
- **Parameters**:
  - `answer_image`: Handwritten answer image (required).
  - `max_marks`: Maximum marks for the question (required).
- **Response**:
  - `Feedback`: Evaluation feedback for the answer.
  - `Score`: Marks obtained.4
