"""
Check the raw text from Flask API response
"""

import requests
import json

BASE_URL = "http://localhost:5000"

data = {
    'jobDescription': """
    Software Engineer - AI/ML Team
    Requirements:
    - 3+ years Python experience
    - Machine learning background
    """,
    'coverLetter': """
    Dear Hiring Manager,
    
    I am interested in this position. I have experience with Python and ML.
    
    Sincerely,
    John Smith
    john.smith@email.com
    (555) 123-4567
    """
}

print("Sending request to Flask API...")
response = requests.post(f"{BASE_URL}/api/generate-cover-letter", data=data)

if response.status_code == 200:
    result = response.json()
    
    cover_letter = result['generatedCoverLetter']
    
    print("\n" + "="*70)
    print("RAW COVER LETTER TEXT (last 200 characters):")
    print("="*70)
    print(cover_letter[-200:])
    
    print("\n" + "="*70)
    print("CHECKING FOR NAME:")
    print("="*70)
    
    # Check various patterns
    patterns = [
        "Sincerely,\nJohn Smith",
        "Sincerely,\n\nJohn Smith",
        "Sincerely,\nJohn",
        "Sincerely,",
    ]
    
    for pattern in patterns:
        if pattern in cover_letter:
            print(f"✓ Found: '{pattern}'")
        else:
            print(f"✗ Not found: '{pattern}'")
    
    # Show what comes after "Sincerely,"
    if "Sincerely," in cover_letter:
        parts = cover_letter.split("Sincerely,")
        after = parts[1] if len(parts) > 1 else "[NOTHING]"
        print(f"\nAfter 'Sincerely,': {repr(after[:50])}")
    
    print("\n" + "="*70)
    print("CONTACT INFO FROM API:")
    print("="*70)
    print(f"Name: {result['contact_info'].get('name')}")
    print(f"Email: {result['contact_info'].get('email')}")
    print(f"Phone: {result['contact_info'].get('phone')}")
    
else:
    print(f"Error: {response.status_code}")