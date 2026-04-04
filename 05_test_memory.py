#!/usr/bin/env python3
"""
Script to test memory retrieval for user_001.

This script demonstrates what the agent remembers about the customer
by retrieving memories from different namespaces.
"""

import json

try:
    from bedrock_agentcore.memory import MemoryClient
except ImportError:
    print("✗ Error: bedrock_agentcore package not found")
    print("  Install with: pip install bedrock-agentcore")
    exit(1)

# Load memory_id from config
with open('memory_config.json') as f:
    config = json.load(f)
    memory_id = config['memory_id']

print("="*80)
print("TESTING MEMORY RETRIEVAL FOR USER_001")
print("="*80)
print(f"Memory ID: {memory_id}")
print(f"Region: us-west-2")
print(f"Customer: user_001")
print("="*80)

# Create memory client
memory_client = MemoryClient(region_name='us-west-2')

# ============================================================================
# RETRIEVE PREFERENCES
# ============================================================================
print("\n📋 RETRIEVING PREFERENCES")
print("Namespace: app/user_001/preferences")
print("Query: 'customer preferences and communication'")
print("-"*80)

try:
    preferences = memory_client.retrieve_memories(
        memory_id=memory_id,
        namespace="app/user_001/preferences",
        query="customer preferences and communication",
        top_k=5
    )
    
    if preferences:
        print(f"✓ Retrieved {len(preferences)} preference(s)\n")
        
        for i, memory in enumerate(preferences, 1):
            print(f"Preference {i}:")
            print(f"{'─'*80}")
            
            content = memory.get('content', {})
            if isinstance(content, dict):
                text = content.get('text', 'N/A')
            else:
                text = str(content)
            
            print(f"Content: {text}")
            
            # Display relevance score
            relevance = memory.get('relevanceScore', 'N/A')
            if isinstance(relevance, (int, float)):
                print(f"Relevance Score: {relevance:.3f}")
            else:
                print(f"Relevance Score: {relevance}")
            print()
    else:
        print("⚠️  No preferences found")
        print("Memory extraction may still be processing (takes 20-30 seconds)\n")
        
except Exception as e:
    print(f"❌ Error retrieving preferences: {e}\n")

# ============================================================================
# RETRIEVE SEMANTIC FACTS
# ============================================================================
print("\n📋 RETRIEVING SEMANTIC FACTS")
print("Namespace: app/user_001/semantic")
print("Query: 'return history and purchases'")
print("-"*80)

try:
    semantic = memory_client.retrieve_memories(
        memory_id=memory_id,
        namespace="app/user_001/semantic",
        query="return history and purchases",
        top_k=5
    )
    
    if semantic:
        print(f"✓ Retrieved {len(semantic)} semantic fact(s)\n")
        
        for i, memory in enumerate(semantic, 1):
            print(f"Fact {i}:")
            print(f"{'─'*80}")
            
            content = memory.get('content', {})
            if isinstance(content, dict):
                text = content.get('text', 'N/A')
            else:
                text = str(content)
            
            print(f"Content: {text}")
            
            relevance = memory.get('relevanceScore', 'N/A')
            if isinstance(relevance, (int, float)):
                print(f"Relevance Score: {relevance:.3f}")
            else:
                print(f"Relevance Score: {relevance}")
            print()
    else:
        print("⚠️  No semantic facts found\n")
        
except Exception as e:
    print(f"❌ Error retrieving semantic facts: {e}\n")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*80)
print("WHAT THE AGENT REMEMBERS ABOUT USER_001:")
print("="*80)

if preferences:
    print("\n✓ Customer Preferences:")
    for i, pref in enumerate(preferences, 1):
        content = pref.get('content', {})
        text = content.get('text', str(content)) if isinstance(content, dict) else str(content)
        # Try to parse JSON if it's a string
        try:
            pref_data = json.loads(text) if isinstance(text, str) and text.startswith('{') else {'preference': text}
            print(f"  {i}. {pref_data.get('preference', text)}")
        except:
            print(f"  {i}. {text}")

if semantic:
    print("\n✓ Known Facts:")
    for i, fact in enumerate(semantic, 1):
        content = fact.get('content', {})
        text = content.get('text', str(content)) if isinstance(content, dict) else str(content)
        print(f"  {i}. {text}")

print("\n" + "="*80)
print("✓ Memory retrieval test complete!")
print("="*80)
