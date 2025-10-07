from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import os

app = Flask(__name__)
CORS(app)  # This enables CORS for all routes

# Get API key from environment variable for security
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyAffCsdRMUUIoHCs1oB2dSSJDKR_OkYWRU')
GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent'

def get_cover_letter_instructions():
    return """
    As an AI assistant you have a 25+ years of experience of being a recruiter and you have read the most professional cover letters. Your task is to help users write effective cover letters using your experience. Follow these guidelines:

    1. Analyze the job description and the user's current cover letter.
    2. Maintain a letter format and also add the company name from the job description after the Hiring manager salutation part
    2. Maintain a professional tone throughout the letter.
    3. Highlight the user's relevant skills and experiences that match the job requirements.
    4. Use specific examples from the user's current cover letter, if applicable.
    5. Ensure the letter is concise, typically not exceeding one page.
    6. Structure the letter with a clear introduction, body, and conclusion.
    7. Customize the content to the specific job and company.
    8. Avoid clichés and generic statements.
    9. Include a call to action in the closing paragraph.
    10. Try to keep the letter down to 4 paragraphs. The first paragraph would be introduction and interest. The second would be technical alignment, the third would be soft skill alignment and the last would be closing paragraphs.
    11. Proofread for grammar and spelling errors.
    12. Maintain the academic information from the previously provided cover letter.
    13. Do not use a lot of adjectives. Try not to make it sound too wordy and write the Cover letters with a professional tone
    14. Just have the cover letter in the response. Do not include any other text.
    15. Do not add any personal information such as email address of Phone number in the body of the cover letter.
    16. Do not repeat the tech stack in the cover letter if it is already mentioned.
    17. Keep the formatting consistent, including font size, style, and spacing.

    Format the cover letter with appropriate salutation and closing. If the hiring manager's name is not provided, use "Dear Hiring Manager,".
    """

def generate_prompt(job_description, cover_letter_text):
    instructions = get_cover_letter_instructions()
    return f"""
    {instructions}

    Job Description:
    {job_description}

    Current Cover Letter:
    {cover_letter_text}

    Based on the above information, please generate an improved cover letter following the provided guidelines.
    """

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Cover Letter Generator API is running"}), 200

@app.route('/api/generate-cover-letter', methods=['POST'])
def generate_cover_letter():
    job_description = request.form.get('jobDescription')
    cover_letter_text = request.form.get('coverLetter')
    
    if not job_description or not cover_letter_text:
        return jsonify({"error": "Both job description and cover letter are required"}), 400

    try:
        # Prepare the request payload for Gemini API
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": generate_prompt(job_description, cover_letter_text)
                        }
                    ]
                }
            ]
        }
        
        # Set up headers
        headers = {
            'Content-Type': 'application/json',
            'X-goog-api-key': GEMINI_API_KEY
        }
        
        # Make the API request
        response = requests.post(
            GEMINI_API_URL,
            headers=headers,
            data=json.dumps(payload)
        )
        
        # Check if request was successful
        if response.status_code != 200:
            return jsonify({"error": f"Gemini API error: {response.status_code} - {response.text}"}), 500
        
        # Parse the response
        response_data = response.json()
        
        # Extract the generated text from Gemini's response structure
        if 'candidates' in response_data and len(response_data['candidates']) > 0:
            generated_cover_letter = response_data['candidates'][0]['content']['parts'][0]['text']
        else:
            return jsonify({"error": "No response generated from Gemini API"}), 500
        
        return jsonify({"generatedCoverLetter": generated_cover_letter})
        
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Network error: {str(e)}"}), 500
    except json.JSONDecodeError as e:
        return jsonify({"error": f"JSON parsing error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

if __name__ == '__main__':
    # Use PORT environment variable for deployment platforms
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)