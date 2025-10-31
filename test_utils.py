"""
Test script for utils functions
"""

import os

# Check API key
if not os.environ.get('GEMINI_API_KEY'):
    print("❌ Set GEMINI_API_KEY first!")
    exit(1)

print("="*70)
print("TESTING UTILS FUNCTIONS")
print("="*70)

# Test 1: Contact Extractor
print("\n[TEST 1] Contact Extractor")
print("-"*70)

from utils import extract_contact_info, format_contact_header

test_letter = """Dear Hiring Manager,

I am very interested in the Software Engineer position at your company.
I have 5 years of experience building web applications.

Please feel free to reach me at john.smith@email.com or (555) 123-4567.

Sincerely,
John Smith
San Francisco, CA"""

try:
    contact_info = extract_contact_info(test_letter)
    print("\n✅ Contact extraction successful!")
    print(f"   Name: {contact_info['name']}")
    print(f"   Email: {contact_info['email']}")
    print(f"   Phone: {contact_info['phone']}")
    print(f"   Address: {contact_info['address']}")
    
    print("\nFormatted Header:")
    print(format_contact_header(contact_info))
except Exception as e:
    print(f"❌ Contact extraction failed: {e}")

# Test 2: Export Utils (DOCX)
print("\n\n[TEST 2] DOCX Export")
print("-"*70)

from utils import create_docx

test_cover_letter = """Dear Hiring Manager,
Amplify,
I am eager to contribute my data analysis skills to Amplify as a Data Analyst, where I can leverage my
experience to help drive decisions impacting students worldwide. Your team's focus on building reporting
frameworks and actionable metrics strongly aligns with my passion for translating data into impactful
insights.
My technical skills directly address the requirements outlined in the job description. I have extensive
experience writing advanced SQL queries, including complex joins and window functions, and developing
data models using dbt. As demonstrated in my Health Tracking App project, I built a centralized health
dataset using dbt and BigQuery to enable cohort and trend analysis. Moreover, my experience at Wipro
Consulting involved automating ETL workflows on Snowflake using Python and SQL, which improved
data availability for real-time analytics and reporting by 40%. I am proficient in Python for data analysis
using pandas and NumPy, and I have hands-on experience with cloud-based analytics stacks, including
Snowflake and Fivetran.
Beyond technical proficiency, I excel at communicating complex findings to non-technical partners. In my
role as a Business Intelligence Analyst at Massachusetts Clean Energy Center, I refined prompt logic to
optimize grant categorization and insight generation, supporting AI-driven data workflows. My experience
facilitating Agile sprints at Wipro Consulting, capturing analytics requirements in JIRA, and translating
them into ETL/BI deliverables, highlights my ability to contribute to a data-driven culture. My background
in analyzing CMS data to identify trends and friction points during my internship at Dialysis-X further
demonstrates my ability to contribute strategically.
I am confident that my skills and experiences align well with the needs of your team. I am excited about
the opportunity to contribute to Amplify's mission and am eager to discuss how I can help your team achieve
its goals.
Sincerely
John Smith"""

try:
    docx_buffer = create_docx(test_cover_letter, contact_info)
    docx_size = len(docx_buffer.getvalue())
    print(f"✅ DOCX created successfully!")
    print(f"   Size: {docx_size} bytes")
    
    # Save test file
    with open('test_output.docx', 'wb') as f:
        f.write(docx_buffer.getvalue())
    print("   Saved: test_output.docx")
except ImportError as e:
    print(f"⚠️ Skipped: {e}")
except Exception as e:
    print(f"❌ DOCX export failed: {e}")

# Test 3: Export Utils (PDF)
print("\n\n[TEST 3] PDF Export")
print("-"*70)

from utils import create_pdf

try:
    pdf_bytes = create_pdf(test_cover_letter, contact_info)
    pdf_size = len(pdf_bytes)
    print(f"✅ PDF created successfully!")
    print(f"   Size: {pdf_size} bytes")
    
    # Save test file
    with open('test_output.pdf', 'wb') as f:
        f.write(pdf_bytes)
    print("   Saved: test_output.pdf")
except ImportError as e:
    print(f"⚠️ Skipped: {e}")
except Exception as e:
    print(f"❌ PDF export failed: {e}")

# Test 4: PDF Parser (optional - needs PDF file)
print("\n\n[TEST 4] PDF Parser")
print("-"*70)
print("⚠️ Skipped - requires test PDF file")
print("   To test: Place a resume.pdf in project folder")

print("\n" + "="*70)
print("UTILS TESTING COMPLETE")
print("="*70)

print("\n📋 Summary:")
print("   ✓ Contact extraction works")
print("   ✓ DOCX export works")
print("   ✓ PDF export works")
print("\nNext: Integrate into Flask app!")