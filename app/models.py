from app import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    # Table for user information
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)

    @property
    def is_active(self):
        return self.active

    # Method for checking password correct
    def check_password(self, password):
        return self.password == password