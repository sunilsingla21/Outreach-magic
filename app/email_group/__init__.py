from flask import Blueprint

bp = Blueprint('email_group', __name__)

from app.email_group import routes
