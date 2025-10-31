"""
Contact Information Extractor
Extract candidate info from cover letter draft using Gemini API
"""

import os
import requests
import json
import re

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent'


def extract_contact_info(cover_letter_text):
    """
    Extract contact information from cover letter text using AI
    
    Args:
        cover_letter_text (str): The user's cover letter draft
    
    Returns:
        dict: Contact info with name, email, phone, address
    """
    print("👤 Extracting contact information...")
    
    prompt = f"""Extract the candidate's contact information from this cover letter.

Cover Letter:
{cover_letter_text}

Extract these fields:
1. Full name (usually after "Sincerely," or at the top)
2. Email address
3. Phone number
4. Address or location (if mentioned)

Return ONLY a JSON object in this exact format (no markdown, no code blocks):
{{
  "name": "Full Name",
  "email": "email@example.com",
  "phone": "123-456-7890",
  "address": "City, State"
}}

If any field is not found, use "Not Found" as the value.
Return ONLY valid JSON, nothing else."""

    try:
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.1,  # Low temperature for consistent extraction
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 512,
            }
        }
        
        headers = {'Content-Type': 'application/json'}
        
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            headers=headers,
            data=json.dumps(payload),
            timeout=15
        )
        
        if response.status_code != 200:
            raise Exception(f"API Error: {response.status_code}")
        
        response_data = response.json()
        response_text = response_data['candidates'][0]['content']['parts'][0]['text'].strip()
        
        # Parse JSON from response
        try:
            # Remove markdown code blocks if present
            response_text = re.sub(r'```json\s*|\s*```', '', response_text)
            response_text = response_text.strip()
            
            # Try to extract JSON
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                contact_info = json.loads(json_match.group())
            else:
                contact_info = json.loads(response_text)
            
            # Ensure all required fields exist
            required_fields = ['name', 'email', 'phone', 'address']
            for field in required_fields:
                if field not in contact_info:
                    contact_info[field] = "Not Found"
            
            # Clean up "Not Found" variations
            for key, value in contact_info.items():
                if not value or value.lower() in ['not found', 'n/a', 'none', '']:
                    contact_info[key] = "Not Found"
            
            print(f"✓ Extracted contact info:")
            print(f"   Name: {contact_info['name']}")
            print(f"   Email: {contact_info['email']}")
            
            return contact_info
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"⚠️ JSON parsing failed: {e}")
            print("Using fallback extraction...")
            return extract_contact_info_fallback(cover_letter_text)
        
    except Exception as e:
        print(f"⚠️ AI extraction failed: {e}")
        print("Using fallback extraction...")
        return extract_contact_info_fallback(cover_letter_text)


def extract_contact_info_fallback(text):
    """
    Fallback method using regex patterns when AI extraction fails
    
    Args:
        text (str): Cover letter text
    
    Returns:
        dict: Extracted contact info
    """
    print("🔍 Using regex fallback extraction...")
    
    contact_info = {
        'name': 'Not Found',
        'email': 'Not Found',
        'phone': 'Not Found',
        'address': 'Not Found'
    }
    
    # Extract email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_match = re.search(email_pattern, text)
    if email_match:
        contact_info['email'] = email_match.group()
    
    # Extract phone (various formats)
    phone_patterns = [
        r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # (123) 456-7890 or 123-456-7890
        r'\+\d{1,3}[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}'  # +1-123-456-7890
    ]
    for pattern in phone_patterns:
        phone_match = re.search(pattern, text)
        if phone_match:
            contact_info['phone'] = phone_match.group()
            break
    
    # Extract name (look after "Sincerely," or similar)
    closing_patterns = [
        r'Sincerely,?\s*\n\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
        r'Best regards,?\s*\n\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
        r'Regards,?\s*\n\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)'
    ]
    for pattern in closing_patterns:
        name_match = re.search(pattern, text, re.IGNORECASE)
        if name_match:
            contact_info['name'] = name_match.group(1).strip()
            break
    
    print(f"✓ Fallback extraction complete:")
    print(f"   Name: {contact_info['name']}")
    print(f"   Email: {contact_info['email']}")
    
    return contact_info


def format_contact_header(contact_info):
    """
    Format contact info into a professional header
    
    Args:
        contact_info (dict): Contact information
    
    Returns:
        str: Formatted header text
    """
    lines = []
    
    if contact_info['name'] != 'Not Found':
        lines.append(contact_info['name'])
    
    contact_line = []
    if contact_info['email'] != 'Not Found':
        contact_line.append(contact_info['email'])
    if contact_info['phone'] != 'Not Found':
        contact_line.append(contact_info['phone'])
    
    if contact_line:
        lines.append(' | '.join(contact_line))
    
    if contact_info['address'] != 'Not Found':
        lines.append(contact_info['address'])
    
    return '\n'.join(lines)


# Test the extractor
if __name__ == "__main__":
    test_letter = """
    Dear Hiring Manager,
    
    I am very interested in this position. I have 5 years of experience in software engineering.
    
    Sincerely,
    John Smith
    john.smith@email.com
    (555) 123-4567
    """
    
    result = extract_contact_info(test_letter)
    print("\nExtracted:")
    print(json.dumps(result, indent=2))
    
    print("\nFormatted Header:")
    print(format_contact_header(result))