from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

from werkzeug.utils import secure_filename

# DB, CACHE
from flask_sqlalchemy import SQLAlchemy


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
