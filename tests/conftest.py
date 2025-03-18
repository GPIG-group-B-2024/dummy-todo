import os
import tempfile
from werkzeug.security import generate_password_hash

import pytest
from todo import create_app
from todo.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')

@pytest.fixture
def app():
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp()

    # Create the app with test configuration
    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })

    # Initialize the database
    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)
        
    yield app

    # Clean up after the test
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def auth(client):
    return AuthActions(client)

class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')