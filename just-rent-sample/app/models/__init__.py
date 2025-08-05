from flask import Blueprint


bp = Blueprint('models', __name__)


from app.models.user import User
from app.models.car import Car
from app.models.car_images import CarImages
