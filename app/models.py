from app import db


class User(db.Model):
    # Table for user information
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    # Define user object's string representation as its username
    def __repr__(self):
        return '<User %r>' % self.username

    # Method for checking password correct
    def check_password(self, password):
        return self.password == password
