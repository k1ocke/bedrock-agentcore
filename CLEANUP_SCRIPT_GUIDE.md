# Cleanup Script Usage Guide

## Overview

The `24_cleanup_aws.py` script safely deletes all AWS resources created for the Bedrock AgentCore project.

## Features

### ✅ Safety Features
- **5-second warning** before deletion starts
- **Cancellation option** (Ctrl+C to abort)
- **Graceful handling** of missing resources
- **Proper deletion order** to avoid dependency errors
- **Color-coded output** for easy monitoring

### 🗑️ Resources Deleted

1. **Runtime Agent** - Deployed AgentCore agent
2. **Gateway Targets** - Lambda targets (waits 5s before gateway deletion)
3. **Gateway** - AgentCore Gateway
4. **Memory** - AgentCore Memory with customer data
5. **Lambda Function** - Order lookup function
6. **Cognito Domain** - OAuth domain (waits 5s before user pool deletion)
7. **Cognito User Pool** - Authentication pool
8. **IAM Roles** - Gateway and runtime execution roles
9. **IAM Policies** - Associated policies
10. **ECR Repository** - Docker container storage

### 🔒 Resources Preserved

- **Knowledge Base** - Shared resource, not deleted
- **CloudWatch Logs** - Kept for audit trail
- **Config Files** - Remain for reference

## Usage

### Prerequisites

Ensure you're on the cleanup branch:

```bash
git checkout cleanup
```

### Run the Script

```bash
python3 24_cleanup_aws.py
```

### What Happens

1. **Configuration Loading**
   - Script loads all config files
   - Displays resources to be deleted

2. **Warning Period**
   - 5-second countdown
   - Press Ctrl+C to cancel

3. **Deletion Process**
   - Deletes resources in proper order
   - Shows progress with color-coded output
   - Handles errors gracefully

4. **Completion**
   - Summary of deleted resources
   - Config files remain for reference

## Output Example

```
================================================================================
                        AWS RESOURCE CLEANUP SCRIPT
================================================================================

Region: us-west-2
This will delete ALL AWS resources created for this project

ℹ Loading configuration files...

================================================================================
                        RESOURCES TO BE DELETED
================================================================================

✗ Runtime Agent: arn:aws:bedrock-agentcore:us-west-2:123456789012:runtime/...
✗ Gateway: returnsrefundsgateway-XXXXXXXXXXXX
✗ Memory: returns_refunds_memory-XXXXXXXXXXXX
✗ Lambda: OrderLookupFunction
✗ Cognito: us-west-2_XXXXXXXXX
✗ IAM Role: ReturnsGatewayRole
✗ IAM Role: AgentCoreRuntimeExecutionRole-XXXXXXXXXX
✗ ECR Repository: returns_refunds_agent

⚠ WARNING: This action cannot be undone!
Starting deletion in 5 seconds...
Press Ctrl+C to cancel

5... 4... 3... 2... 1...

================================================================================
                        STARTING DELETION PROCESS
================================================================================

[Deletion progress with color-coded status messages]

================================================================================
                        CLEANUP COMPLETE
================================================================================

✓ All AWS resources have been deleted
ℹ Configuration files remain for reference
ℹ You can re-deploy by running the setup scripts again

Note: Knowledge Base was NOT deleted (shared resource)
```

## Color Codes

- 🟢 **Green (✓)** - Success
- 🟡 **Yellow (⚠)** - Warning (resource not found/already deleted)
- 🔴 **Red (✗)** - Error
- 🔵 **Cyan (ℹ)** - Information

## Error Handling

### Missing Resources

If a resource is already deleted, the script will:
- Display a warning (yellow)
- Continue with remaining deletions
- Not fail or exit

Example:
```
⚠ Runtime agent not found (already deleted)
```

### Partial Cleanup

If some resources fail to delete:
- Script continues with remaining resources
- Errors are displayed in red
- You can re-run the script to retry

### Configuration Files Missing

If config files are missing:
- Script skips those resources
- Displays warning
- Continues with available configs

## Deletion Order

Resources are deleted in this specific order to avoid dependency errors:

```
1. Runtime Agent
   ↓
2. Gateway Targets (wait 5s)
   ↓
3. Gateway
   ↓
4. Memory
   ↓
5. Lambda Function
   ↓
6. Cognito Domain (wait 5s)
   ↓
7. Cognito User Pool
   ↓
8. IAM Roles & Policies
   ↓
9. ECR Repository
```

## Timing

- **Warning period**: 5 seconds
- **After gateway targets**: 5 second wait
- **After Cognito domain**: 5 second wait
- **After runtime deletion**: 10 second wait
- **Total time**: ~30-60 seconds

## Cancellation

To cancel cleanup:

1. **During warning period**: Press `Ctrl+C`
2. **During deletion**: Press `Ctrl+C` (may leave partial cleanup)

If cancelled during deletion:
- Some resources may be deleted
- Re-run script to complete cleanup
- Script handles already-deleted resources gracefully

## Re-deployment After Cleanup

After cleanup, you can re-deploy:

```bash
# Switch back to main branch
git checkout main

# Run setup scripts
python3 03_create_memory.py
python3 08_create_cognito.py
# ... etc
```

New resource IDs will be generated and saved to config files.

## Troubleshooting

### Script Fails to Import

**Error**: `ModuleNotFoundError: No module named 'bedrock_agentcore_starter_toolkit'`

**Solution**: Install requirements
```bash
pip install -r requirements.txt
```

### Permission Denied

**Error**: `AccessDeniedException`

**Solution**: Check AWS credentials
```bash
aws sts get-caller-identity
```

### Resource Still Exists

**Issue**: Resource not deleted after script runs

**Solution**: 
1. Check AWS Console to verify
2. Re-run the script
3. Manually delete from console if needed

### Config File Not Found

**Warning**: `Config file not found: runtime_config.json`

**Solution**: This is normal if resource was never created. Script will skip it.

## Cost Savings

Running cleanup helps avoid ongoing costs for:
- ✅ AgentCore Runtime compute
- ✅ Lambda invocations
- ✅ Cognito active users
- ✅ AgentCore Memory storage
- ✅ ECR storage
- ✅ CloudWatch Logs storage (if you delete logs separately)

## Safety Recommendations

1. **Review resources** before confirming deletion
2. **Backup important data** from Memory if needed
3. **Export CloudWatch logs** if you need them
4. **Take screenshots** of configurations for reference
5. **Test on non-production** resources first

## What's NOT Deleted

- **Knowledge Base** - Shared resource, may be used by other projects
- **CloudWatch Log Groups** - Kept for audit trail
- **S3 Buckets** - If any were created separately
- **VPC Resources** - If any were created separately
- **Config Files** - Remain in project directory

## Manual Cleanup (If Needed)

If you need to manually delete resources:

### CloudWatch Logs
```bash
aws logs delete-log-group --log-group-name /aws/bedrock-agentcore/runtimes/returns_refunds_agent-XXXXXXXXXXXX-DEFAULT --region us-west-2
```

### Knowledge Base (if desired)
```bash
# Via CloudFormation
aws cloudformation delete-stack --stack-name knowledgebase --region us-west-2
```

## Support

If you encounter issues:
1. Check error messages in red
2. Verify AWS credentials
3. Check AWS Console for resource status
4. Re-run script if needed
5. Refer to AWS documentation for specific services

---

**Script**: `24_cleanup_aws.py`
**Branch**: cleanup
**Region**: us-west-2
**Last Updated**: 2026-04-04
