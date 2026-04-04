#!/usr/bin/env python3
"""
Script to get CloudWatch GenAI Observability dashboard URL.
Provides access to monitoring and tracing for the deployed agent.
"""

import json
import os

print("="*80)
print("CLOUDWATCH GENAI OBSERVABILITY DASHBOARD")
print("="*80)

# Load runtime config if available
agent_name = "returns_refunds_agent"
agent_arn = None

if os.path.exists('runtime_config.json'):
    with open('runtime_config.json') as f:
        runtime_config = json.load(f)
        agent_arn = runtime_config.get('agent_arn')
        agent_name = runtime_config.get('agent_name', agent_name)
    print(f"\n✓ Agent Name: {agent_name}")
    print(f"✓ Agent ARN: {agent_arn}")
else:
    print("\n⚠️  runtime_config.json not found - showing generic dashboard")

# Build dashboard URL
region = "us-west-2"
dashboard_url = f"https://console.aws.amazon.com/cloudwatch/home?region={region}#gen-ai-observability/agent-core"

print("\n" + "="*80)
print("DASHBOARD ACCESS")
print("="*80)
print(f"\n🔍 Dashboard URL:")
print(f"   {dashboard_url}")
print(f"\n📍 Region: {region}")

print("\n" + "="*80)
print("DASHBOARD FEATURES")
print("="*80)
print("\n✓ Agent Performance Metrics:")
print("  - Request latency and throughput")
print("  - Success/failure rates")
print("  - Token usage and costs")

print("\n✓ Request Traces and Spans:")
print("  - Complete conversation flow")
print("  - Tool invocation details")
print("  - Model inference timing")

print("\n✓ Session History:")
print("  - User interactions over time")
print("  - Session duration and patterns")
print("  - Actor-specific analytics")

print("\n✓ Error Analysis:")
print("  - Error rates and patterns")
print("  - Failed requests details")
print("  - Debugging information")

print("\n✓ Integration Monitoring:")
print("  - Memory operations")
print("  - Gateway tool calls")
print("  - Knowledge Base retrievals")

# Log group information
if agent_arn:
    # Extract agent ID from ARN
    agent_id = agent_arn.split('/')[-1]
    log_group = f"/aws/bedrock-agentcore/runtimes/{agent_id}-DEFAULT"
    
    print("\n" + "="*80)
    print("CLOUDWATCH LOGS")
    print("="*80)
    print(f"\n📋 Log Group: {log_group}")
    print("\nView logs with AWS CLI:")
    print(f"   aws logs tail {log_group} --follow")
    print("\nView recent logs:")
    print(f"   aws logs tail {log_group} --since 1h")

print("\n" + "="*80)
print("QUICK ACTIONS")
print("="*80)
print("\n1. Open Dashboard:")
print(f"   {dashboard_url}")
print("\n2. View Agent Traces:")
print("   Navigate to 'Traces' tab in the dashboard")
print("\n3. Analyze Performance:")
print("   Check 'Metrics' tab for performance data")
print("\n4. Debug Issues:")
print("   Use 'Logs' integration to see detailed execution logs")

print("\n" + "="*80)
print("💡 TIP: Bookmark the dashboard URL for easy access!")
print("="*80)
