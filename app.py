from flask import Flask, request, redirect, url_for, render_template, flash
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from database import User, db
from login_form import LoginForm
import ast

# Main file that defines the app and routes. Runs the app if called as main.

# Initialize app and set preferances
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///temp_database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "redacted"

# Initialize database and create tables
db.init_app(app)
with app.app_context():
    db.create_all()

# Initialize login manager to handle user session
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(username):
    return User.query.get(username)


# redirects to base user to either login or home based on if the user is logged in or not
@app.route("/")
def home_redirect():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

# Handles login procedure
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        form = LoginForm(request)
        if not form.is_valid():
            flash("Invalid Username and/or Password!")
            return redirect(url_for('login'))
        login_user(form.get_user())
        return redirect(url_for('home'))
    return render_template("login.html")


# Handles sign up procedure
@app.route("/sign_up", methods=["POST"])
def sign_up():
    form = LoginForm(request)
    if form.get_user() is not None:
        flash("Username already exists!")
        return redirect(url_for('login'))
    form.add_user()
    flash("Successfully Registered! Please Login.")
    return redirect(url_for('login'))

# Logs user out of current session
@app.route("/logout", methods=["POST", "GET"])
def logout():
    logout_user()
    flash("Successfully Logged Out!")
    return redirect(url_for("login"))


@app.route("/home")
@login_required
def home():
    return render_template("home.html")


# Processes input data and retrieves stored data
@app.route("/get_data", methods=["POST"])
@login_required
def get_data():
    keys = request.form["data"]
    data = ast.literal_eval(current_user.data)
    if keys != "":
        keys = keys.split(",")
        data = return_data(data, keys)
    flash_data(data, True)
    return redirect(url_for("home"))


# Processes input data. Sets and stores data
@app.route("/set_data", methods=["POST"])
@login_required
def set_data():
    pairs = request.form["data"]
    pairs = pairs.split(",")
    data = ast.literal_eval(current_user.data)
    new_data, all_data = make_pairs(pairs, data)
    current_user.data = str(all_data)
    db.session.commit()
    flash_data(new_data, False)
    return redirect(url_for("home"))


# Finds the requested data if present, otherwise lets user know no data for that key was found
def return_data(data, keys):
    temp_data = {}
    for key in keys:
        if key in data:
            temp_data[key] = data[key]
        else:
            temp_data[key] = "No Data For Key Found!"
    return temp_data


# pushes all data to flash
def flash_data(data, get):
    if get:
        flash("Retrieved Data:")
    else:
        flash("Set Data:")
    for key in data:
        flash(f"{key}: {data[key]}")


# parses key:value pairs and adds it to the data. Returns new_data for display to user. Returns all data for storage
def make_pairs(pairs, data):
    new_data = {}
    for pair in pairs:
        pair = pair.split(":")
        if len(pair) == 2:
            data[pair[0]] = pair[1]
            new_data[pair[0]] = pair[1]
    return new_data, data


if __name__ == "__main__":
    app.run()