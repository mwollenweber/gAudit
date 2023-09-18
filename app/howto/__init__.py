__author__ = 'mjw'


from flask import Blueprint

howto = Blueprint('howto', __name__)
from . import views

