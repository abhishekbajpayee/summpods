from flask import Flask
from flask_material import Material

def create_app(config_filename="src.conf.BaseConfig"):
    app = Flask(__name__)
    material = Material(app)

    app.config.from_object(config_filename)

    from src.home import home
    app.register_blueprint(home)

    return app
