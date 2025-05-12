"""
Fix Supabase token initialization issues

This script creates a properly formatted .env file and generates
a simple HTML file to test Supabase authentication.
"""

import os
import shutil

def create_env_file():
    """Create a properly formatted .env file with valid credentials"""
    env_content = """# StockMaster Pro Environment Variables
SECRET_KEY=stockmaster_pro_secret_key_please_change_in_production

# Supabase Configuration - Replace with your own credentials
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlvdXItcHJvamVjdC1pZCIsInJvbGUiOiJhbm9uIiwiaWF0IjoxNjQxNzY5MjAwLCJleHAiOjE5NTczNDU2MDB9.your-anon-key-hash
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlvdXItcHJvamVjdC1pZCIsInJvbGUiOiJzZXJ2aWNlX3JvbGUiLCJpYXQiOjE2NDE3NjkyMDAsImV4cCI6MTk1NzM0NTYwMH0.your-service-key-hash

# Make sure to replace the placeholder URLs and keys with your actual Supabase credentials
# You can find these in your Supabase dashboard under Project Settings > API

# Session Configuration
SESSION_COOKIE_SECURE=False
FORCE_ADMIN_SECRET=stockmaster-admin-secret
"""
    
    # Backup existing .env file if it exists
    if os.path.exists(".env"):
        shutil.copy2(".env", ".env.backup")
        print("✅ Backed up existing .env file to .env.backup")
    
    # Write the new .env file
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("✅ Created new .env file with proper Supabase credentials format")
    print("⚠️ Please update the .env file with your actual Supabase credentials")

def create_test_html():
    """Create a simple HTML file to test Supabase authentication"""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Supabase Authentication Test</title>
    <script src="https://unpkg.com/@supabase/supabase-js@2"></script>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        button { padding: 10px 15px; margin: 5px; cursor: pointer; }
        pre { background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow: auto; }
        .success { color: green; }
        .error { color: red; }
    </style>
</head>
<body>
    <h1>Supabase Authentication Test</h1>
    
    <div>
        <h2>Configuration</h2>
        <div>
            <label>Supabase URL:</label>
            <input type="text" id="supabaseUrl" size="50" placeholder="https://your-project-id.supabase.co" />
        </div>
        <div style="margin-top: 10px;">
            <label>Supabase Anon Key:</label>
            <input type="text" id="supabaseKey" size="50" placeholder="your-anon-key" />
        </div>
        <button id="initializeBtn">Initialize Supabase</button>
    </div>
    
    <div style="margin-top: 20px;">
        <h2>Test Authentication</h2>
        <div>
            <label>Email:</label>
            <input type="email" id="email" placeholder="test@example.com" />
        </div>
        <div style="margin-top: 10px;">
            <label>Password:</label>
            <input type="password" id="password" placeholder="password" />
        </div>
        <button id="signUpBtn">Sign Up</button>
        <button id="signInBtn">Sign In</button>
        <button id="getTokenBtn">Get JWT Token</button>
        <button id="checkTokenBtn">Verify Token</button>
    </div>
    
    <div style="margin-top: 20px;">
        <h2>Results</h2>
        <pre id="results">Initialize Supabase client first...</pre>
    </div>
    
    <script>
        let supabase = null;
        
        // Initialize Supabase
        document.getElementById('initializeBtn').addEventListener('click', () => {
            const supabaseUrl = document.getElementById('supabaseUrl').value;
            const supabaseKey = document.getElementById('supabaseKey').value;
            
            if (!supabaseUrl || !supabaseKey) {
                showResults('Please enter Supabase URL and Key', 'error');
                return;
            }
            
            try {
                supabase = supabase.createClient(supabaseUrl, supabaseKey);
                showResults('Supabase client initialized successfully!', 'success');
            } catch (error) {
                showResults(`Error initializing Supabase: ${error.message}`, 'error');
            }
        });
        
        // Sign Up
        document.getElementById('signUpBtn').addEventListener('click', async () => {
            if (!supabase) {
                showResults('Please initialize Supabase client first', 'error');
                return;
            }
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            try {
                const { data, error } = await supabase.auth.signUp({
                    email,
                    password
                });
                
                if (error) throw error;
                showResults(`Sign up successful: ${JSON.stringify(data, null, 2)}`, 'success');
            } catch (error) {
                showResults(`Sign up error: ${error.message}`, 'error');
            }
        });
        
        // Sign In
        document.getElementById('signInBtn').addEventListener('click', async () => {
            if (!supabase) {
                showResults('Please initialize Supabase client first', 'error');
                return;
            }
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            try {
                const { data, error } = await supabase.auth.signInWithPassword({
                    email,
                    password
                });
                
                if (error) throw error;
                showResults(`Sign in successful: ${JSON.stringify(data, null, 2)}`, 'success');
            } catch (error) {
                showResults(`Sign in error: ${error.message}`, 'error');
            }
        });
        
        // Get JWT Token
        document.getElementById('getTokenBtn').addEventListener('click', async () => {
            if (!supabase) {
                showResults('Please initialize Supabase client first', 'error');
                return;
            }
            
            try {
                const { data, error } = await supabase.auth.getSession();
                
                if (error) throw error;
                if (!data.session) {
                    showResults('No active session. Please sign in first.', 'error');
                    return;
                }
                
                const token = data.session.access_token;
                showResults(`JWT Token: ${token}`, 'success');
            } catch (error) {
                showResults(`Get token error: ${error.message}`, 'error');
            }
        });
        
        // Check Token Validity
        document.getElementById('checkTokenBtn').addEventListener('click', async () => {
            if (!supabase) {
                showResults('Please initialize Supabase client first', 'error');
                return;
            }
            
            try {
                const { data, error } = await supabase.auth.getUser();
                
                if (error) throw error;
                showResults(`Token is valid. User data: ${JSON.stringify(data, null, 2)}`, 'success');
            } catch (error) {
                showResults(`Token verification error: ${error.message}`, 'error');
            }
        });
        
        // Helper to show results
        function showResults(message, type) {
            const resultsElem = document.getElementById('results');
            resultsElem.textContent = message;
            resultsElem.className = type;
        }
    </script>
</body>
</html>
"""
    
    # Write the HTML file
    with open("test_supabase_auth.html", "w") as f:
        f.write(html_content)
    
    print("✅ Created test_supabase_auth.html to test Supabase authentication")
    print("   Open this file in a browser to test your Supabase configuration")

def main():
    """Main function to fix Supabase token issues"""
    print("Fixing Supabase Token Initialization Issues")
    print("=" * 50)
    
    # Create a properly formatted .env file
    create_env_file()
    
    # Create a test HTML file
    create_test_html()
    
    print("\nNext steps:")
    print("1. Update the .env file with your actual Supabase project credentials")
    print("2. If using the Python backend, restart your application")
    print("3. Open test_supabase_auth.html in a browser to test authentication")
    print("4. If the issue persists, check the Supabase dashboard for account status")

if __name__ == "__main__":
    main() 