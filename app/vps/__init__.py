from flask import Blueprint

bp = Blueprint('vps', __name__)

from app.vps import routes
