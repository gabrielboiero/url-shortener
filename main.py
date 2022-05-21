import re
import random
import string

from flask import Flask, request, jsonify, redirect

data = {}
app = Flask(__name__)


@app.route('/authenticate', methods=['POST'])
def authenticate():
    pass


@app.route('/register', methods=['POST'])
def register():
    pass


@app.route('/create', methods=['POST'])
def create():
    if 'url' in request.form:
        url = request.form['url']
        if validate(url):
            url_short = random_string()
            data[url_short] = url
            return jsonify({'status': 'success', 'short_version': url_short}), 200
        else:
            return jsonify({'status': 'error', 'message': 'URL is not a valid format'}), 400
    else:
        return jsonify({'status': 'error', 'message': 'Missing "url" parameter'}), 400


@app.route('/retrieve/<url>', methods=['GET'])
def retrieve(url: str):
    if url in data:
        return jsonify({'url': data[url]}), 201
    else:
        return jsonify({'status': 'error', 'message': 'URL not found'}), 404


@app.route('/<url>', methods=['GET'])
def decode(url: str):
    if url in data:
        return redirect(data[url], code=302)
    else:
        return jsonify({'status': 'error', 'message': 'URL not found'}), 404


# Generate a short string containing numbers and upper+lowercase chars, length of 6 chars,
# validate it is not already in use, otherwise generate a new one until is valid
def random_string() -> str:
    while True:
        short = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        if short not in data:
            return short


def validate(url: str) -> bool:
    if url == '' or url is None or len(url) > 2048:
        return False
    pattern = '((http|https)://)(www.)?[a-zA-Z0-9@:%._\\+~#?&//=]{2,256}\\.[a-z]{2,6}\\b([-a-zA-Z0-9@:%._\\+~#?&//=]*)'
    expression = re.compile(pattern)
    return re.search(expression, url) is not None
