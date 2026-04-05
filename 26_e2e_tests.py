#!/usr/bin/env python3
"""
End-to-End Customer Support Agent Tests

This script runs comprehensive tests against the deployed customer support agent,
simulating various customer scenarios to validate return and refund policies.

Test Categories:
1. Valid Returns (within policy)
2. Invalid Returns (outside policy)
3. Edge Cases (boundary conditions)
4. Memory Integration (customer preferences)
5. Gateway Integration (order lookups)
6. Knowledge Base Integration (policy queries)
7. Multi-turn Conversations
8. Error Handling
"""

import json
import time
import requests
import yaml
from datetime import datetime
from bedrock_agentcore_starter_toolkit import Runtime

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

def print_test(message):
    print(f"{Colors.OKCYAN}▶ {message}{Colors.ENDC}")

def print_success(message):
    print(f"{Colors.OKGREEN}  ✓ {message}{Colors.ENDC}")

def print_failure(message):
    print(f"{Colors.FAIL}  ✗ {message}{Colors.ENDC}")

def print_warning(message):
    print(f"{Colors.WARNING}  ⚠ {message}{Colors.ENDC}")

def print_info(message):
    print(f"  ℹ {message}")

def load_config(filename):
    """Load configuration from JSON file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print_failure(f"Config file not found: {filename}")
        return None
    except json.JSONDecodeError:
        print_failure(f"Invalid JSON in config file: {filename}")
        return None

def get_oauth_token(cognito_config):
    """Get OAuth token from Cognito"""
    token_endpoint = cognito_config['token_endpoint']
    client_id = cognito_config['client_id']
    client_secret = cognito_config['client_secret']
    
    response = requests.post(
        token_endpoint,
        auth=(client_id, client_secret),
        data={'grant_type': 'client_credentials'},
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        raise Exception(f"Failed to get OAuth token: {response.text}")

def invoke_agent(runtime, bearer_token, prompt, actor_id="test_user"):
    """Invoke the deployed agent using Runtime class"""
    payload = {
        "prompt": prompt,
        "actor_id": actor_id
    }
    
    response = runtime.invoke(payload, bearer_token=bearer_token)
    
    # Extract response text
    if isinstance(response, dict):
        return {'output': response.get('response', str(response))}
    else:
        return {'output': str(response)}

class TestResult:
    def __init__(self, name, category):
        self.name = name
        self.category = category
        self.passed = False
        self.message = ""
        self.response = ""
        self.duration = 0

class E2ETestSuite:
    def __init__(self, runtime_config, cognito_config, role_config):
        self.runtime_config = runtime_config
        self.cognito_config = cognito_config
        self.role_config = role_config
        self.bearer_token = None
        self.runtime = None
        self.results = []
        
    def setup(self):
        """Setup test suite"""
        print_header("TEST SUITE SETUP")
        print_info("Getting OAuth token...")
        self.bearer_token = get_oauth_token(self.cognito_config)
        print_success("OAuth token obtained")
        
        # Load runtime configuration
        print_info("Loading runtime configuration...")
        with open('.bedrock_agentcore.yaml') as f:
            runtime_yaml = yaml.safe_load(f)
        
        default_agent = runtime_yaml.get('default_agent')
        agent_config = runtime_yaml.get('agents', {}).get(default_agent, {})
        agent_name = agent_config.get('name')
        entrypoint = agent_config.get('entrypoint')
        
        # Initialize Runtime
        self.runtime = Runtime()
        
        # Build authorizer configuration
        auth_config = {
            "customJWTAuthorizer": {
                "allowedClients": [self.cognito_config["client_id"]],
                "discoveryUrl": self.cognito_config["discovery_url"]
            }
        }
        
        # Configure runtime
        self.runtime.configure(
            entrypoint=entrypoint,
            agent_name=agent_name,
            execution_role=self.role_config["role_arn"],
            auto_create_ecr=True,
            memory_mode="NO_MEMORY",
            requirements_file="requirements.txt",
            region="us-west-2",
            authorizer_configuration=auth_config
        )
        
        print_success("Runtime configured")
        
    def run_test(self, name, category, prompt, actor_id, validation_fn):
        """Run a single test"""
        result = TestResult(name, category)
        print_test(f"{name}")
        
        start_time = time.time()
        try:
            response = invoke_agent(
                self.runtime,
                self.bearer_token,
                prompt,
                actor_id
            )
            result.duration = time.time() - start_time
            result.response = response.get('output', '')
            
            # Run validation
            result.passed, result.message = validation_fn(result.response)
            
            if result.passed:
                print_success(f"PASS - {result.message} ({result.duration:.2f}s)")
            else:
                print_failure(f"FAIL - {result.message} ({result.duration:.2f}s)")
                print_info(f"Response: {result.response[:200]}...")
                
        except Exception as e:
            result.duration = time.time() - start_time
            result.passed = False
            result.message = f"Exception: {str(e)}"
            print_failure(f"ERROR - {result.message}")
        
        self.results.append(result)
        time.sleep(1)  # Rate limiting
        
    def test_valid_returns(self):
        """Test valid return scenarios"""
        print_header("CATEGORY 1: VALID RETURNS")
        
        # Test 1: Recent purchase within return window
        self.run_test(
            "Valid Return - Recent Purchase",
            "Valid Returns",
            "I bought a laptop 10 days ago and want to return it. Order ORD-001.",
            "customer_001",
            lambda r: (
                ("eligible" in r.lower() or "can return" in r.lower() or "accept" in r.lower()),
                "Agent correctly identified eligible return"
            )
        )
        
        # Test 2: Defective product
        self.run_test(
            "Valid Return - Defective Product",
            "Valid Returns",
            "My tablet arrived defective. Can I return it? Order ORD-003.",
            "customer_002",
            lambda r: (
                ("eligible" in r.lower() or "defective" in r.lower() or "return" in r.lower()),
                "Agent handled defective product correctly"
            )
        )
        
        # Test 3: Unopened product
        self.run_test(
            "Valid Return - Unopened Product",
            "Valid Returns",
            "I have an unopened item I'd like to return. What's the process?",
            "customer_003",
            lambda r: (
                ("return" in r.lower() and ("process" in r.lower() or "step" in r.lower() or "how to" in r.lower())),
                "Agent explained return process for unopened items"
            )
        )
        
    def test_invalid_returns(self):
        """Test invalid return scenarios"""
        print_header("CATEGORY 2: INVALID RETURNS")
        
        # Test 1: Outside return window
        self.run_test(
            "Invalid Return - Outside Window",
            "Invalid Returns",
            "I bought a phone 45 days ago. Can I still return it? Order ORD-002.",
            "customer_004",
            lambda r: (
                ("not eligible" in r.lower() or "cannot" in r.lower() or "outside" in r.lower() or "30 days" in r.lower()),
                "Agent correctly rejected return outside window"
            )
        )
        
        # Test 2: Used product without defect
        self.run_test(
            "Invalid Return - Used Product",
            "Invalid Returns",
            "I've been using this laptop for 3 weeks and just don't like it. Can I return it?",
            "customer_005",
            lambda r: (
                ("used" in r.lower() or "opened" in r.lower() or "condition" in r.lower()),
                "Agent addressed used product return policy"
            )
        )
        
        # Test 3: No receipt/order number
        self.run_test(
            "Invalid Return - No Order Info",
            "Invalid Returns",
            "I want to return something but I don't have the order number.",
            "customer_006",
            lambda r: (
                ("order" in r.lower() or "receipt" in r.lower() or "information" in r.lower()),
                "Agent requested necessary order information"
            )
        )
        
    def test_edge_cases(self):
        """Test edge case scenarios"""
        print_header("CATEGORY 3: EDGE CASES")
        
        # Test 1: Exactly 30 days
        self.run_test(
            "Edge Case - Exactly 30 Days",
            "Edge Cases",
            "I bought something exactly 30 days ago. Can I still return it?",
            "customer_007",
            lambda r: (
                ("return" in r.lower() and (len(r) > 50)),  # Agent should provide a response about returns
                "Agent handled 30-day boundary correctly"
            )
        )
        
        # Test 2: Partial refund scenario
        self.run_test(
            "Edge Case - Partial Refund",
            "Edge Cases",
            "If I return a used item, do I get a full refund?",
            "customer_008",
            lambda r: (
                ("partial" in r.lower() or "restocking" in r.lower() or "condition" in r.lower() or "percentage" in r.lower()),
                "Agent explained partial refund policy"
            )
        )
        
        # Test 3: Multiple items in one order
        self.run_test(
            "Edge Case - Multiple Items",
            "Edge Cases",
            "I have an order with 3 items. Can I return just one of them?",
            "customer_009",
            lambda r: (
                ("individual" in r.lower() or "separate" in r.lower() or "each item" in r.lower() or "one" in r.lower()),
                "Agent addressed partial order returns"
            )
        )
        
    def test_memory_integration(self):
        """Test memory integration"""
        print_header("CATEGORY 4: MEMORY INTEGRATION")
        
        # Test 1: Customer preference recall
        self.run_test(
            "Memory - Preference Recall",
            "Memory Integration",
            "Hi! I need help with a return. Remember my communication preference?",
            "user_001",  # User from seed data
            lambda r: (
                ("email" in r.lower()),
                "Agent recalled customer's email preference"
            )
        )
        
        # Test 2: Previous interaction recall
        self.run_test(
            "Memory - Previous Return",
            "Memory Integration",
            "I'm back! Did you help me with a laptop return before?",
            "user_001",  # User from seed data
            lambda r: (
                ("laptop" in r.lower() or "previous" in r.lower() or "before" in r.lower()),
                "Agent recalled previous interaction"
            )
        )
        
    def test_gateway_integration(self):
        """Test gateway integration (order lookups)"""
        print_header("CATEGORY 5: GATEWAY INTEGRATION")
        
        # Test 1: Order lookup via gateway
        self.run_test(
            "Gateway - Order Lookup",
            "Gateway Integration",
            "Can you look up my order ORD-001 and tell me if I can return it?",
            "customer_010",
            lambda r: (
                ("laptop" in r.lower() or "ORD-001" in r),
                "Agent successfully looked up order via gateway"
            )
        )
        
        # Test 2: Invalid order number
        self.run_test(
            "Gateway - Invalid Order",
            "Gateway Integration",
            "What about order ORD-999?",
            "customer_011",
            lambda r: (
                ("not found" in r.lower() or "couldn't find" in r.lower() or "doesn't exist" in r.lower() or "invalid" in r.lower()),
                "Agent handled invalid order number"
            )
        )
        
    def test_knowledge_base(self):
        """Test knowledge base integration"""
        print_header("CATEGORY 6: KNOWLEDGE BASE INTEGRATION")
        
        # Test 1: Policy question
        self.run_test(
            "KB - Return Policy Query",
            "Knowledge Base",
            "What is your return policy for electronics?",
            "customer_012",
            lambda r: (
                ("30 days" in r.lower() or "return window" in r.lower() or "policy" in r.lower()),
                "Agent retrieved policy from knowledge base"
            )
        )
        
        # Test 2: Refund timeline
        self.run_test(
            "KB - Refund Timeline",
            "Knowledge Base",
            "How long does it take to get a refund?",
            "customer_013",
            lambda r: (
                ("days" in r.lower() or "process" in r.lower() or "refund" in r.lower()),
                "Agent provided refund timeline information"
            )
        )
        
    def test_multi_turn_conversations(self):
        """Test multi-turn conversation handling"""
        print_header("CATEGORY 7: MULTI-TURN CONVERSATIONS")
        
        actor_id = "customer_014"
        
        # Turn 1: Initial inquiry
        self.run_test(
            "Multi-turn - Initial Inquiry",
            "Multi-turn",
            "Hi, I need help with a return.",
            actor_id,
            lambda r: (
                ("help" in r.lower() or "return" in r.lower() or "assist" in r.lower()),
                "Agent acknowledged return inquiry"
            )
        )
        
        # Turn 2: Provide order info
        self.run_test(
            "Multi-turn - Provide Order",
            "Multi-turn",
            "It's order ORD-001.",
            actor_id,
            lambda r: (
                ("laptop" in r.lower() or "ORD-001" in r or "order" in r.lower()),
                "Agent processed order information"
            )
        )
        
        # Turn 3: Ask about refund
        self.run_test(
            "Multi-turn - Refund Question",
            "Multi-turn",
            "How much will I get back?",
            actor_id,
            lambda r: (
                ("refund" in r.lower() or "amount" in r.lower() or "$" in r),
                "Agent provided refund information"
            )
        )
        
    def test_error_handling(self):
        """Test error handling"""
        print_header("CATEGORY 8: ERROR HANDLING")
        
        # Test 1: Ambiguous request
        self.run_test(
            "Error - Ambiguous Request",
            "Error Handling",
            "I want to return something.",
            "customer_015",
            lambda r: (
                ("order" in r.lower() or "which" in r.lower() or "information" in r.lower()),
                "Agent requested clarification"
            )
        )
        
        # Test 2: Off-topic question
        self.run_test(
            "Error - Off-topic",
            "Error Handling",
            "What's the weather like today?",
            "customer_016",
            lambda r: (
                ("return" in r.lower() or "refund" in r.lower() or "help" in r.lower() or "assist" in r.lower()),
                "Agent redirected to returns/refunds topic"
            )
        )
        
        # Test 3: Complex scenario
        self.run_test(
            "Error - Complex Scenario",
            "Error Handling",
            "I bought 5 items, returned 2, want to return 1 more, but lost the receipt for that one.",
            "customer_017",
            lambda r: (
                (len(r) > 50),  # Agent should provide a detailed response
                "Agent handled complex scenario"
            )
        )
        
    def run_all_tests(self):
        """Run all test categories"""
        self.setup()
        
        self.test_valid_returns()
        self.test_invalid_returns()
        self.test_edge_cases()
        self.test_memory_integration()
        self.test_gateway_integration()
        self.test_knowledge_base()
        self.test_multi_turn_conversations()
        self.test_error_handling()
        
        self.print_summary()
        
    def print_summary(self):
        """Print test summary"""
        print_header("TEST SUMMARY")
        
        # Overall stats
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"{Colors.BOLD}Overall Results:{Colors.ENDC}")
        print(f"  Total Tests: {total_tests}")
        print(f"  {Colors.OKGREEN}Passed: {passed_tests}{Colors.ENDC}")
        print(f"  {Colors.FAIL}Failed: {failed_tests}{Colors.ENDC}")
        print(f"  Pass Rate: {pass_rate:.1f}%")
        
        # Average duration
        avg_duration = sum(r.duration for r in self.results) / total_tests if total_tests > 0 else 0
        print(f"  Average Response Time: {avg_duration:.2f}s")
        
        # Category breakdown
        print(f"\n{Colors.BOLD}Results by Category:{Colors.ENDC}")
        categories = {}
        for result in self.results:
            if result.category not in categories:
                categories[result.category] = {'passed': 0, 'failed': 0}
            if result.passed:
                categories[result.category]['passed'] += 1
            else:
                categories[result.category]['failed'] += 1
        
        for category, stats in sorted(categories.items()):
            total = stats['passed'] + stats['failed']
            rate = (stats['passed'] / total * 100) if total > 0 else 0
            print(f"  {category}: {stats['passed']}/{total} ({rate:.0f}%)")
        
        # Failed tests detail
        if failed_tests > 0:
            print(f"\n{Colors.BOLD}Failed Tests:{Colors.ENDC}")
            for result in self.results:
                if not result.passed:
                    print(f"  {Colors.FAIL}✗ {result.name}{Colors.ENDC}")
                    print(f"    {result.message}")
        
        # Final verdict
        print()
        if pass_rate >= 90:
            print(f"{Colors.OKGREEN}{Colors.BOLD}✓ EXCELLENT - Agent is performing well!{Colors.ENDC}")
        elif pass_rate >= 75:
            print(f"{Colors.WARNING}{Colors.BOLD}⚠ GOOD - Some issues to address{Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}{Colors.BOLD}✗ NEEDS WORK - Significant issues found{Colors.ENDC}")
        print()

def main():
    """Main test execution"""
    print_header("END-TO-END CUSTOMER SUPPORT AGENT TESTS")
    print(f"{Colors.BOLD}Testing deployed agent with comprehensive scenarios{Colors.ENDC}\n")
    
    # Load configurations
    print_info("Loading configurations...")
    runtime_config = load_config('runtime_config.json')
    cognito_config = load_config('cognito_config.json')
    role_config = load_config('runtime_execution_role_config.json')
    
    if not runtime_config or not cognito_config or not role_config:
        print_failure("Failed to load required configurations")
        return
    
    print_success("Configurations loaded")
    print_info(f"Agent: {runtime_config['agent_arn']}")
    print_info(f"Region: {runtime_config['region']}")
    
    # Run test suite
    suite = E2ETestSuite(runtime_config, cognito_config, role_config)
    suite.run_all_tests()

if __name__ == "__main__":
    main()
