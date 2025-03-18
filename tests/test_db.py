import sqlite3
import pytest
from todo.db import get_db

def test_get_db(app):
    # Test getting the database connection
    with app.app_context():
        db = get_db()
        assert db is get_db()

    # Test database operations after the context
    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')

    assert 'closed' in str(e.value)

def test_init_db_command(runner, monkeypatch):
    # Test the init-db CLI command
    class Recorder:
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr('todo.db.init_db', fake_init_db)
    result = runner.invoke(args=['init-db'])
    assert 'Initialized the database.' in result.output
    assert Recorder.called