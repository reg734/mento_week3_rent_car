from flask import Blueprint
from flask_sqlalchemy import SQLAlchemy

bp = Blueprint('models', __name__)
db = SQLAlchemy()

from app.models.user import User
from app.models.car import Car


