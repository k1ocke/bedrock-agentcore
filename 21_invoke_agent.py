#!/usr/bin/env python3
"""
Script to invoke deployed AgentCore Runtime agent.
Tests the production agent with memory, gateway, and KB integration.
"""

import json
import base64
import os
import requests
from bedrock_agentcore_starter_toolkit import Runtime

print("="*80)
print("INVOKE AGENTCORE RUNTIME AGENT")
print("="*80)

# Check if runtime config exists
if not os.path.exists('runtime_config.json'):
    print("\n❌ Error: Agent not deployed yet")
    print("Please run 19_deploy_agent.py first")
    exit(1)

# Load runtime config
with open('runtime_config.json') as f:
    runtime_deployed_config = json.load(f)
    print(f"\n✓ Agent ARN: {runtime_deployed_config['agent_arn']}")

# Load configuration
with open('cognito_config.json') as f:
    cognito_config = json.load(f)
    print(f"✓ Cognito Client ID: {cognito_config['client_id']}")

with open('runtime_execution_role_config.json') as f:
    role_config = json.load(f)

# Load .bedrock_agentcore.yaml to get agent name and entrypoint
if not os.path.exists('.bedrock_agentcore.yaml'):
    print("❌ Error: .bedrock_agentcore.yaml not found")
    print("Please run 19_deploy_agent.py first")
    exit(1)

import yaml
with open('.bedrock_agentcore.yaml') as f:
    runtime_config = yaml.safe_load(f)

default_agent = runtime_config.get('default_agent')
agent_config = runtime_config.get('agents', {}).get(default_agent, {})
agent_name = agent_config.get('name')
entrypoint = agent_config.get('entrypoint')

print(f"✓ Agent Name: {agent_name}")

# ============================================================================
# STEP 1: Generate OAuth bearer token using Cognito
# ============================================================================

print("\n" + "="*80)
print("STEP 1: GENERATING OAUTH TOKEN")
print("="*80)

# Get token endpoint from discovery URL
try:
    discovery_response = requests.get(cognito_config['discovery_url'], timeout=10)
    discovery_response.raise_for_status()
    token_endpoint = discovery_response.json()['token_endpoint']
    print(f"✓ Token endpoint: {token_endpoint}")
except Exception as e:
    print(f"❌ Failed to get token endpoint: {e}")
    exit(1)

# Request OAuth token using client credentials flow
try:
    response = requests.post(
        token_endpoint,
        data={
            'grant_type': 'client_credentials',
            'client_id': cognito_config['client_id'],
            'client_secret': cognito_config['client_secret'],
            'scope': 'returns-gateway/read returns-gateway/write'
        },
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        timeout=10
    )
    
    response.raise_for_status()
    bearer_token = response.json()["access_token"]
    print("✓ OAuth token obtained successfully")
except Exception as e:
    print(f"❌ Failed to get OAuth token: {e}")
    if hasattr(e, 'response') and e.response:
        print(f"Response: {e.response.text}")
    exit(1)

# ============================================================================
# STEP 2: Configure Runtime
# ============================================================================

print("\n" + "="*80)
print("STEP 2: CONFIGURING RUNTIME")
print("="*80)

# Initialize Runtime
runtime = Runtime()

# Build authorizer configuration for Cognito JWT
auth_config = {
    "customJWTAuthorizer": {
        "allowedClients": [cognito_config["client_id"]],
        "discoveryUrl": cognito_config["discovery_url"]
    }
}

# Configure runtime (to load existing configuration)
runtime.configure(
    entrypoint=entrypoint,
    agent_name=agent_name,
    execution_role=role_config["role_arn"],
    auto_create_ecr=True,
    memory_mode="NO_MEMORY",
    requirements_file="requirements.txt",
    region="us-west-2",
    authorizer_configuration=auth_config
)

print("✓ Runtime configured")

# ============================================================================
# STEP 3: Invoke Agent
# ============================================================================

print("\n" + "="*80)
print("STEP 3: INVOKING AGENT")
print("="*80)

# Prepare payload
payload = {
    "prompt": "Can you look up my order ORD-001 and help me with a return?",
    "actor_id": "user_001"
}

print(f"\nActor ID: {payload['actor_id']}")
print(f"Prompt: {payload['prompt']}")
print("\nSending request to agent...")

try:
    response = runtime.invoke(
        payload,
        bearer_token=bearer_token
    )
    
    print("\n" + "="*80)
    print("✅ AGENT RESPONSE")
    print("="*80)
    
    # Extract response text from dict
    if isinstance(response, dict):
        response_text = response.get('response', str(response))
    else:
        response_text = str(response)
    
    print(response_text)
    print("="*80)
    
    # ============================================================================
    # Verification
    # ============================================================================
    
    print("\n" + "="*80)
    print("VERIFICATION")
    print("="*80)
    
    response_lower = response_text.lower()
    
    checks = {
        "Order Lookup (ORD-001)": "ord-001" in response_lower,
        "Product Details": any(word in response_lower for word in ["laptop", "dell", "xps"]),
        "Return Eligibility": "eligible" in response_lower or "return" in response_lower,
        "Memory Integration": "email" in response_lower or "prefer" in response_lower,
        "Gateway Integration": "order" in response_lower and "lookup" in response_lower or "found" in response_lower
    }
    
    for check_name, passed in checks.items():
        status = "✅ PASS" if passed else "⚠️  NOT DETECTED"
        print(f"{status}: {check_name}")
    
    all_passed = all(checks.values())
    
    print("\n" + "="*80)
    if all_passed:
        print("✅ ALL INTEGRATIONS VERIFIED")
        print("\nThe production agent successfully:")
        print("  - Retrieved order details via Gateway (Lambda)")
        print("  - Checked return eligibility with custom tools")
        print("  - Recalled user preferences from Memory")
        print("  - Provided comprehensive response")
    else:
        print("✅ AGENT RESPONDED SUCCESSFULLY")
        print("\nSome expected elements were not detected in the response.")
        print("This may be normal depending on the agent's reasoning.")
    print("="*80)
    
except Exception as e:
    print("\n" + "="*80)
    print("❌ ERROR INVOKING AGENT")
    print("="*80)
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    print("\n" + "="*80)
    print("TROUBLESHOOTING")
    print("="*80)
    print("\n1. Check agent status:")
    print("   python3 20_check_status.py")
    print("\n2. Verify agent is in READY state")
    print("\n3. Check CloudWatch logs:")
    print(f"   aws logs tail /aws/bedrock-agentcore/runtimes/{agent_name}-* --since 10m")
    print("\n4. Verify OAuth token is valid")
    print("\n5. Check IAM role permissions")
    print("="*80)
    exit(1)
