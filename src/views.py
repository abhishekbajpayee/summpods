import logging
import threading
from flask import (
    Blueprint,
    render_template,
    request,
)
from src.lib import (
    taddy,
    summarize,
)
from src.lib.models import (
    Summary,
)

logger = logging.getLogger(__name__)

bp = Blueprint("home", __name__)


@bp.route("/")
def index():
    data = {
        "title": "Home",
        "user": "Friend",
        "content": "Today we are doing some podcast summarization using LLMs!",
    }
    return render_template("index.html", **data)


@bp.route("/podcast_search", methods=["POST"])
def podcast_index():
    term = request.form["term"]
    podcast = taddy.search_or_get_podcast(term=term)
    data = {
        "title": "Podcast Search",
        "term": term,
        "podcast": podcast,
    }
    return render_template("podcast_search.html", **data)


@bp.route("/episodes")
def episodes():
    podcast_uuid = request.args["podcast_uuid"]
    podcast = taddy.search_or_get_podcast(uuid=podcast_uuid)
    episodes = taddy.get_episodes(podcast)
    data = {
        "title": "Episodes",
        "episodes": episodes,
    }
    return render_template("episodes.html", **data)


@bp.route("/summaries")
def summaries():
    # handle job request if episode_uuid is provided
    summary_request = False
    episode_uuid = request.args.get("episode_uuid", None)
    if episode_uuid:
        summary_request = True
        episode = taddy.get_episode(episode_uuid)
        # TODO: simply using threads for this won't scale eventually if traffic was high
        threading.Thread(target=summarize.transcribe_and_summarize, args=(episode,)).start()
    # get summaries to display on page
    summaries = Summary.objects().order_by("-creation_date")
    data = {
        "title": "Summaries",
        "summaries": summaries,
        "summary_request": summary_request,
    }
    return render_template("summaries.html", **data)
