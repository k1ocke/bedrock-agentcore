#!/usr/bin/env python3
"""
Script to seed AgentCore Memory with sample customer conversations.

This script adds two sample conversations for user_001:
1. Customer mentions email preference and previous laptop return
2. Customer asks about return windows for electronics
"""

import json
import time

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

print(f"Using Memory ID: {memory_id}")
print(f"Customer ID: user_001")
print("="*80)

# Create memory client
memory_client = MemoryClient(region_name='us-west-2')

# ============================================================================
# CONVERSATION 1: Customer preferences and previous return
# ============================================================================
print("\n📝 Storing Conversation 1: Email preference and laptop return history")
print("-"*80)

messages_1 = [
    [
        "I prefer to receive notifications via email. Also, I previously returned a defective laptop last month.",
        "USER"
    ],
    [
        "Thank you for letting me know! I've noted your preference for email notifications. I can see you had a previous return experience with a defective laptop. How can I help you today with returns or refunds?",
        "ASSISTANT"
    ]
]

memory_client.create_event(
    memory_id=memory_id,
    actor_id="user_001",
    session_id="session_001",
    messages=messages_1
)

print(f"✓ Stored {len(messages_1)} messages from session_001")

# ============================================================================
# CONVERSATION 2: Return window inquiry
# ============================================================================
print("\n📝 Storing Conversation 2: Return window inquiry")
print("-"*80)

messages_2 = [
    [
        "What are the return windows for electronics? I want to make sure I understand the policy.",
        "USER"
    ],
    [
        "For most electronics, Amazon offers a 30-day return window from the date of delivery. However, some items like Amazon Digital Devices (Echo, Alexa, Fire TV Stick, Kindle) have a 7-day replacement-only policy. Items must be in original condition with all accessories and packaging. Would you like more specific information about a particular type of electronic device?",
        "ASSISTANT"
    ]
]

memory_client.create_event(
    memory_id=memory_id,
    actor_id="user_001",
    session_id="session_002",
    messages=messages_2
)

print(f"✓ Stored {len(messages_2)} messages from session_002")

# ============================================================================
# WAIT FOR MEMORY PROCESSING
# ============================================================================
print("\n" + "="*80)
print("⏳ Waiting 30 seconds for memory processing...")
print("   Memory system is extracting:")
print("   - User preferences (email notifications)")
print("   - Semantic facts (previous laptop return)")
print("   - Conversation summaries")
print("="*80)

time.sleep(30)

print("\n✓ Memory seeding complete!")
print(f"✓ Total conversations stored: 2")
print(f"✓ Total messages stored: {len(messages_1) + len(messages_2)}")
print(f"✓ Memory processing complete!")
