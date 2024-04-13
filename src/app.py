import argparse
import logging
from flask import Flask
from src import (
    taddy,
    transcribe,
)
from src.models import (
    db,
    Episode,
    Podcast,
    Transcription,
    TranscriptionModel,
)
from src.utils import queue

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

    db.init_app(app)

    podcast = taddy.search_podcast(args.search_term)
    if podcast:
        logger.info(podcast.name)
        episodes = taddy.get_episodes(podcast, limitPerPage=25)

    # TODO: these tasks do not execute because this script exists
    queue.enqueue(transcribe.transcribe, kwargs={"episode": episodes[0]})
    queue.enqueue(transcribe.transcribe, kwargs={"episode": episodes[2]})

    logger.info(Podcast.objects())
    logger.info(Episode.objects())
    logger.info(TranscriptionModel.objects())
    logger.info(Transcription.objects())
