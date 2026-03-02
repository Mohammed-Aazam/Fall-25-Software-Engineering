import pytest
import requests

from moj import app, db
from moj.models import User, Joke


def test_submit_joke_persists_ai_fields(monkeypatch):
    """Mocks the AI service, posts a joke, and asserts persisted AI fields."""

    class MockResp:
        status_code = 200

        def json(self):
            return {"rating": "Dad Joke", "score": 2}

    def fake_post(url, json=None, timeout=None):
        return MockResp()

    # Patch requests.post used by the application
    monkeypatch.setattr(requests, "post", fake_post)

    # Use an in-memory DB and disable CSRF for testing
    app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "AI_SERVICE_URL": "http://ai-service",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })

    with app.app_context():
        # Create schema
        db.create_all()

        # Create a user and log in
        user = User(username="tester", email="tester@example.com")
        user.set_password("secret")
        db.session.add(user)
        db.session.commit()

        client = app.test_client()

        # Login via the app's login route so session/cookies are correct
        rv = client.post("/login", data={"username": "tester", "password": "secret"}, follow_redirects=True)
        assert rv.status_code == 200

        # Submit a joke (this triggers the mocked AI call)
        rv = client.post("/submit_joke", data={"body": "This is a test joke"}, follow_redirects=True)
        assert rv.status_code == 200

        # Verify the joke is persisted with AI fields
        joke = Joke.query.filter_by(body="This is a test joke").first()
        assert joke is not None
        assert joke.ai_rating == "Dad Joke"
        assert joke.ai_score == 2

        # Cleanup
        db.session.remove()
        db.drop_all()
