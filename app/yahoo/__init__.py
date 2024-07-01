from flask import Blueprint

bp = Blueprint('yahoo', __name__)

from app.yahoo import routes