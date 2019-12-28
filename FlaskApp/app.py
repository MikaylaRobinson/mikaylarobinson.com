# TODO: Code cleanup 

import config
import json
import os
from datetime import datetime
from flask import Flask, render_template, redirect, request, url_for, flash
from flask_login import current_user, login_user, LoginManager, UserMixin, logout_user, login_required
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_wtf import FlaskForm
from site_utils import make_url_slug
from sqlalchemy.sql import func
from forms import RegistrationForm, LoginForm, NewBlogForm, NewSideProjectForm

app = Flask(__name__)

# dotenv.load_dotenv(os.path.dirname(__file__), ".flaskenv")
app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
app.config["SECRET_KEY"] = config.SECRET_KEY
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(os.getcwd(), 'static', 'uploads')

from models import db, LearningTopics, SideProjects, User
db.init_app(app)

with app.app_context():
    db.create_all()

# Database configuration with SQLAlchemy
login = LoginManager(app)

# Image upload form, needs app variable. 
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)  # set maximum file size, default is 16MB

class ImageUploadForm(FlaskForm):
    photo = FileField(validators=[FileAllowed(photos, u'Image only!'), FileRequired(u'File was empty!')])
    submit = SubmitField(u'Upload')



@app.route("/")
def home_page():
    return render_template("index.html")

@app.route("/about_me")
def about_page():
    return render_template("about.html")

@app.route("/blog")
def topics_page():
    per_page = 5
    page = request.args.get('page', 1, type=int)
    posts = LearningTopics.query.order_by(LearningTopics.date.desc()).paginate(page, per_page, False)
    next_url = url_for('topics_page', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('topics_page', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template("blog.html", posts = posts, next_url = next_url, prev_url = prev_url)

@app.route('/blog/<url_slug>')
def display_blog_post(url_slug):
    post = LearningTopics.query.filter_by(url_slug=url_slug).first()
    
    if post is None:
        return redirect(url_for(topics_page))
    return render_template("post.html", post = post)

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

@app.route("/admin/blog/edit/<url_slug>")
@login_required
def edit_blog_post(url_slug):
    post = LearningTopics.query.filter_by(url_slug=url_slug).first()
    
    if post is None:
        return redirect(url_for(topics_page))
    return render_template("admin_pages/blog_edit.html", post = post)

@app.route("/admin/blog/edit/<url_slug>", methods=['POST'])
@login_required
def edit_blog_post_submit(url_slug):
    post = LearningTopics.query.filter_by(url_slug=url_slug).first()
    post.title = request.form.get('title')
    post.keyword = request.form.get('keyword')
    post.date = request.form.get('date')
    post.tools_used = request.form.get('tools_used')
    post.url_slug = request.form.get('url_slug')
    post.content = request.form.get('content')
    post.image_url = request.form.get('image_url')
    db.session.commit()
    return render_template("admin_pages/control_panel.html")

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

@app.route("/admin/view_images")
@login_required
def admin_view_images():
    all_images = os.listdir(app.config['UPLOADED_PHOTOS_DEST'])
    all_images = ['uploads/' + file for file in all_images]
    return render_template("admin_pages/images_view.html", all_images=all_images)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home_page'))

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

if __name__ == "__main__":
    app.run()