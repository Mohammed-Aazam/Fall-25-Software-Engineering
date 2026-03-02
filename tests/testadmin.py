from moj import db
from moj.models import User, Joke, UserAction


# Helper function to create users in the DB
def make_users():
    user = User(username='testuser', email='user@a.com', role='user')
    user.set_password('a')
    admin = User(username='admin', email='admin@a.com', role='admin')
    admin.set_password('a')
    return user, admin


def test_admin_can_access_panel(client, app):
    """GIVEN a logged-in Admin, WHEN they GET /admin_panel, THEN they see the panel."""
    with app.app_context():
        user, admin = make_users()
        db.session.add_all([user, admin])
        db.session.commit()

    client.post('/login', data={'username': 'admin', 'password': 'a'})
    response = client.get('/admin_panel')

    assert response.status_code == 200
    assert b'Admin Panel' in response.data


def test_user_cannot_access_panel(client, app):
    """GIVEN a logged-in User, WHEN they GET /admin_panel, THEN they get a 403."""
    with app.app_context():
        user, admin = make_users()
        db.session.add_all([user, admin])
        db.session.commit()

    client.post('/login', data={'username': 'testuser', 'password': 'a'})
    response = client.get('/admin_panel')

    assert response.status_code == 403


def test_admin_can_edit_joke_route(client, app):
    """GIVEN a logged-in Admin, WHEN they POST to /admin/edit_joke, THEN the joke is updated."""
    with app.app_context():
        user, admin = make_users()
        joke = Joke(body="Original joke", author=user)
        db.session.add_all([user, admin, joke])
        db.session.commit()
        joke_id = joke.id

    client.post('/login', data={'username': 'admin', 'password': 'a'})
    response = client.post(
        f'/admin/edit_joke/{joke_id}',
        data={
            'body': 'Edited by admin',
            'justification': 'Testing admin powers'
        },
        follow_redirects=True
    )

    # Validate response content
    assert b'Admin Audit Log' in response.data  
    assert response.status_code == 200
    assert b'Admin Panel' in response.data

    # Query DB safely inside app context
    with app.app_context():
        # Find the admin edit action specifically (there may also be a login action)
        log = UserAction.query.filter_by(action_type=UserAction.ADMIN_EDIT_JOKE, target_type='joke', target_id=joke_id).first()
        joke = Joke.query.get_or_404(joke_id)

    # Validate admin action log
    assert log is not None
    assert log.action_type == UserAction.ADMIN_EDIT_JOKE
    assert log.details == "Testing admin powers"
    assert joke.body == 'Edited by admin'


def test_user_cannot_use_admin_edit_route(client, app):
    """GIVEN a logged-in User, WHEN they POST to /admin/edit_joke, THEN they get a 403."""
    with app.app_context():
        user, admin = make_users()
        joke = Joke(body="Original joke", author=user)
        db.session.add_all([user, admin, joke])
        db.session.commit()
        joke_id = joke.id

    client.post('/login', data={'username': 'testuser', 'password': 'a'})
    response = client.post(
        f'/admin/edit_joke/{joke_id}',
        data={
            'body': 'Edited by user',
            'justification': 'Hacking'
        }
    )

    assert response.status_code == 403

    # Verify DB unchanged
    with app.app_context():
        joke = Joke.query.get_or_404(joke_id)

    assert joke.body == 'Original joke'
