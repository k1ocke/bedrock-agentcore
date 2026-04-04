#!/usr/bin/env python3
"""
Comprehensive AWS Resource Cleanup Script

This script safely deletes all AWS resources created for the Bedrock AgentCore project.
It follows proper deletion order to avoid dependency errors and includes safety confirmations.

Resources deleted:
1. Runtime Agent
2. Gateway Targets (wait 5s before gateway deletion)
3. Gateway
4. Memory
5. Lambda Function
6. Cognito Domain (wait 5s before user pool deletion)
7. Cognito User Pool
8. IAM Roles and Policies
9. ECR Repository

Region: us-west-2
"""

import json
import time
import boto3
from botocore.exceptions import ClientError
from bedrock_agentcore_starter_toolkit.operations.memory.manager import MemoryManager

# Configuration
REGION = "us-west-2"
WARNING_SECONDS = 5

# Color codes for output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(message):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")

def print_success(message):
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")

def print_warning(message):
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")

def print_error(message):
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

def print_info(message):
    print(f"{Colors.OKCYAN}ℹ {message}{Colors.ENDC}")

def load_config(filename):
    """Load configuration from JSON file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print_warning(f"Config file not found: {filename}")
        return None
    except json.JSONDecodeError:
        print_error(f"Invalid JSON in config file: {filename}")
        return None

def delete_runtime_agent(config):
    """Delete AgentCore Runtime agent"""
    print_header("DELETING RUNTIME AGENT")
    
    if not config:
        print_warning("No runtime config found - skipping")
        return
    
    agent_arn = config.get('agent_arn')
    if not agent_arn:
        print_warning("No agent ARN found - skipping")
        return
    
    print_info(f"Agent ARN: {agent_arn}")
    
    try:
        client = boto3.client('bedrock-agentcore-control', region_name=REGION)
        
        # Extract agent runtime ID from ARN
        agent_runtime_id = agent_arn.split('/')[-1]
        
        print_info(f"Deleting agent runtime: {agent_runtime_id}")
        client.delete_agent_runtime(agentRuntimeId=agent_runtime_id)
        
        print_success("Runtime agent deleted successfully")
        
        # Wait for deletion to complete
        print_info("Waiting for deletion to complete...")
        time.sleep(10)
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ResourceNotFoundException':
            print_warning("Runtime agent not found (already deleted)")
        else:
            print_error(f"Error deleting runtime agent: {e}")
    except Exception as e:
        print_error(f"Unexpected error: {e}")

def delete_gateway_targets(gateway_config):
    """Delete all targets from gateway"""
    print_header("DELETING GATEWAY TARGETS")
    
    if not gateway_config:
        print_warning("No gateway config found - skipping")
        return
    
    gateway_id = gateway_config.get('gateway_id')
    target_id = gateway_config.get('target_id')
    
    if not gateway_id:
        print_warning("No gateway ID found - skipping")
        return
    
    try:
        client = boto3.client('bedrock-agentcore-control', region_name=REGION)
        
        # List all targets
        print_info(f"Listing targets for gateway: {gateway_id}")
        response = client.list_gateway_targets(gatewayIdentifier=gateway_id)
        
        targets = response.get('targets', [])
        if not targets:
            print_warning("No targets found")
            return
        
        # Delete each target
        for target in targets:
            target_id = target['targetId']
            target_name = target.get('name', 'Unknown')
            print_info(f"Deleting target: {target_name} ({target_id})")
            
            try:
                client.delete_gateway_target(
                    gatewayIdentifier=gateway_id,
                    targetId=target_id
                )
                print_success(f"Target {target_name} deleted")
            except ClientError as e:
                if e.response['Error']['Code'] == 'ResourceNotFoundException':
                    print_warning(f"Target {target_name} not found (already deleted)")
                else:
                    print_error(f"Error deleting target {target_name}: {e}")
        
        print_success("All gateway targets deleted")
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print_warning("Gateway not found (already deleted)")
        else:
            print_error(f"Error listing/deleting targets: {e}")
    except Exception as e:
        print_error(f"Unexpected error: {e}")

def delete_gateway(gateway_config):
    """Delete AgentCore Gateway"""
    print_header("DELETING GATEWAY")
    
    if not gateway_config:
        print_warning("No gateway config found - skipping")
        return
    
    gateway_id = gateway_config.get('gateway_id')
    if not gateway_id:
        print_warning("No gateway ID found - skipping")
        return
    
    print_info(f"Gateway ID: {gateway_id}")
    
    # Wait 5 seconds after target deletion
    print_info("Waiting 5 seconds after target deletion...")
    time.sleep(5)
    
    try:
        client = boto3.client('bedrock-agentcore-control', region_name=REGION)
        
        print_info(f"Deleting gateway: {gateway_id}")
        client.delete_gateway(gatewayIdentifier=gateway_id)
        
        print_success("Gateway deleted successfully")
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print_warning("Gateway not found (already deleted)")
        else:
            print_error(f"Error deleting gateway: {e}")
    except Exception as e:
        print_error(f"Unexpected error: {e}")

def delete_memory(memory_config):
    """Delete AgentCore Memory"""
    print_header("DELETING MEMORY")
    
    if not memory_config:
        print_warning("No memory config found - skipping")
        return
    
    memory_id = memory_config.get('memory_id')
    if not memory_id:
        print_warning("No memory ID found - skipping")
        return
    
    print_info(f"Memory ID: {memory_id}")
    
    try:
        memory_manager = MemoryManager(region=REGION)
        
        print_info(f"Deleting memory: {memory_id}")
        memory_manager.delete_memory(memory_id=memory_id)
        
        print_success("Memory deleted successfully")
        
    except Exception as e:
        error_msg = str(e)
        if 'ResourceNotFoundException' in error_msg or 'not found' in error_msg.lower():
            print_warning("Memory not found (already deleted)")
        else:
            print_error(f"Error deleting memory: {e}")

def delete_lambda_function(lambda_config):
    """Delete Lambda function"""
    print_header("DELETING LAMBDA FUNCTION")
    
    if not lambda_config:
        print_warning("No lambda config found - skipping")
        return
    
    function_name = lambda_config.get('function_name')
    if not function_name:
        print_warning("No function name found - skipping")
        return
    
    print_info(f"Function: {function_name}")
    
    try:
        client = boto3.client('lambda', region_name=REGION)
        
        print_info(f"Deleting Lambda function: {function_name}")
        client.delete_function(FunctionName=function_name)
        
        print_success("Lambda function deleted successfully")
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print_warning("Lambda function not found (already deleted)")
        else:
            print_error(f"Error deleting Lambda function: {e}")
    except Exception as e:
        print_error(f"Unexpected error: {e}")

def delete_cognito_resources(cognito_config):
    """Delete Cognito domain and user pool"""
    print_header("DELETING COGNITO RESOURCES")
    
    if not cognito_config:
        print_warning("No cognito config found - skipping")
        return
    
    user_pool_id = cognito_config.get('user_pool_id')
    domain_prefix = cognito_config.get('domain_prefix')
    
    if not user_pool_id:
        print_warning("No user pool ID found - skipping")
        return
    
    try:
        client = boto3.client('cognito-idp', region_name=REGION)
        
        # Delete domain first
        if domain_prefix:
            print_info(f"Deleting Cognito domain: {domain_prefix}")
            try:
                client.delete_user_pool_domain(
                    Domain=domain_prefix,
                    UserPoolId=user_pool_id
                )
                print_success("Cognito domain deleted")
                
                # Wait 5 seconds before deleting user pool
                print_info("Waiting 5 seconds before deleting user pool...")
                time.sleep(5)
                
            except ClientError as e:
                if e.response['Error']['Code'] == 'ResourceNotFoundException':
                    print_warning("Cognito domain not found (already deleted)")
                else:
                    print_error(f"Error deleting Cognito domain: {e}")
        
        # Delete user pool
        print_info(f"Deleting Cognito user pool: {user_pool_id}")
        client.delete_user_pool(UserPoolId=user_pool_id)
        
        print_success("Cognito user pool deleted successfully")
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print_warning("Cognito user pool not found (already deleted)")
        else:
            print_error(f"Error deleting Cognito user pool: {e}")
    except Exception as e:
        print_error(f"Unexpected error: {e}")

def delete_iam_role(role_name, policy_arn=None):
    """Delete IAM role and optionally detach/delete policy"""
    try:
        client = boto3.client('iam', region_name=REGION)
        
        # Detach policy if provided
        if policy_arn:
            try:
                print_info(f"Detaching policy from role: {role_name}")
                client.detach_role_policy(
                    RoleName=role_name,
                    PolicyArn=policy_arn
                )
                print_success(f"Policy detached from {role_name}")
            except ClientError as e:
                if e.response['Error']['Code'] != 'NoSuchEntity':
                    print_error(f"Error detaching policy: {e}")
        
        # Delete role
        print_info(f"Deleting IAM role: {role_name}")
        client.delete_role(RoleName=role_name)
        print_success(f"IAM role {role_name} deleted")
        
        # Delete policy if provided
        if policy_arn:
            try:
                print_info(f"Deleting IAM policy: {policy_arn}")
                client.delete_policy(PolicyArn=policy_arn)
                print_success("IAM policy deleted")
            except ClientError as e:
                if e.response['Error']['Code'] != 'NoSuchEntity':
                    print_error(f"Error deleting policy: {e}")
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchEntity':
            print_warning(f"IAM role {role_name} not found (already deleted)")
        else:
            print_error(f"Error deleting IAM role {role_name}: {e}")
    except Exception as e:
        print_error(f"Unexpected error: {e}")

def delete_iam_roles(gateway_role_config, runtime_role_config):
    """Delete all IAM roles and policies"""
    print_header("DELETING IAM ROLES AND POLICIES")
    
    # Delete gateway role
    if gateway_role_config:
        role_name = gateway_role_config.get('role_name')
        policy_arn = gateway_role_config.get('policy_arn')
        if role_name:
            print_info(f"Deleting gateway role: {role_name}")
            delete_iam_role(role_name, policy_arn)
    else:
        print_warning("No gateway role config found - skipping")
    
    # Delete runtime role
    if runtime_role_config:
        role_name = runtime_role_config.get('role_name')
        policy_arn = runtime_role_config.get('policy_arn')
        if role_name:
            print_info(f"Deleting runtime role: {role_name}")
            delete_iam_role(role_name, policy_arn)
    else:
        print_warning("No runtime role config found - skipping")

def delete_ecr_repository():
    """Delete ECR repository"""
    print_header("DELETING ECR REPOSITORY")
    
    # Repository name from .bedrock_agentcore.yaml
    repository_name = "returns_refunds_agent"
    
    try:
        client = boto3.client('ecr', region_name=REGION)
        
        print_info(f"Deleting ECR repository: {repository_name}")
        client.delete_repository(
            repositoryName=repository_name,
            force=True  # Delete even if contains images
        )
        
        print_success("ECR repository deleted successfully")
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'RepositoryNotFoundException':
            print_warning("ECR repository not found (already deleted)")
        else:
            print_error(f"Error deleting ECR repository: {e}")
    except Exception as e:
        print_error(f"Unexpected error: {e}")

def main():
    """Main cleanup function"""
    print_header("AWS RESOURCE CLEANUP SCRIPT")
    print(f"{Colors.BOLD}Region: {REGION}{Colors.ENDC}")
    print(f"{Colors.BOLD}This will delete ALL AWS resources created for this project{Colors.ENDC}\n")
    
    # Load all configurations
    print_info("Loading configuration files...")
    runtime_config = load_config('runtime_config.json')
    gateway_config = load_config('gateway_config.json')
    memory_config = load_config('memory_config.json')
    lambda_config = load_config('lambda_config.json')
    cognito_config = load_config('cognito_config.json')
    gateway_role_config = load_config('gateway_role_config.json')
    runtime_role_config = load_config('runtime_execution_role_config.json')
    
    # Display what will be deleted
    print_header("RESOURCES TO BE DELETED")
    
    resources = []
    if runtime_config and runtime_config.get('agent_arn'):
        resources.append(f"✗ Runtime Agent: {runtime_config['agent_arn']}")
    if gateway_config and gateway_config.get('gateway_id'):
        resources.append(f"✗ Gateway: {gateway_config['gateway_id']}")
    if memory_config and memory_config.get('memory_id'):
        resources.append(f"✗ Memory: {memory_config['memory_id']}")
    if lambda_config and lambda_config.get('function_name'):
        resources.append(f"✗ Lambda: {lambda_config['function_name']}")
    if cognito_config and cognito_config.get('user_pool_id'):
        resources.append(f"✗ Cognito: {cognito_config['user_pool_id']}")
    if gateway_role_config and gateway_role_config.get('role_name'):
        resources.append(f"✗ IAM Role: {gateway_role_config['role_name']}")
    if runtime_role_config and runtime_role_config.get('role_name'):
        resources.append(f"✗ IAM Role: {runtime_role_config['role_name']}")
    resources.append(f"✗ ECR Repository: returns_refunds_agent")
    
    if not resources:
        print_warning("No resources found to delete")
        return
    
    for resource in resources:
        print(f"{Colors.FAIL}{resource}{Colors.ENDC}")
    
    # Warning countdown
    print(f"\n{Colors.WARNING}{Colors.BOLD}⚠ WARNING: This action cannot be undone!{Colors.ENDC}")
    print(f"{Colors.WARNING}Starting deletion in {WARNING_SECONDS} seconds...{Colors.ENDC}")
    print(f"{Colors.WARNING}Press Ctrl+C to cancel{Colors.ENDC}\n")
    
    try:
        for i in range(WARNING_SECONDS, 0, -1):
            print(f"{Colors.WARNING}{i}...{Colors.ENDC}", end=' ', flush=True)
            time.sleep(1)
        print("\n")
    except KeyboardInterrupt:
        print(f"\n\n{Colors.OKGREEN}Cleanup cancelled by user{Colors.ENDC}")
        return
    
    # Start deletion process
    print_header("STARTING DELETION PROCESS")
    
    # 1. Delete runtime agent
    delete_runtime_agent(runtime_config)
    
    # 2. Delete gateway targets (wait 5s before gateway)
    delete_gateway_targets(gateway_config)
    
    # 3. Delete gateway
    delete_gateway(gateway_config)
    
    # 4. Delete memory
    delete_memory(memory_config)
    
    # 5. Delete Lambda function
    delete_lambda_function(lambda_config)
    
    # 6. Delete Cognito (domain first, wait 5s, then user pool)
    delete_cognito_resources(cognito_config)
    
    # 7. Delete IAM roles and policies
    delete_iam_roles(gateway_role_config, runtime_role_config)
    
    # 8. Delete ECR repository
    delete_ecr_repository()
    
    # Final summary
    print_header("CLEANUP COMPLETE")
    print_success("All AWS resources have been deleted")
    print_info("Configuration files remain for reference")
    print_info("You can re-deploy by running the setup scripts again")
    print(f"\n{Colors.BOLD}Note: Knowledge Base was NOT deleted (shared resource){Colors.ENDC}\n")

if __name__ == "__main__":
    main()
