#!/usr/bin/env python3
"""
Fix URL references in templates
This script fixes url_for() references in templates that point to non-existent endpoints
"""

import os
import re
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def fix_url_reference(file_path, old_endpoint, new_endpoint):
    """Fix a specific URL reference in a template file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create the pattern to match url_for with the old endpoint
    pattern = r"url_for\(['\"]" + re.escape(old_endpoint) + r"['\"](.*?)\)"
    replacement = r"url_for('" + new_endpoint + r"'\1)"
    
    new_content = re.sub(pattern, replacement, content)
    
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        logging.info(f"✓ Fixed url_for('{old_endpoint}') to url_for('{new_endpoint}') in {file_path}")
        return True
    else:
        logging.warning(f"No changes made to {file_path}")
        return False

def main():
    """Fix all incorrect URL references in templates."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    templates_dir = os.path.join(base_dir, 'backend', 'templates')
    
    # Map of incorrect endpoints to their correct replacements
    endpoint_fixes = {
        'dashboard': 'dashboard.dashboard',
        'promotions.edit_promotion': 'promotions.promotions',  # Temporary fix - replace with actual endpoint
        'promotions.delete_promotion': 'promotions.promotions',  # Temporary fix - replace with actual endpoint
        'inventory.edit_consumption_rule': 'inventory.consumption_rules',  # Temporary fix
        'inventory.delete_consumption_rule': 'inventory.consumption_rules'  # Temporary fix
    }
    
    fixes_made = 0
    
    # Process each template file for each problematic endpoint
    for root, _, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, templates_dir)
                
                for old_endpoint, new_endpoint in endpoint_fixes.items():
                    if fix_url_reference(file_path, old_endpoint, new_endpoint):
                        fixes_made += 1
    
    logging.info(f"Fixed {fixes_made} URL references in templates")
    
    return 0

if __name__ == "__main__":
    exit(main())
