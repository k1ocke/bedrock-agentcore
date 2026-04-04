"""
Test script for returns_refunds_agent
Tests various agent capabilities with sample questions
"""

import os
import sys
import importlib.util

# Set required environment variable
os.environ["KNOWLEDGE_BASE_ID"] = "0V8NBMOVAM"

# Import run_agent from 01_returns_refunds_agent.py using importlib
spec = importlib.util.spec_from_file_location("returns_agent", "01_returns_refunds_agent.py")
returns_agent = importlib.util.module_from_spec(spec)
sys.modules["returns_agent"] = returns_agent
spec.loader.exec_module(returns_agent)

# Get the run_agent function
run_agent = returns_agent.run_agent

def print_separator():
    """Print a visual separator"""
    print("\n" + "="*80 + "\n")

def test_question(question: str, test_number: int):
    """Test a single question with the agent"""
    print(f"TEST {test_number}: {question}")
    print("-" * 80)
    try:
        response = run_agent(question)
        print(f"RESPONSE:\n{response}")
    except Exception as e:
        print(f"ERROR: {str(e)}")
    print_separator()

if __name__ == "__main__":
    print_separator()
    print("TESTING RETURNS & REFUNDS AGENT")
    print_separator()
    
    # Test 1: Current time tool
    test_question("What time is it?", 1)
    
    # Test 2: Return eligibility check
    test_question("Can I return a laptop I purchased 25 days ago?", 2)
    
    # Test 3: Refund calculation
    test_question(
        "Calculate my refund for a $500 item returned due to defect in like-new condition",
        3
    )
    
    # Test 4: Policy explanation
    test_question("Explain the return policy for electronics in a simple way", 4)
    
    # Test 5: Knowledge base retrieval
    test_question(
        "Use the retrieve tool to search the knowledge base for 'Amazon return policy for electronics'",
        5
    )
    
    # Test 6: Return eligibility for old purchase (should be ineligible)
    test_question("Can I return a iPad I purchased 3 years ago?", 6)
    
    print("="*80)
    print("ALL TESTS COMPLETED")
    print("="*80)
