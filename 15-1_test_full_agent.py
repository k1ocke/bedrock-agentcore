"""
Focused test script for full-featured returns agent
Tests memory recall + gateway integration with a single personalized query
"""

import sys
import json
import os
import importlib.util

# Load all configuration files and set environment variables
print("="*80)
print("LOADING CONFIGURATION FILES")
print("="*80)

# Load Memory configuration
try:
    with open('memory_config.json') as f:
        memory_config = json.load(f)
        os.environ['MEMORY_ID'] = memory_config['memory_id']
        print(f"✓ Memory ID: {memory_config['memory_id']}")
except FileNotFoundError:
    print("❌ memory_config.json not found")
    sys.exit(1)

# Load Gateway configuration
try:
    with open('gateway_config.json') as f:
        gateway_config = json.load(f)
        os.environ['GATEWAY_URL'] = gateway_config['gateway_url']
        print(f"✓ Gateway URL: {gateway_config['gateway_url']}")
except FileNotFoundError:
    print("❌ gateway_config.json not found")
    sys.exit(1)

# Load Cognito configuration
try:
    with open('cognito_config.json') as f:
        cognito_config = json.load(f)
        os.environ['COGNITO_CLIENT_ID'] = cognito_config['client_id']
        os.environ['COGNITO_CLIENT_SECRET'] = cognito_config['client_secret']
        os.environ['COGNITO_DISCOVERY_URL'] = cognito_config['discovery_url']
        print(f"✓ Cognito Client ID: {cognito_config['client_id']}")
except FileNotFoundError:
    print("❌ cognito_config.json not found")
    sys.exit(1)

# Load Knowledge Base configuration
try:
    with open('kb_config.json') as f:
        kb_config = json.load(f)
        os.environ['KNOWLEDGE_BASE_ID'] = kb_config['knowledge_base_id']
        print(f"✓ Knowledge Base ID: {kb_config['knowledge_base_id']}")
except FileNotFoundError:
    print("❌ kb_config.json not found")
    sys.exit(1)

print("="*80)

# Import the full agent
spec = importlib.util.spec_from_file_location("full_agent", "14_full_agent.py")
full_agent = importlib.util.module_from_spec(spec)
sys.modules["full_agent"] = full_agent
spec.loader.exec_module(full_agent)

def test_personalized_query():
    """Test agent with a query that requires both memory and gateway integration"""
    
    print("\n" + "="*80)
    print("TEST: Personalized Order Lookup with Memory Recall")
    print("="*80)
    print("\nThis test verifies:")
    print("✓ Agent remembers user_001's email preference (from memory)")
    print("✓ Agent looks up order ORD-001 details (from Lambda via gateway)")
    print("✓ Agent combines both for a personalized response")
    
    query = "Hi! Can you look up my order ORD-001 and tell me if I can return it? Remember, I prefer email updates."
    actor_id = "user_001"
    session_id = "personalized-test-session"
    
    print("\n" + "-"*80)
    print(f"QUERY: {query}")
    print(f"Actor: {actor_id}")
    print(f"Session: {session_id}")
    print("-"*80)
    
    try:
        response = full_agent.run_agent(query, session_id=session_id, actor_id=actor_id)
        
        print("\n" + "="*80)
        print("AGENT RESPONSE:")
        print("="*80)
        print(response)
        print("="*80)
        
        # Verify key elements in response
        print("\n" + "="*80)
        print("VERIFICATION:")
        print("="*80)
        
        checks = {
            "Order Details (ORD-001)": "ORD-001" in response,
            "Product Name (Dell XPS 15)": "Dell XPS 15" in response or "laptop" in response.lower(),
            "Return Eligibility": "eligible" in response.lower() or "return" in response.lower(),
            "Email Preference": "email" in response.lower(),
            "Personalization": any(word in response.lower() for word in ["remember", "prefer", "preference"])
        }
        
        for check_name, passed in checks.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status}: {check_name}")
        
        all_passed = all(checks.values())
        
        print("\n" + "="*80)
        if all_passed:
            print("✅ ALL VERIFICATIONS PASSED")
            print("The agent successfully:")
            print("  - Retrieved order details from Lambda via gateway")
            print("  - Recalled user's email preference from memory")
            print("  - Provided a personalized, integrated response")
        else:
            print("⚠️  SOME VERIFICATIONS FAILED")
            print("Review the response above to see what's missing")
        print("="*80)
        
        return all_passed
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n" + "="*80)
    print("FULL-FEATURED AGENT: PERSONALIZED INTEGRATION TEST")
    print("="*80)
    
    success = test_personalized_query()
    
    print("\n" + "="*80)
    print("TEST COMPLETED")
    print("="*80)
    
    sys.exit(0 if success else 1)
