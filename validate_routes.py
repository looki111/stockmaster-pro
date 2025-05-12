#!/usr/bin/env python3
"""
Route validation script for StockMaster Pro
This script scans template files for url_for calls and validates that the endpoints exist.
Run this before deploying to catch BuildError issues.
"""

import os
import re
import sys
from pathlib import Path

def find_template_files(root_dir):
    """Find all template files in the given directory and subdirectories."""
    template_files = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.html'):
                template_files.append(os.path.join(root, file))
    return template_files

def extract_endpoints(template_file):
    """Extract all url_for endpoints from a template file."""
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match url_for calls: {{ url_for('endpoint') }}
    pattern = r"url_for\('([^']+)'"
    endpoints = re.findall(pattern, content)
    
    return endpoints

def verify_endpoint_files(endpoints, routes_dir):
    """Verify that endpoint files exist and have the right function."""
    missing_endpoints = []
    
    for endpoint in endpoints:
        if '.' in endpoint:  # Format: blueprint.function
            blueprint, function = endpoint.split('.')
            
            # Check if blueprint file exists
            blueprint_file = os.path.join(routes_dir, f"{blueprint}.py")
            if not os.path.exists(blueprint_file):
                missing_endpoints.append(f"Blueprint file not found: {blueprint_file} for endpoint {endpoint}")
                continue
            
            # Check if function exists in blueprint
            with open(blueprint_file, 'r', encoding='utf-8') as f:
                blueprint_content = f.read()
            
            # Look for the route function definition
            function_pattern = rf"def\s+{function}\s*\("
            if not re.search(function_pattern, blueprint_content):
                missing_endpoints.append(f"Function '{function}' not found in {blueprint_file} for endpoint {endpoint}")
    
    return missing_endpoints

def main():
    """Main function."""
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]
    else:
        root_dir = 'backend'
    
    template_dir = os.path.join(root_dir, 'templates')
    routes_dir = os.path.join(root_dir, 'routes')
    
    if not os.path.exists(template_dir):
        print(f"Template directory not found: {template_dir}")
        return 1
    
    if not os.path.exists(routes_dir):
        print(f"Routes directory not found: {routes_dir}")
        return 1
    
    template_files = find_template_files(template_dir)
    print(f"Found {len(template_files)} template files")
    
    all_endpoints = set()
    for template_file in template_files:
        endpoints = extract_endpoints(template_file)
        all_endpoints.update(endpoints)
    
    print(f"Found {len(all_endpoints)} unique endpoints")
    
    missing_endpoints = verify_endpoint_files(all_endpoints, routes_dir)
    
    if missing_endpoints:
        print("\nPotential issues found:")
        for issue in missing_endpoints:
            print(f"- {issue}")
        return 1
    else:
        print("All endpoints appear to be valid!")
        return 0

if __name__ == "__main__":
    sys.exit(main()) 