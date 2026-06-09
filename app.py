from flask import Flask
import os

app = Flask(__name__)

VERSION = os.environ.get('APP_VERSION', 'unknown')
COLOR = os.environ.get('APP_COLOR', 'unknown')

@app.route('/')
def home():
    return f'''
    <html>
        <body style="font-family: Arial; text-align: center; padding: 50px;
                     background-color: {'#E3F2FD' if COLOR == 'blue' else '#E8F5E9'}">
            <h1>Flask Blue-Green Demo</h1>
            <h2 style="color: {'#1565C0' if COLOR == 'blue' else '#2E7D32'}">
                {COLOR.upper()} environment
            </h2>
            <p>Version: {VERSION}</p>
            <p>Deployed via Jenkins Blue-Green pipeline</p>
        </body>
    </html>
    '''

@app.route('/health')
def health():
    return {"status": "healthy", "version": VERSION, "color": COLOR}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
