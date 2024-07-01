from flask import Blueprint

bp = Blueprint('seed_batch', __name__)

from app.seed_batch import routes