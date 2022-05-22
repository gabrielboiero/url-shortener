import re
import random
import string
import jwt
import datetime
from flask import Flask, request, jsonify, redirect
from functools import wraps

data = {}
users = {}
app = Flask(__name__)
app.config['SECRET_KEY'] = 'UrlShortenerApp'
app.config['TOKEN_EXPIRATION_TIME'] = 1800  # time span in seconds


def verify_jwt_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        jwt_token = request.headers.get('jwt_token')
        if not jwt_token:
            return jsonify({'status': 'error', 'error': 'Missing "jwt_token" in headers'}), 400
        try:
            jwt.decode(jwt_token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.exceptions.InvalidTokenError:
            return jsonify({'status': 'error', 'message': 'Invalid token or expired'}), 404
        except Exception as e:
            return jsonify({'status': 'error', 'message': f'Exception processing token: {e}'}), 400

        return f(*args, **kwargs)
    return decorated


@app.route('/authenticate', methods=['POST'])
def authenticate():
    if 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        if email in users and users[email] == request.form['password']:
            jwt_token = jwt.encode(
                {'user': email,
                 'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=app.config['TOKEN_EXPIRATION_TIME'])
                 },
                app.config['SECRET_KEY'],
                algorithm='HS256'
            )
            return jsonify({'jwt_token': jwt_token})
        else:
            return jsonify({'status': 'error', 'message': f'Invalid email or password'}), 404
    else:
        return jsonify({'status': 'error', 'message': 'Missing email or password'}), 400


@app.route('/register', methods=['POST'])
def register():
    if 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        if email not in users:
            users[email] = request.form['password']
            return jsonify({'status': 'success', 'message': f'User {email} created successfully'}), 200
        else:
            return jsonify({'status': 'error', 'message': f'User {email} already exists'}), 409
    else:
        return jsonify({'status': 'error', 'message': 'Missing email or password'}), 400


@app.route('/create', methods=['POST'])
@verify_jwt_token
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
@verify_jwt_token
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
