#!/usr/bin/env python3
"""
Script to list AgentCore Gateway targets.

Prerequisites:
- gateway_config.json (from gateway creation)
"""

import json
import boto3

print("="*80)
print("LISTING GATEWAY TARGETS")
print("="*80)

# Load configuration
print("\n📝 Loading gateway configuration...")
print("-"*80)

with open('gateway_config.json') as f:
    gateway_config = json.load(f)
    print(f"✓ Loaded gateway config")
    print(f"  Gateway ID: {gateway_config['gateway_id']}")
    print(f"  Gateway Name: {gateway_config['name']}")

# Initialize AgentCore control plane client
gateway_client = boto3.client("bedrock-agentcore-control", region_name='us-west-2')

# List targets using correct API method
print(f"\n📝 Retrieving targets from gateway...")
print("-"*80)

response = gateway_client.list_gateway_targets(
    gatewayIdentifier=gateway_config["gateway_id"]
)

targets = response.get("items", [])

print(f"✓ Found {len(targets)} target(s)")

# Display targets
if targets:
    print("\n" + "="*80)
    print("GATEWAY TARGETS")
    print("="*80)
    
    for i, target in enumerate(targets, 1):
        print(f"\n{i}. {target.get('name', 'N/A')}")
        print(f"   {'─'*76}")
        print(f"   Target ID: {target.get('targetId', 'N/A')}")
        print(f"   Status: {target.get('status', 'unknown')}")
        print(f"   Description: {target.get('description', 'N/A')}")
        
        # Display target configuration if available
        if 'targetConfiguration' in target:
            config = target['targetConfiguration']
            if 'mcp' in config and 'lambda' in config['mcp']:
                lambda_config = config['mcp']['lambda']
                print(f"   Lambda ARN: {lambda_config.get('lambdaArn', 'N/A')}")
                
                # Display tool schema if available
                if 'toolSchema' in lambda_config:
                    tool_schema = lambda_config['toolSchema']
                    if 'inlinePayload' in tool_schema:
                        tools = tool_schema['inlinePayload']
                        print(f"   Tools: {len(tools)}")
                        for tool in tools:
                            print(f"     - {tool.get('name', 'N/A')}: {tool.get('description', 'N/A')[:60]}...")
else:
    print("\n⚠️  No targets found in gateway")

# Summary
print("\n" + "="*80)
print("✓ TARGET LISTING COMPLETE")
print("="*80)
print(f"\nGateway: {gateway_config['name']}")
print(f"Gateway ID: {gateway_config['gateway_id']}")
print(f"Total Targets: {len(targets)}")
print("="*80)
