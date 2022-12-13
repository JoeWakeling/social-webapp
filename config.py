import os

# Enable file uploading with max 1MB file due to pythonanywhere 512MB quota
ALLOWED_EXTENSIONS = {"png, jpg, jpeg, gif"}
MAX_CONTENT_LENGTH = 1024 * 1024

# Enable CSRF protection
WTF_CSRF_ENABLED = True
SECRET_KEY = '0zickgICiLIgQlgBlemFSY9sll8HOd3e'

# SQLite config
basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = True
