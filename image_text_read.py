import PIL.Image
import os
import google.generativeai as genai
import json
from dotenv import load_dotenv
load_dotenv()
# Config the Google AI API
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("API key not add to env variable")
genai.configure(api_key = API_KEY)


def main():
    image_path = input("Image Path: ").strip()

    try:
        sample_file = PIL.Image.open(image_path)
    except Exception as e:
        print(f"Error opening image file: {e}")
        return

    # Choose a Gemini Model
    model = genai.GenerativeModel(model_name = 'gemini-1.5-flash')

    # Prompt
    prompt = "Extract text for the handwriting (only provide text of the image in the response nothing else"

    # Get the Text
    try:
        response = model.generate_content([prompt, sample_file])

        # Prepare the output data
        new_entry = {
            "ID": f"Image_ID_{image_path}",
            "Text": response.text
        }

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
        with open(output_file_path, 'w') as json_file:
            json.dump(existing_data, json_file, indent = 4)

        # Display the text
        print(response.text)

    except Exception as e:
        print(f"Error is extracting text: {e}")


if __name__ == "__main__":
    main()