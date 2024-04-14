import argparse
import logging
from flask import Flask
from flask_mongoengine import MongoEngine
from src.lib import (
    taddy,
    summarize,
)
from src.lib.models import (
    Episode,
    Podcast,
    Transcription,
    TranscriptionModel,
)

logger = logging.getLogger(__name__)


# Function to parse command line arguments
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-st", "--search_term", required=True,
        help="The search term used to find the podcast series."
    )
    log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    parser.add_argument(
        "-ll", "--log_level", choices=log_levels,
        default="INFO", help="The log level (default: INFO)"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    logging.basicConfig(level=args.log_level)

    app = Flask(__name__)
    app.config["MONGODB_SETTINGS"] = {
        "db": "summpods",
        "host": "localhost",
        "port": 27017
    }

    db = MongoEngine()
    db.init_app(app)

    podcast = taddy.search_or_get_podcast(term=args.search_term)
    if podcast:
        logger.info(podcast.name)
        episodes = taddy.get_episodes(podcast, limitPerPage=25)

    summarize.transcribe_and_summarize(episodes[0])

    logger.info(Podcast.objects())
    logger.info(Episode.objects())
    logger.info(TranscriptionModel.objects())
    logger.info(Transcription.objects())
