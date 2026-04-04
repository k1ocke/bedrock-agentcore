# Bedrock AgentCore - Returns & Refunds Agent

A production-ready AI agent built with AWS Bedrock AgentCore that handles customer returns and refunds with full memory, gateway, and knowledge base integration.

## Features

- **Memory Integration**: Remembers customer preferences and conversation history using AgentCore Memory
- **Gateway Integration**: Accesses Lambda functions via AgentCore Gateway for order lookups
- **Knowledge Base**: Retrieves Amazon return policy information using Bedrock Knowledge Base
- **Custom Tools**: Return eligibility checking, refund calculations, and policy formatting
- **Production Deployment**: Deployed to AgentCore Runtime with full observability

## Architecture

### Components

1. **Agent**: Strands-based conversational agent with custom tools
2. **Memory**: AgentCore Memory with semantic, preference, and summary strategies
3. **Gateway**: MCP Gateway connecting to Lambda functions
4. **Knowledge Base**: Bedrock Knowledge Base for policy documents
5. **Lambda**: Order lookup function with mock data
6. **Cognito**: OAuth authentication for gateway access
7. **IAM Roles**: Execution roles for gateway and runtime

### Deployment

The agent is deployed to AWS Bedrock AgentCore Runtime with:
- Region: us-west-2
- Model: Claude Sonnet 4.5
- Auto-scaling and health monitoring
- CloudWatch logging and X-Ray tracing

## Scripts

### Setup Scripts (01-13)
- `01_returns_refunds_agent.py` - Basic agent with KB integration
- `03_create_memory.py` - Create AgentCore Memory
- `04_seed_memory.py` - Seed memory with sample conversations
- `06_memory_enabled_agent.py` - Agent with memory integration
- `08_create_cognito.py` - Create Cognito user pool
- `09_create_gateway_role.py` - Create IAM role for gateway
- `10_create_lambda.py` - Create order lookup Lambda
- `11_create_gateway.py` - Create AgentCore Gateway
- `12_add_lambda_to_gateway.py` - Register Lambda as gateway target

### Testing Scripts (02, 05, 07, 13, 15)
- `02_test_agent.py` - Test basic agent
- `05_test_memory.py` - Test memory retrieval
- `07_test_memory_agent.py` - Test memory-enabled agent
- `13_list_gateway_targets.py` - List gateway targets
- `15_test_full_agent.py` - Test full-featured agent

### Runtime Deployment (16-23)
- `16_create_runtime_role.py` - Create runtime execution role
- `17_runtime_agent.py` - Runtime-ready agent code
- `19_deploy_agent.py` - Deploy to AgentCore Runtime
- `20_check_status.py` - Check deployment status
- `21_invoke_agent.py` - Invoke production agent
- `22_get_dashboard.py` - Get observability dashboard
- `23_get_logs_info.py` - Get CloudWatch logs info

## Requirements

See `requirements.txt` for Python dependencies:
- strands-agents
- bedrock-agentcore
- boto3
- mcp

## Configuration

Configuration files are required but not included in the repository for security.

**Sample templates** are provided in the `config-samples/` directory with placeholder values.

### Required Configuration Files

- `memory_config.json` - Memory ID
- `cognito_config.json` - Cognito credentials
- `gateway_config.json` - Gateway URL and ID
- `lambda_config.json` - Lambda ARN and tool schema
- `kb_config.json` - Knowledge Base ID
- `runtime_config.json` - Agent ARN
- `gateway_role_config.json` - Gateway IAM role
- `runtime_execution_role_config.json` - Runtime IAM role

### Setup Configuration

1. Copy sample files from `config-samples/` to project root
2. Run the numbered setup scripts (03, 08, 09, 10, 11, 12, 16, 19)
3. Each script will populate its corresponding config file with actual values

See `config-samples/README.md` for detailed instructions.

## Usage

### Local Testing
```bash
python3 14_full_agent.py
```

### Deploy to Runtime
```bash
python3 19_deploy_agent.py
python3 20_check_status.py
```

### Invoke Production Agent
```bash
python3 21_invoke_agent.py
```

### Monitor
```bash
python3 22_get_dashboard.py
python3 23_get_logs_info.py
```

## Custom Tools

1. **check_return_eligibility**: Validates if an item can be returned
2. **calculate_refund_amount**: Calculates refund based on condition
3. **format_policy_response**: Formats policy information
4. **current_time**: Returns current timestamp
5. **retrieve**: Searches knowledge base for policy info
6. **lookup_order**: Retrieves order details via gateway

## License

MIT
