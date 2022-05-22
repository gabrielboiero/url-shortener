# url-shortener

URL Shortener in Python - Assessment task

## Disclaimer

This is a sample app intended to solve the URL-Shortener problem commonly used in developer interviews, and should not
be used in a production environment due to its limitations on security and in the generator algorithm.

## Functional assumptions

* For simplicity no database is used, all data stored in-memory dictionaries, if app is restarted all stored data would
  be lost.
* Shortened URLs using a length of 6 chars should be enough for testing purpose. 
* Authentication Tokens expire in 30 minutes.
* Clients should send request from forms.
* Authentication token is a header field in HTTP request, labeled `jwt_token`.

### Random string generator algorithm

The process follows the idea to be as simple as possible, in both, random generation and collision avoidance. Since the
expected amount of URLs to be shortened are just a few, intended for testing purpose only, it does not follow any best
approach or performance rules used in real production environments.

### Requirements

* Python3
* curl (for command line testing)

## Installation

```shell
python -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

## Execution

```shell
export FLASK_APP=main
flask run
```

### Create users

```shell
curl --request POST \
  --url http://127.0.0.1:5000/register \
  --header 'Content-Type: multipart/form-data' \
  --form email=yes@hello.com \
  --form password=123
```

Expected result should be:

```json
{
  "message": "User yes@hello.com created successfully",
  "status": "success"
}
```

### Authenticate users

```shell
curl --request POST \
  --url http://127.0.0.1:5000/authenticate \
  --header 'Content-Type: multipart/form-data' \
  --form email=yes@hello.com \
  --form password=123
```

Expected result should contain the JWT token:

```json
{
  "status": "success",
  "jwt_token": "eyJ0eXAiOiJKV1QiLCJhbGc....21_DJyJLZhmEMw2OyjZZ26g67V1bzHA"
}
```

### Shortening URLs

```shell
curl --request POST \
  --url http://127.0.0.1:5000/create \
  --header 'Content-Type: multipart/form-data' \
  --header 'jwt_token: eyJ0eXAiOiJKV1QiLCJhbGc....21_DJyJLZhmEMw2OyjZZ26g67V1bzHA' \
  --form url=https://shortcut.io/about/
```

Result should be like this:

```json
{
  "short_version": "nonXuN",
  "status": "success"
}
```

### Decoding URLs

Open in browser `127.0.0.1:5000/<short_url>`, redirection should be done to original URL and there is no need to pass the `jwt_token`, since anyone should be able to decode a URL

From previous example: Open in browser `127.0.0.1:5000/nonXuN`, this should redirect to `https://shortcut.io/about/`

### Running tests

```shell
source venv/bin/activate  # Only if venv is not active yet
python3 -m pytest --verbose test_main.py
```