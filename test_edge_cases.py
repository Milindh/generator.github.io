"""
Edge Case Testing for Multi-Agent Cover Letter System
Tests various edge cases to ensure robustness
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_case(test_name, job_description, cover_letter, expected_behavior):
    """Run a single test case"""
    print("\n" + "="*70)
    print(f"TEST: {test_name}")
    print("="*70)
    print(f"Expected: {expected_behavior}")
    print("-"*70)
    
    data = {
        'jobDescription': job_description,
        'coverLetter': cover_letter
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/generate-cover-letter", data=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ Status: SUCCESS")
            print(f"\nWorkflow:")
            print(f"  - Score: {result['workflow']['final_score']}/10")
            print(f"  - Time: {result['workflow']['total_time']}s")
            print(f"  - Iterations: {result['workflow']['total_iterations']}")
            
            print(f"\nContact Info:")
            print(f"  - Name: {result['contact_info'].get('name', 'Not Found')}")
            print(f"  - Email: {result['contact_info'].get('email', 'Not Found')}")
            
            # Check for company name mentions
            cover_letter_text = result['generatedCoverLetter']
            
            # Check for placeholders
            if '[' in cover_letter_text and ']' in cover_letter_text:
                print(f"\n⚠️  WARNING: Found placeholders in output")
                import re
                placeholders = re.findall(r'\[([^\]]+)\]', cover_letter_text)
                for p in placeholders:
                    print(f"     - [{p}]")
            else:
                print(f"\n✅ No placeholders found")
            
            # Show first 200 chars
            print(f"\nGenerated Cover Letter (first 200 chars):")
            print(cover_letter_text[:200] + "...")
            
            # Check signature
            if "Sincerely," in cover_letter_text:
                after_sincerely = cover_letter_text.split("Sincerely,")[-1].strip()
                if after_sincerely and after_sincerely != "[Your Name]":
                    print(f"\n✅ Signature present: {after_sincerely[:50]}")
                else:
                    print(f"\n⚠️  Signature missing or placeholder")
            
            return True, result
            
        else:
            print(f"❌ Status: FAILED ({response.status_code})")
            print(f"Error: {response.json()}")
            return False, None
            
    except requests.exceptions.Timeout:
        print(f"❌ Status: TIMEOUT")
        return False, None
    except Exception as e:
        print(f"❌ Status: ERROR - {e}")
        return False, None


def main():
    print("\n" + "="*70)
    print("EDGE CASE TEST SUITE")
    print("="*70)
    print("\nMake sure Flask app is running: python app.py")
    
    input("\nPress Enter to start tests...")
    
    results = []
    
    # ================================================================
    # TEST 1: Missing Company Name
    # ================================================================
    test1_job = """
    Senior Software Engineer
    
    Requirements:
    - 5+ years of Python experience
    - Strong understanding of web frameworks
    - Experience with databases (SQL, NoSQL)
    - Cloud platform experience (AWS/GCP/Azure)
    - Excellent problem-solving skills
    
    Responsibilities:
    - Design and implement scalable backend systems
    - Collaborate with cross-functional teams
    - Mentor junior engineers
    - Optimize application performance
    """
    
    test1_draft = """
    Dear Hiring Manager,
    
    I am excited to apply for this position. I have 6 years of Python experience
    and have built several web applications. I work well in teams and enjoy
    solving complex problems.
    
    Sincerely,
    Sarah Johnson
    sarah.j@email.com
    (555) 987-6543
    """
    
    result = test_case(
        "Missing Company Name",
        test1_job,
        test1_draft,
        "Should use generic terms like 'your organization' or 'the company'"
    )
    results.append(("Missing Company Name", result[0]))
    time.sleep(2)
    
    # ================================================================
    # TEST 2: Missing Contact Info
    # ================================================================
    test2_job = """
    Data Analyst at TechCorp
    
    We're seeking a Data Analyst to join our analytics team.
    
    Requirements:
    - 3+ years experience in data analysis
    - SQL and Python proficiency
    - Experience with visualization tools (Tableau, PowerBI)
    - Strong communication skills
    """
    
    test2_draft = """
    Dear Hiring Manager,
    
    I am very interested in the Data Analyst position. I have worked with data
    for 4 years and am proficient in SQL and Python. I have created many
    dashboards and reports.
    
    I would love to discuss this opportunity further.
    
    Best regards,
    """
    
    result = test_case(
        "Missing Contact Info",
        test2_job,
        test2_draft,
        "Should use fallback extraction or default to [Your Name]"
    )
    results.append(("Missing Contact Info", result[0]))
    time.sleep(2)
    
    # ================================================================
    # TEST 3: Minimum Length Inputs
    # ================================================================
    test3_job = """
    Marketing Manager position. Requirements: 5 years experience, digital marketing skills, team leadership.
    """
    
    test3_draft = """
    Dear Hiring Manager,
    
    I am interested in the Marketing Manager role. I have 6 years of experience
    in digital marketing and have led teams of up to 5 people. I would like to
    contribute to your company's growth.
    
    Sincerely,
    Alex Martinez
    alex.m@company.com
    """
    
    result = test_case(
        "Minimum Length Inputs",
        test3_job,
        test3_draft,
        "Should still generate a valid cover letter despite short inputs"
    )
    results.append(("Minimum Length Inputs", result[0]))
    time.sleep(2)
    
    # ================================================================
    # TEST 4: Non-Technical Role (Marketing)
    # ================================================================
    test4_job = """
    Content Marketing Manager at BrandBoost
    
    We're looking for a creative Content Marketing Manager to lead our content strategy.
    
    Requirements:
    - 5+ years in content marketing
    - Strong writing and editing skills
    - SEO knowledge
    - Social media expertise
    - Experience with content management systems
    - Analytics and performance tracking
    
    Responsibilities:
    - Develop content strategy
    - Create engaging blog posts and articles
    - Manage social media campaigns
    - Analyze content performance
    """
    
    test4_draft = """
    Dear Hiring Manager,
    
    I am excited about the Content Marketing Manager opportunity. I have 6 years
    of experience creating content strategies and managing social media campaigns.
    I've increased organic traffic by 150% in my current role.
    
    Sincerely,
    Emily Chen
    emily.chen@gmail.com
    """
    
    result = test_case(
        "Non-Technical Role (Marketing)",
        test4_job,
        test4_draft,
        "Should generate marketing-focused cover letter with appropriate language"
    )
    results.append(("Non-Technical Role", result[0]))
    time.sleep(2)
    
    # ================================================================
    # TEST 5: Entry-Level Position
    # ================================================================
    test5_job = """
    Junior Software Developer at StartupXYZ
    
    We're hiring entry-level developers to join our growing team!
    
    Requirements:
    - Bachelor's in Computer Science or related field
    - Knowledge of JavaScript and React
    - Understanding of web development basics
    - Enthusiasm to learn
    - Good communication skills
    
    No prior work experience required - we'll train you!
    """
    
    test5_draft = """
    Dear Hiring Manager,
    
    I recently graduated with a degree in Computer Science and am excited to
    start my career. I completed several projects using React and JavaScript
    during my studies. I am eager to learn and grow with a supportive team.
    
    Sincerely,
    Michael Brown
    michael.b@university.edu
    (555) 123-9999
    """
    
    result = test_case(
        "Entry-Level Position",
        test5_job,
        test5_draft,
        "Should generate appropriate entry-level cover letter emphasizing potential"
    )
    results.append(("Entry-Level Position", result[0]))
    time.sleep(2)
    
    # ================================================================
    # TEST 6: Senior Leadership Role
    # ================================================================
    test6_job = """
    Director of Engineering at GlobalTech Industries
    
    We're seeking an experienced Director of Engineering to lead our technical teams.
    
    Requirements:
    - 10+ years in software engineering
    - 5+ years in leadership roles
    - Experience managing multiple teams (50+ engineers)
    - Strategic planning and execution
    - Budget management
    - Strong technical background
    - Excellent stakeholder management
    """
    
    test6_draft = """
    Dear Hiring Manager,
    
    With 12 years of engineering experience including 6 years in leadership,
    I am excited about the Director of Engineering role. I currently manage
    60 engineers across 4 teams and have delivered multiple successful products.
    
    Sincerely,
    David Kim
    david.kim@executive.com
    (555) 777-8888
    """
    
    result = test_case(
        "Senior Leadership Role",
        test6_job,
        test6_draft,
        "Should generate executive-level cover letter with strategic focus"
    )
    results.append(("Senior Leadership Role", result[0]))
    
    # ================================================================
    # SUMMARY
    # ================================================================
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All edge case tests passed! System is robust.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review the errors above.")
    
    print("="*70 + "\n")


if __name__ == "__main__":
    main()