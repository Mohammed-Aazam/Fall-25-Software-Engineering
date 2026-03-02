import click
from moj import app, db
from moj.models import User

@app.cli.command("init-admin")
@click.argument("username")
def init_admin(username):
    """Grants admin privileges to a user."""
    user = User.query.filter_by(username=username).first()
    if not user:
        print(f"Error: User '{username}' not found.")
        return

    user.role = 'admin'
    db.session.commit()
    print(f"Success! User '{username}' is now an admin.")
