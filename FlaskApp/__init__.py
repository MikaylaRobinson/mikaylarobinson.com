from flask import Flask, render_template
app = Flask(__name__)

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