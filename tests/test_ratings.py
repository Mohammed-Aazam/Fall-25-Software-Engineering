from moj import db, app
from moj.models import User, Joke, Rating
import pytest

# Helper function to create users & jokes
@pytest.fixture
def setup_db(app):
    with app.app_context():
        user_a = User(username='user_a', email='a@a.com')
        user_a.set_password('a')
        user_b = User(username='user_b', email='b@b.com')
        user_b.set_password('b')
        joke_a = Joke(body="Joke from A", author=user_a)
        db.session.add_all([user_a, user_b, joke_a])
        db.session.commit()
        yield user_a, user_b, joke_a

def test_average_rating_model(app, setup_db):
    """
    GIVEN a Joke and two Ratings
    WHEN the joke.average_rating() method is called
    THEN the correct average is returned
    """
    user_a, user_b, joke_a = setup_db
    with app.app_context():
        # Add two ratings
        r1 = Rating(score=5, user_id=user_a.id, joke_id=joke_a.id)
        r2 = Rating(score=3, user_id=user_b.id, joke_id=joke_a.id)
        db.session.add_all([r1, r2])
        db.session.commit()

        # Check the average
        assert joke_a.average_rating() == 4.0

def test_rate_joke_happy_path(client, setup_db):
    """
    GIVEN user_B (logged in) and joke_A (by user_A)
    WHEN user_B POSTs a rating
    THEN a new Rating is created in the database
    """
    user_a, user_b, joke_a = setup_db

    # Log in as user_B
    client.post('/login', data={'username': 'user_b', 'password': 'b'})

    # Post the rating
    response = client.post(f'/rate_joke/{joke_a.id}', data={
        'score': 5
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Your rating has been submitted!" in response.data

    # Check the DB
    rating = Rating.query.first()
    assert rating is not None
    assert rating.score == 5
    assert rating.user_id == user_b.id

def test_cant_rate_own_joke(client, setup_db):
    """
    GIVEN user_A (logged in) and joke_A (by user_A)
    WHEN user_A tries to POST a rating
    THEN no Rating is created and a flash message is shown
    """
    user_a, user_b, joke_a = setup_db

    # Log in as user_A
    client.post('/login', data={'username': 'user_a', 'password': 'a'})

    response = client.post(f'/rate_joke/{joke_a.id}', data={
        'score': 5
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"You cannot rate your own joke." in response.data

    # Check DB
    rating = Rating.query.first()
    assert rating is None

def test_cant_rate_twice(client, setup_db):
    """
    GIVEN user_B has already rated joke_A
    WHEN user_B tries to POST a rating again
    THEN no new Rating is created
    """
    user_a, user_b, joke_a = setup_db
    with app.app_context():
        # Add the first rating
        r1 = Rating(score=5, user_id=user_b.id, joke_id=joke_a.id)
        db.session.add(r1)
        db.session.commit()

    # Log in as user_B
    client.post('/login', data={'username': 'user_b', 'password': 'b'})

    # Try to post again
    response = client.post(f'/rate_joke/{joke_a.id}', data={
        'score': 1
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"You have already rated this joke." in response.data

    # Check DB
    assert Rating.query.count() == 1
