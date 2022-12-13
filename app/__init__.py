import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# Create Flask instance
app = Flask(__name__)
# Load app config file
app.config.from_object('config')

# Create app database object instance
db = SQLAlchemy(app)
# Create Migrate instance
migrate = Migrate(app, db, render_as_batch=True)

# Create login manager instance
login_manager = LoginManager()
# Configure login manager for flask app
login_manager.init_app(app)
# Redirect to explore if unauthenticated user tries accessing a route decorated by @login_required
login_manager.login_view = "/explore"
# Redirect to explore page when reauthentication needed
login_manager.refresh_view = "/explore"
# If hash of IP and useragent doesn't match hash of previous requests, delete session
login_manager.session_protection = "strong"

# Import views module for dynamic content & models module for database
from app import views, models


# Define how flask-login gets user object w/ user id in session
@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(int(user_id))