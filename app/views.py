import os
import hashlib
import secrets
from app import app, db, models
from flask import render_template, request, redirect, flash
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import desc


# Route to handle user signup
@app.route("/signup", methods=["GET", "POST"])
def signup():
    # Get user's inputted username, password and display name from the request
    username = request.form["username"]
    password = request.form["password"]
    display_name = request.form["display_name"]
    # Query db to check if username taken
    user = models.User.query.filter_by(username=username).first()
    if user is None:
        # Username not taken, generate a random 16 char hex salt
        salt = secrets.token_hex(8)
        # Salt & hash password
        h = hashlib.sha512()
        h.update(bytes.fromhex(salt))
        h.update(password.encode("utf-8"))
        hashed_password = h.hexdigest()
        # Create new user with username, hashed password and display name
        new_user = models.User(username=username, password=hashed_password,
                               salt=salt, display_name=display_name)
        # Add and Commit new user to database
        db.session.add(new_user)
        db.session.commit()
        # Signup successful, redirect to home
        return redirect("/home", code=302)
    else:
        # Signup failed, return false
        return "Signup failed"

# Route to handle user login
@app.route("/login", methods=["GET", "POST"])
def login():
    # Get user's inputted username and password from the request
    username = request.form.get("username")
    password = request.form.get("password")
    # Query db w/ username
    user = models.User.query.filter_by(username=username).first()
    if user is not None:
        # Hash and salt inputted password
        h = hashlib.sha512()
        h.update(bytes.fromhex(user.salt))
        h.update(password.encode("utf-8"))
        hashed_password = h.hexdigest()
        if user.check_password(hashed_password):
            login_user(user)
            # Login successful, redirect to home
            return redirect("/home", code=302)
        else:
            # Password incorrect
            return "Login failed"
    else:
        # Username not found
        return "Login failed"


# Route to handle user logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    # Logout successful, redirect to home
    return redirect("/explore", code=302)


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


# Route to change user's display name
@app.route("/change_display_name", methods=["GET", "POST"])
@login_required
def change_display_name():
    # Get user's inputted new display name
    display_name = request.form["change_display_name"]
    current_user.display_name = display_name
    db.session.commit()
    # Name change successful, refresh settings page
    return redirect("/settings", code=302)


# Route to change user's password
@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    # Get user's inputted new display name
    new_password = request.form["change_password"]
    # Salt and hash new password
    h = hashlib.sha512()
    h.update(bytes.fromhex(current_user.salt))
    h.update(new_password.encode("utf-8"))
    hashed_new_password = h.hexdigest()
    current_user.password = hashed_new_password
    db.session.commit()
    # Name change successful, refresh settings page
    return redirect("/settings", code=302)


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
        return redirect("/profile/" + new_friend_username, code=302)


# Route to handle removing a friend
@app.route("/remove-friend/<friend_username>", methods=["GET", "POST"])
@login_required
def remove_friend(friend_username):
    # Get user object of new friend
    friend = models.User.query.filter_by(username=friend_username).first()
    if friend is None:
        # Invalid friend to remove
        return "User to remove as friend not found"
    else:
        # User found, remove friendship from database
        db.session.delete(models.Friendship.query.filter_by(user1_id=current_user.id, user2_id=friend.id).first())
        db.session.commit()
        return redirect("/friends", code=302)


# Function to check if users file upload is a valid file type
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {"png, jpg, jpeg, gif"}


# Route to handle user file uploads
@app.route('/upload_file', methods=['GET', 'POST'])
@login_required
def upload_file():
    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    # If the user does not select a file, the browser submits an empty file without a filename.
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file:  # validate file type
        upload_directory = os.path.join(app.root_path, "static/assets/profile-imgs/")
        # check if the directory exists
        if not os.path.exists(upload_directory):
            # create the directory
            os.makedirs(upload_directory)

        file_extension = file.filename.rsplit('.', 1)[1].lower()
        file.save(upload_directory + current_user.username + '.' + file_extension)
        return redirect("/settings")
    return redirect("/settings")


# Route to handle user posting
@app.route("/post", methods=["GET", "POST"])
@login_required
def post():
    # Get user's post text (body) from form
    body = request.form.get("post-body")
    # Create new post object from models
    new_post = models.Post(poster_id=current_user.id, body=body)
    # Add and Commit post object to database
    db.session.add(new_post)
    db.session.commit()
    # New post saved to db, redirect to home
    return redirect("/home", code=302)


# Route to redirect index to homepage
@app.route("/")
def index():
    return redirect("/home")


# Route to display homepage with user's timeline
@app.route("/home")
@login_required
def home():
    # Get list of friend's ids
    friend_ids = [x.id for x in current_user.friends.all()]
    # Add user's id to see their own posts in timeline
    friend_ids.append(current_user.id)
    # Get all posts by user's friends to display timeline
    posts = models.Post.query \
        .with_entities(models.User.username, models.User.display_name,
                       models.Post.time_posted, models.Post.body) \
        .filter(models.Post.poster_id.in_(friend_ids)) \
        .join(models.User, models.Post.poster_id == models.User.id) \
        .order_by(desc(models.Post.time_posted))

    return render_template("posts.html",
                           title="Home",
                           content_heading="Your timeline",
                           current_user=current_user,
                           posts=posts)


# Route to display explore page with all posts
@app.route("/explore")
def explore():
    # Get all posts to display on homescreen
    posts = models.Post.query \
        .with_entities(models.User.username, models.User.display_name, models.Post.time_posted, models.Post.body) \
        .join(models.User, models.Post.poster_id == models.User.id) \
        .order_by(desc(models.Post.time_posted))
    return render_template("posts.html",
                           title="Explore",
                           content_heading="All posts",
                           current_user=current_user,
                           posts=posts)


# Route to display list of user's friends
@app.route("/friends")
@login_required
def friends():
    # Get friends of user
    all_friends = current_user.friends.all()
    return render_template("friends.html",
                           title="Friends",
                           content_heading="Your friends",
                           current_user=current_user,
                           friends=all_friends)


# Route to redirect /profile to /profile/username
@login_required
@app.route("/profile")
def profile_redirect():
    return redirect("/profile/" + current_user.username)


# Route to display user's profile
@app.route("/profile/<profile_owner_username>")
@login_required
def profile(profile_owner_username):
    # Get user object of profile owner
    profile_owner = models.User.query.filter_by(username=profile_owner_username).first()
    if profile_owner is None:
        # Invalid username in url
        return "User not found"
    else:
        # Username in url found, get profile owner's posts
        posts = models.Post.query \
            .with_entities(models.Post.poster_id, models.User.username, models.User.display_name,
                           models.Post.time_posted, models.Post.body) \
            .filter_by(poster_id=profile_owner.id) \
            .join(models.User, models.Post.poster_id == models.User.id) \
            .order_by(desc(models.Post.time_posted))
        # Get user's friends
        all_friends = current_user.friends.all()
        # Render profile page
        return render_template("profiles.html",
                               title="Profile",
                               content_heading=profile_owner.display_name + "'s profile",
                               current_user=current_user,
                               profile_owner=profile_owner,
                               posts=posts,
                               friends=all_friends)


# Route to display settings page
@app.route("/settings")
def settings():
    username = current_user.username if current_user.is_authenticated else ""
    return render_template("settings.html",
                           title="Settings",
                           content_heading="Your settings",
                           current_user=current_user, )
