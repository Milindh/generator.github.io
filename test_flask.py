"""
Test Flask API endpoints
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health check endpoint"""
    print("\n" + "="*70)
    print("TEST 1: Health Check")
    print("="*70)
    
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_generate_cover_letter():
    """Test cover letter generation"""
    print("\n" + "="*70)
    print("TEST 2: Generate Cover Letter")
    print("="*70)
    
    data = {
        'jobDescription': """
        Hatch is an Equal Opportunity/Affirmative Action Employer with a strong institutional commitment to the achievement of excellence and diversity among its technical and professional staff.

Duties And Responsibilities

Pursuit Delivery

Lead proposal development efforts to prepare high-quality deliverables and submissions in a timely, efficient, and cost-effective manner. This may consist of working with Pursuit Managers and pursuit delivery team to gather appropriate material/information needed to meet the requirements of the RFP; assembling and packaging of proposals/documents from inception through final product; working with Manager, Graphics Department, and/or administrative personnel to facilitate any work needing completed; and contacting of subconsultants and/or teaming partners to assure all information is accurately provided.
Ensure all materials meet the requirements of the client by following the corporate Quality Assurance Plan (QAP).
Proactively develop, maintain, and continuously apply the proposal planning process for each proposal.
Write and synthesize proposal narrative as required.

Content Development

Requires the ability to comprehend and synthesize technical content and craft a narrative that highlights the broader impacts of our work.
Print Materials: Authoring content for various materials including (but not limited to): brochures, flyers, proposal materials, newsletters, internal communiques, etc.
Digital Content: Edit and update website content, as needed.

Presentations/Conferences

Prepare or assist in the preparation of materials for client presentations, including, but not limited to: large-format presentation boards, PowerPoint presentations, and handouts.
Assist with conferences, trade shows, etc. (May include, but is not limited to, development of exhibit materials, shipping of display booth and accessories, and coordination of materials and display booth.)

Misc. Marketing Tasks

Work with other members of the Marketing Team to ensure that all resumes, project descriptions, boilerplate materials, etc. are updated and prepared for inclusion into the corporate marketing database system. 
Along with other members of the Marketing Team, maintain centralized electronic filing of all marketing materials (i.e., proposals, SOQ's, collateral materials, etc.). 
Other duties as assigned.

Misc. Administrative Tasks

Responsible for registering, classifying, managing, tracking, filing and distributing of all electronic and hard copy project deliverables and other documentation as required by the project. This includes design and vendor documentation and other controlled documents as defined by the project
Also responsible for the quality checking of documents as defined in the project document control procedures and scanning, printing, copying of documentation, and preparing CD’s as required
Responsible for facilitating progressive turnover deliverable documentation (if required) and final handover in accordance with the project documentation handover matrix.

Education And Experience

Bachelor's degree in Marketing, Communication, English, or Journalism or related field.
This role requires exceptional communication, analytical and client engagement skills. The general environment can be highly stressful due to resource fluctuations and tight deadlines and requires one to manage multiple tasks and priorities simultaneously 
Ability to manage multiple projects and deadlines (required).
Strong demonstrated written communication skills with an ability to write in a variety of mediums as well as an ability to effectively speak to diverse constituencies and a keen eye for editing (required).
Superb attention to detail (required).
Ability to effectively work as a member of a team (required).
Experience with electronic document management and document control systems 
Through understanding of the requirements of tracking vendor data and engineering processes, and how these interrelate with other areas of project activities 
Ability to interpret, write and apply complex procedures 
Familiarity with social media platforms and content development- LinkedIn, Twitter, etc.
Availability to work flexible hours, including evenings, weekends and holidays when deadlines deem necessary.
Interest in or familiarity with the engineering, technology, and/or sustainability fields is a plus.
3 – 5 years of experience.

Why join us?

Work with great people to make a difference
Collaborate on exciting projects to develop innovative solutions
 Top employer 


        """,
        'coverLetter': """
        Milindh Ravikiran Kashyap
ravikirankashyap.m@northeastern.edu | (857)-376-1804 | linkedin.com/in/milindhkashyap | github.com/Milindh
SUMMARY
Data and Business Analytics professional with experience developing, validating, and governing data systems. Skilled in
Python and SQL for data modeling, analysis, and automation, with a strong foundation in data integrity validation and
compliance reporting.
EDUCATION
Northeastern University Boston, MA
MS in Information Systems 3.7/4.0 Expected Graduation: Dec 2025
Coursework - Data Warehousing, Time Series Forecasting, Natural Language Processing, Information Retrieval
Visveswaraya Technical University Bangalore, India
BE in Electronics and Telecommunication 3.9/4.0 May 2018 - May 2022
TECHNICAL SKILLS
Programming Languages: Python, SQL, PL/SQL, Java, DAX, MySQL, PostgreSQL
Analytical & Reporting Tools: Tableau, Power BI, R Studio, Excel, Statistical Analysis, Quicksight, Jira, QlikSense
Data Engineering Tools: Apache Spark, Airflow, AWS Glue, AWS Redshift, Snowflake, Talend, Alteryx
ML Frameworks: TensorFlow, PyTorch, XGBoost, LightGBM, Scikit-learn, Google Gemini LLM, LangGraph
PROFESSIONAL EXPERIENCE
Massachusetts Clean Energy Center Jan 2025 - Present
Business Intelligence Analyst |Time Series Modeling, GCP, ETL workflows, Data Analysis, Power BI Boston, MA
• Gathered business requirements for Salesforce CRM implementation by interviewing stakeholders, ensuring alignment with
business goals and system capabilities.
• Led the RFP process by coordinating with vendors and internal teams to evaluate solutions against data governance
standards, streamlining vendor selection
• Collaborated with Product Owners to define KPIs, SLAs, and data definitions, improving transparency in performance
reporting.
• Created process flow diagrams in Lucidchart to visualize reporting workflows, enabling teams to streamline KPI delivery
• Supported Agile sprint reviews by documenting analytics requirements and summarizing outcomes for leadership reporting
Dialysis-X May 2024-Aug 2024
Business Intelligence Analyst | SQL, Financial Analysis, Strategy, Data Analysis, Tableau, Snowflake Boston, MA
• Partnered with business leads to gather analytical requirements for financial reporting, bridging data teams and executive
stakeholders
• Automated data ingestion and cleansing workflows with Alteryx and dbt, cutting manual preparation time and improving
delivery consistency for analytics.
• Created Tableau dashboards that consolidated operational KPIs, reducing manual data requests and improving reporting
turnaround
• Partnered with cross-functional teams to interpret insights and refine business strategies, ensuring data-driven improvements
in patient care
Wipro Consulting Mar 2021-Jun 2023
Data Engineer | SQL, Snowflake, Data Factory, Requirement Analysis, Alteryx, AWS Redshift, JIRA Bangalore, India
• Automated ETL workflows on Snowflake using Python and SQL, improving data availability for real-time analytics
• Centralized multi-platform customer data into Redshift using SQL, standardizing 5M+ records into structured datasets
for financial trend analysis and Power BI reporting.
• Built real-time KPI dashboards in Power BI connected to Snowflake, supporting stakeholders with live insights across
finance, sales, and operations
• Partnered with engineering teams to add SQL/Python validation checks in Snowflake pipelines, reducing data quality issues
and downstream errors by half
• Facilitated Agile sprints by capturing analytics requirements in JIRA and translating them into ETL/BI deliverables, ensuring
consistent delivery across 12+ sprint cycles
PROJECTS
Health Tracking App | Snowflake Cortex, LangGraph, Llama, Snowflake, dbt, Python, Streamlit
• Built a centralized health dataset by ingesting smartwatch metrics into BigQuery and modeling with dbt, enabling cohort
and trend analysis.
• Developed a Streamlit dashboard to visualize time-series activity and KPIs for interactive health tracking.
Cover Letter Generator | Google Gemini, Snowflake, Python, LangChain, StreamLit
• Developed an AI-powered multi-agent system using Google Gemini LLM to automate personalized cover letter generation
tailored to different job descriptions and user profiles.
• Implemented backend logic in Python and Flask, enabling seamless integration between the LLM agents

        """
    }
    
    print("Sending request...")
    response = requests.post(f"{BASE_URL}/api/generate-cover-letter", data=data)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        
        print("\n✅ SUCCESS!")
        print(f"\nWorkflow Summary:")
        print(f"  - Total iterations: {result['workflow']['total_iterations']}")
        print(f"  - Initial score: {result['workflow']['initial_score']}/10")
        print(f"  - Final score: {result['workflow']['final_score']}/10")
        print(f"  - Improvement: +{result['workflow']['improvement']} points")
        print(f"  - Total time: {result['workflow']['total_time']}s")
        print(f"  - Stop reason: {result['workflow']['stop_reason']}")
        
        print(f"\nScores:")
        for key, value in result['scores'].items():
            print(f"  - {key.replace('_', ' ').title()}: {value}/10")
        
        print(f"\nContact Info:")
        print(f"  - Name: {result['contact_info'].get('name', 'Not Found')}")
        print(f"  - Email: {result['contact_info'].get('email', 'Not Found')}")
        print(f"  - Phone: {result['contact_info'].get('phone', 'Not Found')}")
        
        print(f"\nGenerated Cover Letter (first 300 chars):")
        print(result['generatedCoverLetter'][:300] + "...")
        
        print(f"\nFeedback:")
        if result['feedback']['issues']:
            print("  Issues:")
            for issue in result['feedback']['issues']:
                print(f"    - {issue}")
        if result['feedback']['suggestions']:
            print("  Suggestions:")
            for suggestion in result['feedback']['suggestions']:
                print(f"    - {suggestion}")
        
        return True, result
    else:
        print(f"\n❌ FAILED")
        print(f"Error: {response.json()}")
        return False, None


def test_download_docx(cover_letter, contact_info):
    """Test DOCX download"""
    print("\n" + "="*70)
    print("TEST 3: Download DOCX")
    print("="*70)
    
    data = {
        'coverLetter': cover_letter,
        'contactInfo': contact_info
    }
    
    response = requests.post(
        f"{BASE_URL}/api/download/docx",
        json=data
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        # Save file
        with open('test_flask_output.docx', 'wb') as f:
            f.write(response.content)
        print("✅ DOCX saved as: test_flask_output.docx")
        print(f"   File size: {len(response.content)} bytes")
        return True
    else:
        print(f"❌ FAILED: {response.text}")
        return False


def test_download_pdf(cover_letter, contact_info):
    """Test PDF download"""
    print("\n" + "="*70)
    print("TEST 4: Download PDF")
    print("="*70)
    
    data = {
        'coverLetter': cover_letter,
        'contactInfo': contact_info
    }
    
    response = requests.post(
        f"{BASE_URL}/api/download/pdf",
        json=data
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        # Save file
        with open('test_flask_output.pdf', 'wb') as f:
            f.write(response.content)
        print("✅ PDF saved as: test_flask_output.pdf")
        print(f"   File size: {len(response.content)} bytes")
        return True
    else:
        print(f"❌ FAILED: {response.text}")
        return False


if __name__ == "__main__":
    print("\n" + "="*70)
    print("FLASK API TEST SUITE")
    print("="*70)
    print("\nMake sure Flask app is running:")
    print("  python app.py")
    print("\nThen run this test script in another terminal.")
    print("="*70)
    
    input("\nPress Enter to start tests...")
    
    results = []
    
    # Test 1: Health check
    results.append(("Health Check", test_health()))
    
    # Test 2: Generate cover letter
    success, api_result = test_generate_cover_letter()
    results.append(("Generate Cover Letter", success))
    
    if success and api_result:
        # Test 3 & 4: Downloads (only if generation succeeded)
        cover_letter = api_result['generatedCoverLetter']
        contact_info = api_result['contact_info']
        
        results.append(("Download DOCX", test_download_docx(cover_letter, contact_info)))
        results.append(("Download PDF", test_download_pdf(cover_letter, contact_info)))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! Flask API is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
    
    print("="*70 + "\n")