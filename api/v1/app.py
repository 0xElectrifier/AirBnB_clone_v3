#!/usr/bin/python3
"""Create the app object of our flask application
"""
from api.v1.views import app_views
from flask import Blueprint
from flask import Flask
from flask import jsonify
from flask_cors import CORS
from models import storage
from os import getenv

HBNB_API_HOST = getenv('HBNB_API_HOST')
HBNB_API_PORT = getenv('HBNB_API_PORT')
if HBNB_API_HOST is None:
    HBNB_API_HOST = '0.0.0.0'
if HBNB_API_PORT is None:
    HBNB_API_PORT = '5000'

app = Flask(__name__)
app.register_blueprint(app_views)

cors = CORS(app, resources={r"/api/v1/*": {"origins": "0.0.0.0"}})


@app.teardown_appcontext
def teardown(exc):
    """An operation to run after every application context"""
    storage.close()


@app.errorhandler(404)
def page_not_found(error):
    """Returns a view on error 404"""
    return jsonify({"error": "Not found"}), 404


if __name__ == '__main__':
    app.run(host=HBNB_API_HOST, port=HBNB_API_PORT, threaded=True)
