
#!/usr/bin/env python
"""
Test Token Fix for StockMaster Pro

This script provides a simple Flask app to test token verification.
"""

import os
import json
import logging
from flask import Flask, request, jsonify, render_template_string

# Try to import the patched token verification
try:
    from auth.patched_token_verify import verify_supabase_token, get_token_from_request
except ImportError:
    from auth.supabase_auth import verify_supabase_token, get_token_from_request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'test_secret_key'

# Test token verification page
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Token Verification Test</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="supabase-url" content="{{ supabase_url }}">
    <meta name="supabase-key" content="{{ supabase_key }}">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.5;
        }
        h1, h2 {
            color: #333;
        }
        .result {
            margin: 20px 0;
            padding: 15px;
            border-radius: 4px;
        }
        .success {
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
        }
        .error {
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }
        .code {
            font-family: monospace;
            background-color: #f5f5f5;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
        }
        button, input {
            padding: 8px 12px;
            margin: 5px 0;
        }
        button {
            background-color: #0066cc;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background-color: #0056b3;
        }
    </style>
    <script src="https://unpkg.com/@supabase/supabase-js@2"></script>
</head>
<body>
    <h1>Token Verification Test</h1>
    
    <div id="login-form">
        <h2>Sign in to get a token</h2>
        <div>
            <label for="email">Email:</label>
            <input type="email" id="email" placeholder="Your email">
        </div>
        <div>
            <label for="password">Password:</label>
            <input type="password" id="password" placeholder="Your password">
        </div>
        <button onclick="signIn()">Sign In</button>
    </div>
    
    <div id="token-result" class="result" style="display: none;"></div>
    
    <div id="token-test" style="display: none;">
        <h2>Test Token Verification</h2>
        <button onclick="testToken()">Test Token Verification</button>
        <div id="test-result" class="result" style="display: none;"></div>
    </div>
    
    <script>
        // Initialize Supabase client
        const supabaseUrl = document.querySelector('meta[name="supabase-url"]').content;
        const supabaseKey = document.querySelector('meta[name="supabase-key"]').content;
        const supabase = supabase.createClient(supabaseUrl, supabaseKey);
        
        let currentToken = null;
        
        async function signIn() {
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            if (!email || !password) {
                showError("Please enter email and password");
                return;
            }
            
            try {
                const { data, error } = await supabase.auth.signInWithPassword({
                    email: email,
                    password: password
                });
                
                if (error) {
                    showError(`Login error: ${error.message}`);
                    return;
                }
                
                currentToken = data.session.access_token;
                
                // Show token
                const resultDiv = document.getElementById('token-result');
                resultDiv.className = 'result success';
                resultDiv.innerHTML = `
                    <h3>Successfully signed in!</h3>
                    <p>Token received (first 20 chars): ${currentToken.substring(0, 20)}...</p>
                `;
                resultDiv.style.display = 'block';
                
                // Show token test section
                document.getElementById('token-test').style.display = 'block';
            } catch (error) {
                showError(`Unexpected error: ${error.message}`);
            }
        }
        
        async function testToken() {
            if (!currentToken) {
                showError("No token available. Please sign in first.");
                return;
            }
            
            try {
                const response = await fetch('/verify-token', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${currentToken}`
                    }
                });
                
                const result = await response.json();
                
                const resultDiv = document.getElementById('test-result');
                
                if (result.valid) {
                    resultDiv.className = 'result success';
                    resultDiv.innerHTML = `
                        <h3>Token is valid!</h3>
                        <p>User ID: ${result.user_id || 'unknown'}</p>
                        <p>Email: ${result.email || 'unknown'}</p>
                        <pre class="code">${JSON.stringify(result.payload, null, 2)}</pre>
                    `;
                } else {
                    resultDiv.className = 'result error';
                    resultDiv.innerHTML = `
                        <h3>Token verification failed</h3>
                        <p>Error: ${result.error || 'Unknown error'}</p>
                    `;
                }
                
                resultDiv.style.display = 'block';
            } catch (error) {
                showError(`Test request error: ${error.message}`);
            }
        }
        
        function showError(message) {
            const resultDiv = document.getElementById('token-result');
            resultDiv.className = 'result error';
            resultDiv.textContent = message;
            resultDiv.style.display = 'block';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    # Get Supabase config from environment
    supabase_url = os.getenv('SUPABASE_URL', '')
    supabase_key = os.getenv('SUPABASE_KEY', '')
    
    return render_template_string(
        HTML_TEMPLATE, 
        supabase_url=supabase_url,
        supabase_key=supabase_key
    )

@app.route('/verify-token', methods=['POST'])
def verify_token():
    # Get token from request
    token = get_token_from_request(request)
    
    if not token:
        return jsonify({
            'valid': False,
            'error': 'No token provided in request'
        })
    
    # Verify token
    is_valid, payload = verify_supabase_token(token)
    
    if not is_valid:
        return jsonify({
            'valid': False,
            'error': 'Token verification failed'
        })
    
    return jsonify({
        'valid': True,
        'user_id': payload.get('sub'),
        'email': payload.get('email'),
        'payload': payload
    })

if __name__ == '__main__':
    import sys
    
    # Use port from argument or default to 5002
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5002
    
    print(f"\nTest token verification app starting on http://localhost:{port}/")
    print("Open this URL in your browser to test token verification\n")
    
    app.run(debug=True, port=port)
