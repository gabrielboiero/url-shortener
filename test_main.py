import random
import string
import time

import pytest
import main
from assertpy import assert_that


@pytest.fixture()
def app():
    main.app.config.update({
        'TESTING': True,
        'TOKEN_EXPIRATION_TIME': 5
    })
    yield main.app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def registered_random_user(client):
    random_username = ''.join(random.choices(string.ascii_lowercase, k=12))
    email = f'{random_username}@email.com'
    response = client.post('/register', data={
        'email': email,
        'password': 'abc123xyz'
    })
    assert_that(response.status_code).is_equal_to(200)
    return email


@pytest.fixture()
def authenticated_user_token(registered_random_user, client):
    response = client.post('/authenticate', data={
        'email': registered_random_user,
        'password': 'abc123xyz'
    })
    assert_that(response.status_code).is_equal_to(200)
    return response.json['jwt_token']


def test_register_user(client):
    response = client.post('/register', data={
        'email': 'test@email.com',
        'password': 'abc123xyz'
    })
    assert_that(response.status_code).is_equal_to(200)


def test_authenticate_user(client):
    response = client.post('/authenticate', data={
        'email': 'test@email.com',
        'password': 'abc123xyz'
    })
    assert_that(response.status_code).is_equal_to(200)
    assert_that(response.json).contains_entry({'status': 'success'})
    assert_that(response.json).contains_key('jwt_token')


def test_authenticate_invalid_user(client):
    response = client.post('/authenticate', data={
        'email': 'other@email.com',
        'password': 'qwertyui'
    })
    assert_that(response.status_code).is_equal_to(404)
    assert_that(response.json).contains_entry({'status': 'error'})
    assert_that(response.json).contains_entry({'message': 'Invalid email or password'})


def test_create_short_url(authenticated_user_token, client):
    response = client.post('/create', data={'url': 'https://shortcut.io/about/'},
                           headers={'jwt_token': authenticated_user_token})
    assert_that(response.status_code).is_equal_to(200)
    assert_that(response.json).contains_key('short_version')


def test_expired_token(authenticated_user_token, client):
    time.sleep(6)  # Ensure that token has expired from 5s override in config fixture
    response = client.post('/create', data={'url': 'https://shortcut.io/about/'},
                           headers={'jwt_token': authenticated_user_token})
    assert_that(response.status_code).is_equal_to(404)
    assert_that(response.json).contains_entry({'status': 'error'})
    assert_that(response.text).contains('expired')


def test_create_and_redirect(authenticated_user_token, client):
    response = client.post('/create', data={'url': 'https://shortcut.io/about/'},
                           headers={'jwt_token': authenticated_user_token})
    assert_that(response.status_code).is_equal_to(200)
    short_url = response.json['short_version']
    response = client.get(f'/{short_url}')
    assert_that(response.status_code).is_equal_to(302)


def test_retrieve_url(authenticated_user_token, client):
    response = client.post('/create', data={'url': 'https://shortcut.io/about/'},
                           headers={'jwt_token': authenticated_user_token})
    assert_that(response.status_code).is_equal_to(200)
    short_url = response.json['short_version']
    response = client.get(f'/retrieve/{short_url}',
                          headers={'jwt_token': authenticated_user_token})
    assert_that(response.status_code).is_equal_to(201)
    assert_that(response.json).contains_entry({'url': 'https://shortcut.io/about/'})
