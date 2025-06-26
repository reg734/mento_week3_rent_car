from flask import Blueprint

bp = Blueprint('controller', __name__)

from . import pages_controller



