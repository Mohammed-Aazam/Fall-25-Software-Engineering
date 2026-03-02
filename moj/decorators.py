from functools import wraps
from flask import abort
from flask_login import current_user
from moj.models import Joke

def admin_required(f):
    """
    A decorator to restrict access to admin users.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 1. Check if the current_user is not authenticated or not admin
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)

        # If the check passes, run the original route function
        return f(*args, **kwargs)

    return decorated_function

def author_required(f):
    """
    A decorator to restrict access to a joke's author.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        joke_id = kwargs.get('joke_id')

        # Fetch the joke (404 if not found)
        joke = Joke.query.get_or_404(joke_id)

        # Authorization check: must be the author
        if joke.author != current_user:
            abort(403)

        return f(*args, **kwargs)

    return decorated_function
