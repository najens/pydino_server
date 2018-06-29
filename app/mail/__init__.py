from flask import Blueprint


# Setup site blueprint
mail = Blueprint(
    'mail',
    __name__,
    template_folder='./templates',
    static_folder='./static',
    static_url_path='/app/emails/static'
)

# Import blueprint views
from .views import emails, contact, send_email  # noqa
