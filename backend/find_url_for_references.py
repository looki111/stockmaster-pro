"""
Find all url_for() references in the templates
"""

import os
import re
import sys
from flask import Flask

def find_url_for_references():
    """Find all url_for() references in the templates"""
    # Create a Flask app
    app = Flask(__name__)
    
    # Import the app
    from app import app as main_app
    
    # Get all available routes
    available_routes = set()
    for rule in main_app.url_map.iter_rules():
        available_routes.add(rule.endpoint)
    
    print(f"Available routes: {sorted(available_routes)}")
    
    # Find all template files
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    template_files = []
    for root, dirs, files in os.walk(template_dir):
        for file in files:
            if file.endswith('.html'):
                template_files.append(os.path.join(root, file))
    
    # Find all url_for() references in the templates
    url_for_pattern = re.compile(r"url_for\(['\"]([^'\"]+)['\"]")
    references = []
    
    for template_file in template_files:
        with open(template_file, 'r', encoding='utf-8') as f:
            try:
                content = f.read()
                for line_num, line in enumerate(content.split('\n'), 1):
                    for match in url_for_pattern.finditer(line):
                        endpoint = match.group(1)
                        references.append({
                            'file': os.path.relpath(template_file, os.path.dirname(__file__)),
                            'line': line_num,
                            'endpoint': endpoint,
                            'valid': endpoint in available_routes
                        })
            except UnicodeDecodeError:
                print(f"Error reading file: {template_file}")
    
    # Print all invalid references
    invalid_references = [ref for ref in references if not ref['valid']]
    
    if invalid_references:
        print("\nInvalid url_for() references:")
        for ref in invalid_references:
            print(f"{ref['file']}:{ref['line']} - url_for('{ref['endpoint']}')")
    else:
        print("\nAll url_for() references are valid!")
    
    # Print all references
    print("\nAll url_for() references:")
    for ref in references:
        status = "✓" if ref['valid'] else "✗"
        print(f"{status} {ref['file']}:{ref['line']} - url_for('{ref['endpoint']}')")
    
    return references

if __name__ == "__main__":
    find_url_for_references()
