#!/usr/bin/env python3
"""
Test utility for the Career Copilot Agent job tracker feature.
This script helps verify that the job tracker feature works correctly.
"""

import json
from app.orchestrator import CareerCopilotOrchestrator
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    print("Career Copilot - Job Tracker Test Utility")
    print("========================================")
    print("\nThis utility tests the job tracker functionality")
    print("to make sure it correctly handles Google Sheets integration.\n")
    
    # Sample job data
    job_data = {
        "date_applied": "2025-08-24",
        "company": "Demo Company",
        "position": "Python Developer",
        "status": "Applied",
        "source": "LinkedIn",
        "contact_person": "HR Manager",
        "next_action": "Follow up next week",
        "application_link": "https://example.com/jobs/123",
        "notes": "This is a test entry from the hackathon demo"
    }
    
    # Get sheet ID from env or use default
    sheet_id = os.getenv("SHEET_ID", "1Pf2DhcyiHcRb03ue8LxXemqQe33mArsElXztMG0-2QY")
    sheet_tab = os.getenv("SHEET_TAB", "Applications")
    
    print(f"Using sheet ID: {sheet_id}")
    print(f"Using sheet tab: {sheet_tab}")
    print("Running job tracker with sample job data...")
    
    orch = CareerCopilotOrchestrator()
    
    try:
        result = orch.update_job_tracker(job_data, sheet_id, sheet_tab)
        
        if "error" in result:
            print(f"\n❌ Error: {result['error']}")
            if "raw" in result:
                print("\nRaw output:")
                print(result["raw"])
        elif "success" in result and result["success"]:
            print("\n✅ Success! Job tracker update successful.")
            if "demo_mode" in result and result["demo_mode"]:
                print("\n[DEMO MODE] Data was processed but not written to actual sheet")
            else:
                print(f"\nRows appended: {result.get('row_count_appended', 'unknown')}")
            
            print(f"\nMessage: {result.get('message', 'No message')}")
            
            # Write to file for inspection
            with open("job_tracker_test_output.json", "w") as f:
                json.dump(result, f, indent=2)
            print("\nFull output written to 'job_tracker_test_output.json'")
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
