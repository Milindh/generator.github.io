"""
Quick test script for agents in VS Code
"""

import os

# Check environment variable
if not os.environ.get('GEMINI_API_KEY'):
    print("❌ ERROR: GEMINI_API_KEY not set!")
    print("\nRun this first:")
    print('  export GEMINI_API_KEY="your_key"  # Mac/Linux')
    print('  set GEMINI_API_KEY=your_key       # Windows CMD')
    exit(1)

print("✅ API Key found!")
print("Starting agent tests...\n")

# Import agents
try:
    from agents.workflow import run_single_iteration_workflow, get_final_cover_letter, get_workflow_summary
    print("✅ Successfully imported agents!\n")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("\nMake sure you have:")
    print("  - agents/__init__.py")
    print("  - agents/producer_agent.py")
    print("  - agents/critic_agent.py")
    print("  - agents/workflow.py")
    exit(1)

# Sample data
SAMPLE_JOB = """
Software Engineer - AI/ML Team

Requirements:
- 3+ years Python experience
- Machine learning background
- Strong problem-solving skills
- Team collaboration
"""

SAMPLE_DRAFT = """
Dear Hiring Manager,

I am interested in the Software Engineer position. I have experience with Python 
and have worked on some ML projects. I am a good team player and problem solver.

Sincerely,
Jane Smith
"""

print("="*70)
print("RUNNING WORKFLOW TEST")
print("="*70)

try:
    # Run workflow
    results = run_single_iteration_workflow(SAMPLE_JOB, SAMPLE_DRAFT)
    
    # Get results
    final_letter = get_final_cover_letter(results)
    summary = get_workflow_summary(results)
    
    # Display results
    print("\n" + "="*70)
    print("✅ TEST SUCCESSFUL!")
    print("="*70)
    
    print(f"\nInitial Score: {summary['initial_score']}/10")
    print(f"Final Score: {summary['final_score']}/10")
    print(f"Improvement: +{summary['improvement']} points")
    print(f"Total Time: {summary['total_time']}s")
    print(f"Stop Reason: {summary['stop_reason']}")
    
    print("\n" + "="*70)
    print("FINAL COVER LETTER:")
    print("="*70)
    print(final_letter)
    
    print("\n" + "="*70)
    print("FINAL SCORES:")
    print("="*70)
    for key, value in summary['final_critique']['scores'].items():
        print(f"  {key.replace('_', ' ').title()}: {value}/10")
    
    print("\n✅ All agents working correctly!")
    
except Exception as e:
    print(f"\n❌ TEST FAILED: {e}")
    import traceback
    traceback.print_exc()