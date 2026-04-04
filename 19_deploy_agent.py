#!/usr/bin/env python3
"""
Script to deploy returns agent to AgentCore Runtime.

This script:
1. Loads all configuration files
2. Configures runtime deployment settings
3. Sets environment variables
4. Deploys to AgentCore Runtime
5. Saves agent ARN to runtime_config.json
"""

import json
import os
from bedrock_agentcore_starter_toolkit import Runtime

print("="*80)
print("AGENTCORE RUNTIME DEPLOYMENT")
print("="*80)

# ============================================================================
# STEP 1: Load all configuration files
# ============================================================================

print("\n1. Loading configuration files...")

# Load Memory configuration
try:
    with open('memory_config.json') as f:
        memory_config = json.load(f)
        print(f"   ✓ Memory ID: {memory_config['memory_id']}")
except FileNotFoundError:
    print("   ❌ Error: memory_config.json not found")
    exit(1)

# Load Gateway configuration
try:
    with open('gateway_config.json') as f:
        gateway_config = json.load(f)
        print(f"   ✓ Gateway URL: {gateway_config['gateway_url']}")
except FileNotFoundError:
    print("   ❌ Error: gateway_config.json not found")
    exit(1)

# Load Cognito configuration
try:
    with open('cognito_config.json') as f:
        cognito_config = json.load(f)
        print(f"   ✓ Cognito Client ID: {cognito_config['client_id']}")
except FileNotFoundError:
    print("   ❌ Error: cognito_config.json not found")
    exit(1)

# Load Runtime Execution Role configuration
try:
    with open('runtime_execution_role_config.json') as f:
        role_config = json.load(f)
        print(f"   ✓ Execution Role ARN: {role_config['role_arn']}")
except FileNotFoundError:
    print("   ❌ Error: runtime_execution_role_config.json not found")
    exit(1)

# Load Knowledge Base configuration
try:
    with open('kb_config.json') as f:
        kb_config = json.load(f)
        print(f"   ✓ Knowledge Base ID: {kb_config['knowledge_base_id']}")
except FileNotFoundError:
    print("   ❌ Error: kb_config.json not found")
    exit(1)

# ============================================================================
# STEP 2: Configure runtime deployment settings
# ============================================================================

print("\n2. Configuring AgentCore Runtime deployment...")

# Initialize Runtime
runtime = Runtime()

# Build authorizer configuration for Cognito JWT
auth_config = {
    "customJWTAuthorizer": {
        "allowedClients": [cognito_config["client_id"]],
        "discoveryUrl": cognito_config["discovery_url"]
    }
}

# Configure runtime deployment
runtime.configure(
    entrypoint="17_runtime_agent.py",
    agent_name="returns_refunds_agent",
    execution_role=role_config["role_arn"],
    auto_create_ecr=True,
    memory_mode="NO_MEMORY",  # Memory is handled via environment variables
    requirements_file="requirements.txt",
    region="us-west-2",
    authorizer_configuration=auth_config
)

print("   ✓ Runtime configured successfully")
print("   ✓ Configuration saved to .bedrock_agentcore.yaml")

# ============================================================================
# STEP 3: Build environment variables
# ============================================================================

print("\n3. Setting environment variables...")

env_vars = {
    "MEMORY_ID": memory_config["memory_id"],
    "KNOWLEDGE_BASE_ID": kb_config["knowledge_base_id"],
    "GATEWAY_URL": gateway_config["gateway_url"],
    "COGNITO_CLIENT_ID": cognito_config["client_id"],
    "COGNITO_CLIENT_SECRET": cognito_config["client_secret"],
    "COGNITO_DISCOVERY_URL": cognito_config["discovery_url"],
    "OAUTH_SCOPES": "returns-gateway/read returns-gateway/write"
}

print("\n   Environment variables:")
for key in env_vars:
    if "SECRET" in key:
        print(f"     {key}: ***")
    else:
        print(f"     {key}: {env_vars[key]}")

# ============================================================================
# STEP 4: Deploy to AgentCore Runtime
# ============================================================================

print("\n" + "="*80)
print("LAUNCHING AGENT TO AGENTCORE RUNTIME")
print("="*80)
print("\nThis process will:")
print("  1. Create CodeBuild project")
print("  2. Build Docker container from your agent code")
print("  3. Push container to Amazon ECR")
print("  4. Deploy to AgentCore Runtime")
print("\n⏱️  Expected time: 5-10 minutes")
print("\n☕ Grab a coffee while the deployment runs...")
print("="*80)

try:
    launch_result = runtime.launch(
        env_vars=env_vars,
        auto_update_on_conflict=True
    )
    
    agent_arn = launch_result.agent_arn
    
    print("\n" + "="*80)
    print("✓ DEPLOYMENT INITIATED SUCCESSFULLY!")
    print("="*80)
    print(f"\nAgent ARN: {agent_arn}")
    
    # ============================================================================
    # STEP 5: Save agent ARN to runtime_config.json
    # ============================================================================
    
    print("\n5. Saving runtime configuration...")
    
    runtime_output_config = {
        "agent_arn": agent_arn,
        "agent_name": "returns_refunds_agent",
        "region": "us-west-2",
        "memory_id": memory_config["memory_id"],
        "gateway_url": gateway_config["gateway_url"],
        "knowledge_base_id": kb_config["knowledge_base_id"]
    }
    
    with open('runtime_config.json', 'w') as f:
        json.dump(runtime_output_config, f, indent=2)
    
    print("   ✓ Configuration saved to runtime_config.json")
    
    # ============================================================================
    # Next Steps
    # ============================================================================
    
    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    print("\n1. Monitor deployment status:")
    print("   The agent is being built and deployed in the background")
    print("   This may take 5-10 minutes to complete")
    print("\n2. Check status:")
    print("   Create a script to check runtime status using:")
    print("   runtime.status()")
    print("\n3. Wait for status 'READY':")
    print("   The agent must be in READY state before you can invoke it")
    print("\n4. Once READY, test your agent:")
    print("   Create a script to invoke the agent with test queries")
    print("\n" + "="*80)
    print("DEPLOYMENT SUMMARY")
    print("="*80)
    print(f"  Agent Name: returns_refunds_agent")
    print(f"  Agent ARN: {agent_arn}")
    print(f"  Region: us-west-2")
    print(f"  Entrypoint: 17_runtime_agent.py")
    print(f"  Memory: {memory_config['memory_id']}")
    print(f"  Gateway: {gateway_config['gateway_url']}")
    print(f"  Knowledge Base: {kb_config['knowledge_base_id']}")
    print("="*80)

except Exception as e:
    print(f"\n❌ Deployment failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
