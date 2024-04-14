import argparse
import logging
from flask import Flask
from flask_admin import Admin
from flask_material import Material
from flask_mongoengine import MongoEngine
from src.lib import models

logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()
    log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    parser.add_argument(
        "-ll", "--log_level", choices=log_levels,
        default="INFO", help="The log level (default: INFO)"
    )
    return parser.parse_args()


def create_app(config_filename="src.conf.flask_conf.BaseConfig"):
    app = Flask(__name__)

    # init MongoDB connection
    app.config["MONGODB_SETTINGS"] = {
        "db": "summpods",
        "host": "localhost",
        "port": 27017
    }
    db = MongoEngine()
    db.init_app(app)

    # init Material
    _ = Material(app)

    # init Admin
    admin = Admin(app)
    admin.add_view(models.PodcastView(models.Podcast))
    admin.add_view(models.EpisodeView(models.Episode))
    admin.add_view(models.TranscriptionView(models.Transcription))
    admin.add_view(models.SummaryView(models.Summary))

    app.config.from_object(config_filename)

    from src.views import bp
    app.register_blueprint(bp)

    return app


if __name__ == "__main__":
    args = parse_args()
    logging.basicConfig(level=args.log_level)
    # TODO: investigage host 0.0.0.0 vs default 127.0.0.1
    create_app("src.conf.flask_conf.DevelopmentConfig").run(host="0.0.0.0")
