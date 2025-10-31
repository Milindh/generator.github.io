"""
Workflow Orchestrator - Single Iteration Multi-Agent System
Coordinates Producer, Critic, and Refiner agents for one refinement loop
"""

import time
from .producer_agent import generate_cover_letter, refine_cover_letter
from .critic_agent import critique_cover_letter

# Import contact extractor from utils
try:
    from utils.contact_extractor import extract_contact_info
    CONTACT_EXTRACTOR_AVAILABLE = True
except ImportError:
    CONTACT_EXTRACTOR_AVAILABLE = False
    print("⚠️ Contact extractor not available")


def run_single_iteration_workflow(job_description, user_draft, quality_threshold=9.0):
    """
    Run single iteration cover letter generation workflow
    
    Workflow: Extract Contact → Generate → Critique → [Decision Point]
              - If score >= threshold: STOP (use first draft)
              - If score < threshold: Refine → Final Critique
    
    This saves 6-10 seconds when initial draft is already high quality!
    
    Args:
        job_description (str): The job posting text
        user_draft (str): User's current cover letter
        quality_threshold (float): Score threshold to skip refinement (default 9.0)
    
    Returns:
        dict: Complete workflow results with iterations and scores
    """
    
    print("\n" + "="*70)
    print("STARTING COVER LETTER GENERATION - SINGLE ITERATION MODE")
    print("="*70)
    
    workflow_start = time.time()
    results = {
        'drafts': [],
        'critiques': [],
        'timings': {},
        'final_score': 0.0,
        'improvement': 0.0,
        'stop_reason': '',
        'contact_info': {}
    }
    
    try:
        # STEP 0: Extract Contact Information
        print("\n[STEP 0/4] Extracting contact information...")
        step_start = time.time()
        
        candidate_name = None
        if CONTACT_EXTRACTOR_AVAILABLE:
            try:
                contact_info = extract_contact_info(user_draft)
                results['contact_info'] = contact_info
                candidate_name = contact_info.get('name')
                print(f"✓ Extracted name: {candidate_name}")
            except Exception as e:
                print(f"⚠️ Contact extraction failed: {e}")
                candidate_name = None
        else:
            print("⚠️ Skipping contact extraction (utils not available)")
        
        results['timings']['contact_extraction'] = round(time.time() - step_start, 2)
        
        # STEP 1: Generate Initial Draft
        print("\n[STEP 1/4] Generating initial draft...")
        step_start = time.time()
        
        initial_draft = generate_cover_letter(job_description, user_draft, candidate_name)
        results['drafts'].append(initial_draft)
        results['timings']['generation'] = round(time.time() - step_start, 2)
        
        print(f"⏱️  Generation time: {results['timings']['generation']}s")
        
        # STEP 2: Critique Initial Draft
        print("\n[STEP 2/4] Evaluating initial draft...")
        step_start = time.time()
        
        initial_critique = critique_cover_letter(initial_draft, job_description, user_draft)
        results['critiques'].append(initial_critique)
        results['timings']['critique_1'] = round(time.time() - step_start, 2)
        
        initial_score = initial_critique['overall_score']
        print(f"📊 Initial Score: {initial_score}/10")
        print(f"⏱️  Critique time: {results['timings']['critique_1']}s")
        
        # Check if initial draft already meets threshold (EARLY EXIT)
        if initial_score >= quality_threshold:
            results['final_score'] = initial_score
            results['improvement'] = 0.0
            results['stop_reason'] = 'quality_threshold_met_early'
            
            workflow_time = round(time.time() - workflow_start, 2)
            results['timings']['total'] = workflow_time
            
            # FINAL GUARANTEE: Inject name if missing (early exit path)
            final_draft = results['drafts'][-1]
            if candidate_name and candidate_name != "Not Found":
                if "[Your Name]" in final_draft:
                    final_draft = final_draft.replace("[Your Name]", candidate_name)
                    results['drafts'][-1] = final_draft
                    print(f"✓ Injected name: {candidate_name}")
                elif "Sincerely," in final_draft:
                    after_sincerely = final_draft.split("Sincerely,")[-1].strip()
                    if not after_sincerely or candidate_name not in after_sincerely:
                        parts = final_draft.split("Sincerely,")
                        final_draft = parts[0] + f"Sincerely,\n{candidate_name}"
                        results['drafts'][-1] = final_draft
                        print(f"✓ Injected name after Sincerely: {candidate_name}")
            
            print(f"\n🎉 EARLY EXIT: Quality threshold met on first draft!")
            print(f"   Score: {initial_score}/10 >= {quality_threshold}/10")
            print(f"   ⚡ Saved ~8 seconds by skipping refinement")
            print(f"   ✅ Using initial draft as final version")
            
            print("\n" + "="*70)
            print(f"WORKFLOW COMPLETE - {workflow_time}s total (Fast Path)")
            print(f"Final Score: {initial_score}/10")
            print(f"Stop Reason: {results['stop_reason']}")
            print("="*70 + "\n")
            
            return results
        
        # STEP 3: Refine Based on Critique
        print("\n[STEP 3/4] Refining cover letter...")
        print(f"Addressing {len(initial_critique['issues'])} issues...")
        step_start = time.time()
        
        refined_draft = refine_cover_letter(
            initial_draft, 
            initial_critique, 
            job_description, 
            user_draft,
            candidate_name  # Pass the extracted name
        )
        results['drafts'].append(refined_draft)
        results['timings']['refinement'] = round(time.time() - step_start, 2)
        
        print(f"⏱️  Refinement time: {results['timings']['refinement']}s")
        
        # STEP 4: Final Critique
        print("\n[STEP 4/4] Final evaluation...")
        step_start = time.time()
        
        final_critique = critique_cover_letter(refined_draft, job_description, user_draft)
        results['critiques'].append(final_critique)
        results['timings']['critique_2'] = round(time.time() - step_start, 2)
        
        final_score = final_critique['overall_score']
        improvement = round(final_score - initial_score, 1)
        
        results['final_score'] = final_score
        results['improvement'] = improvement
        results['stop_reason'] = 'single_iteration_complete'
        
        print(f"📊 Final Score: {final_score}/10")
        print(f"📈 Improvement: +{improvement} points")
        print(f"⏱️  Final critique time: {results['timings']['critique_2']}s")
        
        # Summary
        workflow_time = round(time.time() - workflow_start, 2)
        results['timings']['total'] = workflow_time
        
        # FINAL GUARANTEE: Inject name if missing
        final_draft = results['drafts'][-1]
        if candidate_name and candidate_name != "Not Found":
            if "[Your Name]" in final_draft:
                final_draft = final_draft.replace("[Your Name]", candidate_name)
                results['drafts'][-1] = final_draft
                print(f"✓ Injected name: {candidate_name}")
            elif "Sincerely," in final_draft:
                # Check if name is already there
                after_sincerely = final_draft.split("Sincerely,")[-1].strip()
                if not after_sincerely or candidate_name not in after_sincerely:
                    parts = final_draft.split("Sincerely,")
                    final_draft = parts[0] + f"Sincerely,\n{candidate_name}"
                    results['drafts'][-1] = final_draft
                    print(f"✓ Injected name after Sincerely: {candidate_name}")
        
        print("\n" + "="*70)
        print(f"WORKFLOW COMPLETE - {workflow_time}s total")
        print(f"Initial Score: {initial_score}/10")
        print(f"Final Score: {final_score}/10")
        print(f"Improvement: +{improvement} points")
        print(f"Stop Reason: {results['stop_reason']}")
        print("="*70 + "\n")
        
        return results
        
    except Exception as e:
        print(f"\n❌ Workflow failed: {e}")
        raise


def get_final_cover_letter(workflow_results):
    """
    Extract the best cover letter from workflow results
    
    Args:
        workflow_results (dict): Results from run_single_iteration_workflow
    
    Returns:
        str: The best cover letter (last draft)
    """
    return workflow_results['drafts'][-1]


def get_workflow_summary(workflow_results):
    """
    Generate a human-readable summary of the workflow
    
    Args:
        workflow_results (dict): Results from run_single_iteration_workflow
    
    Returns:
        dict: Formatted summary for API response
    """
    num_iterations = len(workflow_results['drafts'])
    
    return {
        'total_iterations': num_iterations,
        'initial_score': workflow_results['critiques'][0]['overall_score'],
        'final_score': workflow_results['final_score'],
        'improvement': workflow_results['improvement'],
        'total_time': workflow_results['timings']['total'],
        'stop_reason': workflow_results['stop_reason'],
        'final_critique': workflow_results['critiques'][-1]
    }


# Example usage (for testing)
if __name__ == "__main__":
    # Test with sample data
    test_job = """
    Senior Software Engineer position requiring:
    - 5+ years Python experience
    - Cloud architecture (AWS/Azure)
    - Team leadership
    - Agile methodologies
    """
    
    test_draft = """
    Dear Hiring Manager,
    
    I am writing to express my interest in the Senior Software Engineer position.
    I have experience in Python and cloud technologies. I have worked on several
    projects and believe I would be a good fit.
    
    Sincerely,
    John Doe
    """
    
    results = run_single_iteration_workflow(test_job, test_draft)
    
    print("\n📄 FINAL COVER LETTER:")
    print(get_final_cover_letter(results))
    
    print("\n📊 SUMMARY:")
    import json
    summary = get_workflow_summary(results)
    print(json.dumps(summary, indent=2))