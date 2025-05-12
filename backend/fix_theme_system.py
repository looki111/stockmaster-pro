#!/usr/bin/env python3
"""
Fix Theme System for StockMaster Pro
This script updates all HTML templates to ensure they use the new theme system.
It replaces existing theme toggle code with calls to the theme manager.
"""

import os
import re
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def find_template_files(template_dir):
    """Find all template files in the given directory and subdirectories."""
    template_files = []
    for root, _, files in os.walk(template_dir):
        for file in files:
            if file.endswith('.html'):
                template_files.append(os.path.join(root, file))
    return template_files

def fix_theme_toggle_in_template(template_file):
    """Fix theme toggle code in a single template file."""
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if file has theme toggle script
    if 'themeToggle' in content and ('classList.add' in content or 'localStorage.setItem' in content):
        logging.info(f"Fixing theme toggle in {template_file}")
        
        # Find the script tag containing the theme toggle code
        # This pattern looks for script tags that contain theme toggle code
        pattern = r'<script>(\s*.*?themeToggle.*?\s*function|\s*document\.addEventListener.*?themeToggle|\s*.*?themeToggle.*?addEventListener).*?</script>'
        script_tags = re.findall(pattern, content, re.DOTALL)
        
        if script_tags:
            # Replace old theme toggle implementation with new one
            new_content = content
            for script in script_tags:
                if 'themeToggle' in script and 'theme' in script.lower():
                    # Replace the entire script tag that handles theme toggle
                    script_pattern = r'<script>(\s*.*?themeToggle.*?\s*function|\s*document\.addEventListener.*?themeToggle|\s*.*?themeToggle.*?addEventListener).*?</script>'
                    replacement = """<script>
  // Theme system is now handled by theme-manager.js
  // No additional code needed here as it's automatically initialized
</script>"""
                    new_content = re.sub(script_pattern, replacement, new_content, flags=re.DOTALL)
            
            # Make sure theme toggle element has proper ID and aria-label
            toggle_pattern = r'<button[^>]*id=["\']?themeToggle["\']?[^>]*>'
            if not re.search(toggle_pattern, new_content):
                # Find a button that looks like a theme toggle but doesn't have the id
                theme_btn_pattern = r'<button[^>]*class=["\'].*?(theme|mode).*?["\'][^>]*>'
                theme_buttons = re.findall(theme_btn_pattern, new_content)
                
                for btn in theme_buttons:
                    if 'id=' not in btn and ('theme' in btn.lower() or 'mode' in btn.lower() or 'dark' in btn.lower()):
                        # Add id to this button
                        replacement = btn.replace('<button', '<button id="themeToggle"')
                        new_content = new_content.replace(btn, replacement)
            
            if new_content != content:
                with open(template_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                logging.info(f"✓ Updated theme toggle in {template_file}")
                return True
            else:
                logging.warning(f"No changes needed in {template_file}")
        else:
            logging.warning(f"Could not find theme toggle script in {template_file}")
    
    return False

def fix_html_structure(template_file):
    """Fix HTML structure to support theme classes."""
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if the root html element has lang attribute
    html_tag_pattern = r'<html[^>]*>'
    html_tag = re.search(html_tag_pattern, content)
    
    if html_tag:
        html_tag_str = html_tag.group(0)
        
        # Check if it doesn't have a class attribute and see if we need to add theme-light class
        if 'class=' not in html_tag_str and 'theme-' not in html_tag_str:
            new_html_tag = html_tag_str.replace('<html', '<html class="theme-light"')
            new_content = content.replace(html_tag_str, new_html_tag)
            
            if new_content != content:
                with open(template_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                logging.info(f"✓ Added theme class to html tag in {template_file}")
                return True
    
    return False

def ensure_head_meta_tags(template_file):
    """Ensure necessary meta tags are in the head section."""
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if head section exists
    head_pattern = r'<head>.*?</head>'
    head_match = re.search(head_pattern, content, re.DOTALL)
    
    if head_match:
        head_content = head_match.group(0)
        
        # Check for theme-color meta tag
        if 'name="theme-color"' not in head_content:
            new_head = head_content.replace('<head>', '<head>\n  <meta name="theme-color" content="#ffffff">')
            new_content = content.replace(head_content, new_head)
            
            if new_content != content:
                with open(template_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                logging.info(f"✓ Added theme-color meta tag in {template_file}")
                return True
    
    return False

def main():
    """Main function to fix theme system in all templates."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(script_dir, 'templates')
    
    if not os.path.exists(template_dir):
        logging.error(f"Template directory not found: {template_dir}")
        return 1
    
    # Find all template files
    template_files = find_template_files(template_dir)
    logging.info(f"Found {len(template_files)} template files")
    
    # Track changes
    files_updated = 0
    toggle_fixes = 0
    html_fixes = 0
    meta_fixes = 0
    
    # Process each template file
    for template_file in template_files:
        toggle_fixed = fix_theme_toggle_in_template(template_file)
        html_fixed = fix_html_structure(template_file)
        meta_fixed = ensure_head_meta_tags(template_file)
        
        if toggle_fixed:
            toggle_fixes += 1
        if html_fixed:
            html_fixes += 1
        if meta_fixed:
            meta_fixes += 1
        
        if toggle_fixed or html_fixed or meta_fixed:
            files_updated += 1
    
    logging.info(f"Theme system fix complete:")
    logging.info(f"- Files updated: {files_updated}/{len(template_files)}")
    logging.info(f"- Theme toggle fixes: {toggle_fixes}")
    logging.info(f"- HTML structure fixes: {html_fixes}")
    logging.info(f"- Meta tag fixes: {meta_fixes}")
    
    return 0

if __name__ == "__main__":
    exit(main()) 