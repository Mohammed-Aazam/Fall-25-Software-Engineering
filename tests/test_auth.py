from moj.models import User, UserAction
from moj import db


def test_register_new_user(client):
    """
    GIVEN a client and a new user's details
    WHEN the '/register' route is posted to (POST)
    THEN check that the user is created in the database and they are
            redirected to the login page.
    """
    # 1. Post the form data to the register route
    response = client.post('/register', data={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'password123',
        'password2': 'password123'
    }, follow_redirects=True)  # <-- 'follow_redirects' is key!

    # 2. Check the response
    assert response.status_code == 200
    # Check that we were redirected to the login page
    assert b'Sign In' in response.data
    assert b'Congratulations' in response.data  # Check for flash message

    # 3. Check the database
    user = User.query.filter_by(username='newuser').first()
    assert user is not None
    assert user.email == 'new@example.com'
    assert user.check_password('password123')
    assert not user.check_password('wrongpassword')


def test_login_and_logout_user(client, app):
    """
    GCIVEN a client and a test user
    WHEN the '/login' and '/logout' routes are used
    THEN check that the user session is managed correctly.
    """
    # --- Create a test user in the database ---
    # We need a user to log in *with*
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpassword')
        db.session.add(user)
        db.session.commit()

    # --- Test Login ---
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpassword'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Home' in response.data  # Redirected to index
    assert b'Sign In' not in response.data  # Login link is gone
    assert b'Logout' in response.data  # Logout link appears

    # --- Test Logout ---
    response = client.get('/logout', follow_redirects=True)

    assert response.status_code == 200
    assert b'Sign In' in response.data  # Redirected to login
    assert b'Logout' not in response.data  # Logout link is gone


def test_login_creates_log_entry(client, app):
    """
    GIVEN a valid user in the DB
    WHEN the client POSTs to /login with correct credentials
    THEN a UserAction row is created with action_type UserAction.LOGIN linked to that user
    """
    with app.app_context():
        user = User(username='loguser', email='log@example.com')
        user.set_password('secret')
        db.session.add(user)
        db.session.commit()
        uid = user.id

    response = client.post('/login', data={
        'username': 'loguser',
        'password': 'secret'
    }, follow_redirects=True)

    assert response.status_code == 200

    with app.app_context():
        action = UserAction.query.filter_by(user_id=uid, action_type=UserAction.LOGIN).first()
        assert action is not None
        assert action.action_type == UserAction.LOGIN
        assert action.user_id == uid
