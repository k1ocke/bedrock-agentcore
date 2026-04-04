#!/usr/bin/env python3
"""
File Cleanup Script

This script deletes all generated files from the Bedrock AgentCore project,
leaving only the repository structure, documentation, and sample configs.

Files deleted:
- Python scripts (01-25)
- Config JSON files
- Docker files
- Requirements file
- Runtime configuration files
- Generated agent files

Files preserved:
- README files
- Documentation
- Config samples
- .git directory
- .kiro directory
"""

import os
import time
import glob
from pathlib import Path

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

def delete_file(filepath):
    """Delete a single file"""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            print_success(f"Deleted: {filepath}")
            return True
        else:
            print_warning(f"Not found: {filepath}")
            return False
    except Exception as e:
        print_error(f"Error deleting {filepath}: {e}")
        return False

def delete_files_by_pattern(pattern, description):
    """Delete files matching a glob pattern"""
    print_info(f"Deleting {description}...")
    files = glob.glob(pattern)
    
    if not files:
        print_warning(f"No files found matching: {pattern}")
        return 0
    
    deleted_count = 0
    for filepath in files:
        if delete_file(filepath):
            deleted_count += 1
    
    return deleted_count

def main():
    """Main cleanup function"""
    print_header("FILE CLEANUP SCRIPT")
    print(f"{Colors.BOLD}This will delete all generated files from the project{Colors.ENDC}\n")
    
    # Define file patterns to delete
    file_patterns = {
        "Python Scripts (01-25)": [
            "01_*.py", "02_*.py", "03_*.py", "04_*.py", "05_*.py",
            "06_*.py", "07_*.py", "08_*.py", "09_*.py", "10_*.py",
            "11_*.py", "12_*.py", "13_*.py", "14_*.py", "15_*.py",
            "15-1_*.py", "16_*.py", "17_*.py", "19_*.py", "20_*.py",
            "21_*.py", "22_*.py", "23_*.py", "24_*.py", "25_*.py"
        ],
        "Config JSON Files": [
            "*_config.json",
            "cognito_config.json",
            "gateway_config.json",
            "gateway_role_config.json",
            "kb_config.json",
            "lambda_config.json",
            "memory_config.json",
            "runtime_config.json",
            "runtime_execution_role_config.json"
        ],
        "Docker Files": [
            "Dockerfile",
            ".dockerignore"
        ],
        "Runtime Configuration": [
            ".bedrock_agentcore.yaml"
        ],
        "Requirements": [
            "requirements.txt"
        ],
        "Setup Scripts": [
            "setup_github_remote.sh"
        ]
    }
    
    # Collect all files to delete
    all_files = []
    print_header("FILES TO BE DELETED")
    
    for category, patterns in file_patterns.items():
        print(f"\n{Colors.BOLD}{category}:{Colors.ENDC}")
        category_files = []
        for pattern in patterns:
            files = glob.glob(pattern)
            category_files.extend(files)
        
        if category_files:
            for f in sorted(category_files):
                print(f"{Colors.FAIL}  ✗ {f}{Colors.ENDC}")
                all_files.append(f)
        else:
            print(f"{Colors.WARNING}  (no files found){Colors.ENDC}")
    
    if not all_files:
        print_warning("\nNo files found to delete")
        return
    
    print(f"\n{Colors.BOLD}Total files to delete: {len(all_files)}{Colors.ENDC}")
    
    # Files that will be preserved
    print_header("FILES PRESERVED")
    preserved = [
        "README.md",
        "CLEANUP_BRANCH_README.md",
        "CLEANUP_BRANCH_SUMMARY.md",
        "CLEANUP_SCRIPT_GUIDE.md",
        "CONFIG_SAMPLES_SUMMARY.md",
        "GITHUB_SETUP_COMPLETE.md",
        ".gitignore",
        ".git/ (directory)",
        ".kiro/ (directory)",
        "config-samples/ (directory)",
        "agentcore-mcp-server/ (directory)",
        "agentcore-workflow/ (directory)",
        "__pycache__/ (directory)"
    ]
    
    for item in preserved:
        print(f"{Colors.OKGREEN}  ✓ {item}{Colors.ENDC}")
    
    # Warning countdown
    WARNING_SECONDS = 5
    print(f"\n{Colors.WARNING}{Colors.BOLD}⚠ WARNING: This will delete {len(all_files)} files!{Colors.ENDC}")
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
    
    total_deleted = 0
    total_failed = 0
    total_missing = 0
    
    for category, patterns in file_patterns.items():
        print(f"\n{Colors.BOLD}{category}{Colors.ENDC}")
        for pattern in patterns:
            files = glob.glob(pattern)
            for filepath in files:
                try:
                    if os.path.exists(filepath):
                        os.remove(filepath)
                        print_success(f"Deleted: {filepath}")
                        total_deleted += 1
                    else:
                        print_warning(f"Not found: {filepath}")
                        total_missing += 1
                except Exception as e:
                    print_error(f"Error deleting {filepath}: {e}")
                    total_failed += 1
    
    # Final summary
    print_header("CLEANUP COMPLETE")
    print(f"{Colors.OKGREEN}✓ Files deleted: {total_deleted}{Colors.ENDC}")
    if total_missing > 0:
        print(f"{Colors.WARNING}⚠ Files not found: {total_missing}{Colors.ENDC}")
    if total_failed > 0:
        print(f"{Colors.FAIL}✗ Files failed: {total_failed}{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}Preserved:{Colors.ENDC}")
    print(f"  • Documentation files (README.md, guides)")
    print(f"  • Config samples (config-samples/)")
    print(f"  • Git repository (.git/)")
    print(f"  • Kiro settings (.kiro/)")
    print(f"  • MCP server code (agentcore-mcp-server/)")
    
    print(f"\n{Colors.OKCYAN}ℹ You can re-run setup scripts to regenerate files{Colors.ENDC}\n")

if __name__ == "__main__":
    main()
