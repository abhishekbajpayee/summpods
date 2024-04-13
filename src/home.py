from flask import (
    Blueprint,
    render_template,
)

home = Blueprint("home", __name__, url_prefix="/")


@home.route("/")
def index():
    data = {
        "title": "Home",
        "user": "Friend",
        "content": "Today we are doing some podcast summarization using LLMs!",
    }
    return render_template("index.html", **data)
