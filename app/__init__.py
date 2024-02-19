from flask import Flask, url_for, request, jsonify
from openai import AsyncOpenAI
import os
from flask_cors import CORS
from dotenv import load_dotenv

import tempfile
import boto3
from werkzeug.utils import secure_filename
from datetime import datetime
import io

# DB, CACHE
from flask_sqlalchemy import SQLAlchemy
from redis import Redis


db = SQLAlchemy()


def create_app():
    app = Flask(__name__, static_folder='static')
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    load_dotenv()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:@localhost/lingospeak'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()
        
        from .routes import api
        app.register_blueprint(api)

    return app
