from flask import Blueprint

bp = Blueprint('controller', __name__)

from app.controllers import pages_controller



