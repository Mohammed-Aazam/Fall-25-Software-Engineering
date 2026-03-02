import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()

class Config:
    """Set Flask configuration variables."""

    # CRITICAL: Flask-WTF (forms) requires a SECRET_KEY
    # This key is used to prevent CSRF attacks.
    # Load the secret key from the .env file.
    # The app will crash if this is not set, which is good.

    
    AI_SERVICE_URL = os.environ.get('AI_SERVICE_URL')
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # Database configuration
  
    # Read from .env, but use the old path as a fallback
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, 'moj.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False
