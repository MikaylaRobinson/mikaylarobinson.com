import config
import json
import os
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash
from flask_login import current_user, login_user, LoginManager, UserMixin, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_wtf import FlaskForm
from site_utils import make_url_slug
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegistrationForm, LoginForm, NewBlogForm, NewSideProjectForm

app = Flask(__name__)

# dotenv.load_dotenv(os.path.dirname(__file__), ".flaskenv")
app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
app.config["SECRET_KEY"] = config.SECRET_KEY
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(os.getcwd(), 'static', 'uploads')

# Database configuration with SQLAlchemy
db = SQLAlchemy(app)
login = LoginManager(app)

# Image upload form, needs app variable. 
# TODO: Refactor file structure
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)  # set maximum file size, default is 16MB

class ImageUploadForm(FlaskForm):
    photo = FileField(validators=[FileAllowed(photos, u'Image only!'), FileRequired(u'File was empty!')])
    submit = SubmitField(u'Upload')

class LearningTopics(db.Model):
    __tablename__ = "learning_topics"
    id = db.Column(db.Integer, primary_key = True)
    date = db.Column(db.DateTime)
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

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if not "date"}

class SideProjects(db.Model):
    __tablename__ = "side_projects"
    id = db.Column(db.Integer, primary_key = True)
    date = db.Column(db.DateTime)
    keyword = db.Column(db.String(120))
    title = db.Column(db.String(120))
    tools_used = db.Column(db.String(120))
    url_slug = db.Column(db.String(120))
    content = db. Column(db.String())
    image_url = db.Column(db.String(250))

    def __init__(self, date, keyword, title, tools_used, url_slug, content, image_url):
        self.date = date
        self.keyword = keyword
        self.title = title
        self.tools_used = tools_used
        self.url_slug = url_slug
        self.content = content
        self.image_url = image_url

# Borrowed from: https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins
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

if config.CREATE_DATABASE:
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
        if form.secret_pass.data != config.SECRET_PASSWORD:
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
        # Retrieve user by username
        user = User.query.filter_by(username=form.username.data).first()
        # Early exit if user doesn't exist in DB, or password check fails
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('log_user_in'))

        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('home_page'))
    return render_template('login.html', title='Sign In', form=form)

@app.route("/control_panel")
@login_required
def control_panel_route():
    return render_template("admin_pages/control_panel.html")

@app.route("/admin/blog/new", methods=['GET', 'POST'])
@login_required
def admin_blog_new_route():
    form = NewBlogForm()
    
    if form.validate_on_submit():
        url_slug = make_url_slug(form.title.data)
        post = LearningTopics(date=datetime.now(), keyword=form.keyword.data, title=form.title.data, tools_used=form.tools_used.data, url_slug=url_slug, content=form.content.data, image_url=None)
        db.session.add(post)
        db.session.commit()
        flash("Post Added")
        return redirect(url_for("control_panel_route"))
    return render_template("admin_pages/blog_new.html",form=form)

@app.route("/admin/project/new", methods=['GET', 'POST'])
@login_required
def admin_project_new_route():
    form = NewSideProjectForm()
    
    if form.validate_on_submit():
        url_slug = make_url_slug(form.title.data)
        post = SideProjects(date=datetime.now(), keyword=form.keyword.data, title=form.title.data , tools_used=form.tools_used.data, url_slug=url_slug, content=form.content.data, image_url=None)
        db.session.add(post)
        db.session.commit()
        flash("Post Added")
        return redirect(url_for("control_panel_route"))
    return render_template("admin_pages/project_new.html",form=form)

@app.route("/admin/blog/view_all")
@login_required
def admin_blog_view_all():
    posts = LearningTopics.query.all()
    return render_template("admin_pages/blog_view_all.html", posts=posts)

@app.route("/admin/project/view_all")
@login_required
def admin_project_view_all():
    posts = SideProjects.query.all()
    return render_template("admin_pages/project_view_all.html", posts=posts)

@app.route("/api/blog/posts")
def api_blog_posts_route():
    posts = LearningTopics.query.all()
    return json.dumps([post.as_dict() for post in posts])

@app.route('/admin/blog/delete/<id>', methods=['POST'])
@login_required
def delete_blog_post_route(id):
    post = LearningTopics.query.filter_by(id=id).first()
    
    if post is None:
        return json.dumps({"error":"Post does not exist"})

    db.session.delete(post)
    db.session.commit()
    return json.dumps({"status":"ok"})

@app.route('/admin/project/delete/<id>', methods=['POST'])
@login_required
def delete_project_post_route(id):
    post = SideProjects.query.filter_by(id=id).first()
    
    if post is None:
        return json.dumps({"error":"Post does not exist"})

    db.session.delete(post)
    db.session.commit()
    return json.dumps({"status":"ok"})

@app.route('/admin/image_upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    form = ImageUploadForm()
    if form.validate_on_submit():
        filename = photos.save(form.photo.data)
        file_url = photos.url(filename)
    else:
        file_url = None
    return render_template('admin_pages/upload.html', form=form, file_url=file_url)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home_page'))

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

if __name__ == "__main__":
    app.run()