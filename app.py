from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
        # A simple message to show which version is running
            return 'Hello from my CI/CD Pipeline! Version 1'

        if __name__ == '__main__':
                app.run(host='0.0.0.0', port=5000)
