# Check requirements.txt for the required libraries
import os

from flask import Flask
from flask_session import Session
from flask_bootstrap import Bootstrap

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='6CjhxNkAYEx2AJfK',
        SESSION_TYPE = 'filesystem'
    )
    Session(app)
    

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import bp_retrieve, bp_logs, bp_visualize, bp_dev, bp_tutorial
    app.register_blueprint(bp_retrieve.bp)
    app.register_blueprint(bp_logs.bp)
    app.register_blueprint(bp_visualize.bp)
    app.register_blueprint(bp_dev.bp)
    app.register_blueprint(bp_tutorial.bp)
    bootstrap = Bootstrap(app)

    return app