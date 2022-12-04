import os

# Enable CSRF protection
WTF_CSRF_ENABLED = True
SECRET_KEY = '0zickgICiLIgQlgBlemFSY9sll8HOd3e'

# SQLite config
basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = True