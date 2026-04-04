#!/usr/bin/env python3
"""
Script to check AgentCore Runtime deployment status.
Monitors until READY or FAILED state.
"""

import json
import os
import time
from bedrock_agentcore_starter_toolkit import Runtime

print("="*80)
print("AGENTCORE RUNTIME STATUS CHECK")
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

# Load configuration files
with open('runtime_execution_role_config.json') as f:
    role_config = json.load(f)
with open('cognito_config.json') as f:
    cognito_config = json.load(f)

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
print(f"✓ Entrypoint: {entrypoint}")

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
print("\n" + "="*80)
print("LOADING RUNTIME CONFIGURATION")
print("="*80)

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

print("✓ Configuration loaded")

# Monitor status until READY or FAILED
print("\n" + "="*80)
print("MONITORING DEPLOYMENT STATUS")
print("="*80)

max_attempts = 30  # Monitor for up to 5 minutes (30 * 10 seconds)
attempt = 0
previous_status = None

while attempt < max_attempts:
    try:
        # Check status
        status_response = runtime.status()
        status = status_response.endpoint["status"]
        
        # Only print if status changed
        if status != previous_status:
            timestamp = time.strftime("%H:%M:%S")
            print(f"\n[{timestamp}] Status: {status}")
            previous_status = status
        
        # Check terminal states
        if status == "READY":
            print("\n" + "="*80)
            print("✅ AGENT IS READY!")
            print("="*80)
            print(f"\nAgent ARN: {runtime_deployed_config['agent_arn']}")
            print(f"Region: us-west-2")
            print(f"Status: {status}")
            print("\nEndpoint Details:")
            print(json.dumps(status_response.endpoint, indent=2, default=str))
            print("\n" + "="*80)
            print("NEXT STEPS")
            print("="*80)
            print("\n1. Test your agent:")
            print("   Create a script to invoke the agent with test queries")
            print("\n2. View logs:")
            print(f"   aws logs tail /aws/bedrock-agentcore/runtimes/{agent_name}-* --follow")
            print("\n3. Monitor in CloudWatch:")
            print("   https://console.aws.amazon.com/cloudwatch/home?region=us-west-2#gen-ai-observability/agent-core")
            print("="*80)
            exit(0)
        
        elif status in ["CREATE_FAILED", "UPDATE_FAILED", "FAILED"]:
            print("\n" + "="*80)
            print("❌ DEPLOYMENT FAILED!")
            print("="*80)
            print(f"\nAgent ARN: {runtime_deployed_config['agent_arn']}")
            print(f"Status: {status}")
            print("\nEndpoint Details:")
            print(json.dumps(status_response.endpoint, indent=2, default=str))
            print("\n" + "="*80)
            print("TROUBLESHOOTING")
            print("="*80)
            print("\n1. Check CloudWatch logs for error details:")
            print(f"   aws logs tail /aws/bedrock-agentcore/runtimes/{agent_name}-* --since 1h")
            print("\n2. Verify IAM role permissions:")
            print(f"   Role ARN: {role_config['role_arn']}")
            print("\n3. Check CodeBuild logs for build errors")
            print("\n4. Verify all configuration files are correct")
            print("="*80)
            exit(1)
        
        elif status in ["CREATING", "UPDATING"]:
            # Still in progress
            if attempt == 0:
                print(f"\n⏳ Deployment in progress...")
                print(f"   This may take a few minutes")
                print(f"   Checking every 10 seconds...")
            else:
                # Print a dot to show progress
                print(".", end="", flush=True)
            
            attempt += 1
            time.sleep(10)
        
        else:
            print(f"\n⚠️  Unknown status: {status}")
            print(f"   Continuing to monitor...")
            attempt += 1
            time.sleep(10)
    
    except Exception as e:
        print(f"\n❌ Error checking status: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

# Timeout reached
print("\n\n" + "="*80)
print("⏱️  MONITORING TIMEOUT")
print("="*80)
print(f"\nStatus check timed out after {max_attempts * 10} seconds")
print(f"Last known status: {previous_status}")
print("\nThe deployment may still be in progress.")
print("Run this script again to continue monitoring.")
print("="*80)
