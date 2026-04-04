#!/usr/bin/env python3
"""
Script to create Lambda function for order lookup.

This script creates:
- Lambda function that looks up order details by order ID
- Returns order information including return eligibility
"""

import json
import boto3
import zipfile
import io
from botocore.exceptions import ClientError

# Configuration
REGION = "us-west-2"
FUNCTION_NAME = "OrderLookupFunction"
TOOL_NAME = "lookup_order"

print("="*80)
print("CREATING LAMBDA FUNCTION FOR ORDER LOOKUP")
print("="*80)
print(f"Region: {REGION}")
print(f"Function Name: {FUNCTION_NAME}")
print(f"Tool Name: {TOOL_NAME}")
print("="*80)

# Create clients
lambda_client = boto3.client('lambda', region_name=REGION)
iam_client = boto3.client('iam')
sts_client = boto3.client('sts')

try:
    # Get AWS account ID
    account_id = sts_client.get_caller_identity()['Account']
    
    # ========================================================================
    # STEP 1: Create Lambda Execution Role
    # ========================================================================
    print(f"\n📝 Step 1: Creating Lambda execution role...")
    print("-"*80)
    
    lambda_role_name = "OrderLookupLambdaRole"
    
    # Trust policy for Lambda
    lambda_trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    try:
        role_response = iam_client.create_role(
            RoleName=lambda_role_name,
            AssumeRolePolicyDocument=json.dumps(lambda_trust_policy),
            Description="Execution role for OrderLookupFunction Lambda"
        )
        lambda_role_arn = role_response['Role']['Arn']
        print(f"✓ Role created: {lambda_role_arn}")
        
        # Attach basic Lambda execution policy
        iam_client.attach_role_policy(
            RoleName=lambda_role_name,
            PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
        )
        print(f"✓ Attached AWSLambdaBasicExecutionRole policy")
        
        # Wait for role to propagate
        print("⏳ Waiting for role to propagate...")
        import time
        time.sleep(10)
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
            print(f"⚠️  Role '{lambda_role_name}' already exists, retrieving ARN...")
            role_response = iam_client.get_role(RoleName=lambda_role_name)
            lambda_role_arn = role_response['Role']['Arn']
            print(f"✓ Using existing role: {lambda_role_arn}")
        else:
            raise
    
    # ========================================================================
    # STEP 2: Create Lambda Function Code
    # ========================================================================
    print(f"\n📝 Step 2: Creating Lambda function code...")
    print("-"*80)
    
    # Lambda function code with mock order data
    lambda_code = '''
import json
from datetime import datetime, timedelta

# Mock order database
ORDERS = {
    "ORD-001": {
        "order_id": "ORD-001",
        "product_name": "Dell XPS 15 Laptop",
        "purchase_date": (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d"),
        "amount": 1299.99,
        "category": "electronics",
        "status": "delivered"
    },
    "ORD-002": {
        "order_id": "ORD-002",
        "product_name": "iPhone 12",
        "purchase_date": (datetime.now() - timedelta(days=400)).strftime("%Y-%m-%d"),
        "amount": 799.99,
        "category": "electronics",
        "status": "delivered"
    },
    "ORD-003": {
        "order_id": "ORD-003",
        "product_name": "Samsung Galaxy Tab",
        "purchase_date": (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d"),
        "amount": 449.99,
        "category": "electronics",
        "status": "delivered",
        "defective": True
    }
}

def check_return_eligibility(purchase_date_str, category):
    """Check if order is eligible for return"""
    try:
        purchase_date = datetime.strptime(purchase_date_str, "%Y-%m-%d")
        today = datetime.now()
        days_since_purchase = (today - purchase_date).days
        
        # 30-day return window for electronics
        return_window = 30
        
        if days_since_purchase <= return_window:
            return {
                "eligible": True,
                "reason": f"Within {return_window}-day return window ({days_since_purchase} days since purchase)"
            }
        else:
            return {
                "eligible": False,
                "reason": f"Outside {return_window}-day return window ({days_since_purchase} days since purchase)"
            }
    except Exception as e:
        return {
            "eligible": False,
            "reason": f"Error checking eligibility: {str(e)}"
        }

def lambda_handler(event, context):
    """
    Lambda handler for order lookup.
    
    Expected input:
    {
        "order_id": "ORD-001"
    }
    """
    try:
        # Parse input
        if isinstance(event, str):
            event = json.loads(event)
        
        order_id = event.get('order_id', '').strip()
        
        if not order_id:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'order_id is required'
                })
            }
        
        # Look up order
        order = ORDERS.get(order_id)
        
        if not order:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'error': f'Order {order_id} not found',
                    'available_orders': list(ORDERS.keys())
                })
            }
        
        # Check return eligibility
        eligibility = check_return_eligibility(
            order['purchase_date'],
            order['category']
        )
        
        # Build response
        response_data = {
            'order_id': order['order_id'],
            'product_name': order['product_name'],
            'purchase_date': order['purchase_date'],
            'amount': order['amount'],
            'category': order['category'],
            'status': order['status'],
            'return_eligible': eligibility['eligible'],
            'return_eligibility_reason': eligibility['reason']
        }
        
        # Add defective flag if present
        if order.get('defective'):
            response_data['defective'] = True
            response_data['return_eligible'] = True
            response_data['return_eligibility_reason'] = 'Defective item - eligible for return regardless of date'
        
        return {
            'statusCode': 200,
            'body': json.dumps(response_data)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'Internal error: {str(e)}'
            })
        }
'''
    
    # Create ZIP file in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)
    
    zip_buffer.seek(0)
    zip_content = zip_buffer.read()
    
    print(f"✓ Lambda code created ({len(zip_content)} bytes)")
    
    # ========================================================================
    # STEP 3: Create Lambda Function
    # ========================================================================
    print(f"\n📝 Step 3: Creating Lambda function...")
    print("-"*80)
    
    try:
        function_response = lambda_client.create_function(
            FunctionName=FUNCTION_NAME,
            Runtime='python3.10',
            Role=lambda_role_arn,
            Handler='lambda_function.lambda_handler',
            Code={'ZipFile': zip_content},
            Description='Looks up order details by order ID for returns processing',
            Timeout=30,
            MemorySize=128
        )
        
        function_arn = function_response['FunctionArn']
        print(f"✓ Lambda function created: {function_arn}")
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceConflictException':
            print(f"⚠️  Function '{FUNCTION_NAME}' already exists, updating code...")
            lambda_client.update_function_code(
                FunctionName=FUNCTION_NAME,
                ZipFile=zip_content
            )
            function_response = lambda_client.get_function(FunctionName=FUNCTION_NAME)
            function_arn = function_response['Configuration']['FunctionArn']
            print(f"✓ Lambda function updated: {function_arn}")
        else:
            raise
    
    # ========================================================================
    # STEP 4: Create Tool Schema for Gateway
    # ========================================================================
    print(f"\n📝 Step 4: Creating tool schema for Gateway...")
    print("-"*80)
    
    tool_schema = {
        "name": TOOL_NAME,
        "description": "Look up order details by order ID. Returns order information including product name, purchase date, amount, and return eligibility status.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The order ID to look up (e.g., ORD-001, ORD-002, ORD-003)"
                }
            },
            "required": ["order_id"]
        }
    }
    
    print(f"✓ Tool schema created for '{TOOL_NAME}'")
    
    # ========================================================================
    # STEP 5: Save Configuration
    # ========================================================================
    print(f"\n📝 Step 5: Saving configuration to lambda_config.json...")
    print("-"*80)
    
    config = {
        "function_arn": function_arn,
        "function_name": FUNCTION_NAME,
        "tool_name": TOOL_NAME,
        "tool_schema": tool_schema,
        "region": REGION,
        "sample_orders": ["ORD-001", "ORD-002", "ORD-003"]
    }
    
    with open('lambda_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ Configuration saved to lambda_config.json")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "="*80)
    print("✓ LAMBDA FUNCTION SETUP COMPLETE!")
    print("="*80)
    print(f"\nFunction ARN: {function_arn}")
    print(f"Tool Name: {TOOL_NAME}")
    print(f"\nSample Orders:")
    print(f"  - ORD-001: Recent laptop (15 days ago) - Eligible")
    print(f"  - ORD-002: Old phone (400 days ago) - Not eligible")
    print(f"  - ORD-003: Defective tablet (10 days ago) - Eligible (defective)")
    print("\n" + "="*80)
    print("✓ Ready for Gateway integration!")
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
