# -----------------------------------------------------------------
# Flask Application 2.0
# Purpose: A slightly more advanced Flask app that demonstrates
#          reading environment variables and displaying pod info.
# -----------------------------------------------------------------

import os
import socket
from flask import Flask, jsonify

app = Flask(__name__)

# --- Configuration ---
# Get the application version from an environment variable.
# The 'v1.0' is a default value if the variable isn't set.
APP_VERSION = os.environ.get('APP_VERSION', 'v1.0 - Default')

@app.route('/')
def home():
    """Main endpoint that returns a simple HTML page."""
    
    # Get the hostname of the container/pod where this code is running.
    pod_hostname = socket.gethostname()
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>CI/CD Deployed App</title>
        <style>
            body {{ 
                font-family: sans-serif; 
                background-color: #2c3e50; 
                color: #ecf0f1; 
                text-align: center; 
                padding-top: 100px; 
            }}
            h1 {{ color: #1abc9c; }}
            p {{ font-size: 1.2em; }}
            .hostname {{ 
                background-color: #34495e; 
                padding: 10px; 
                border-radius: 5px; 
                display: inline-block;
                margin-top: 20px;
                color: #f1c40f;
            }}
        </style>
    </head>
    <body>
        <h1>Welcome to My CI/CD Deployed Application!</h1>
        <p>This application was automatically deployed by my Jenkins pipeline.</p>
        <p>Application Version: <strong>{APP_VERSION}</strong></p>
        <div class="hostname">
            Served from Pod: <strong>{pod_hostname}</strong>
        </div>
    </body>
    </html>
    """
    return html

@app.route('/health')
def health_check():
    """A simple health check endpoint."""
    return jsonify(status="ok", version=APP_VERSION)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
