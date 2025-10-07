from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)

# Configure CORS - will be more specific in production
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:*", "https://*.netlify.app"],
        "methods": ["POST", "GET", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# CRITICAL: Get API key from environment variable only
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY environment variable is not set!")

GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent'

def get_cover_letter_instructions():
    """Returns the system instructions for cover letter generation"""
    return """
    As an AI assistant with 25+ years of recruiting experience, you have read thousands of professional cover letters. Your task is to help users write effective cover letters using your expertise. Follow these guidelines:

    1. Analyze the job description and the user's current cover letter thoroughly.
    2. Maintain a proper business letter format with the company name from the job description after the "Dear Hiring Manager" salutation.
    3. Maintain a professional yet personable tone throughout the letter.
    4. Highlight the user's relevant skills and experiences that directly match the job requirements.
    5. Use specific examples from the user's current cover letter when applicable.
    6. Ensure the letter is concise, typically not exceeding one page (300-400 words).
    7. Structure the letter with:
       - Paragraph 1: Introduction and expression of interest
       - Paragraph 2: Technical skills alignment with job requirements
       - Paragraph 3: Soft skills and cultural fit alignment
       - Paragraph 4: Strong closing with clear call to action
    8. Customize the content to the specific job and company mentioned.
    9. Avoid clichés and generic statements like "I am writing to apply for..."
    10. Include a compelling call to action in the closing paragraph.
    11. Maintain all academic credentials and educational information from the original cover letter.
    12. Use strong, active verbs but avoid excessive adjectives.
    13. Write with clarity and professionalism - avoid overly flowery language.
    14. Do NOT include any personal contact information (email, phone, address) in the body.
    15. Do NOT repeat technical terms or stack mentions unnecessarily.
    16. Keep formatting consistent with proper spacing and structure.
    17. Start with proper salutation and end with professional closing (e.g., "Sincerely,").
    
    IMPORTANT: Return ONLY the cover letter text. Do not include any explanatory text, notes, or comments outside the letter itself.
    
    If the hiring manager's name is not provided, use "Dear Hiring Manager,".
    """

def generate_prompt(job_description, cover_letter_text):
    """Generates the complete prompt for the AI"""
    instructions = get_cover_letter_instructions()
    return f"""{instructions}

Job Description:
{job_description}

Current Cover Letter:
{cover_letter_text}

Based on the above information, generate an improved, professional cover letter following all the provided guidelines. Return only the cover letter text with no additional commentary."""

def validate_input(job_description, cover_letter_text):
    """Validates user input"""
    errors = []
    
    if not job_description or len(job_description.strip()) < 50:
        errors.append("Job description must be at least 50 characters long")
    
    if not cover_letter_text or len(cover_letter_text.strip()) < 100:
        errors.append("Cover letter must be at least 100 characters long")
    
    if len(job_description) > 10000:
        errors.append("Job description is too long (max 10,000 characters)")
    
    if len(cover_letter_text) > 10000:
        errors.append("Cover letter is too long (max 10,000 characters)")
    
    return errors

@app.route('/', methods=['GET'])
def home():
    """Health check endpoint"""
    return jsonify({
        "message": "Cover Letter Generator API is running",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }), 200

@app.route('/api/health', methods=['GET'])
def health_check():
    """Detailed health check"""
    api_key_status = "configured" if GEMINI_API_KEY else "missing"
    return jsonify({
        "status": "healthy",
        "api_key_status": api_key_status,
        "timestamp": datetime.utcnow().isoformat()
    }), 200

@app.route('/api/generate-cover-letter', methods=['POST'])
def generate_cover_letter():
    """Main endpoint to generate cover letters"""
    
    # Check if API key is configured
    if not GEMINI_API_KEY:
        return jsonify({
            "error": "API key not configured. Please contact administrator."
        }), 500
    
    # Get form data
    job_description = request.form.get('jobDescription', '').strip()
    cover_letter_text = request.form.get('coverLetter', '').strip()
    
    # Validate input
    validation_errors = validate_input(job_description, cover_letter_text)
    if validation_errors:
        return jsonify({
            "error": "Validation failed",
            "details": validation_errors
        }), 400

    try:
        # Prepare the request payload for Gemini API
        payload = {
            "contents": [{
                "parts": [{
                    "text": generate_prompt(job_description, cover_letter_text)
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 2048,
            }
        }
        
        # Set up headers
        headers = {
            'Content-Type': 'application/json'
        }
        
        # Make the API request with timeout
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            headers=headers,
            data=json.dumps(payload),
            timeout=30
        )
        
        # Check if request was successful
        if response.status_code != 200:
            error_message = f"Gemini API error: {response.status_code}"
            try:
                error_data = response.json()
                if 'error' in error_data:
                    error_message += f" - {error_data['error'].get('message', 'Unknown error')}"
            except:
                error_message += f" - {response.text[:200]}"
            
            return jsonify({"error": error_message}), 500
        
        # Parse the response
        response_data = response.json()
        
        # Extract the generated text from Gemini's response structure
        if 'candidates' in response_data and len(response_data['candidates']) > 0:
            candidate = response_data['candidates'][0]
            if 'content' in candidate and 'parts' in candidate['content']:
                generated_cover_letter = candidate['content']['parts'][0]['text']
                
                # Clean up the response (remove any markdown formatting if present)
                generated_cover_letter = generated_cover_letter.strip()
                
                return jsonify({
                    "generatedCoverLetter": generated_cover_letter,
                    "success": True
                })
        
        return jsonify({
            "error": "No response generated from Gemini API. Please try again."
        }), 500
        
    except requests.exceptions.Timeout:
        return jsonify({
            "error": "Request timed out. Please try again."
        }), 504
    except requests.exceptions.RequestException as e:
        return jsonify({
            "error": f"Network error: {str(e)}"
        }), 500
    except json.JSONDecodeError as e:
        return jsonify({
            "error": f"JSON parsing error: {str(e)}"
        }), 500
    except KeyError as e:
        return jsonify({
            "error": f"Unexpected API response format: {str(e)}"
        }), 500
    except Exception as e:
        # Log the error (in production, use proper logging)
        print(f"Unexpected error: {str(e)}")
        return jsonify({
            "error": "An unexpected error occurred. Please try again later."
        }), 500

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({
        "error": "Endpoint not found"
    }), 404

@app.errorhandler(405)
def method_not_allowed(e):
    """Handle 405 errors"""
    return jsonify({
        "error": "Method not allowed"
    }), 405

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    return jsonify({
        "error": "Internal server error"
    }), 500

if __name__ == '__main__':
    # Use PORT environment variable for deployment platforms
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)