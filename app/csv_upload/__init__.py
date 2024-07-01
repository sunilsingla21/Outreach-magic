from flask import Blueprint

bp = Blueprint('csv_upload', __name__)

from app.csv_upload import routes