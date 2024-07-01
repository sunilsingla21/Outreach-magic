from flask import Blueprint

bp = Blueprint('proxy_details', __name__)

from app.proxy_details import routes
