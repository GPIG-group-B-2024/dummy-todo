import pytest
from todo.db import get_db

def test_index(client, auth):

    # Test accessing the index page after login
    auth.login()
    response = client.get('/')
    assert b'To-Do List' in response.data

def test_create(client, auth):
    # Test creating a task
    auth.login()
    response = client.post(
        '/create',
        data={'title': 'Test Task', 'description': 'This is a test task'}
    )
    assert response.headers['Location'] == '/'

    with client.application.app_context():
        db = get_db()
        task = db.execute(
            "SELECT * FROM task WHERE title = 'Test Task'"
        ).fetchone()
        assert task is not None

def test_update(client, auth):
    # Test updating a task
    auth.login()
    client.post(
        '/create',
        data={'title': 'Test Task', 'description': 'This is a test task'}
    )

    response = client.post(
        '/1/update',
        data={'title': 'Updated Task', 'description': 'Updated description', 'completed': 'on'}
    )
    assert response.headers['Location'] == '/'

    with client.application.app_context():
        db = get_db()
        task = db.execute(
            "SELECT * FROM task WHERE id = 1"
        ).fetchone()
        assert task['title'] == 'Updated Task'
        assert task['completed'] == 1

def test_delete(client, auth):
    # Test deleting a task
    auth.login()
    client.post(
        '/create',
        data={'title': 'Test Task', 'description': 'This is a test task'}
    )

    response = client.post('/1/delete')
    assert response.headers['Location'] == '/'

    with client.application.app_context():
        db = get_db()
        task = db.execute(
            "SELECT * FROM task WHERE id = 1"
        ).fetchone()
        assert task is None