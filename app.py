from flask import Flask, render_template, redirect, flash, request, session, g
from sqlalchemy.exc import IntegrityError
from models import User, Post, Place, Vote, connect_db, db
import os

app = Flask(__name__)
app.testing = True

if app.testing:
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        os.environ.get('DATABASE_URL_TEST', 'postgresql:///crime_scope_test'))
else:
    try:
        prodURI = os.getenv('DATABASE_URL')
        prodURI = prodURI.replace("postgres://", "postgresql://")
        app.config['SQLALCHEMY_DATABASE_URI'] = prodURI

    except:
        app.config['SQLALCHEMY_DATABASE_URI'] = (
            os.environ.get('DATABASE_URL', 'postgresql:///crime_scope'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "emircepocs192837465")
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

print("####################################")
print("####################################")
print(app.config['SQLALCHEMY_DATABASE_URI'])
print("####################################")
print("####################################")


@app.route("/")
def home():

    return "HELLO"
