"""
Critic Agent - Evaluates cover letters
Uses Gemini API to provide structured feedback
"""

import requests
import json
import os
import re

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent'

def critique_cover_letter(cover_letter, job_description, user_draft):
    """
    Evaluate cover letter quality with structured scoring
    
    Args:
        cover_letter (str): The cover letter to evaluate
        job_description (str): Original job posting
        user_draft (str): User's original draft (for context)
    
    Returns:
        dict: Critique with scores, issues, and suggestions
    """
    print("🔍 Critic: Evaluating cover letter...")
    
    word_count = len(cover_letter.split())
    
    prompt = f"""You are a senior HR professional with 25+ years of experience evaluating cover letters.

Job Description:
{job_description}

User's Original Draft (for context):
{user_draft}

Cover Letter to Evaluate ({word_count} words):
{cover_letter}

Evaluate this cover letter on these 5 criteria (score 1-10 each):

1. **Job Alignment (1-10)**: Does it address specific job requirements and qualifications?
2. **Skill Highlighting (1-10)**: Does it effectively showcase relevant skills and experiences?
3. **Professional Tone (1-10)**: Is the language appropriate, confident, and professional?
4. **Specific Examples (1-10)**: Does it include concrete achievements and quantifiable results?
5. **Length & Structure (1-10)**: Is it well-structured, concise (300-400 words), and properly formatted?

You MUST respond in this EXACT JSON format (no markdown, no code blocks):
{{
  "scores": {{
    "job_alignment": 8,
    "skill_highlighting": 7,
    "professional_tone": 9,
    "specific_examples": 6,
    "length": 8
  }},
  "overall_score": 7.6,
  "issues": [
    "First specific issue found",
    "Second specific issue found",
    "Third specific issue found"
  ],
  "suggestions": [
    "First actionable suggestion",
    "Second actionable suggestion",
    "Third actionable suggestion"
  ]
}}

Be specific and actionable in your feedback. Each issue and suggestion should reference actual content.
Return ONLY valid JSON, nothing else."""

    try:
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.3,  # Lower temperature for more consistent JSON
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 1024,
            }
        }
        
        headers = {'Content-Type': 'application/json'}
        
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            headers=headers,
            data=json.dumps(payload),
            timeout=30
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
                critique = json.loads(json_match.group())
            else:
                critique = json.loads(response_text)
            
            # Validate structure
            if 'scores' not in critique or 'overall_score' not in critique:
                raise ValueError("Missing required fields")
            
            # Calculate overall score if missing or zero
            if critique['overall_score'] == 0:
                scores = critique['scores']
                overall = sum(scores.values()) / len(scores)
                critique['overall_score'] = round(overall, 1)
            
            print(f"✓ Evaluation complete: {critique['overall_score']}/10")
            
            return critique
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"⚠️ JSON parsing failed: {e}")
            print("Using fallback critique...")
            
            # Fallback critique based on word count analysis
            length_score = 10 if 300 <= word_count <= 400 else (8 if 250 <= word_count <= 450 else 6)
            
            return {
                'scores': {
                    'job_alignment': 7,
                    'skill_highlighting': 7,
                    'professional_tone': 8,
                    'specific_examples': 6,
                    'length': length_score
                },
                'overall_score': 7.2,
                'issues': [
                    'Could not parse detailed feedback from AI',
                    'Manual review recommended'
                ],
                'suggestions': [
                    'Review alignment with job requirements',
                    'Add more specific examples and quantifiable achievements'
                ]
            }
        
    except Exception as e:
        print(f"✗ Critic failed: {e}")
        # Return minimal fallback
        return {
            'scores': {
                'job_alignment': 7,
                'skill_highlighting': 7,
                'professional_tone': 7,
                'specific_examples': 7,
                'length': 7
            },
            'overall_score': 7.0,
            'issues': ['Evaluation failed - using estimated scores'],
            'suggestions': ['Please review the cover letter manually']
        }