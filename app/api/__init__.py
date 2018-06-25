from flask import Blueprint


# Setup api blueprint
api = Blueprint('api', __name__)

# Import blueprint views
from .views import (users, login, projects, teams, brackets, matches,  #noqa
    topics)  # noqa
