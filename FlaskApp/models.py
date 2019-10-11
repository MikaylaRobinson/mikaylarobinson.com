from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Database configuration with SQLAlchemy
db = SQLAlchemy()

class LearningTopics(db.Model):
    __tablename__ = "blog"
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