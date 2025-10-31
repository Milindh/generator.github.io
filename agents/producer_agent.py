"""
Producer Agent - Generates cover letters
Uses Gemini API to create initial drafts
"""

import requests
import json
import os

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent'

def generate_cover_letter(job_description, user_draft, candidate_name=None):
    """
    Generate initial cover letter based on job description and user's draft
    
    Args:
        job_description (str): The job posting text
        user_draft (str): User's current cover letter
        candidate_name (str, optional): Candidate's name for signature
    
    Returns:
        str: Generated cover letter
    """
    print("✍️ Producer: Generating cover letter...")
    
    # Use provided name or placeholder
    signature_name = candidate_name if candidate_name and candidate_name != "Not Found" else "[Your Name]"
    
    prompt = f"""You are an expert cover letter writer with 25+ years of recruiting experience.

Job Description:
{job_description}

User's Current Cover Letter:
{user_draft}

Candidate Name: {signature_name}

IMPORTANT: Carefully read the job description and extract the company name. Use this company name throughout the cover letter instead of generic terms or placeholders.

Write an improved, professional cover letter (300-400 words) that:
1. Addresses specific job requirements from the description
2. Highlights relevant skills and experiences from the user's draft
3. Uses professional yet personable tone
4. Includes concrete examples and achievements
5. Shows enthusiasm for the role
6. Uses the actual company name from the job description (never use [Company Name] or generic terms)

STRUCTURE - YOU MUST FOLLOW THIS EXACT FORMAT:
Dear Hiring Manager,

[Write paragraph 1 here: Opening - Express interest in the specific role at [ACTUAL COMPANY NAME]. State why you're a strong candidate. 3-4 sentences. DO NOT mention where you found the job posting (no "as advertised on LinkedIn/website")]

[Write paragraph 2 here: Technical Skills - Detail relevant technical skills and experience that match the job requirements. 4-5 sentences with specific examples from the user's draft.]

[Write paragraph 3 here: Soft Skills & Impact - Discuss soft skills, achievements, and how you'll contribute to [ACTUAL COMPANY NAME]'s goals. 4-5 sentences.]

[Write paragraph 4 here: Closing - Express enthusiasm about joining [ACTUAL COMPANY NAME] and request next steps. 2-3 sentences.]

Sincerely,
{signature_name}

CRITICAL FORMATTING RULES:
- You MUST include blank lines between paragraphs (press Enter twice after each paragraph)
- Start with "Dear Hiring Manager," followed by TWO line breaks
- Each paragraph must be separated by ONE blank line
- IMPORTANT: End with "Sincerely," on one line, then on the NEXT line write EXACTLY: {signature_name}
- The signature MUST be "{signature_name}" - do not change it, do not omit it
- Do NOT include contact information (email, phone, address) in the body
- Do NOT use clichés like "I am writing to apply for..."
- Use strong action verbs and be specific
- CRITICAL: Extract the ACTUAL company name from the job description and use it (do NOT use [Company Name] placeholder)
- DO NOT mention where the job was posted (no "as advertised on LinkedIn", "on your website", "on Indeed", etc.)
- DO NOT use any other placeholders like [mention specific project], [Previous Company], or any [bracketed text]
- If you don't know specific details about previous companies, write generally (e.g., "in my previous role" or "at a previous company")
- Be specific about the candidate's skills and experience from their draft

SIGNATURE EXAMPLE:
Sincerely,
{signature_name}

Return ONLY the formatted cover letter following this structure. No explanations."""

    try:
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 2048,
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
        cover_letter = response_data['candidates'][0]['content']['parts'][0]['text'].strip()
        
        # Post-process: Ensure name is after "Sincerely,"
        if signature_name and signature_name != "[Your Name]":
            # Replace [Your Name] placeholder with actual name
            if "[Your Name]" in cover_letter:
                cover_letter = cover_letter.replace("[Your Name]", signature_name)
                print(f"✓ Replaced [Your Name] with {signature_name}")
            # Also check if name is missing entirely after Sincerely
            elif "Sincerely," in cover_letter and signature_name not in cover_letter.split("Sincerely,")[-1]:
                parts = cover_letter.split("Sincerely,")
                # Add name after Sincerely if it's not there
                cover_letter = parts[0] + f"Sincerely,\n{signature_name}"
                print(f"✓ Added {signature_name} after Sincerely,")
        
        word_count = len(cover_letter.split())
        print(f"✓ Generated {word_count} words")
        
        return cover_letter
        
    except Exception as e:
        print(f"✗ Producer failed: {e}")
        raise


def refine_cover_letter(draft, critique, job_description, user_draft, candidate_name=None):
    """
    Refine cover letter based on critique feedback
    
    Args:
        draft (str): Previous draft
        critique (dict): Critique with scores and feedback
        job_description (str): Original job posting
        user_draft (str): Original user draft
        candidate_name (str, optional): Candidate's name for signature
    
    Returns:
        str: Refined cover letter
    """
    print("♻️ Producer: Refining based on critique...")
    
    # Use provided name or placeholder
    signature_name = candidate_name if candidate_name and candidate_name != "Not Found" else "[Your Name]"
    
    # Format critique for prompt
    critique_text = f"""Overall Score: {critique['overall_score']}/10

Issues Found:
{chr(10).join('- ' + issue for issue in critique['issues'])}

Suggestions for Improvement:
{chr(10).join('- ' + suggestion for suggestion in critique['suggestions'])}

Score Breakdown:
- Job Alignment: {critique['scores']['job_alignment']}/10
- Skill Highlighting: {critique['scores']['skill_highlighting']}/10
- Professional Tone: {critique['scores']['professional_tone']}/10
- Specific Examples: {critique['scores']['specific_examples']}/10
- Length & Structure: {critique['scores']['length']}/10"""

    prompt = f"""You are refining a cover letter based on expert feedback.

Previous Draft:
{draft}

Expert Critique:
{critique_text}

Job Description:
{job_description}

Original User Draft (for reference):
{user_draft}

Candidate Name: {signature_name}

IMPORTANT: Make sure to use the actual company name from the job description throughout the letter. Never use placeholders.

Improve the cover letter by addressing ALL the issues mentioned in the critique.
Keep what's working well, fix what's not.

YOU MUST FOLLOW THIS EXACT FORMAT:
Dear Hiring Manager,

[Paragraph 1: Opening - Express interest in the role at [ACTUAL COMPANY NAME]. 3-4 sentences. NO mention of where job was posted.]

[Paragraph 2: Technical skills with specific examples - 4-5 sentences]

[Paragraph 3: Soft skills and impact at [ACTUAL COMPANY NAME] - 4-5 sentences]

[Paragraph 4: Strong closing about joining [ACTUAL COMPANY NAME] - 2-3 sentences]

Sincerely,
{signature_name}

CRITICAL FORMATTING RULES:
- Include blank lines between ALL paragraphs (press Enter twice after each paragraph)
- Start with "Dear Hiring Manager," followed by TWO line breaks
- Separate each body paragraph with ONE blank line
- IMPORTANT: End with "Sincerely," on one line, then on the NEXT line write EXACTLY: {signature_name}
- The signature MUST be "{signature_name}" - do not change it, do not omit it
- 300-400 words total
- No contact information in body
- Professional tone throughout
- CRITICAL: Use the ACTUAL company name from job description (do NOT use [Company Name] placeholder)
- DO NOT mention where the job was posted (no "as advertised on...", "on your website", etc.)
- DO NOT use any other placeholders like [mention specific project], [Previous Company], or any [bracketed text]
- If you don't know specific details, write generally without brackets
- Be specific based on the critique and user's draft - no placeholders allowed

SIGNATURE EXAMPLE:
Sincerely,
{signature_name}

Return ONLY the improved cover letter following this exact format. No explanations."""

    try:
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 2048,
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
        refined_letter = response_data['candidates'][0]['content']['parts'][0]['text'].strip()
        
        # Post-process: Ensure name is after "Sincerely,"
        if signature_name and signature_name != "[Your Name]":
            # Replace [Your Name] placeholder with actual name
            if "[Your Name]" in refined_letter:
                refined_letter = refined_letter.replace("[Your Name]", signature_name)
                print(f"✓ Replaced [Your Name] with {signature_name}")
            # Also check if name is missing entirely after Sincerely
            elif "Sincerely," in refined_letter and signature_name not in refined_letter.split("Sincerely,")[-1]:
                parts = refined_letter.split("Sincerely,")
                # Add name after Sincerely if it's not there
                refined_letter = parts[0] + f"Sincerely,\n{signature_name}"
                print(f"✓ Added {signature_name} after Sincerely,")
        
        word_count = len(refined_letter.split())
        print(f"✓ Refined version: {word_count} words")
        
        return refined_letter
        
    except Exception as e:
        print(f"✗ Refiner failed: {e}")
        raise