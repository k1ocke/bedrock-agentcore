# End-to-End Testing Guide

## Overview

The `26_e2e_tests.py` script provides comprehensive end-to-end testing for the deployed customer support agent, validating all integrations and policy enforcement.

## Test Coverage

### 8 Test Categories

1. **Valid Returns** (3 tests) - Returns that should be accepted
2. **Invalid Returns** (3 tests) - Returns that should be rejected
3. **Edge Cases** (3 tests) - Boundary conditions
4. **Memory Integration** (2 tests) - Customer preference recall
5. **Gateway Integration** (2 tests) - Order lookup via Lambda
6. **Knowledge Base** (2 tests) - Policy information retrieval
7. **Multi-turn Conversations** (3 tests) - Context maintenance
8. **Error Handling** (3 tests) - Ambiguous/off-topic requests

**Total**: 21+ test scenarios

## Features

### Comprehensive Validation

- ✅ **Policy Enforcement**: Valid vs invalid returns
- ✅ **Integration Testing**: Memory, Gateway, Knowledge Base
- ✅ **Conversation Flow**: Multi-turn interactions
- ✅ **Error Handling**: Edge cases and ambiguous requests
- ✅ **Performance**: Response time tracking
- ✅ **Detailed Reporting**: Pass/fail rates by category

### Test Scenarios

#### Valid Returns
- Recent purchase within 30-day window
- Defective product returns
- Unopened product returns

#### Invalid Returns
- Purchase outside 30-day window
- Used products without defects
- Missing order information

#### Edge Cases
- Exactly 30-day boundary
- Partial refund scenarios
- Multiple items in one order

#### Memory Integration
- Customer preference recall (email preference)
- Previous interaction history

#### Gateway Integration
- Successful order lookups (ORD-001, ORD-002, ORD-003)
- Invalid order number handling

#### Knowledge Base
- Return policy queries
- Refund timeline information

#### Multi-turn Conversations
- Context maintenance across turns
- Follow-up question handling
- Information accumulation

#### Error Handling
- Ambiguous requests requiring clarification
- Off-topic questions
- Complex multi-part scenarios

## Usage

### Prerequisites

Ensure you have:
- Deployed agent (runtime_config.json)
- Cognito credentials (cognito_config.json)
- Active AWS resources

### Run Tests

```bash
python3 26_e2e_tests.py
```

### Expected Output

```
================================================================================
                   END-TO-END CUSTOMER SUPPORT AGENT TESTS
================================================================================

Testing deployed agent with comprehensive scenarios

ℹ Loading configurations...
✓ Configurations loaded
ℹ Agent: arn:aws:bedrock-agentcore:us-west-2:123456789012:runtime/...
ℹ Region: us-west-2

================================================================================
                              TEST SUITE SETUP
================================================================================

ℹ Getting OAuth token...
✓ OAuth token obtained

================================================================================
                            CATEGORY 1: VALID RETURNS
================================================================================

▶ Valid Return - Recent Purchase
  ✓ PASS - Agent correctly identified eligible return (2.34s)

▶ Valid Return - Defective Product
  ✓ PASS - Agent handled defective product correctly (1.89s)

▶ Valid Return - Unopened Product
  ✓ PASS - Agent explained return process for unopened items (2.12s)

[... more test categories ...]

================================================================================
                              TEST SUMMARY
================================================================================

Overall Results:
  Total Tests: 21
  Passed: 19
  Failed: 2
  Pass Rate: 90.5%
  Average Response Time: 2.15s

Results by Category:
  Valid Returns: 3/3 (100%)
  Invalid Returns: 3/3 (100%)
  Edge Cases: 2/3 (67%)
  Memory Integration: 2/2 (100%)
  Gateway Integration: 2/2 (100%)
  Knowledge Base: 2/2 (100%)
  Multi-turn: 3/3 (100%)
  Error Handling: 2/3 (67%)

Failed Tests:
  ✗ Edge Case - Exactly 30 Days
    Agent response did not clearly address 30-day boundary
  ✗ Error - Complex Scenario
    Agent response was too brief for complex scenario

✓ EXCELLENT - Agent is performing well!
```

## Test Results Interpretation

### Pass Rates

- **90%+**: Excellent - Agent is production-ready
- **75-89%**: Good - Minor issues to address
- **<75%**: Needs work - Significant issues found

### Response Times

- **<2s**: Excellent
- **2-4s**: Good
- **>4s**: May need optimization

### Common Failure Patterns

1. **Policy Boundary Issues**: Agent unclear on exact 30-day cutoff
2. **Complex Scenarios**: Agent struggles with multi-part questions
3. **Memory Recall**: Agent doesn't recall previous interactions
4. **Gateway Errors**: Order lookup failures
5. **KB Integration**: Policy information not retrieved

## Customization

### Add New Tests

```python
# Add to appropriate test category method
self.run_test(
    "Test Name",
    "Category",
    "Customer prompt here",
    "customer_id",
    lambda r: (
        ("expected text" in r.lower()),
        "Validation message"
    )
)
```

### Modify Validation Logic

```python
# Custom validation function
def custom_validation(response):
    # Your validation logic
    if "expected" in response.lower():
        return True, "Validation passed"
    else:
        return False, "Validation failed"

self.run_test(
    "Test Name",
    "Category",
    "Prompt",
    "actor_id",
    custom_validation
)
```

### Adjust Test Data

Modify test prompts to match your:
- Order numbers (ORD-001, ORD-002, etc.)
- Customer IDs (user_001, customer_001, etc.)
- Policy details (30-day window, etc.)

## Troubleshooting

### OAuth Token Errors

**Error**: `Failed to get OAuth token`

**Solution**: Check cognito_config.json credentials
```bash
cat cognito_config.json
```

### Agent Invocation Errors

**Error**: `Agent invocation failed: 403`

**Solution**: Verify bearer token and agent ARN
```bash
cat runtime_config.json
```

### All Tests Failing

**Issue**: Agent not responding correctly

**Solution**: 
1. Check agent status: `python3 20_check_status.py`
2. View logs: `python3 23_get_logs_info.py`
3. Test manually: `python3 21_invoke_agent.py`

### Timeout Errors

**Issue**: Tests timing out

**Solution**: Increase timeout or check agent performance
```python
# In invoke_agent function
response = requests.post(url, headers=headers, json=payload, timeout=30)
```

### Memory Tests Failing

**Issue**: Agent not recalling preferences

**Solution**: 
1. Verify memory seeded: `python3 05_test_memory.py`
2. Check actor_id matches: Use `user_001` from seed data
3. Wait for memory processing (20-30 seconds after seeding)

### Gateway Tests Failing

**Issue**: Order lookups not working

**Solution**:
1. Verify gateway targets: `python3 13_list_gateway_targets.py`
2. Check Lambda function exists
3. Test gateway connectivity

## Best Practices

### Before Running Tests

1. ✅ **Verify agent is deployed**: `python3 20_check_status.py`
2. ✅ **Check all configs exist**: runtime, cognito, gateway, memory
3. ✅ **Seed memory if needed**: `python3 04_seed_memory.py`
4. ✅ **Wait for memory processing**: 20-30 seconds after seeding

### During Testing

1. ✅ **Monitor output**: Watch for patterns in failures
2. ✅ **Note response times**: Identify slow operations
3. ✅ **Check error messages**: Understand failure reasons
4. ✅ **Let tests complete**: Don't interrupt mid-run

### After Testing

1. ✅ **Review summary**: Analyze pass rates by category
2. ✅ **Investigate failures**: Check agent logs for failed tests
3. ✅ **Document issues**: Note patterns for improvement
4. ✅ **Re-run if needed**: Verify fixes with another test run

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: E2E Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run E2E tests
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        run: python3 26_e2e_tests.py
```

## Performance Benchmarks

### Expected Response Times

| Test Category | Expected Time | Acceptable Range |
|---------------|---------------|------------------|
| Valid Returns | 1.5-2.5s | <4s |
| Invalid Returns | 1.5-2.5s | <4s |
| Edge Cases | 2-3s | <5s |
| Memory Integration | 2-3s | <5s |
| Gateway Integration | 2-4s | <6s |
| Knowledge Base | 2-4s | <6s |
| Multi-turn | 1.5-2.5s | <4s |
| Error Handling | 1.5-2.5s | <4s |

### Optimization Tips

If response times are slow:
1. Check agent model configuration (temperature, max tokens)
2. Optimize tool implementations
3. Review memory retrieval settings
4. Check gateway/Lambda performance
5. Monitor CloudWatch metrics

## Test Data

### Order Numbers Used

- **ORD-001**: Recent laptop purchase (eligible for return)
- **ORD-002**: Old phone purchase (outside return window)
- **ORD-003**: Defective tablet (eligible for return)

### Customer IDs Used

- **user_001**: Has seeded memory (email preference, laptop return history)
- **customer_001-017**: Test customers for various scenarios

### Policy Assumptions

- **Return Window**: 30 days from purchase
- **Condition**: Unopened or defective items eligible
- **Refund**: Full refund for unopened, partial for used
- **Process**: Requires order number/receipt

## Extending the Test Suite

### Add New Category

```python
def test_new_category(self):
    """Test new category"""
    print_header("CATEGORY 9: NEW CATEGORY")
    
    self.run_test(
        "Test Name",
        "New Category",
        "Test prompt",
        "actor_id",
        lambda r: (True, "Validation message")
    )
```

### Add to run_all_tests

```python
def run_all_tests(self):
    self.setup()
    # ... existing tests ...
    self.test_new_category()  # Add here
    self.print_summary()
```

## Reporting

### Generate Test Report

The script automatically generates:
- Overall pass/fail statistics
- Category-level breakdown
- Failed test details
- Performance metrics
- Final verdict

### Export Results

To save results to file:

```python
# Add to print_summary method
with open('test_results.json', 'w') as f:
    json.dump({
        'total': total_tests,
        'passed': passed_tests,
        'failed': failed_tests,
        'pass_rate': pass_rate,
        'categories': categories,
        'failed_tests': [r.name for r in self.results if not r.passed]
    }, f, indent=2)
```

---

**Script**: `26_e2e_tests.py`
**Branch**: main
**Last Updated**: 2026-04-04
**Test Count**: 21+ scenarios across 8 categories
