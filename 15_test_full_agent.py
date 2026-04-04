"""
Test script for the full-featured returns agent with Memory, Gateway, and Knowledge Base
Tests all integrations: custom tools, memory recall, gateway tool invocation, and KB retrieval
"""

import sys
import importlib.util

# Import the full agent
spec = importlib.util.spec_from_file_location("full_agent", "14_full_agent.py")
full_agent = importlib.util.module_from_spec(spec)
sys.modules["full_agent"] = full_agent
spec.loader.exec_module(full_agent)

def test_agent(query: str, actor_id: str = "default-actor", session_id: str = "default-session"):
    """Test the agent with a query"""
    print("\n" + "="*80)
    print(f"QUERY: {query}")
    print(f"Actor: {actor_id}, Session: {session_id}")
    print("="*80)
    
    try:
        response = full_agent.run_agent(query, session_id=session_id, actor_id=actor_id)
        print("\nRESPONSE:")
        print("-"*80)
        print(response)
        print("-"*80)
        return response
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("\n" + "="*80)
    print("TESTING FULL-FEATURED RETURNS AGENT")
    print("="*80)
    print("\nThis test will verify:")
    print("✓ Custom tools (check_return_eligibility, calculate_refund_amount, format_policy_response)")
    print("✓ Built-in tools (current_time, retrieve)")
    print("✓ Memory integration (recall user_001's preferences and history)")
    print("✓ Gateway integration (lookup_order tool via Lambda)")
    print("✓ Knowledge Base integration (retrieve tool)")
    
    # Test 1: Memory recall with user_001
    print("\n" + "="*80)
    print("TEST 1: Memory Recall")
    print("="*80)
    test_agent(
        "Hi! I'm thinking about returning something. What do you remember about my preferences?",
        actor_id="user_001",
        session_id="test-session-1"
    )
    
    # Test 2: Gateway tool - Order lookup
    print("\n" + "="*80)
    print("TEST 2: Gateway Tool - Order Lookup")
    print("="*80)
    test_agent(
        "Can you look up order ORD-001 for me?",
        actor_id="user_001",
        session_id="test-session-1"
    )
    
    # Test 3: Custom tool - Return eligibility
    print("\n" + "="*80)
    print("TEST 3: Custom Tool - Return Eligibility")
    print("="*80)
    test_agent(
        "Can I return a laptop I purchased on 2026-03-15?",
        actor_id="user_001",
        session_id="test-session-1"
    )
    
    # Test 4: Custom tool - Refund calculation
    print("\n" + "="*80)
    print("TEST 4: Custom Tool - Refund Calculation")
    print("="*80)
    test_agent(
        "Calculate my refund for a $500 item in opened condition that I'm returning because I changed my mind",
        actor_id="user_001",
        session_id="test-session-1"
    )
    
    # Test 5: Knowledge Base retrieval
    print("\n" + "="*80)
    print("TEST 5: Knowledge Base Retrieval")
    print("="*80)
    test_agent(
        "What's the return policy for electronics?",
        actor_id="user_001",
        session_id="test-session-1"
    )
    
    # Test 6: Combined - Gateway + Custom tools
    print("\n" + "="*80)
    print("TEST 6: Combined - Gateway + Custom Tools")
    print("="*80)
    test_agent(
        "Look up order ORD-002 and tell me if I can still return it. If yes, calculate the refund assuming it's in used condition.",
        actor_id="user_001",
        session_id="test-session-1"
    )
    
    # Test 7: Current time tool
    print("\n" + "="*80)
    print("TEST 7: Built-in Tool - Current Time")
    print("="*80)
    test_agent(
        "What time is it?",
        actor_id="user_001",
        session_id="test-session-1"
    )
    
    # Test 8: All integrations together
    print("\n" + "="*80)
    print("TEST 8: All Integrations Together")
    print("="*80)
    test_agent(
        "Look up order ORD-003, check if it's eligible for return, calculate the refund for a defective item in new condition, and remind me of my communication preferences.",
        actor_id="user_001",
        session_id="test-session-1"
    )
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETED")
    print("="*80)
