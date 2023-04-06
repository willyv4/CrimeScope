from flask import Flask, render_template, redirect, flash, request, session, g
from sqlalchemy.exc import IntegrityError
from models import User, Post, Place, Vote, connect_db, db
from forms import CitySearchForm, LoginForm, UserAddForm
from places_api import get_city_url, get_crime_data
import os
import time

CURR_USER_KEY = "curr_user"

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


@app.before_request
def add_user_to_g():
    """ If a user is logged in add current user to Flask global """

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """ handle user signup.

    create new user and add to database. redirect to home page

    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")
    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('user/login.html', form=form)


@app.route('/', methods=["GET", "POST"])
def homepage():
    """Show homepage:

    """

    if g.user:

        form = CitySearchForm()

        if form.validate_on_submit():
            city = form.city.data
            state = form.state.data
            place = f"{city} {state}"
            place_url, place_type = get_city_url(place)

            existing_place = Place.query.filter_by(city_url=place_url).first()
            if existing_place:
                return redirect(f'/{place_url}/{place_type}/')
            else:
                # time.sleep(1)
                if place_url:
                    place = Place(city_url=place_url, city=city, state=state)
                    db.session.add(place)
                    db.session.commit()

                    return redirect(f'/{place_url}/{place_type}/')
                else:
                    print("cant find place!")
                    flash(
                        "Whoops, looks like that search didn't work try something else", "danger")

        return render_template("home.html", form=form)
    else:
        return render_template('home-anon.html')


@app.route('/<place_url>/<place_type>/', methods=["GET", "POST"])
def show_crime_data(place_url, place_type):

    crime_data = get_crime_data(place_url, place_type)

    # structure api data dynamically for prompt
    crime_data = crime_data['crime-safety']

    # extract and compare violent crime data
    violent_crime_list = []
    violent_crimes = crime_data['Violent Crimes']
    for crime_name, crime_values in violent_crimes.items():
        crime_value = crime_values['value']
        national_crime = crime_values['national']
        violent_crime_list.append(
            f"{crime_name} index of {crime_value} compared to the national average of {national_crime}")

    # extract and compare property crime data
    property_crime_list = []
    property_crimes = crime_data['Property Crimes']
    for crime_name, crime_values in property_crimes.items():
        crime_value = crime_values['value']
        national_crime = crime_values['national']
        property_crime_list.append(
            f"{crime_name} index of {crime_value} compared to the national average of {national_crime}")

    return render_template("users/show_crime_data.html", v_crime=violent_crime_list, p_crime=property_crime_list)
