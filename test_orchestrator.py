#!/usr/bin/env python3

from app.orchestrator import CareerCopilotOrchestrator

def test_orchestrator():
    print("Creating orchestrator...")
    try:
        orchestrator = CareerCopilotOrchestrator()
        print("✅ Orchestrator created successfully")
        
        print("Getting available tools...")
        tools = orchestrator.get_available_tools()
        print(f"✅ Found {len(tools)} tools")
        
        if tools:
            print("Available tools:")
            for i, tool in enumerate(tools[:10]):  # Show first 10 tools
                print(f"  {i+1}. {tool}")
        else:
            print("❌ No tools available")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_orchestrator()
