"""
Simple script to check for url_for references in templates
"""

import os
import re
from pathlib import Path

def find_url_for_references():
    """Find all url_for references in templates"""
    # Find all template files
    template_dir = Path('backend/templates')
    template_files = list(template_dir.glob('**/*.html'))
    
    # Find all url_for references in the templates
    url_for_pattern = re.compile(r"url_for\(['\"]([^'\"]+)['\"]")
    references = []
    
    for template_file in template_files:
        try:
            content = template_file.read_text(encoding='utf-8')
            for line_num, line in enumerate(content.split('\n'), 1):
                for match in url_for_pattern.finditer(line):
                    endpoint = match.group(1)
                    references.append({
                        'file': str(template_file.relative_to(Path('backend'))),
                        'line': line_num,
                        'endpoint': endpoint
                    })
        except UnicodeDecodeError:
            print(f"Error reading file: {template_file}")
    
    # Group references by endpoint
    endpoints = {}
    for ref in references:
        endpoint = ref['endpoint']
        if endpoint not in endpoints:
            endpoints[endpoint] = []
        endpoints[endpoint].append(f"{ref['file']}:{ref['line']}")
    
    # Print all references grouped by endpoint
    print("\nAll url_for references grouped by endpoint:")
    for endpoint, locations in sorted(endpoints.items()):
        print(f"Endpoint: {endpoint}")
        for location in locations:
            print(f"  - {location}")
    
    return references

if __name__ == "__main__":
    find_url_for_references()
