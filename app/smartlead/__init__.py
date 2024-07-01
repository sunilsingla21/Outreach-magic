from flask import Blueprint

bp = Blueprint('smartlead', __name__)

from app.smartlead import routes
