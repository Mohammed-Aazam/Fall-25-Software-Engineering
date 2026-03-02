from moj.models import User, Joke, UserAction
from moj import db


def test_hello_world(client):
    """
    GIVEN a configured test client (from conftest.py)
    WHEN the '/' route is requested (GET)
    THEN check that the response is a 302 (redirect)
    """
    # The index route is now protected by @login_required
    # An unauthenticated client should be redirected.
    response = client.get('/')
    assert response.status_code == 302
    assert 'login' in response.location  # Check that it redirects to login


def test_edit_joke(client, app):
    """
    GIVEN a user and a joke
    WHEN the user edits their joke via POST to /edit_joke/<id>
    THEN the joke body in the database should be updated
    """
    with app.app_context():
        user = User(username='editor', email='editor@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()

        joke = Joke(body='Original joke', author=user)
        db.session.add(joke)
        db.session.commit()
        joke_id = joke.id

    # Log in
    response = client.post('/login', data={'username': 'editor', 'password': 'password'}, follow_redirects=True)
    assert response.status_code == 200

    # Post update
    response = client.post(f'/edit_joke/{joke_id}', data={'body': 'Updated joke'}, follow_redirects=True)
    assert response.status_code == 200

    # Verify DB changed
    with app.app_context():
        j = Joke.query.get(joke_id)
        assert j.body == 'Updated joke'


def test_cannot_edit_others_joke(client, app):
    """
    GIVEN two users where user_a authored a joke
    WHEN user_b attempts to edit user_a's joke
    THEN the response should be 403 and the joke should remain unchanged
    """
    with app.app_context():
        user_a = User(username='user_a', email='a@example.com')
        user_a.set_password('passworda')
        user_b = User(username='user_b', email='b@example.com')
        user_b.set_password('passwordb')
        db.session.add_all([user_a, user_b])
        db.session.commit()

        joke = Joke(body='A joke', author=user_a)
        db.session.add(joke)
        db.session.commit()
        joke_id = joke.id

    # Log in as user_b
    response = client.post('/login', data={'username': 'user_b', 'password': 'passwordb'}, follow_redirects=True)
    assert response.status_code == 200

    # Attempt to edit user_a's joke
    response = client.post(f'/edit_joke/{joke_id}', data={'body': 'Hacked!'}, follow_redirects=False)
    assert response.status_code == 403

    # Verify joke unchanged
    with app.app_context():
        j = Joke.query.get(joke_id)
        assert j.body == 'A joke'


def test_delete_joke(client, app):
    """
    GIVEN a user and a joke
    WHEN the user deletes their joke via POST to /delete_joke/<id>
    THEN the joke should be removed from the database
    """
    with app.app_context():
        user = User(username='deleter', email='deleter@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()

        joke = Joke(body='To be deleted', author=user)
        db.session.add(joke)
        db.session.commit()
        joke_id = joke.id

    # Log in
    response = client.post('/login', data={'username': 'deleter', 'password': 'password'}, follow_redirects=True)
    assert response.status_code == 200

    # Delete via POST
    response = client.post(f'/delete_joke/{joke_id}', follow_redirects=True)
    assert response.status_code == 200

    # Verify DB no longer contains the joke
    with app.app_context():
        j = Joke.query.get(joke_id)
        assert j is None


def test_cannot_delete_others_joke(client, app):
    """
    GIVEN two users where user_a authored a joke
    WHEN user_b attempts to delete user_a's joke
    THEN the response should be 403 and the joke should remain
    """
    with app.app_context():
        user_a = User(username='delete_a', email='a_del@example.com')
        user_a.set_password('passworda')
        user_b = User(username='delete_b', email='b_del@example.com')
        user_b.set_password('passwordb')
        db.session.add_all([user_a, user_b])
        db.session.commit()

        joke = Joke(body='Not your joke', author=user_a)
        db.session.add(joke)
        db.session.commit()
        joke_id = joke.id

    # Log in as user_b
    response = client.post('/login', data={'username': 'delete_b', 'password': 'passwordb'}, follow_redirects=True)
    assert response.status_code == 200

    # Attempt to delete user_a's joke
    response = client.post(f'/delete_joke/{joke_id}', follow_redirects=False)
    assert response.status_code == 403

    # Verify joke still exists
    with app.app_context():
        j = Joke.query.get(joke_id)
        assert j is not None


def test_my_activity_page(client, app):
    """
    GIVEN a logged-in user with two actions and another user with one action
    WHEN the logged-in user GETs /my_activity
    THEN the response is 200 and shows only the two actions for the logged-in user
    """
    with app.app_context():
        user1 = User(username='active', email='a@a.com')
        user1.set_password('p')
        user2 = User(username='other', email='o@o.com')
        user2.set_password('p')
        db.session.add_all([user1, user2])
        db.session.commit()

        a1 = UserAction(user_id=user1.id, action_type=UserAction.LOGIN, details='first')
        a2 = UserAction(user_id=user1.id, action_type=UserAction.LOGIN, details='second')
        a3 = UserAction(user_id=user2.id, action_type=UserAction.LOGIN, details='other')
        db.session.add_all([a1, a2, a3])
        db.session.commit()

    # Log in as user1
    response = client.post('/login', data={'username': 'active', 'password': 'p'}, follow_redirects=True)
    assert response.status_code == 200

    # GET the my_activity page
    response = client.get('/my_activity')
    assert response.status_code == 200

    # Should contain the two details for user1 and not the other user's detail
    assert b'first' in response.data
    assert b'second' in response.data
    assert b'other' not in response.data
