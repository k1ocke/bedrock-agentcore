#!/usr/bin/env python3
"""
Script to create Cognito User Pool for Gateway authentication.

This script sets up:
- Cognito User Pool (secure login system)
- User Pool Domain (for OAuth endpoints)
- App Client with OAuth support (machine-to-machine authentication)
"""

import json
import boto3
import time
from botocore.exceptions import ClientError

# Configuration
REGION = "us-west-2"
POOL_NAME = "returns-gateway-pool"
DOMAIN_PREFIX = "returns-gateway"  # Must be globally unique
APP_CLIENT_NAME = "returns-gateway-client"

print("="*80)
print("CREATING COGNITO USER POOL FOR GATEWAY AUTHENTICATION")
print("="*80)
print(f"Region: {REGION}")
print(f"Pool Name: {POOL_NAME}")
print(f"Domain Prefix: {DOMAIN_PREFIX}")
print("="*80)

# Create Cognito client
cognito_client = boto3.client('cognito-idp', region_name=REGION)

try:
    # ========================================================================
    # STEP 1: Create User Pool
    # ========================================================================
    print("\n📝 Step 1: Creating Cognito User Pool...")
    print("-"*80)
    
    user_pool_response = cognito_client.create_user_pool(
        PoolName=POOL_NAME,
        Policies={
            'PasswordPolicy': {
                'MinimumLength': 8,
                'RequireUppercase': False,
                'RequireLowercase': False,
                'RequireNumbers': False,
                'RequireSymbols': False
            }
        },
        AutoVerifiedAttributes=['email'],
        Schema=[
            {
                'Name': 'email',
                'AttributeDataType': 'String',
                'Required': True,
                'Mutable': True
            }
        ]
    )
    
    user_pool_id = user_pool_response['UserPool']['Id']
    print(f"✓ User Pool created: {user_pool_id}")
    
    # ========================================================================
    # STEP 2: Create User Pool Domain
    # ========================================================================
    print(f"\n📝 Step 2: Creating User Pool Domain...")
    print("-"*80)
    
    try:
        domain_response = cognito_client.create_user_pool_domain(
            Domain=DOMAIN_PREFIX,
            UserPoolId=user_pool_id
        )
        print(f"✓ Domain created: {DOMAIN_PREFIX}.auth.{REGION}.amazoncognito.com")
    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidParameterException':
            print(f"⚠️  Domain '{DOMAIN_PREFIX}' already exists, trying with timestamp...")
            # Add timestamp to make it unique
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            DOMAIN_PREFIX = f"{DOMAIN_PREFIX}-{timestamp}"
            domain_response = cognito_client.create_user_pool_domain(
                Domain=DOMAIN_PREFIX,
                UserPoolId=user_pool_id
            )
            print(f"✓ Domain created: {DOMAIN_PREFIX}.auth.{REGION}.amazoncognito.com")
        else:
            raise
    
    # Wait for domain to be ready
    print("⏳ Waiting for domain to become active...")
    time.sleep(5)
    
    # ========================================================================
    # STEP 3: Create Resource Server (for custom scopes) - MUST BE BEFORE APP CLIENT
    # ========================================================================
    print(f"\n📝 Step 3: Creating Resource Server for custom scopes...")
    print("-"*80)
    
    try:
        resource_server_response = cognito_client.create_resource_server(
            UserPoolId=user_pool_id,
            Identifier='returns-gateway',
            Name='Returns Gateway API',
            Scopes=[
                {
                    'ScopeName': 'read',
                    'ScopeDescription': 'Read access to returns gateway'
                },
                {
                    'ScopeName': 'write',
                    'ScopeDescription': 'Write access to returns gateway'
                }
            ]
        )
        print(f"✓ Resource Server created with read/write scopes")
    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidParameterException':
            print(f"⚠️  Resource Server already exists, continuing...")
        else:
            raise
    
    # ========================================================================
    # STEP 4: Create App Client with OAuth support
    # ========================================================================
    print(f"\n📝 Step 4: Creating App Client with OAuth support...")
    print("-"*80)
    
    app_client_response = cognito_client.create_user_pool_client(
        UserPoolId=user_pool_id,
        ClientName=APP_CLIENT_NAME,
        GenerateSecret=True,  # Required for machine-to-machine auth
        ExplicitAuthFlows=[
            'ALLOW_REFRESH_TOKEN_AUTH',
            'ALLOW_USER_SRP_AUTH'
        ],
        AllowedOAuthFlows=['client_credentials'],  # Machine-to-machine
        AllowedOAuthScopes=['returns-gateway/read', 'returns-gateway/write'],
        AllowedOAuthFlowsUserPoolClient=True,
        SupportedIdentityProviders=['COGNITO']
    )
    
    client_id = app_client_response['UserPoolClient']['ClientId']
    print(f"✓ App Client created: {client_id}")
    
    # ========================================================================
    # STEP 5: Get Client Secret
    # ========================================================================
    print(f"\n📝 Step 5: Retrieving Client Secret...")
    print("-"*80)
    
    client_details = cognito_client.describe_user_pool_client(
        UserPoolId=user_pool_id,
        ClientId=client_id
    )
    
    client_secret = client_details['UserPoolClient']['ClientSecret']
    print(f"✓ Client Secret retrieved")
    
    # ========================================================================
    # STEP 6: Build Configuration URLs
    # ========================================================================
    print(f"\n📝 Step 6: Building configuration URLs...")
    print("-"*80)
    
    # Token endpoint (hosted UI domain)
    token_endpoint = f"https://{DOMAIN_PREFIX}.auth.{REGION}.amazoncognito.com/oauth2/token"
    
    # Discovery URL (IDP domain - CRITICAL for AgentCore)
    discovery_url = f"https://cognito-idp.{REGION}.amazonaws.com/{user_pool_id}/.well-known/openid-configuration"
    
    print(f"✓ Token Endpoint: {token_endpoint}")
    print(f"✓ Discovery URL: {discovery_url}")
    
    # ========================================================================
    # STEP 7: Save Configuration
    # ========================================================================
    print(f"\n📝 Step 7: Saving configuration to cognito_config.json...")
    print("-"*80)
    
    config = {
        "user_pool_id": user_pool_id,
        "domain_prefix": DOMAIN_PREFIX,
        "client_id": client_id,
        "client_secret": client_secret,
        "token_endpoint": token_endpoint,
        "discovery_url": discovery_url,
        "region": REGION
    }
    
    with open('cognito_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ Configuration saved to cognito_config.json")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "="*80)
    print("✓ COGNITO SETUP COMPLETE!")
    print("="*80)
    print(f"\nUser Pool ID: {user_pool_id}")
    print(f"Domain Prefix: {DOMAIN_PREFIX}")
    print(f"Client ID: {client_id}")
    print(f"Client Secret: {client_secret[:10]}...")
    print(f"\nToken Endpoint: {token_endpoint}")
    print(f"Discovery URL: {discovery_url}")
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
