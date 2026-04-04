#!/usr/bin/env python3
"""
Script to add Lambda target to AgentCore Gateway.

Prerequisites:
- gateway_config.json (from gateway creation)
- lambda_config.json (from Lambda creation)
"""

import json
import boto3

print("="*80)
print("ADDING LAMBDA TARGET TO GATEWAY")
print("="*80)

# Load configuration files
print("\n📝 Loading configuration files...")
print("-"*80)

with open('gateway_config.json') as f:
    gateway_config = json.load(f)
    print(f"✓ Loaded gateway config")
    print(f"  Gateway ID: {gateway_config['gateway_id']}")

with open('lambda_config.json') as f:
    lambda_config = json.load(f)
    print(f"✓ Loaded Lambda config")
    print(f"  Function ARN: {lambda_config['function_arn']}")
    print(f"  Tool Name: {lambda_config['tool_name']}")

# Initialize AgentCore control plane client
gateway_client = boto3.client("bedrock-agentcore-control", region_name='us-west-2')

# Extract Lambda ARN and tool schema from config
lambda_arn = lambda_config['function_arn']
tool_schema = [lambda_config['tool_schema']]

# Build Lambda target configuration with MCP protocol
lambda_target_config = {
    "mcp": {
        "lambda": {
            "lambdaArn": lambda_arn,
            "toolSchema": {
                "inlinePayload": tool_schema
            }
        }
    }
}

# Use gateway's IAM role for Lambda invocation
credential_config = [{"credentialProviderType": "GATEWAY_IAM_ROLE"}]

# Create target
print("\n📝 Adding Lambda target to gateway...")
print("-"*80)
print(f"Gateway ID: {gateway_config['gateway_id']}")
print(f"Target Name: OrderLookup")
print(f"Lambda ARN: {lambda_arn}")
print(f"Tool Name: {lambda_config['tool_name']}")

create_response = gateway_client.create_gateway_target(
    gatewayIdentifier=gateway_config["gateway_id"],
    name="OrderLookup",
    description="Lambda function for looking up order details by order ID",
    targetConfiguration=lambda_target_config,
    credentialProviderConfigurations=credential_config
)

target_id = create_response["targetId"]

print(f"\n✓ Lambda target added successfully!")
print(f"  Target ID: {target_id}")
print(f"  Target Name: OrderLookup")

# Update gateway config with target info
print("\n📝 Updating gateway_config.json with target info...")
print("-"*80)

gateway_config['target_id'] = target_id
gateway_config['target_name'] = 'OrderLookup'
gateway_config['lambda_arn'] = lambda_arn

with open('gateway_config.json', 'w') as f:
    json.dump(gateway_config, f, indent=2)

print(f"✓ Configuration updated")

# Summary
print("\n" + "="*80)
print("✓ LAMBDA TARGET SETUP COMPLETE!")
print("="*80)
print(f"\nGateway ID: {gateway_config['gateway_id']}")
print(f"Gateway URL: {gateway_config['gateway_url']}")
print(f"\nTarget ID: {target_id}")
print(f"Target Name: OrderLookup")
print(f"Tool Name: {lambda_config['tool_name']}")
print(f"\nLambda Function: {lambda_config['function_name']}")
print(f"Lambda ARN: {lambda_arn}")
print("\n" + "="*80)
print("✓ Gateway is ready for agent integration!")
print("="*80)
