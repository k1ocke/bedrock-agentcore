# Configuration Files - Sample Templates

This directory contains sample configuration file templates with placeholder values. These files show the structure and variable names needed for the Bedrock AgentCore project.

## ⚠️ Important Security Notes

- **NEVER commit actual configuration files to version control**
- The actual config files are excluded via `.gitignore`
- Replace all placeholder values with your actual AWS resource IDs
- Keep your actual config files in the project root directory (not in this folder)

## Configuration Files Overview

### 1. memory_config.json
**Purpose**: Stores AgentCore Memory resource information

**Created by**: `03_create_memory.py`

**Used by**: 
- `04_seed_memory.py`
- `05_test_memory.py`
- `06_memory_enabled_agent.py`
- `14_full_agent.py`
- `17_runtime_agent.py`
- `19_deploy_agent.py`

**Variables**:
- `memory_id`: Unique identifier for the memory resource (format: `name-XXXXXXXXXXXX`)
- `name`: Human-readable name for the memory
- `region`: AWS region (e.g., `us-west-2`)

---

### 2. cognito_config.json
**Purpose**: Stores Cognito User Pool and OAuth credentials for gateway authentication

**Created by**: `08_create_cognito.py`

**Used by**:
- `11_create_gateway.py`
- `14_full_agent.py`
- `19_deploy_agent.py`
- `21_invoke_agent.py`

**Variables**:
- `user_pool_id`: Cognito User Pool ID (format: `us-west-2_XXXXXXXXX`)
- `domain_prefix`: Custom domain prefix for Cognito hosted UI
- `client_id`: OAuth client ID (24 characters)
- `client_secret`: OAuth client secret (56 characters)
- `token_endpoint`: OAuth token endpoint URL
- `discovery_url`: OIDC discovery URL (IDP format, not hosted UI)
- `region`: AWS region

**⚠️ Security**: The `client_secret` is highly sensitive - never expose it publicly

---

### 3. gateway_config.json
**Purpose**: Stores AgentCore Gateway information and target details

**Created by**: 
- `11_create_gateway.py` (gateway info)
- `12_add_lambda_to_gateway.py` (target info)

**Used by**:
- `13_list_gateway_targets.py`
- `14_full_agent.py`
- `19_deploy_agent.py`

**Variables**:
- `id` / `gateway_id`: Gateway unique identifier
- `gateway_url`: MCP endpoint URL for the gateway
- `gateway_arn`: Full ARN of the gateway resource
- `name`: Human-readable gateway name
- `region`: AWS region
- `target_id`: Unique identifier for the Lambda target
- `target_name`: Human-readable target name
- `lambda_arn`: ARN of the Lambda function attached to gateway

---

### 4. kb_config.json
**Purpose**: Stores Bedrock Knowledge Base information

**Created by**: `01_returns_refunds_agent.py` (retrieved from CloudFormation)

**Used by**:
- `01_returns_refunds_agent.py`
- `06_memory_enabled_agent.py`
- `14_full_agent.py`
- `17_runtime_agent.py`
- `19_deploy_agent.py`

**Variables**:
- `knowledge_base_id`: Unique identifier for the knowledge base (10 characters)
- `region`: AWS region
- `retrieved_from`: Source of the KB ID (e.g., CloudFormation stack name)
- `retrieved_at`: Date when the ID was retrieved

---

### 5. lambda_config.json
**Purpose**: Stores Lambda function details and MCP tool schema

**Created by**: `10_create_lambda.py`

**Used by**: `12_add_lambda_to_gateway.py`

**Variables**:
- `function_arn`: Full ARN of the Lambda function
- `function_name`: Lambda function name
- `tool_name`: Name of the tool as exposed through MCP
- `tool_schema`: MCP tool schema definition (JSON object)
  - `name`: Tool name
  - `description`: What the tool does
  - `inputSchema`: JSON Schema for tool parameters
- `region`: AWS region
- `sample_data`: Example data for testing (optional)

---

### 6. gateway_role_config.json
**Purpose**: Stores IAM role information for gateway execution

**Created by**: `09_create_gateway_role.py`

**Used by**: `11_create_gateway.py`

**Variables**:
- `role_arn`: Full ARN of the IAM role
- `role_name`: IAM role name
- `policy_arn`: Full ARN of the attached IAM policy
- `policy_name`: IAM policy name
- `region`: AWS region

---

### 7. runtime_execution_role_config.json
**Purpose**: Stores IAM role information for AgentCore Runtime execution

**Created by**: `16_create_runtime_role.py`

**Used by**: `19_deploy_agent.py`

**Variables**:
- `role_name`: IAM role name (includes random suffix)
- `role_arn`: Full ARN of the IAM role
- `policy_name`: IAM policy name (includes random suffix)
- `policy_arn`: Full ARN of the attached IAM policy
- `region`: AWS region

---

### 8. runtime_config.json
**Purpose**: Stores deployed agent runtime information

**Created by**: `19_deploy_agent.py`

**Used by**:
- `20_check_status.py`
- `21_invoke_agent.py`
- `22_get_dashboard.py`
- `23_get_logs_info.py`

**Variables**:
- `agent_arn`: Full ARN of the deployed agent runtime
- `agent_name`: Agent name
- `region`: AWS region
- `memory_id`: Associated memory resource ID
- `gateway_url`: Associated gateway URL
- `knowledge_base_id`: Associated knowledge base ID

---

## Setup Instructions

### Step 1: Copy Sample Files

```bash
# Copy all sample files to the project root (remove .sample extension)
cp config-samples/*.sample ../

# Or copy individually as needed
cp config-samples/memory_config.json.sample ../memory_config.json
```

### Step 2: Run Setup Scripts

Run the numbered scripts in order. Each script will populate its corresponding config file:

```bash
# Create memory
python3 03_create_memory.py

# Create Cognito
python3 08_create_cognito.py

# Create gateway role
python3 09_create_gateway_role.py

# Create Lambda
python3 10_create_lambda.py

# Create gateway
python3 11_create_gateway.py

# Add Lambda to gateway
python3 12_add_lambda_to_gateway.py

# Create runtime role
python3 16_create_runtime_role.py

# Deploy to runtime
python3 19_deploy_agent.py
```

### Step 3: Verify Configuration

Check that all config files have been created with actual values:

```bash
ls -la ../*.json
```

---

## AWS Account ID Format

Throughout these configs, you'll see AWS account IDs in ARNs. The format is:
- `arn:aws:service:region:123456789012:resource/name`
- Replace `123456789012` with your actual 12-digit AWS account ID

---

## Common Placeholder Patterns

- `XXXXXXXXXX`: 10-character alphanumeric ID
- `XXXXXXXXXXXX`: 12-character alphanumeric ID
- `123456789012`: AWS account ID (12 digits)
- `us-west-2`: AWS region
- `YYYY-MM-DD`: Date format
- `YYYYMMDDHHMMSS`: Timestamp format

---

## Troubleshooting

### Missing Config File Error

If a script fails with "Config file not found":
1. Check which config file is missing
2. Run the script that creates that config file
3. Verify the file exists in the project root

### Invalid Values Error

If a script fails with "Invalid resource ID":
1. Check the config file has actual values (not placeholders)
2. Verify the resource exists in AWS
3. Ensure the region matches your AWS resources

---

## Security Best Practices

1. ✅ Keep actual config files in project root (excluded by .gitignore)
2. ✅ Never commit files with actual AWS resource IDs
3. ✅ Use IAM roles with least-privilege permissions
4. ✅ Rotate Cognito client secrets regularly
5. ✅ Use AWS Secrets Manager for production deployments
6. ✅ Enable CloudTrail logging for audit trails

---

**Last Updated**: 2026-04-04
