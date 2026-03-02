import os
import sys
import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Ensure the app uses an in-memory database for tests by setting the env var
os.environ.setdefault('DATABASE_URL', 'sqlite:///:memory:')

from moj import app as flask_app
from moj import db


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",  # Use in-memory db
        "WTF_CSRF_ENABLED": False,  # Disable CSRF for testing forms
    })

    # --- Setup database ---
    with flask_app.app_context():
        db.create_all()  # Create all tables
        yield flask_app  # Run the test
        db.session.remove()  # Clean up
        db.drop_all()  # Drop all tables


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()
