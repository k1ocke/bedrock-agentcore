#!/usr/bin/env python3
"""
Script to create AgentCore Gateway.

Prerequisites:
- cognito_config.json (from Cognito setup)
- gateway_role_config.json (from IAM role setup)
"""

import json
import boto3

print("="*80)
print("CREATING AGENTCORE GATEWAY")
print("="*80)

# Load configuration
print("\n📝 Loading configuration files...")
print("-"*80)

with open('cognito_config.json') as f:
    cognito_config = json.load(f)
    print(f"✓ Loaded Cognito config")
    print(f"  Client ID: {cognito_config['client_id']}")
    print(f"  Discovery URL: {cognito_config['discovery_url']}")

with open('gateway_role_config.json') as f:
    role_config = json.load(f)
    print(f"✓ Loaded IAM role config")
    print(f"  Role ARN: {role_config['role_arn']}")

# Initialize AgentCore control plane client
gateway_client = boto3.client("bedrock-agentcore-control", region_name='us-west-2')

# Build auth configuration for Cognito JWT
auth_config = {
    "customJWTAuthorizer": {
        "allowedClients": [cognito_config["client_id"]],
        "discoveryUrl": cognito_config["discovery_url"]
    }
}

# Create gateway
print("\n📝 Creating AgentCore Gateway...")
print("-"*80)
print(f"Name: ReturnsRefundsGateway")
print(f"Protocol: MCP")
print(f"Authorizer: CUSTOM_JWT (Cognito)")

create_response = gateway_client.create_gateway(
    name="ReturnsRefundsGateway",
    roleArn=role_config["role_arn"],
    protocolType="MCP",
    authorizerType="CUSTOM_JWT",
    authorizerConfiguration=auth_config,
    description="Gateway for returns and refunds agent to access order lookup tools"
)

# Extract gateway details
gateway_id = create_response["gatewayId"]
gateway_url = create_response["gatewayUrl"]
gateway_arn = create_response["gatewayArn"]

print(f"✓ Gateway created successfully!")
print(f"  Gateway ID: {gateway_id}")
print(f"  Gateway URL: {gateway_url}")
print(f"  Gateway ARN: {gateway_arn}")

# Save gateway config
print("\n📝 Saving configuration to gateway_config.json...")
print("-"*80)

config = {
    "id": gateway_id,
    "gateway_id": gateway_id,
    "gateway_url": gateway_url,
    "gateway_arn": gateway_arn,
    "name": "ReturnsRefundsGateway",
    "region": "us-west-2"
}

with open('gateway_config.json', 'w') as f:
    json.dump(config, f, indent=2)

print(f"✓ Configuration saved to gateway_config.json")

# Summary
print("\n" + "="*80)
print("✓ GATEWAY SETUP COMPLETE!")
print("="*80)
print(f"\nGateway ID: {gateway_id}")
print(f"Gateway URL: {gateway_url}")
print(f"\nAuthentication: Cognito JWT")
print(f"Protocol: MCP")
print("\n" + "="*80)
print("✓ Ready to add Lambda targets!")
print("="*80)
