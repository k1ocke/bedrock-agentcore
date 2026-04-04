#!/usr/bin/env python3
"""
Script to verify memories were stored and processed correctly.
"""

import json
from bedrock_agentcore.memory import MemoryClient

# Load memory_id from config
with open('memory_config.json') as f:
    config = json.load(f)
    memory_id = config['memory_id']

print(f"Verifying Memory ID: {memory_id}")
print("="*80)

# Create memory client
memory_client = MemoryClient(region_name='us-west-2')

# Check preferences namespace
print("\n📋 Checking PREFERENCES namespace (app/user_001/preferences)")
print("-"*80)
try:
    preferences = memory_client.retrieve_memories(
        memory_id=memory_id,
        namespace="app/user_001/preferences",
        query="customer preferences notifications",
        top_k=5
    )
    
    if preferences:
        print(f"✓ Found {len(preferences)} preference(s)")
        for i, pref in enumerate(preferences, 1):
            content = pref.get('content', {})
            text = content.get('text', str(content)) if isinstance(content, dict) else str(content)
            print(f"  {i}. {text}")
    else:
        print("⚠️  No preferences found yet (may still be processing)")
except Exception as e:
    print(f"❌ Error: {e}")

# Check semantic namespace
print("\n📋 Checking SEMANTIC namespace (app/user_001/semantic)")
print("-"*80)
try:
    semantic = memory_client.retrieve_memories(
        memory_id=memory_id,
        namespace="app/user_001/semantic",
        query="laptop return defective",
        top_k=5
    )
    
    if semantic:
        print(f"✓ Found {len(semantic)} semantic fact(s)")
        for i, fact in enumerate(semantic, 1):
            content = fact.get('content', {})
            text = content.get('text', str(content)) if isinstance(content, dict) else str(content)
            print(f"  {i}. {text}")
    else:
        print("⚠️  No semantic facts found yet (may still be processing)")
except Exception as e:
    print(f"❌ Error: {e}")

# Check summary namespace
print("\n📋 Checking SUMMARY namespace (app/user_001/session_001/summary)")
print("-"*80)
try:
    summary = memory_client.retrieve_memories(
        memory_id=memory_id,
        namespace="app/user_001/session_001/summary",
        query="conversation summary",
        top_k=5
    )
    
    if summary:
        print(f"✓ Found {len(summary)} summary/summaries")
        for i, summ in enumerate(summary, 1):
            content = summ.get('content', {})
            text = content.get('text', str(content)) if isinstance(content, dict) else str(content)
            print(f"  {i}. {text[:200]}...")
    else:
        print("⚠️  No summaries found yet (may still be processing)")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*80)
print("✓ Memory verification complete!")
print("\nNote: If some namespaces show no results, the memory system may still be")
print("processing. Memory extraction takes 20-30 seconds after storing messages.")
