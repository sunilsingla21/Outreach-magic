from flask import Blueprint

bp = Blueprint('google', __name__)

from app.google import routes