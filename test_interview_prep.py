#!/usr/bin/env python3
"""
Test utility for the Career Copilot Agent interview prep feature.
This script helps verify that the interview prep feature works correctly.
"""

import json
from app.orchestrator import CareerCopilotOrchestrator

def main():
    print("Career Copilot - Interview Prep Test Utility")
    print("===========================================")
    print("\nThis utility tests the interview preparation functionality")
    print("to make sure it correctly handles JSON responses.\n")
    
    # Sample job description
    job_description = """
    Senior Python Developer (AI/LLM Focus)
    
    We're seeking an experienced Python developer with a strong background in AI and LLMs.
    
    Requirements:
    - 2+ years of Python development experience
    - Knowledge of AI, LLMs, and multi-agent systems
    - Experience with cloud deployment and API development
    """
    
    # Sample user profile
    user_profile = {
        "name": "Demo User",
        "experience_years": 3,
        "skills": ["Python", "Java", "React"]
    }
    
    print("Running interview prep with sample job description...")
    orch = CareerCopilotOrchestrator()
    
    try:
        result = orch.generate_interview_questions(job_description, user_profile)
        
        if "error" in result:
            print(f"\n❌ Error: {result['error']}")
            if "raw" in result:
                print("\nRaw output:")
                print(result["raw"])
        elif "interview_prep" in result:
            print("\n✅ Success! Interview prep generated correctly.")
            questions = result["interview_prep"]
            print(f"\nGenerated {len(questions)} interview questions.")
            
            # Print a sample question
            if questions:
                print("\nSample Question:")
                sample = questions[0]
                print(f"Category: {sample.get('category', 'N/A')}")
                print(f"Question: {sample.get('question', 'N/A')}")
                print(f"Key Points: {', '.join(sample.get('key_points', ['N/A']))}")
                
            # Write to file for inspection
            with open("interview_prep_test_output.json", "w") as f:
                json.dump(result, f, indent=2)
            print("\nFull output written to 'interview_prep_test_output.json'")
        else:
            print("\n❌ Unexpected result structure:")
            print(result)
            
    except Exception as e:
        print(f"\n❌ Exception: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\nTest complete!")
    
if __name__ == "__main__":
    main()
