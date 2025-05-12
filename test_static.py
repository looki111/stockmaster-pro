from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__, static_folder='backend/static', template_folder='backend/templates')

@app.route('/')
def index():
    return render_template('login.html', lang='en')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', lang='en')

@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('backend/static', path)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
