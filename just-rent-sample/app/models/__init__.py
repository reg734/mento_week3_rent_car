from flask import Blueprint


bp = Blueprint('models', __name__)


from app.models.users import User
from app.models.cars import Car
from app.models.car_images import CarImage
from app.models.popular_cars import PopularCar
from app.models.my_favorites import MyFavorite
from app.models.bookings import Booking
from app.models.prices import Price
from app.models.locations import Location
from app.models.orders import Order

