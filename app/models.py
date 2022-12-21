from app import db
from flask_login import UserMixin
from datetime import datetime


class User(UserMixin, db.Model):
    # Table for user accounts & profiles
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), unique=True, nullable=False)
    # SHA-512 hash represented as 128 hex chars
    password = db.Column(db.String(32), nullable=False)
    # Salt to prevent rainbow table attacks represented as 16 hex chars
    salt = db.Column(db.String(16), nullable=False)
    display_name = db.Column(db.String(16), nullable=False)
    theme = db.Column(db.String(16))
    active = db.Column(db.Boolean, nullable=False, default=True)
    posts = db.relationship("Post", backref="user", lazy="dynamic")
    friends = db.relationship(  # friendship many-to-many relationship betwen users
        "User",
        secondary="friendship",
        primaryjoin="User.id == Friendship.user1_id",
        secondaryjoin="User.id == Friendship.user2_id",
        lazy="dynamic"
    )

    def is_active(self):
        return self.active

    # Method for checking password correct
    def check_password(self, password):
        return self.password == password


# Association table for friendship many-to-many relationship
class Friendship(db.Model):
    # Table for user friendships
    user1_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    user2_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)


class Post(db.Model):
    # Table for user posts
    id = db.Column(db.Integer, primary_key=True)
    poster_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    time_posted = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    body = db.Column(db.String(1024), nullable=False)