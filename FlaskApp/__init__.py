import os
import dotenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask import Flask, render_template

app = Flask(__name__)

dotenv.load_dotenv(os.path.dirname(__file__), '.flaskenv')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("SQLALCHEMY_DATABASE_URI")

# Database configuration with SQLAlchemy
db = SQLAlchemy(app)

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

if __name__ == "__main__":
    app.run()