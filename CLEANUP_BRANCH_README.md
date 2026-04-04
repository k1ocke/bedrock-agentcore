# Cleanup Branch

This branch contains cleanup scripts for tearing down AWS resources created by the Bedrock AgentCore project.

## Purpose

The cleanup scripts allow you to:
- Delete all AWS resources created during setup
- Clean up in the correct order to avoid dependency errors
- Optionally preserve specific resources
- Verify deletion of all resources

## Branch Strategy

- **main branch**: Contains setup and deployment scripts
- **cleanup branch**: Contains teardown and cleanup scripts

This separation keeps the main branch focused on building and deploying, while cleanup operations are isolated in this branch.

## Cleanup Scripts (To Be Created)

The following cleanup scripts will be created in this branch:

### Individual Resource Cleanup

1. **90_delete_runtime.py** - Delete AgentCore Runtime agent
2. **91_delete_gateway_targets.py** - Remove Lambda targets from gateway
3. **92_delete_gateway.py** - Delete AgentCore Gateway
4. **93_delete_lambda.py** - Delete Lambda function
5. **94_delete_cognito.py** - Delete Cognito User Pool
6. **95_delete_memory.py** - Delete AgentCore Memory
7. **96_delete_gateway_role.py** - Delete gateway IAM role and policy
8. **97_delete_runtime_role.py** - Delete runtime IAM role and policy

### Comprehensive Cleanup

9. **99_cleanup_all.py** - Delete all resources in correct order

## Cleanup Order

Resources must be deleted in reverse order of creation to avoid dependency errors:

```
1. Runtime Agent (depends on: role, memory, gateway, KB)
2. Gateway Targets (depends on: gateway, lambda)
3. Gateway (depends on: role, cognito)
4. Lambda Function (standalone)
5. Cognito User Pool (standalone)
6. Memory (standalone)
7. Gateway IAM Role (standalone)
8. Runtime IAM Role (standalone)
```

**Note**: Knowledge Base is NOT deleted as it may be shared across projects.

## Safety Features

Each cleanup script will:
- Load configuration from JSON files
- Display what will be deleted
- Ask for confirmation before deletion
- Handle errors gracefully
- Report success/failure
- Update or remove config files after deletion

## Usage

### Switch to Cleanup Branch

```bash
git checkout cleanup
```

### Run Individual Cleanup Scripts

```bash
# Delete runtime agent
python3 90_delete_runtime.py

# Delete gateway
python3 92_delete_gateway.py

# etc.
```

### Run Complete Cleanup

```bash
# Delete everything in correct order
python3 99_cleanup_all.py
```

### Return to Main Branch

```bash
git checkout main
```

## Configuration Files

Cleanup scripts read from the same config files as setup scripts:
- `runtime_config.json`
- `gateway_config.json`
- `lambda_config.json`
- `cognito_config.json`
- `memory_config.json`
- `gateway_role_config.json`
- `runtime_execution_role_config.json`

After successful deletion, scripts will either:
- Remove the config file, OR
- Update it to mark resources as deleted

## Verification

After cleanup, verify resources are deleted:

```bash
# Check AWS Console
# - Bedrock AgentCore Runtime
# - AgentCore Gateway
# - Lambda Functions
# - Cognito User Pools
# - AgentCore Memory
# - IAM Roles and Policies
```

## Partial Cleanup

You can run individual cleanup scripts to delete specific resources while preserving others.

For example, to delete only the runtime agent but keep everything else:

```bash
python3 90_delete_runtime.py
```

## Re-deployment After Cleanup

After cleanup, you can re-deploy by:

1. Switching back to main branch: `git checkout main`
2. Running setup scripts again (they will create new resources)
3. New resource IDs will be generated and saved to config files

## Important Notes

- **Knowledge Base is NOT deleted** - It may be used by other projects
- **Config files remain** - They show what was deleted (marked as deleted)
- **Cleanup is irreversible** - Make sure you want to delete before confirming
- **Check dependencies** - Some resources depend on others

## Cost Savings

Running cleanup scripts helps avoid ongoing AWS costs for:
- AgentCore Runtime (compute)
- Lambda functions (invocations)
- Cognito User Pools (active users)
- AgentCore Memory (storage)
- CloudWatch Logs (storage)

## Development Workflow

### Typical Development Cycle

1. **Setup**: `git checkout main` → Run setup scripts
2. **Develop**: Test and iterate on your agent
3. **Cleanup**: `git checkout cleanup` → Run cleanup scripts
4. **Repeat**: Switch back to main and start over

### Production Deployment

For production, you typically:
- Run setup scripts once
- Keep resources running
- Only use cleanup when decommissioning

---

**Branch**: cleanup
**Created**: 2026-04-04
**Status**: Ready for cleanup script development
