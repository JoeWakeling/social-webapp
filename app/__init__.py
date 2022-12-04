from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Create Flask instance
app = Flask(__name__)
# Load app config file
app.config.from_object('config')

# Create app database object instance
db = SQLAlchemy(app)

# Create Migrate instance
migrate = Migrate(app, db)

# Import views module for dynamic content & models module for database
from app import views, models