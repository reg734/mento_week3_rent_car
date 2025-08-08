from flask import Blueprint

bp = Blueprint('api', __name__)

from app.api import cars
from app.api import my_favorites
