#!/usr/bin/env python3
"""
Script to get CloudWatch log group information for agent logs.
Provides log group name and AWS CLI commands for viewing logs.
"""

import json
import os
from datetime import datetime

print("="*80)
print("CLOUDWATCH LOGS INFORMATION")
print("="*80)

# Check if runtime config exists
if not os.path.exists('runtime_config.json'):
    print("\n❌ Error: runtime_config.json not found")
    print("Please run 19_deploy_agent.py first")
    exit(1)

# Load configuration
with open('runtime_config.json') as f:
    runtime_config = json.load(f)

agent_arn = runtime_config["agent_arn"]
agent_name = runtime_config.get("agent_name", "returns_refunds_agent")
region = runtime_config.get("region", "us-west-2")

print(f"\n✓ Agent Name: {agent_name}")
print(f"✓ Agent ARN: {agent_arn}")
print(f"✓ Region: {region}")

# Extract agent ID from ARN
agent_id = agent_arn.split('/')[-1]

# Build log group name
log_group = f"/aws/bedrock-agentcore/runtimes/{agent_id}-DEFAULT"

# Get current date for log stream prefix
current_date = datetime.now().strftime("%Y/%m/%d")

print("\n" + "="*80)
print("LOG GROUP DETAILS")
print("="*80)
print(f"\n📋 Log Group Name:")
print(f"   {log_group}")
print(f"\n📅 Current Date: {current_date}")
print(f"📍 Region: {region}")

# Build CLI commands
tail_command = f'aws logs tail {log_group} --log-stream-name-prefix "{current_date}/[runtime-logs]" --follow'
recent_command = f'aws logs tail {log_group} --log-stream-name-prefix "{current_date}/[runtime-logs]" --since 1h'
otel_command = f'aws logs tail {log_group} --log-stream-names "otel-rt-logs" --follow'
all_streams_command = f'aws logs tail {log_group} --follow'

print("\n" + "="*80)
print("AWS CLI COMMANDS")
print("="*80)

print("\n1️⃣  Tail Runtime Logs (Real-time):")
print(f"   {tail_command}")

print("\n2️⃣  View Recent Runtime Logs (Last Hour):")
print(f"   {recent_command}")

print("\n3️⃣  Tail OpenTelemetry Logs:")
print(f"   {otel_command}")

print("\n4️⃣  Tail All Log Streams:")
print(f"   {all_streams_command}")

print("\n" + "="*80)
print("LOG STREAM TYPES")
print("="*80)
print("\n📝 Runtime Logs:")
print("   - Agent execution logs")
print("   - Tool invocations")
print("   - Error messages")
print("   - Custom print statements")

print("\n📊 OpenTelemetry Logs:")
print("   - Distributed tracing data")
print("   - Performance metrics")
print("   - Span information")

print("\n" + "="*80)
print("USEFUL FILTERS")
print("="*80)
print("\n🔍 Filter by log level:")
print(f"   aws logs tail {log_group} --filter-pattern ERROR")

print("\n🔍 Filter by keyword:")
print(f"   aws logs tail {log_group} --filter-pattern 'user_001'")

print("\n🔍 View logs from specific time:")
print(f"   aws logs tail {log_group} --since 30m")
print(f"   aws logs tail {log_group} --since 2h")

print("\n" + "="*80)
print("CLOUDWATCH CONSOLE")
print("="*80)
console_url = f"https://console.aws.amazon.com/cloudwatch/home?region={region}#logsV2:log-groups/log-group/{log_group.replace('/', '$252F')}"
print(f"\n🌐 View in Console:")
print(f"   {console_url}")

print("\n" + "="*80)
print("💡 TIP: Use --follow flag to stream logs in real-time!")
print("="*80)
