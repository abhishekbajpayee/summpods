import argparse
import logging
from flask import Flask
from flask_material import Material
from src.models import (
    TranscriptionModel,
    db
)

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
    app.config["MONGODB_SETTINGS"] = {
        "db": "summpods",
        "host": "localhost",
        "port": 27017
    }
    db.init_app(app)

    # fetch and print existing models
    models = TranscriptionModel.objects.all()
    logger.info(models)

    _ = Material(app)

    app.config.from_object(config_filename)

    from src.home import home
    app.register_blueprint(home)

    return app


if __name__ == "__main__":
    args = parse_args()
    logging.basicConfig(level=args.log_level)
    # TODO: investigage host 0.0.0.0 vs default 127.0.0.1
    create_app("src.conf.flask_conf.DevelopmentConfig").run(host="0.0.0.0")
