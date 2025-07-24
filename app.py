from flask import Flask

app = Flask(__name__)

@app.route('/')
def show_msg():
    return 'finally gitea webhooks working 201 request!, K3d - Kubernetes running!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
