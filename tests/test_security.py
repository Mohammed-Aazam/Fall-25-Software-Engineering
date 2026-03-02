from moj import db
from moj.models import User, Joke
import pytest

# Helper fixture to log in a user
@pytest.fixture
def logged_in_user(client, app):
    with app.app_context():
        user = User(username='test', email='test@test.com')
        user.set_password('a')
        db.session.add(user)
        db.session.commit()

    client.post('/login', data={'username': 'test', 'password': 'a'})
    return user

def test_xss_attack_is_escaped(client, app, logged_in_user):
    """
    GIVEN a logged-in user
    WHEN they post a joke with a <script> tag
    THEN the tag is 'escaped' as text and not rendered as HTML
    """
    # WHEN: They post a joke with a <script> tag
    # (Update '/create_joke' if your route is named differently)
    client.post('/submit_joke', data={
        'body': 'A joke with <script>alert(1)</script> tag'
    }, follow_redirects=True)

    # AND they view the index page
    response = client.get('/index')

    # THEN: The <script> tag is *escaped*, not rendered
    assert response.status_code == 200

    # The literal < > characters are GONE
    assert b'<script>alert(1)</script>' not in response.data

    # They have been REPLACED with HTML-safe codes
    assert b'&lt;script&gt;alert(1)&lt;/script&gt;' in response.data
    print("XSS test passed: <script> was successfully escaped.")
