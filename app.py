from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    return "Hello Nuclear Geeks"

@app.route('/abc', methods=['GET'])
def index1():
    return "Hello Nuclear Geeks"

if __name__ == '__main__':
    app.run()