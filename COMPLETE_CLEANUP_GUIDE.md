# Complete Cleanup Guide

This guide covers both AWS resource cleanup and local file cleanup for the Bedrock AgentCore project.

## Overview

Two cleanup scripts are available:

1. **24_cleanup_aws.py** - Deletes AWS resources (costs money if left running)
2. **25_cleanup_files.py** - Deletes local project files (can be regenerated)

## Quick Start

### Complete Cleanup (AWS + Files)

```bash
# Switch to cleanup branch
git checkout cleanup

# Delete AWS resources
python3 24_cleanup_aws.py

# Delete local files
python3 25_cleanup_files.py
```

### AWS Resources Only

```bash
git checkout cleanup
python3 24_cleanup_aws.py
```

### Local Files Only

```bash
git checkout cleanup
python3 25_cleanup_files.py
```

---

## Script 1: AWS Resource Cleanup

### Purpose
Delete all AWS resources to avoid ongoing costs.

### What Gets Deleted

| Resource | Description | Cost Impact |
|----------|-------------|-------------|
| Runtime Agent | Deployed AgentCore agent | High - compute costs |
| Gateway | AgentCore Gateway | Medium - API calls |
| Memory | AgentCore Memory | Low - storage costs |
| Lambda | Order lookup function | Low - invocation costs |
| Cognito | User pool & domain | Low - active user costs |
| IAM Roles | Execution roles | None - free |
| ECR Repository | Docker images | Low - storage costs |

### What's Preserved

- ✅ Knowledge Base (shared resource)
- ✅ CloudWatch Logs (audit trail)
- ✅ Config files (for reference)

### Usage

```bash
python3 24_cleanup_aws.py
```

**Output**:
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

✗ Runtime Agent: arn:aws:bedrock-agentcore:...
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

[Deletion process with color-coded output]

================================================================================
                        CLEANUP COMPLETE
================================================================================

✓ All AWS resources have been deleted
```

### Deletion Order

1. Runtime Agent (waits 10s)
2. Gateway Targets → **5s wait** → Gateway
3. Memory
4. Lambda Function
5. Cognito Domain → **5s wait** → User Pool
6. IAM Roles & Policies
7. ECR Repository

### Time Required
- **Total**: ~30-60 seconds
- **Warning**: 5 seconds
- **Execution**: 25-55 seconds

---

## Script 2: Local File Cleanup

### Purpose
Delete all generated project files, leaving only documentation and repository structure.

### What Gets Deleted

| Category | Files | Count |
|----------|-------|-------|
| Python Scripts | 01-25_*.py | ~25 files |
| Config Files | *_config.json | ~8 files |
| Docker Files | Dockerfile, .dockerignore | 2 files |
| Runtime Config | .bedrock_agentcore.yaml | 1 file |
| Requirements | requirements.txt | 1 file |
| Setup Scripts | setup_github_remote.sh | 1 file |

**Total**: ~38 files

### What's Preserved

- ✅ README.md and all documentation
- ✅ config-samples/ directory
- ✅ .git/ directory (repository)
- ✅ .kiro/ directory (settings)
- ✅ agentcore-mcp-server/ directory
- ✅ agentcore-workflow/ directory
- ✅ .gitignore

### Usage

```bash
python3 25_cleanup_files.py
```

**Output**:
```
================================================================================
                        FILE CLEANUP SCRIPT
================================================================================

This will delete all generated files from the project

================================================================================
                        FILES TO BE DELETED
================================================================================

Python Scripts (01-25):
  ✗ 01_returns_refunds_agent.py
  ✗ 02_test_agent.py
  ✗ 03_create_memory.py
  [... 22 more files ...]

Config JSON Files:
  ✗ memory_config.json
  ✗ cognito_config.json
  [... 6 more files ...]

Docker Files:
  ✗ Dockerfile
  ✗ .dockerignore

Runtime Configuration:
  ✗ .bedrock_agentcore.yaml

Requirements:
  ✗ requirements.txt

Total files to delete: 38

================================================================================
                        FILES PRESERVED
================================================================================

  ✓ README.md
  ✓ CLEANUP_BRANCH_README.md
  ✓ config-samples/ (directory)
  ✓ .git/ (directory)
  [... more preserved files ...]

⚠ WARNING: This will delete 38 files!
Starting deletion in 5 seconds...
Press Ctrl+C to cancel

5... 4... 3... 2... 1...

[Deletion process]

================================================================================
                        CLEANUP COMPLETE
================================================================================

✓ Files deleted: 38
```

### Time Required
- **Total**: ~10 seconds
- **Warning**: 5 seconds
- **Execution**: ~5 seconds

---

## Complete Cleanup Workflow

### Step 1: Prepare

```bash
# Ensure you're on cleanup branch
git checkout cleanup

# Verify you have the cleanup scripts
ls -la 24_cleanup_aws.py 25_cleanup_files.py
```

### Step 2: AWS Cleanup

```bash
# Delete AWS resources
python3 24_cleanup_aws.py

# Wait for completion (~30-60 seconds)
# Verify in AWS Console if needed
```

### Step 3: File Cleanup

```bash
# Delete local files
python3 25_cleanup_files.py

# Wait for completion (~10 seconds)
```

### Step 4: Verify

```bash
# Check remaining files
ls -la

# Should see:
# - README files
# - config-samples/
# - .git/
# - .kiro/
# - agentcore-mcp-server/
# - Cleanup scripts (24, 25)
```

### Step 5: Return to Main

```bash
# Switch back to main branch
git checkout main

# Main branch still has all original files
```

---

## Safety Features

### Both Scripts Include

- ✅ **5-second warning** before deletion
- ✅ **Cancellation option** (Ctrl+C)
- ✅ **Graceful error handling** (missing resources/files)
- ✅ **Color-coded output** (green/yellow/red/cyan)
- ✅ **Detailed progress** reporting
- ✅ **Final summary** with counts

### Cancellation

Press `Ctrl+C` during the 5-second warning to cancel:

```
⚠ WARNING: This action cannot be undone!
Starting deletion in 5 seconds...
Press Ctrl+C to cancel

5... 4... 3... ^C

✓ Cleanup cancelled by user
```

---

## Re-deployment After Cleanup

### Full Re-deployment

```bash
# Switch to main branch
git checkout main

# Run setup scripts in order
python3 03_create_memory.py
python3 08_create_cognito.py
python3 09_create_gateway_role.py
python3 10_create_lambda.py
python3 11_create_gateway.py
python3 12_add_lambda_to_gateway.py
python3 16_create_runtime_role.py
python3 19_deploy_agent.py

# New resource IDs will be generated
```

### Partial Re-deployment

You can re-run individual scripts to recreate specific resources.

---

## Cost Savings

### AWS Resources (24_cleanup_aws.py)

Running this script saves costs for:

| Resource | Monthly Cost (Estimate) |
|----------|------------------------|
| Runtime Agent | $50-200 (compute) |
| Lambda | $1-10 (invocations) |
| Cognito | $0-5 (active users) |
| Memory | $1-5 (storage) |
| ECR | $0.10/GB (storage) |
| Gateway | $0-10 (API calls) |

**Total Savings**: $50-230/month

### Local Files (25_cleanup_files.py)

- Frees disk space (~5-10 MB)
- Cleans up generated files
- No cost impact

---

## Troubleshooting

### AWS Cleanup Issues

**Problem**: Script fails with permission error

**Solution**: Check AWS credentials
```bash
aws sts get-caller-identity
```

**Problem**: Resource not found error

**Solution**: Normal - resource already deleted. Script continues.

**Problem**: Dependency error

**Solution**: Script handles deletion order automatically. Re-run if needed.

### File Cleanup Issues

**Problem**: Permission denied

**Solution**: Check file permissions
```bash
chmod +w filename
```

**Problem**: Files not found

**Solution**: Normal - files already deleted or never created.

**Problem**: Script deletes wrong files

**Solution**: Script only deletes specific patterns. Review before confirming.

---

## Comparison Table

| Feature | AWS Cleanup | File Cleanup |
|---------|-------------|--------------|
| **Purpose** | Delete cloud resources | Delete local files |
| **Cost Impact** | High ($50-230/month) | None |
| **Reversible** | No (must re-deploy) | No (must re-run scripts) |
| **Time** | 30-60 seconds | 10 seconds |
| **Dependencies** | AWS credentials | File system access |
| **Preserves** | KB, logs, configs | Docs, samples, .git |
| **Warning** | 5 seconds | 5 seconds |
| **Cancellable** | Yes (Ctrl+C) | Yes (Ctrl+C) |

---

## Best Practices

### Before Cleanup

1. ✅ **Backup important data** from Memory
2. ✅ **Export CloudWatch logs** if needed
3. ✅ **Take screenshots** of configurations
4. ✅ **Verify you're on cleanup branch**
5. ✅ **Test on non-production** first

### During Cleanup

1. ✅ **Read the warning** carefully
2. ✅ **Review resources** to be deleted
3. ✅ **Don't interrupt** during deletion
4. ✅ **Watch for errors** in output
5. ✅ **Wait for completion** message

### After Cleanup

1. ✅ **Verify in AWS Console** (for AWS cleanup)
2. ✅ **Check file system** (for file cleanup)
3. ✅ **Review summary** output
4. ✅ **Switch back to main** if done
5. ✅ **Document any issues** encountered

---

## Development Workflow

### Typical Cycle

```
1. Setup (main branch)
   ↓
2. Develop & Test
   ↓
3. AWS Cleanup (cleanup branch)
   ↓
4. File Cleanup (cleanup branch)
   ↓
5. Return to Main
   ↓
6. Repeat
```

### Production Deployment

```
1. Setup (main branch)
   ↓
2. Deploy to Production
   ↓
3. Keep Running
   ↓
4. Cleanup Only When Decommissioning
```

---

## FAQ

### Q: Can I run cleanup scripts on main branch?

**A**: Yes, but they're designed for the cleanup branch. Switch with `git checkout cleanup`.

### Q: What if I accidentally delete everything?

**A**: AWS resources are gone (must re-deploy). Local files can be restored from git: `git checkout main`.

### Q: Can I delete only specific resources?

**A**: Not with these scripts. They're designed for complete cleanup. Manually delete specific resources via AWS Console.

### Q: Will this delete my Knowledge Base?

**A**: No, Knowledge Base is preserved (shared resource).

### Q: Can I undo the cleanup?

**A**: No, but you can re-deploy by running setup scripts again.

### Q: How long does complete cleanup take?

**A**: AWS cleanup: 30-60 seconds. File cleanup: 10 seconds. Total: ~1-2 minutes.

### Q: What if cleanup fails partway through?

**A**: Re-run the script. It handles already-deleted resources gracefully.

### Q: Do I need to run both scripts?

**A**: No. Run AWS cleanup to save costs. Run file cleanup to clean local files. Or run both.

---

## Support

If you encounter issues:

1. Check error messages (color-coded)
2. Verify AWS credentials and permissions
3. Check AWS Console for resource status
4. Review script output for details
5. Re-run scripts if needed
6. Refer to individual script guides

---

**Scripts**: `24_cleanup_aws.py`, `25_cleanup_files.py`
**Branch**: cleanup
**Last Updated**: 2026-04-04
