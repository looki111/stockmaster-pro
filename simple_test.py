from flask import Flask, render_template, send_from_directory, url_for

app = Flask(__name__, 
            static_url_path='/static',
            static_folder='backend/static',
            template_folder='backend/templates')

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Static Test</title>
        <link rel="stylesheet" href="/static/css/test.css">
    </head>
    <body>
        <h1>Static File Test</h1>
        <p>If you can see this page with styling, static file serving is working!</p>
        <script src="/static/js/test.js"></script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True, port=5001)
