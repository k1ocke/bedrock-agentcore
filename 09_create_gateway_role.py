#!/usr/bin/env python3
"""
Script to create IAM role for AgentCore Gateway.

This script creates:
- IAM role that the gateway can assume
- Policy granting permission to invoke Lambda functions
"""

import json
import boto3
from botocore.exceptions import ClientError

# Configuration
REGION = "us-west-2"
ROLE_NAME = "ReturnsGatewayRole"
POLICY_NAME = "ReturnsGatewayLambdaInvokePolicy"

print("="*80)
print("CREATING IAM ROLE FOR AGENTCORE GATEWAY")
print("="*80)
print(f"Region: {REGION}")
print(f"Role Name: {ROLE_NAME}")
print(f"Policy Name: {POLICY_NAME}")
print("="*80)

# Create IAM client
iam_client = boto3.client('iam')
sts_client = boto3.client('sts')

try:
    # Get AWS account ID
    account_id = sts_client.get_caller_identity()['Account']
    print(f"\nAWS Account ID: {account_id}")
    
    # ========================================================================
    # STEP 1: Create IAM Role
    # ========================================================================
    print(f"\n📝 Step 1: Creating IAM Role...")
    print("-"*80)
    
    # Trust policy - allows AgentCore Gateway service to assume this role
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "bedrock-agentcore.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    try:
        role_response = iam_client.create_role(
            RoleName=ROLE_NAME,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="IAM role for AgentCore Gateway to invoke Lambda functions",
            MaxSessionDuration=3600
        )
        
        role_arn = role_response['Role']['Arn']
        print(f"✓ Role created: {role_arn}")
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
            print(f"⚠️  Role '{ROLE_NAME}' already exists, retrieving ARN...")
            role_response = iam_client.get_role(RoleName=ROLE_NAME)
            role_arn = role_response['Role']['Arn']
            print(f"✓ Using existing role: {role_arn}")
        else:
            raise
    
    # ========================================================================
    # STEP 2: Create IAM Policy for Lambda Invocation
    # ========================================================================
    print(f"\n📝 Step 2: Creating IAM Policy for Lambda invocation...")
    print("-"*80)
    
    # Policy document - grants permission to invoke Lambda functions
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "lambda:InvokeFunction"
                ],
                "Resource": f"arn:aws:lambda:{REGION}:{account_id}:function:*"
            }
        ]
    }
    
    try:
        policy_response = iam_client.create_policy(
            PolicyName=POLICY_NAME,
            PolicyDocument=json.dumps(policy_document),
            Description="Allows AgentCore Gateway to invoke Lambda functions"
        )
        
        policy_arn = policy_response['Policy']['Arn']
        print(f"✓ Policy created: {policy_arn}")
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
            print(f"⚠️  Policy '{POLICY_NAME}' already exists, retrieving ARN...")
            policy_arn = f"arn:aws:iam::{account_id}:policy/{POLICY_NAME}"
            print(f"✓ Using existing policy: {policy_arn}")
        else:
            raise
    
    # ========================================================================
    # STEP 3: Attach Policy to Role
    # ========================================================================
    print(f"\n📝 Step 3: Attaching policy to role...")
    print("-"*80)
    
    try:
        iam_client.attach_role_policy(
            RoleName=ROLE_NAME,
            PolicyArn=policy_arn
        )
        print(f"✓ Policy attached to role")
    except ClientError as e:
        if e.response['Error']['Code'] == 'LimitExceeded':
            print(f"⚠️  Policy already attached to role")
        else:
            raise
    
    # ========================================================================
    # STEP 4: Save Configuration
    # ========================================================================
    print(f"\n📝 Step 4: Saving configuration to gateway_role_config.json...")
    print("-"*80)
    
    config = {
        "role_arn": role_arn,
        "role_name": ROLE_NAME,
        "policy_arn": policy_arn,
        "policy_name": POLICY_NAME,
        "region": REGION
    }
    
    with open('gateway_role_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ Configuration saved to gateway_role_config.json")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "="*80)
    print("✓ GATEWAY IAM ROLE SETUP COMPLETE!")
    print("="*80)
    print(f"\nRole ARN: {role_arn}")
    print(f"Policy ARN: {policy_arn}")
    print(f"\nPermissions granted:")
    print(f"  - Invoke Lambda functions in {REGION}")
    print("\n" + "="*80)
    print("✓ Ready for Gateway creation!")
    print("="*80)

except ClientError as e:
    print(f"\n❌ Error: {e}")
    print(f"Error Code: {e.response['Error']['Code']}")
    print(f"Error Message: {e.response['Error']['Message']}")
    exit(1)
except Exception as e:
    print(f"\n❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
