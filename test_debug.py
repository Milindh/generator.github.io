"""
Debug test - Step by step testing
"""

import os
import sys

print("="*70)
print("STEP 1: Checking API Key")
print("="*70)

api_key = os.environ.get('GEMINI_API_KEY')
if not api_key:
    print("❌ GEMINI_API_KEY not found!")
    sys.exit(1)
else:
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-5:]}")
    print(f"   Length: {len(api_key)} characters")

print("\n" + "="*70)
print("STEP 2: Testing Imports")
print("="*70)

try:
    print("Importing producer_agent...")
    from agents.producer_agent import generate_cover_letter
    print("✅ producer_agent imported")
except ImportError as e:
    print(f"❌ Failed to import producer_agent: {e}")
    sys.exit(1)

try:
    print("Importing critic_agent...")
    from agents.critic_agent import critique_cover_letter
    print("✅ critic_agent imported")
except ImportError as e:
    print(f"❌ Failed to import critic_agent: {e}")
    sys.exit(1)

try:
    print("Importing workflow...")
    from agents.workflow import run_single_iteration_workflow
    print("✅ workflow imported")
except ImportError as e:
    print(f"❌ Failed to import workflow: {e}")
    sys.exit(1)

print("\n" + "="*70)
print("STEP 3: Testing Producer Agent Only")
print("="*70)

test_job = "Software Engineer with Python experience required."
test_draft = "Dear Hiring Manager,\n\nI am interested in this role. I have Python experience.\n\nSincerely,\nJohn"

try:
    print("Calling generate_cover_letter...")
    result = generate_cover_letter(test_job, test_draft)
    print(f"\n✅ SUCCESS! Generated {len(result)} characters")
    print(f"\nFirst 200 characters:\n{result[:200]}...")
except Exception as e:
    print(f"\n❌ FAILED: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)