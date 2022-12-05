from app import app, db, models
from flask import render_template, request, redirect
from flask_login import login_user, logout_user, login_required, current_user


# Route to handle user login
@app.route("/login", methods=["GET", "POST"])
def login():
    # Get user's inputted username and password from the request
    username = request.form.get("username")
    password = request.form.get("password")
    # Query db w/ username
    user = models.User.query.filter_by(username=username).first()
    if user is not None and user.check_password(password):
        login_user(user)
        # Login successful, redirect to home
        return redirect("/", code=302)
    else:
        # Login failed, return false
        return "Login failed"


# Route to handle user logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    # Logout successful, redirect to home
    return redirect("/", code=302)


# Route to handle user signup
@app.route("/signup", methods=["GET", "POST"])
def signup():
    # Get user's inputted username and password from the request
    username = request.form["username"]
    password = request.form["password"]
    # Query db to check if username taken
    user = models.User.query.filter_by(username=username).first()
    if user is None:
        # Username not taken, create new user
        new_user = models.User(username=username, password=password)
        # Add and Commit new user to database
        db.session.add(new_user)
        db.session.commit()
        # Signup successful, return true
        return redirect("/", code=302)
    else:
        # Signup failed, return false
        return "Signup failed"


# Route to check login state
@app.route("/auth_check")
def auth_check():
    # Check if user's id in session
    if current_user.is_authenticated:
        # User logged in, return true
        return "Logged in"
    else:
        # User not logged in, return false
        return "Not logged in"


# Route to display homepage
@app.route("/")
def index():
    return render_template("home.html", title="home")
