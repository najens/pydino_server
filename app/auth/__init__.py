from flask import Blueprint


# Setup site blueprint
auth = Blueprint(
    'auth',
    __name__,
    # template_folder='./templates',
    # static_folder='./static',
    # static_url_path='/app/site/static'
)

# Import blueprint views
from .views import tokens  # noqa
