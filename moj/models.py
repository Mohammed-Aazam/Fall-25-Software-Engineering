from sqlalchemy.sql import func
from moj import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import datetime


# This "user_loader" callback is used to reload the user object
# from the user ID stored in the session.
@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)

    # New columns from Lecture 5
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(10), index=True, default='user')

    jokes = db.relationship('Joke', backref='author', lazy='dynamic')

    # New methods from Lecture 5
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Joke(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(280), nullable=False)
    # AI analysis fields (nullable so existing rows remain valid)
    ai_rating = db.Column(db.String(30), nullable=True)
    ai_score = db.Column(db.Integer, nullable=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    ratings = db.relationship('Rating', backref='joke', lazy='dynamic')

    def average_rating(self):
        """Calculates the average rating for this joke."""
        avg = db.session.query(func.avg(Rating.score)) \
            .filter(Rating.joke_id == self.id) \
            .scalar() # .scalar() returns a single value (or None)

        return round(avg, 1) if avg else "Not rated"

    def __repr__(self):
        return '<Joke {}>'.format(self.body)
    
class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, index=True, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.datetime.now(datetime.timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    joke_id = db.Column(db.Integer, db.ForeignKey('joke.id'))

    def __repr__(self):
        return f'<Rating {self.score} for Joke {self.joke_id} by User {self.user_id}>'


class UserAction(db.Model):
    # --- ACTION TYPE CONSTANTS ---
    # This is our "code table" in Python.
    LOGIN = "User Login"
    CREATE_JOKE = "Create Joke"
    ADMIN_EDIT_JOKE = "Admin Edit Joke"
    ADMIN_EDIT_USER = "Admin Edit User"
    # --- End Constants ---

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')

    action_type = db.Column(db.String(50), index=True) 

    target_type = db.Column(db.String(50))
    target_id = db.Column(db.Integer)
    details = db.Column(db.String(256))

    def __repr__(self):
        return f'<UserAction {self.user.username} {self.action_type}>'
