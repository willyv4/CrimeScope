from app import db
from models import User, Place, Post, Vote

db.drop_all()
db.create_all()
