#!/usr/bin/env python3
"""
Script to check if GitHub workflows that perform git push operations have appropriate permissions.
This script helps ensure that workflows requiring "contents: write" permission are properly configured.
"""

import os
import re
import yaml
from pathlib import Path

def check_for_git_push_operations(content):
    """Check if content contains git push operations or actions that might push changes."""
    push_patterns = [
        r'git\s+push',
        r'git\s+commit.*&&.*git\s+push',
        r'uses:.*git-auto-commit',
        r'uses:.*commit.*action',
        r'uses:.*push.*action',
        r'run:.*git\s+push',
        # Add more patterns as needed
    ]
    
    for pattern in push_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return True
    return False

def check_workflow_file(workflow_path):
    """Check a single workflow file for git push operations and permissions."""
    try:
        with open(workflow_path, 'r') as f:
            content = f.read()
            
        # Check if workflow has git push operations
        has_git_push = check_for_git_push_operations(content)
        
        if not has_git_push:
            return True, "No git push operations found"
            
        # Parse YAML to check permissions
        try:
            workflow = yaml.safe_load(content)
        except yaml.YAMLError as e:
            return False, f"Failed to parse YAML: {e}"
            
        # Check if workflow has contents: write permission
        permissions = workflow.get('permissions', {})
        
        # Check both top-level and job-level permissions
        has_contents_write = False
        
        # Check top-level permissions
        if isinstance(permissions, dict) and permissions.get('contents') == 'write':
            has_contents_write = True
        elif permissions == 'write-all':
            has_contents_write = True
            
        # Check job-level permissions
        jobs = workflow.get('jobs', {})
        for job_name, job_config in jobs.items():
            job_permissions = job_config.get('permissions', {})
            if isinstance(job_permissions, dict) and job_permissions.get('contents') == 'write':
                has_contents_write = True
            elif job_permissions == 'write-all':
                has_contents_write = True
                
        if has_contents_write:
            return True, "Has git push operations and appropriate permissions"
        else:
            return False, "Has git push operations but missing 'contents: write' permission"
            
    except Exception as e:
        return False, f"Error reading file: {e}"

def main():
    """Main function to check all workflow files."""
    workflows_dir = Path('.github/workflows')
    
    if not workflows_dir.exists():
        print("No .github/workflows directory found")
        return 1
        
    issues_found = False
    
    for workflow_file in workflows_dir.glob('*.y*ml'):
        is_valid, message = check_workflow_file(workflow_file)
        
        if is_valid:
            print(f"✅ {workflow_file.name}: {message}")
        else:
            print(f"❌ {workflow_file.name}: {message}")
            issues_found = True
            
    if issues_found:
        print("\nSome workflows need attention. Please add 'contents: write' permission to workflows that perform git push operations.")
        return 1
    else:
        print("\nAll workflows have appropriate permissions.")
        return 0

if __name__ == "__main__":
    exit(main())