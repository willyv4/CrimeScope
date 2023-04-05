import bcrypt
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


bcrypt = Bcrypt()
db = SQLAlchemy()


def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)
    app.app_context().push()


class Users(db.Model):
    """Users table"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow(),
    )


class Places(db.Model):
    """ Places table """

    __tablename__ = "places"

    city_url = db.Column(db.Text, nullable=False, primary_key=True)
    city = db.Column(db.Text, nullable=False)
    state = db.Column(db.Text, nullable=False)


class Posts(db.Model):
    """Posts table """

    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    place_city_url = db.ForeignKey("places.city_url", primary_key=True)
    user_id = db.ForeignKey("users.id", primary_key=True, ondelete="CASCADE")
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow())

    place = db.relationship('Places', backref='posts')
    user = db.relationship('Users', backref='posts',
                           cascade='all, delete-orphan')


class Votes(db.Model):
    """ Accuracy Votes table """

    __tablename__ = "votes"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    post_id = db.ForeignKey("posts.id", nullable=False)
    user_id = db.ForeignKey("users.id", ondelete="CASCADE", nullable=False)
