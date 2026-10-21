from flask import Flask, flash, redirect, url_for
from flask import request, jsonify
import requests, json
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
from flask_mail import Mail
import os
from dotenv import load_dotenv
load_dotenv()  # Local .env only; cloud values come from application settings

app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY')
if not app.secret_key or len(app.secret_key) < 32:
    raise RuntimeError('Set SECRET_KEY to a random value of at least 32 characters.')
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=os.getenv('COOKIE_SECURE', 'false').lower() == 'true',
    MAX_CONTENT_LENGTH=5 * 1024 * 1024,
)


database_url = os.getenv('DATABASE_URL', 'sqlite:///shop.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql+psycopg://', 1)
elif database_url.startswith('postgresql://'):
    database_url = database_url.replace('postgresql://', 'postgresql+psycopg://', 1)
if os.getenv('APP_ENV') == 'production' and not database_url.startswith('postgresql+psycopg://'):
    raise RuntimeError('Cloud deployments require a PostgreSQL DATABASE_URL.')
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping': True}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER']= os.getenv('MAIL_USERNAME')


db= SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
mail = Mail(app)


def admin_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Access Denied: You are not authorized to access admin page.')
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return decorated_function


from shop.user import routes
from shop.products import routes
from shop.admin import routes



      
        


    
from shop import cloud_commands
