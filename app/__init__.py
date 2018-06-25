#!/usr/bin/env python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_mail import Mail
from flask_cors import CORS


# Initialize app
app = Flask(
    __name__,
    template_folder='../../client/build',
    static_folder='../../client/build/static')

app.config.from_object('config')

# Initialize Flask_SQLAlchemy
db = SQLAlchemy(app)

# Initialize Flask-Cors
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "expose_headers": ["access", "refresh"]
    }
}, supports_credentials=True)

# Initialize Flask-JWT-Extended
jwt = JWTManager(app)

# Initialize Flask-Marshmallow
ma = Marshmallow(app)

# Initialize Flask-Mail
mail = Mail(app)

# Import blueprints
from app.auth import auth as auth_blueprint  # noqa
from app.api import api as api_blueprint  # noqa
from app.mail import mail as mail_blueprint  # noqa

# Register the blueprints
app.register_blueprint(auth_blueprint)
app.register_blueprint(api_blueprint, url_prefix="/api/v1")
app.register_blueprint(mail_blueprint, url_prefix="/api/v1")
