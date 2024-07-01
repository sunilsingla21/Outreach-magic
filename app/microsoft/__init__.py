from flask import Blueprint

bp = Blueprint('microsoft', __name__)

from app.microsoft import routes