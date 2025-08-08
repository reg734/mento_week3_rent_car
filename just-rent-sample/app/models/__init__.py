from flask import Blueprint


bp = Blueprint('models', __name__)


from app.models.user import User
from app.models.car import Car
from app.models.car_images import CarImages
from app.models.popular_cars import PopularCar
from app.models.my_favorite import MyFavorites
