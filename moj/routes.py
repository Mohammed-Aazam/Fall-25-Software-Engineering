import requests
from moj import app
from flask import render_template, redirect, url_for, request, abort, flash, jsonify
# API endpoint to return all jokes as JSON
@app.route('/api/jokes', methods=['GET'])
def api_jokes():
    jokes = Joke.query.order_by(Joke.timestamp.desc()).all()

    jokes_list = []
    for joke in jokes:
        jokes_list.append({
            'id': joke.id,
            'body': joke.body,
            'timestamp': joke.timestamp.isoformat() if joke.timestamp else None,
            'author_username': joke.author.username,
            'ai_rating': joke.ai_rating
            # NOTE: Only expose data you want the public to see!
        })

    return jsonify({'jokes': jokes_list, 'count': len(jokes_list)})
from flask_login import login_user, logout_user, current_user, login_required
from moj.models import User, Joke, UserAction
from moj import db
from moj.forms import LoginForm, RegistrationForm, JokeForm, ChangePasswordForm, AdminJokeForm, AdminUserForm, AdminDeleteJokeForm
from moj.forms import RatingForm
from moj.models import Rating
from moj.decorators import admin_required, author_required



@app.route('/profile/<username>')  # <-- This is a dynamic route!
@login_required
def profile(username):
    """
    Shows a user's profile page, complete with their jokes.
    """
    # 1. Query for the user, or return a 404
    #    This is the "R" in CRUD for the User model.
    user = User.query.filter_by(username=username).first_or_404()

    # 2. Query for that user's jokes
    #    This is the "R" in CRUD for the Joke model, filtered!
    jokes = Joke.query.filter_by(author=user).order_by(Joke.timestamp.desc()).all()

    # 3. Pass the user and their jokes to the template
    return render_template('profile.html', user=user, jokes=jokes)


@app.route('/')
@app.route('/index')
@login_required
def index():
    """Renders the main index.html page with a feed of jokes."""
    # 1. Query the database
    jokes_list = Joke.query.order_by(Joke.timestamp.desc()).all()

    # 2. Pass the list to the template
    return render_template('index.html', title='Home', jokes=jokes_list)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm() # <-- Instantiate the form
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)

        # Log the login action for auditing
        try:
            new_action = UserAction(user=current_user, action_type=UserAction.LOGIN)
            db.session.add(new_action)
            db.session.commit()
        except Exception:
            # If logging fails, do not prevent login flow; fail silently
            db.session.rollback()

        return redirect(url_for('index'))

    return render_template('login.html', title='Sign In', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm() # <-- Instantiate the form
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form) # <-- Pass 'form'


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))  # Send them to login page


@app.route('/staff_lounge')
@login_required  # This is the AuthN (authentication) check
def staff_lounge():
    return "Welcome to the staff lounge, {}!".format(current_user.username)


@app.route('/admin_panel')
@login_required
@admin_required
def admin_panel():

    # Get data for the dashboard
    users = User.query.order_by(User.username).all()
    jokes = Joke.query.order_by(Joke.timestamp.desc()).all()

    # Include recent admin actions for audit purposes
    admin_types = [UserAction.ADMIN_EDIT_JOKE, UserAction.ADMIN_EDIT_USER]
    actions = UserAction.query.filter(UserAction.action_type.in_(admin_types)).order_by(UserAction.timestamp.desc()).all()

    return render_template('admin_panel.html', 
                            title="Admin Panel", 
                            users=users, 
                            jokes=jokes,
                            actions=actions)

@app.route('/submit_joke', methods=['GET', 'POST'])
@login_required
def submit_joke():
    form = JokeForm()
    if form.validate_on_submit():
        ai_url = app.config['AI_SERVICE_URL']
        try:
            response = requests.post(
                f"{ai_url}/rate_joke",
                json={'body': form.body.data},
                timeout=2 # Don't hang forever!
            )
            # Safe defaults
            ai_rating = None
            ai_score = None

            # Parse response when successful
            if response.status_code == 200:
                data = response.json() # e.g. {'rating': 'Dad Joke', 'score': 2}
                ai_rating = data.get('rating')
                ai_score = data.get('score')
                flash(f"AI Analysis: {ai_rating} (Score: {ai_score})", "info")
            else:
                flash("AI Service returned an unexpected response.", "warning")

        except requests.exceptions.RequestException:
            flash("AI Service invalid or down.", "warning")
        # Create the Joke object — include AI fields if available (nullable in DB)
        joke = Joke(
            body=form.body.data,
            author=current_user,
            ai_rating=ai_rating if 'ai_rating' in locals() else None,
            ai_score=ai_score if 'ai_score' in locals() else None
        )
        db.session.add(joke)
        db.session.commit()
        flash('Your joke has been submitted!')
        return redirect(url_for('index'))

    return render_template('submit_joke.html', title='Submit Joke', form=form)


@app.route('/my_activity')
@login_required
def my_activity():
    """Show the current user's activity log."""
    actions = UserAction.query.filter_by(
        user=current_user
    ).order_by(UserAction.timestamp.desc()).all()

    return render_template('my_activity.html', title='My Activity', actions=actions)


@app.route('/edit_joke/<int:joke_id>', methods=['GET', 'POST'])
@login_required
@author_required
def edit_joke(joke_id):
    # Find the joke or 404
    joke = Joke.query.get_or_404(joke_id)

    form = JokeForm()
    if form.validate_on_submit():
        # Update and commit
        joke.body = form.body.data
        db.session.commit()
        flash('Your joke has been updated!')
        return redirect(url_for('profile', username=current_user.username))

    # Pre-populate form on GET
    elif request.method == 'GET':
        form.body.data = joke.body

    return render_template('edit_joke.html', title='Edit Joke', form=form)

@app.route('/rate_joke/<int:joke_id>', methods=['GET', 'POST'])
@login_required
def rate_joke(joke_id):
    joke = Joke.query.get_or_404(joke_id)
    form = RatingForm()

    # --- RBAC / Business Logic Checks ---
    # 1. You can't rate your own joke
    if joke.author == current_user:
        flash("You cannot rate your own joke.", "error")
        return redirect(url_for('index'))

    # 2. You can only rate a joke once
    existing_rating = Rating.query.filter_by(user_id=current_user.id, 
                                             joke_id=joke.id).first()
    if existing_rating:
        flash("You have already rated this joke.", "info")
        return redirect(url_for('index'))
    # --- End Checks ---

    if form.validate_on_submit():
        new_rating = Rating(
            score=form.score.data,
            user_id=current_user.id,
            joke_id=joke.id
        )
        db.session.add(new_rating)
        db.session.commit()
        flash("Your rating has been submitted!", "success")
        return redirect(url_for('index'))

    return render_template('rate_joke.html', title='Rate Joke', 
                            form=form, joke=joke)

@app.route('/delete_joke/<int:joke_id>', methods=['POST'])
@login_required
@author_required
def delete_joke(joke_id):
    # Find the joke or 404
    joke = Joke.query.get_or_404(joke_id)

    db.session.delete(joke)
    db.session.commit()
    flash('Joke deleted.')
    return redirect(url_for('profile', username=current_user.username))

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        # Verify that old password is correct
        if not current_user.check_password(form.old_password.data):
            flash('Incorrect old password. Please try again.')
            return redirect(url_for('change_password'))

        # Set new password
        current_user.set_password(form.new_password.data)
        db.session.commit()

        flash('Your password has been changed successfully!')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        for field, errors in form.errors.items():
            for error in errors:
                flash(error, 'danger')

    return render_template('change_password.html', title='Change Password', form=form)


@app.route('/admin/edit_joke/<int:joke_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_joke(joke_id):

    joke = Joke.query.get_or_404(joke_id)
    form = AdminJokeForm() # <-- Use the new admin form
    delete_form = AdminDeleteJokeForm()

    if form.validate_on_submit():
        # 2. Perform the action
        joke.body = form.body.data
        db.session.commit()

        # 3. TODO (Lec 10): Log the action
        # We have the justification: form.justification.data
        justification = None
        try:
            justification = form.justification.data
        except Exception:
            justification = request.form.get('justification')

        # Record the admin action in the audit log
        ua = UserAction(user_id=current_user.id,
                        action_type=UserAction.ADMIN_EDIT_JOKE,
                        target_type='joke',
                        target_id=joke.id,
                        details=justification)
        db.session.add(ua)
        db.session.commit()

        flash('Admin edit successful.')
        return redirect(url_for('admin_panel'))

    elif request.method == 'GET':
        form.body.data = joke.body

    return render_template('admin_edit_joke.html', 
                            title='Admin Edit Joke', form=form, delete_form=delete_form, joke=joke)

@app.route('/admin/delete_joke/<int:joke_id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_joke(joke_id):

    joke = Joke.query.get_or_404(joke_id)
    form = AdminDeleteJokeForm() 

    if form.validate_on_submit():
        justification = form.justification.data
        
        #constraint to be added is double checking with a pop up modal.
        db.session.delete(joke)
        db.session.commit()

        flash(f'Joke ID {joke_id} has been permanently deleted. Justification: "{justification}"', 'success')
        return redirect(url_for('admin_panel'))
            
    return redirect(url_for('admin_edit_joke', joke_id=joke_id))



@app.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_user(user_id):
    
    if request.method == 'GET':
        user = User.query.get_or_404(user_id)
        form = AdminUserForm()
        form.role.data = user.role
        return render_template('admin_edit_user.html', 
                                title='Admin Edit User', form=form, user=user)
    
    elif request.method == 'POST':
        form = AdminUserForm()
        if form.validate_on_submit():
            # 2. Perform the action
            user = User.query.get_or_404(user_id)
            user.role = form.role.data
            db.session.commit()

            # Capture the admin justification (form may differ between tests/templates)
            justification = None
            try:
                justification = form.justification.data
            except Exception:
                justification = request.form.get('justification')

            # Record the admin action in the audit log
            ua = UserAction(user_id=current_user.id,
                            action_type=UserAction.ADMIN_EDIT_USER,
                            target_type='user',
                            target_id=user.id,
                            details=justification)
            db.session.add(ua)
            db.session.commit()

            flash('User role updated to {}.'.format(form.role.data))
            return redirect(url_for('admin_panel'))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(error, 'danger')
    
    form = AdminUserForm()
    user = User.query.get_or_404(user_id)
    return render_template('admin_edit_user.html', 
                            title='Admin Edit User', form=form, user=user)
