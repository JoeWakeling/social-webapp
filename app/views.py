import os
import hashlib
import secrets
from app import app, db, models
from flask import render_template, request, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import desc, func
from app.forms import SignupForm, LoginForm, NewPostForm, ChangeDisplayNameForm, ChangePasswordForm


# Route to handle user signup
@app.route("/signup", methods=["POST"])
def signup():
    # Get user's inputted username, password and display name from the request
    username = request.form.get("username").lower()
    password = request.form.get("password")
    display_name = request.form.get("display_name")
    # Query db to check if username taken
    user = models.User.query.filter_by(username=username).first()
    if user is not None:
        # Username taken, log and return false
        app.logger.warning("Failed signup (username taken), username: " + username)
        return "Error: username already in use"
    else:
        # Username not taken, generate a random 16 char hex salt
        salt = secrets.token_hex(8)
        # Salt & hash password
        h = hashlib.sha512()
        h.update(bytes.fromhex(salt))
        h.update(password.encode("utf-8"))
        hashed_password = h.hexdigest()
        # Create new user with username, hashed password and display name
        new_user = models.User(username=username, password=hashed_password, salt=salt,
                               display_name=display_name, theme="light")
        # Add and Commit new user to database
        db.session.add(new_user)
        db.session.commit()
        # Signup successful, log signup & redirect to home
        app.logger.info("Successful signup, username: " + username)
        return "Success: account created, please sign in"


# Route to handle user login
@app.route("/login", methods=["POST"])
def login():
    # Get user's inputted username and password from the request
    username = request.form.get("username").lower()
    password = request.form.get("password")
    # Query db w/ username
    user = models.User.query.filter_by(username=username).first()
    if user is None:
        # Username not found
        app.logger.warning("Failed login (username not found), username: " + username)
        return "Error: username or password incorrect"
    else:
        # Hash and salt inputted password
        h = hashlib.sha512()
        h.update(bytes.fromhex(user.salt))
        h.update(password.encode("utf-8"))
        hashed_password = h.hexdigest()
        if not user.check_password(hashed_password):
            # Password incorrect, log & return false
            app.logger.warning("Failed login (incorrect password), username: " + username)
            return "Error: username or password incorrect"
        else:
            login_user(user)
            # Login successful, log & redirect to home
            app.logger.info("Successful login, username: " + username)
            return url_for("home")


# Route to handle user logout
@app.route("/logout", methods=["GET"])
@login_required
def logout():
    username = current_user.username
    logout_user()
    # Logout successful, log & redirect to home
    app.logger.info("Successful logout, username: " + username)
    return redirect("/explore", code=303)


# Route to handle adding a friend
@login_required
@app.route("/add-friend/<new_friend_username>", methods=["POST"])
def add_friend(new_friend_username):
    # Get user object of new friend
    new_friend = models.User.query.filter_by(username=new_friend_username).first()
    if new_friend is None:
        # Invalid new friend username, log & return false
        app.logger.warning("Failed friend add (friend not found)" +
                           "username: " + current_user.username + " friend: " + new_friend_username)
        return "User to add as friend not found"
    else:
        # User found, add friendship to database
        current_user.friends.append(new_friend)
        db.session.commit()
        # Successfully added friend, log and redirect to friends profile
        app.logger.info("Successful friend add," +
                        "username: " + current_user.username + " friend: " + new_friend_username)
        return redirect("/profile/" + new_friend_username, code=303)


# Route to handle removing a friend
@app.route("/remove-friend/<friend_username>", methods=["POST"])
@login_required
def remove_friend(friend_username):
    # Get user object of new friend
    friend = models.User.query.filter_by(username=friend_username).first()
    if friend is None:
        # Invalid remove friend username, log & return false
        app.logger.warning("Failed friend remove (friend not found)" +
                           "username: " + current_user.username + " friend: " + friend_username)
        return "User to remove as friend not found"
    else:
        # User found, remove friendship from database
        db.session.delete(models.Friendship.query.filter_by(user1_id=current_user.id, user2_id=friend.id).first())
        db.session.commit()
        # Successfully removed friend, log and redirect friends profile
        app.logger.info("Successful friend remove," +
                        "username: " + current_user.username + " friend: " + friend_username)
        return redirect("/friends", code=303)


# Route to handle user changing profile picture
@app.route('/change_pfp', methods=['POST'])
@login_required
def change_pfp():
    # check if the post request has a file
    if 'file' not in request.files:
        return "Error: no file uploaded"
    file = request.files['file']
    # If the user does not select a file, the browser submits an empty file without a filename.
    if file.filename == '':
        return "Error: no file uploaded"
    if not file:
        return "Error: no file uploaded"
    else:
        upload_directory = os.path.join(app.root_path, "static/assets/profile-imgs/")
        # check if the directory exists
        if not os.path.exists(upload_directory):
            # create the directory
            os.makedirs(upload_directory)
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        if file_extension != "jpg":
            return "Invalid file type"
        file.save(upload_directory + current_user.username + '.' + file_extension)
        # Successfully changed pfp, log & refresh settings page
        app.logger.info("Successful pfp change, username: " + current_user.username)
        return redirect("/settings", code=303)


# Route to change user's display name
@app.route("/change_display_name", methods=["POST"])
@login_required
def change_display_name():
    #  Get new display name
    display_name = request.form.get("display_name")
    if current_user.display_name == display_name:
        return "Error: new display name same as old display name"
    current_user.display_name = display_name
    db.session.commit()
    # Display name change successful, log & refresh settings page
    app.logger.info("Successful display name change, username: " + current_user.username +
                    ", new display name: " + current_user.display_name)
    return url_for("settings")


# Route to change user's password
@app.route("/change_password", methods=["POST"])
@login_required
def change_password():
    #  Get new and old passwords
    old_password = request.form.get("old_password")
    new_password = request.form.get("new_password")
    # Check if old password correct
    h_old = hashlib.sha512()
    h_old.update(bytes.fromhex(current_user.salt))
    h_old.update(old_password.encode("utf-8"))
    hashed_old_password = h_old.hexdigest()
    if hashed_old_password != current_user.password:
        app.logger.warning("Failed password change (incorrect old password) username: " + current_user.username)
        return "Error: incorrect old password"
    else:
        # Salt and hash new password
        h_new = hashlib.sha512()
        h_new.update(bytes.fromhex(current_user.salt))
        h_new.update(new_password.encode("utf-8"))
        hashed_new_password = h_new.hexdigest()
        current_user.password = hashed_new_password
        db.session.commit()
        # Name change successful, log & refresh settings page
        app.logger.info("Successful password change, username: " + current_user.username)
        return "Success: password changed"


# Route to set user's selected theme
@app.route("/set_theme", methods=["POST"])
@login_required
def set_theme():
    # Get selected theme from form
    theme = request.form.get("theme-dropdown").lower()
    # Update db with selection
    current_user.theme = theme
    db.session.commit()
    # Set theme successful, log & refresh settings page
    app.logger.info("Successful theme selection, username: " + current_user.username)
    return redirect("/settings", code=303)


# Route to get user's selected theme
@app.route("/get-theme", methods=["POST"])
def get_theme():
    # Check if user's id in session
    if current_user.is_authenticated:
        theme = str(current_user.theme)
        # User logged in, return theme
        return theme
    else:
        # User not logged in, default to light theme
        return "light"


@app.route("/new_post", methods=["POST"])
@login_required
def new_post():
    # Create instance of new post form
    new_post_form = NewPostForm()
    # When form submitted
    if new_post_form.validate_on_submit():
        # Get user's post text (body) from form
        body = request.form.get("body")
        # Create new post object from models
        new_post_obj = models.Post(poster_id=current_user.id, body=body)
        # Add and Commit post object to database
        db.session.add(new_post_obj)
        db.session.commit()
        # New post saved to db, redirect to home
        app.logger.info("Successful post, " +
                        "username: " + current_user.username + "post_id:" + str(new_post_obj.id))
        return redirect("/home", code=303)


# Route to redirect index to homepage
@app.route("/")
def index():
    return redirect("/home")


# Route to display homepage with user's timeline
@app.route("/home", methods=["GET"])
@login_required
def home():
    # Create instance of new post form
    new_post_form = NewPostForm()

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

    # Get list (top 3) of featured users (most posts) for aside content
    featured_users = models.User.query \
        .join(models.Post, models.Post.poster_id == models.User.id) \
        .group_by(models.User.id) \
        .order_by(func.count(models.Post.id).desc()) \
        .limit(3) \
        .all()

    return render_template("home.html",
                           title="Home",
                           content_heading="Your timeline",
                           current_user=current_user,
                           posts=posts,
                           featured_users=featured_users,
                           new_post_form=new_post_form,
                           theme=current_user.theme)


# Route to display explore page with all posts
@app.route("/explore", methods=["GET"])
def explore():
    # Create instances of login & signup form
    signup_form = SignupForm()
    login_form = LoginForm()

    # Get all posts to display on explore page
    posts = models.Post.query \
        .with_entities(models.User.username, models.User.display_name, models.Post.time_posted, models.Post.body) \
        .join(models.User, models.Post.poster_id == models.User.id) \
        .order_by(desc(models.Post.time_posted))

    # Get list (top 3) of featured users (most posts) for aside content
    featured_users = models.User.query \
        .join(models.Post, models.Post.poster_id == models.User.id) \
        .group_by(models.User.id) \
        .order_by(func.count(models.Post.id).desc()) \
        .limit(3) \
        .all()

    # Get user's selected theme or default to light if not logged in
    if current_user.is_authenticated:
        theme = current_user.theme
    else:
        theme = "light"

    return render_template("explore.html",
                           title="Explore",
                           content_heading="All posts",
                           current_user=current_user,
                           posts=posts,
                           featured_users=featured_users,
                           signup_form=signup_form,
                           login_form=login_form,
                           theme=theme)


# Route to display list of user's friends
@app.route("/friends")
@login_required
def friends():
    # Get friends of user
    all_friends = current_user.friends.all()

    # Get list (top 3) of featured users (most posts) for aside content
    featured_users = models.User.query \
        .join(models.Post, models.Post.poster_id == models.User.id) \
        .group_by(models.User.id) \
        .order_by(func.count(models.Post.id).desc()) \
        .limit(3) \
        .all()

    return render_template("friends.html",
                           title="Friends",
                           content_heading="Your friends",
                           featured_users=featured_users,
                           current_user=current_user,
                           friends=all_friends,
                           theme=current_user.theme)


# Route to redirect /profile to /profile/username
@login_required
@app.route("/profile")
def profile_redirect():
    return redirect("/profile/" + current_user.username, code=301)


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

        # Get user's friends for add/remove friend button
        all_friends = current_user.friends.all()

        # Get list (top 3) of featured users (most posts) for aside content
        featured_users = models.User.query \
            .join(models.Post, models.Post.poster_id == models.User.id) \
            .group_by(models.User.id) \
            .order_by(func.count(models.Post.id).desc()) \
            .limit(3) \
            .all()

        # Render profile page
        return render_template("profiles.html",
                               title="Profile",
                               content_heading=profile_owner.display_name + "'s profile",
                               current_user=current_user,
                               profile_owner=profile_owner,
                               featured_users=featured_users,
                               posts=posts,
                               friends=all_friends,
                               theme=current_user.theme)


# Route to display settings page
@app.route("/settings")
@login_required
def settings():
    # Initialise form instances
    change_display_name_form = ChangeDisplayNameForm()
    change_password_form = ChangePasswordForm()
    # Render settings page
    return render_template("settings.html",
                           title="Settings",
                           content_heading="Your settings",
                           current_user=current_user,
                           change_display_name_form=change_display_name_form,
                           change_password_form=change_password_form,
                           theme=current_user.theme)
