import dotenv
import os
from flask import Flask, render_template, redirect, url_for, flash
from flask_login import current_user, login_user, LoginManager, UserMixin, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

app = Flask(__name__)

dotenv.load_dotenv(os.path.dirname(__file__), ".flaskenv")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_DATABASE_URI")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

# Database configuration with SQLAlchemy
db = SQLAlchemy(app)
login = LoginManager(app)

class LearningTopics(db.Model):
    __tablename__ = "learning_topics"
    id = db.Column(db.Integer, primary_key = True)
    date = db.Column(db.Date, unique = True)
    keyword = db.Column(db.String(120))
    title = db.Column(db.String(250))
    tools_used = db.Column(db.String(120))
    url_slug = db.Column(db.String(120))
    content = db.Column(db.String())
    image_url = db.Column(db.String(250))

    def __init__(self, date, keyword, title, tools_used, url_slug, content, image_url):
        self.date = date
        self.keyword = keyword
        self.title = title
        self.tools_used = tools_used
        self.url_slug = url_slug
        self.content = content
        self.image_url = image_url

class SideProjects(db.Model):
    __tablename__ = "side_projects"
    id = db.Column(db.Integer, primary_key = True)
    date = db.Column(db.Date, unique = True)
    keyword = db.Column(db.String(120))
    title = db.Column(db.String(120))
    tools_used = db.Column(db.String(120))
    project_url = db.Column(db.String(120))
    content = db. Column(db.String())
    image_url = db.Column(db.String(250))

    def __init__(self, date, keyword, title, tools_used, project_url, content, image_url):
        self.date = date
        self.keyword = keyword
        self.title = title
        self.tools_used = tools_used
        self.project_url = project_url
        self.content = content
        self.image_url = image_url

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean)

    def __repr__(self):
        return "<User {}>".format(self.username)    

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_is_admin(self, is_admin):
        self.is_admin = is_admin

class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")])
    secret_pass = PasswordField("Entry Code", validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Please use a different username.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Please use a different email address.")

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


if os.environ.get("CREATE_DATABASE"):
    print("Creating database")
    db.create_all()

@app.route("/")
def home_page():
    return render_template("index.html")

@app.route("/about_me")
def about_page():
    return render_template("about.html")

@app.route("/learning_topics")
def topics_page():
    return render_template("topics.html")

@app.route("/side_projects")
def projects_page():
    return render_template("projects.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        # Use secret password to prevent unwanted registrations
        if form.secret_pass != os.environ.get("SECRET_PASSWORD"):
            flash("I don't think you should be doing this.")
            return redirect(url_for("home_page"))
            
        user = User(username=form.username.data, email=form.email.data)

        if form.username.data == "mikayla":
            user.set_is_admin(True)

        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congratulations, you are now a registered user!")
        return redirect(url_for("home_page"))
    return render_template("register.html", title="Register", form=form)

@app.route('/login', methods=['GET', 'POST'])
def log_user_in():
    if current_user.is_authenticated:
        flash("Logged in")
        return redirect(url_for('home_page'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('home_page'))
    return render_template('login.html', title='Sign In', form=form)

@app.route("/control_panel")
@login_required
def control_panel_route():
    return render_template("control_panel.html")

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home_page'))

if __name__ == "__main__":
    app.run()