"""
Simple Flask app to test Supabase connection
"""

import os
from flask import Flask, render_template
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
app.config.update(
    SECRET_KEY='test-key',
    SUPABASE_URL=os.getenv('SUPABASE_URL', ''),
    SUPABASE_KEY=os.getenv('SUPABASE_KEY', '')
)

@app.route('/')
def index():
    return render_template('test_supabase.html')

if __name__ == '__main__':
    print("Supabase URL:", app.config['SUPABASE_URL'])
    print("Supabase Key (first 10 chars):", app.config['SUPABASE_KEY'][:10] + "..." if app.config['SUPABASE_KEY'] else "Not set")
    app.run(debug=True, port=5001) 