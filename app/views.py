from app import app, db, models
from flask import render_template, request, redirect
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import desc


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
@app.route("/auth-check")
def auth_check():
    # Check if user's id in session
    if current_user.is_authenticated:
        # User logged in, return true
        return "Logged in"
    else:
        # User not logged in, return false
        return "Not logged in"


# Route to handle adding a friend
@login_required
@app.route("/add-friend/<new_friend_username>", methods=["GET", "POST"])
def add_friend(new_friend_username):
    # Get user object of new friend
    new_friend = models.User.query.filter_by(username=new_friend_username).first()
    if new_friend is None:
        # Invalid new friend username
        return "User to add as friend not found"
    else:
        # User found, add friendship to database
        current_user.friends.append(new_friend)
        db.session.commit()
        return redirect("/", code=302)


# Route to handle user posting
@app.route("/add", methods=["GET", "POST"])
def post():
    if current_user.is_authenticated:
        # Get user's post text (body) from form
        body = request.form.get("post-body")
        # Create new post object from models
        new_post = models.Post(poster_id=current_user.id, body=body)
        # Add and Commit post object to database
        db.session.add(new_post)
        db.session.commit()
        # New post saved to db, redirect to home
        return redirect("/", code=302)
    else:
        # User not logged in, can't post
        return redirect("/", code=302)


# Route to display homepage with user's timeline
@app.route("/")
def index():
    # Get username for nav profile card
    username = current_user.username
    # Get friends of user
    # Get list of friend's ids
    friend_ids = [x.id for x in current_user.friends.all()]
    # Get all posts by user's friend to display timeline
    posts = models.Post.query\
        .with_entities(models.User.username, models.Post.time_posted, models.Post.body) \
        .filter(models.Post.poster_id.in_(friend_ids))\
        .join(models.User, models.Post.poster_id == models.User.id)\
        .order_by(desc(models.Post.time_posted))
    return render_template("posts.html",
                           title="Home",
                           username=username,
                           posts=posts)


# Route to display explore page with all posts
@app.route("/explore")
def explore():
    # Get username for nav profile card
    username = current_user.username
    # Get all posts to display on homescreen
    posts = models.Post.query\
        .with_entities(models.User.username, models.Post.time_posted, models.Post.body)\
        .join(models.User, models.Post.poster_id == models.User.id)\
        .order_by(desc(models.Post.time_posted))
    return render_template("posts.html",
                           title="Explore",
                           username=username,
                           posts=posts)


# Route to display list of user's friends
@app.route("/friends")
@login_required
def friends():
    # Get username for nav profile card
    username = current_user.username
    # Get friends of user
    all_friends = current_user.friends.all()
    return render_template("friends.html",
                           title="Friends",
                           username=username,
                           friends=all_friends)


# Route to display user's profile
@app.route("/profile/<profile_owner_username>")
@login_required
def profile(profile_owner_username):
    # Get username for nav profile card
    username = current_user.username
    # Get user object of profile owner
    profile_owner = models.User.query.filter_by(username=profile_owner_username).first()
    if profile_owner is None:
        # Invalid username in url
        return "User not found"
    else:
        # Username in url found, get profile owner's posts
        posts = models.Post.query\
            .with_entities(models.Post.poster_id, models.User.username, models.Post.time_posted, models.Post.body)\
            .filter_by(poster_id=profile_owner.id)\
            .join(models.User, models.Post.poster_id == models.User.id)\
            .order_by(desc(models.Post.time_posted))
        # Render profile page
        return render_template("profile.html",
                               title="Profile",
                               username=username,
                               profile_owner=profile_owner,
                               posts=posts)

