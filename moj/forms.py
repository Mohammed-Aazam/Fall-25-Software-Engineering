# In moj/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from moj.models import User
from wtforms import TextAreaField
from wtforms.validators import Length
import re


class LoginForm(FlaskForm):
    """Form for user login."""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    """Form for new user registration."""
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    # Custom validator
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    # Custom validator
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')
        


class JokeForm(FlaskForm):
    """Form for submitting a new joke."""
    body = TextAreaField('Joke Body', validators=[
        DataRequired(), Length(min=1, max=280)])
    submit = SubmitField('Submit Joke')
    
class ChangePasswordForm(FlaskForm):
    """Form for changing password."""
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    new_password2 = PasswordField(
        'Repeat New Password', validators=[DataRequired(), EqualTo('new_password')]
    )
    submit = SubmitField('Change Password')

    #Custom password complexity validator
    def validate_new_password(self, new_password):
        password = new_password.data

        if len(password) < 15:
            raise ValidationError('Password must be at least 15 characters long.')

        if not re.search(r'\d', password):
            raise ValidationError('Password must contain at least one digit (0-9).')

        if not re.search(r'[A-Z]', password):
            raise ValidationError('Password must contain at least one uppercase letter (A-Z).')

        if not re.search(r'[a-z]', password):
            raise ValidationError('Password must contain at least one lowercase letter (a-z).')

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError('Password must contain at least one special character (e.g., !@#$%^&*).')
        
class AdminJokeForm(JokeForm):
    """
    Extends the base JokeForm with a mandatory
    justification field for admin actions.
    """
    justification = TextAreaField(
        'Admin Justification',
        validators=[DataRequired(), Length(min=5, max=256)]
    )


class AdminDeleteJokeForm(FlaskForm):
    """
    Form for deleting a joke, requiring only an admin justification.
    """
    justification = TextAreaField(
        'Admin Justification for Deletion',
        validators=[DataRequired(), Length(min=5, max=256)]
    )
    submit = SubmitField('Delete Joke')
    

class AdminUserForm(FlaskForm):
    """Form for admin to edit user roles from regular user to admin and vice versa with mandatory justification."""
    role = SelectField('User Role',
                       choices=[('user', 'User'), ('admin', 'Admin')],
                       validators=[DataRequired()])
    justification = TextAreaField(
        'Admin Justification',
        validators=[DataRequired(), Length(min=5, max=256)]
    )
    submit = SubmitField('Update User Role')


class RatingForm(FlaskForm):
    # We use 'coerce=int' to make sure the data comes back as a number
    score = SelectField('Rating (1-5)',
                        choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'),
                                 (4, '4 Stars'), (5, '5 Stars')],
                        coerce=int)
    submit = SubmitField('Submit Rating')
