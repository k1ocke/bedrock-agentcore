#!/usr/bin/env python3
"""
Test script for memory-enabled returns agent.

This script tests if the agent can recall customer preferences and history
from AgentCore Memory.
"""

import os
import sys
import json
import importlib.util

# Load configuration files
print("="*80)
print("LOADING CONFIGURATION")
print("="*80)

# Load Memory ID
try:
    with open('memory_config.json') as f:
        memory_config = json.load(f)
        memory_id = memory_config['memory_id']
        print(f"✓ Memory ID loaded: {memory_id}")
except FileNotFoundError:
    print("❌ Error: memory_config.json not found")
    sys.exit(1)

# Load Knowledge Base ID
try:
    with open('kb_config.json') as f:
        kb_config = json.load(f)
        kb_id = kb_config['knowledge_base_id']
        print(f"✓ Knowledge Base ID loaded: {kb_id}")
except FileNotFoundError:
    print("❌ Error: kb_config.json not found")
    sys.exit(1)

# Set environment variables (the agent will also load from config files)
os.environ["MEMORY_ID"] = memory_id
os.environ["KNOWLEDGE_BASE_ID"] = kb_id

print("="*80)

# Import run_agent from 06_memory_enabled_agent.py using importlib
print("\nImporting memory-enabled agent...")
spec = importlib.util.spec_from_file_location("memory_agent", "06_memory_enabled_agent.py")
memory_agent = importlib.util.module_from_spec(spec)
sys.modules["memory_agent"] = memory_agent
spec.loader.exec_module(memory_agent)

# Get the run_agent function
run_agent = memory_agent.run_agent

print("✓ Agent imported successfully")
print("="*80)

# Test with user_001
print("\n" + "="*80)
print("TESTING MEMORY-ENABLED AGENT WITH USER_001")
print("="*80)
print("\nCustomer: user_001")
print("Session: session_test_001")
print("\nQuestion: 'Hi! I'm thinking about returning something. What do you remember about my preferences?'")
print("\n" + "-"*80)
print("AGENT RESPONSE:")
print("-"*80 + "\n")

try:
    # Run the agent with user_001's question
    response = run_agent(
        user_input="Hi! I'm thinking about returning something. What do you remember about my preferences?",
        session_id="session_test_001",
        actor_id="user_001"
    )
    
    print(response)
    
    print("\n" + "="*80)
    print("MEMORY RECALL ANALYSIS")
    print("="*80)
    
    # Check if the agent mentioned key information from memory
    response_lower = response.lower()
    
    print("\n✓ Checking what the agent remembered:")
    print("-"*80)
    
    # Check for email preference
    if "email" in response_lower:
        print("✅ Email notification preference: RECALLED")
    else:
        print("❌ Email notification preference: NOT MENTIONED")
    
    # Check for laptop return history
    if "laptop" in response_lower or "defective" in response_lower:
        print("✅ Previous laptop return: RECALLED")
    else:
        print("❌ Previous laptop return: NOT MENTIONED")
    
    # Check for personalization
    if any(word in response_lower for word in ["remember", "recall", "previous", "preference", "history"]):
        print("✅ Personalized response: YES")
    else:
        print("⚠️  Personalized response: UNCLEAR")
    
    print("\n" + "="*80)
    print("✓ Memory-enabled agent test complete!")
    print("="*80)
    
except Exception as e:
    print(f"\n❌ Error running agent: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
