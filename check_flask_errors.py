#!/usr/bin/env python3
"""
Check for common Flask errors in StockMaster Pro
This script analyzes the application code to find potential issues.
"""

import os
import re
import sys
from pathlib import Path

def analyze_blueprints(routes_dir):
    """Analyze blueprints to find registration issues."""
    issues = []
    
    # Get all route files
    route_files = [f for f in os.listdir(routes_dir) if f.endswith('.py')]
    
    for route_file in route_files:
        file_path = os.path.join(routes_dir, route_file)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if blueprint is defined
        blueprint_match = re.search(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*Blueprint\(', content)
        if not blueprint_match:
            issues.append(f"No Blueprint defined in {route_file}")
            continue
        
        blueprint_name = blueprint_match.group(1)
        
        # Check routes without @login_required
        route_matches = re.finditer(r'@' + re.escape(blueprint_name) + r'\.route\([\'"]([^\'"]+)[\'"](.*?)\n\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)', content, re.DOTALL)
        
        for match in route_matches:
            route_path = match.group(1)
            route_decorators = match.group(2)
            func_name = match.group(3)
            
            if '@login_required' not in route_decorators and 'login' not in func_name and 'register' not in func_name:
                issues.append(f"Route {route_path} in {route_file} may be missing @login_required")
    
    return issues

def analyze_templates(template_dir):
    """Analyze templates for common issues."""
    issues = []
    
    # Get all template files
    template_files = []
    for root, _, files in os.walk(template_dir):
        for file in files:
            if file.endswith('.html'):
                template_files.append(os.path.join(root, file))
    
    for template_file in template_files:
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for unclosed tags
        unclosed_tags = []
        for tag in ['div', 'span', 'p', 'a', 'button', 'form', 'table', 'tr', 'td', 'th']:
            open_count = len(re.findall(r'<' + tag + r'[^>]*>', content))
            close_count = len(re.findall(r'</' + tag + '>', content))
            
            if open_count > close_count:
                unclosed_tags.append(f"{tag} ({open_count - close_count})")
        
        if unclosed_tags:
            issues.append(f"Potentially unclosed tags in {template_file}: {', '.join(unclosed_tags)}")
        
        # Check for hardcoded URLs
        hardcoded_urls = re.findall(r'href=[\'"]/(.*?)[\'"]', content)
        if hardcoded_urls:
            issues.append(f"Hardcoded URLs in {template_file}: {', '.join(hardcoded_urls)}")
    
    return issues

def check_app_initialization(app_dir):
    """Check app initialization for common issues."""
    issues = []
    
    # Look for app.py or similar files
    app_files = [f for f in os.listdir(app_dir) if f in ['app.py', '__init__.py', 'main.py', 'wsgi.py']]
    
    for app_file in app_files:
        file_path = os.path.join(app_dir, app_file)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for debug=True in production
        if 'app.run' in content and 'debug=True' in content and 'if __name__' not in content:
            issues.append(f"app.run(debug=True) found outside if __name__ == '__main__' block in {app_file}")
        
        # Check for missing blueprint registrations
        blueprint_imports = re.findall(r'from\s+routes\.([a-zA-Z_][a-zA-Z0-9_]*)\s+import\s+([a-zA-Z_][a-zA-Z0-9_]*)', content)
        
        for module, blueprint_var in blueprint_imports:
            if f"app.register_blueprint({blueprint_var})" not in content:
                issues.append(f"Blueprint {blueprint_var} imported but not registered in {app_file}")
    
    return issues

def main():
    """Main function."""
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]
    else:
        root_dir = 'backend'
    
    routes_dir = os.path.join(root_dir, 'routes')
    template_dir = os.path.join(root_dir, 'templates')
    
    if not os.path.exists(routes_dir):
        print(f"Routes directory not found: {routes_dir}")
        return 1
    
    if not os.path.exists(template_dir):
        print(f"Template directory not found: {template_dir}")
        return 1
    
    print("Analyzing Flask application...")
    
    # Analyze blueprints
    blueprint_issues = analyze_blueprints(routes_dir)
    if blueprint_issues:
        print("\nBlueprint issues:")
        for issue in blueprint_issues:
            print(f"- {issue}")
    
    # Analyze templates
    template_issues = analyze_templates(template_dir)
    if template_issues:
        print("\nTemplate issues:")
        for issue in template_issues:
            print(f"- {issue}")
    
    # Check app initialization
    app_issues = check_app_initialization(root_dir)
    if app_issues:
        print("\nApplication initialization issues:")
        for issue in app_issues:
            print(f"- {issue}")
    
    if not (blueprint_issues or template_issues or app_issues):
        print("No common Flask issues found!")
        return 0
    else:
        print("\nPlease review and fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 