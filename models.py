import bcrypt
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
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


class User(db.Model):
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

    posts = db.relationship('Post', backref='users',
                            cascade='all, delete-orphan')
    votes = db.relationship('Post', secondary='votes')

    @classmethod
    def signup(cls, username, email, password):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


class Place(db.Model):
    """ Places table """

    __tablename__ = "places"

    city_url = db.Column(db.Text, nullable=False, primary_key=True)
    city = db.Column(db.Text, nullable=False)
    state = db.Column(db.Text, nullable=False)


class Post(db.Model):
    """Posts table """

    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)

    place_city_url = db.Column(db.Text, db.ForeignKey(
        "places.city_url"), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey(
        "users.id", ondelete="CASCADE"))

    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow())

    place = db.relationship('Place', backref='posts')
    user = db.relationship('User')
    votes = db.relationship('Vote', backref='post')

    @property
    def num_votes(self):
        return db.session.query(func.count(Vote.id)).filter_by(post_id=self.id).scalar()


class Vote(db.Model):
    """Accuracy Votes table"""

    __tablename__ = "votes"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)
