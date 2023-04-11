import requests
from turtle import pos
from flask import Flask, render_template, redirect, flash, request, session, g, jsonify, url_for
from sqlalchemy.exc import IntegrityError
from models import User, Post, Place, Vote, connect_db, db
from forms import CitySearchForm, EditUserForm, LoginForm, UserAddForm
from openAI_api import generate_ai_response
from places_api import get_city_url, get_crime_data
from sqlalchemy import desc, func
import os
import time
import json


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

        flash(f"Welcome back {user.username}")
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

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()

    flash("Goodbye!", "success")
    return redirect('/login')


@app.route('/', methods=["GET", "POST"])
def homepage():
    """Show homepage:
    """
    place_url = None
    city = None
    place_type = None

    if g.user:

        form = CitySearchForm()

        if form.validate_on_submit():
            city = form.city.data
            state = form.state.data
            place = f"{city} {state}"
            place_url, place_type = get_city_url(place)

            existing_place = Place.query.filter_by(city_url=place_url).first()
            if existing_place:
                return redirect(f'/{place_url}/{place_type}/{city}')
            else:
                if place_url:
                    place = Place(city_url=place_url, city=city, state=state)
                    db.session.add(place)
                    db.session.commit()

                    time.sleep(1)
                    return redirect(f'/{place_url}/{place_type}/{city}')
                else:
                    print("cant find place!")
                    flash(
                        "Whoops, looks like that search didn't work try something else", "danger")

        return render_template("home.html", form=form, place_url=place_url, city=city, place_type=place_type)
    else:
        return render_template('home-anon.html')


@app.route('/<place_url>/<place_type>/<city>', methods=["GET", "POST"])
def show_crime_data(place_url, place_type, city):

    if not g.user:
        flash("Access unauthorized.", "danger")

        return redirect("/")

    time.sleep(1)
    crime_data = get_crime_data(place_url, place_type)

    crimes = crime_data['crime-safety']

    session["crimes"] = crimes
    session["city"] = city

    # extract and compare violent crime data
    violent_crime_list = []
    violent_crimes = crimes['Violent Crimes']
    for crime_name, crime_values in violent_crimes.items():
        crime_value = crime_values['value']
        national_crime = crime_values['national']
        violent_crime_list.append(
            f"{crime_name} index of {crime_value} compared to the national average of {national_crime}")

    # extract and compare property crime data
    property_crime_list = []
    property_crimes = crimes['Property Crimes']
    for crime_name, crime_values in property_crimes.items():
        crime_value = crime_values['value']
        national_crime = crime_values['national']
        property_crime_list.append(
            f"{crime_name} index of {crime_value} compared to the national average of {national_crime}")

    posts = Post.query.filter_by(place_city_url=place_url).\
        outerjoin(Vote).group_by(Post.id).\
        order_by(desc(func.count(Vote.id))).all()

    return render_template("users/show_crime_data.html", posts=posts, place_url=place_url, city=city, v_crime=violent_crime_list, p_crime=property_crime_list)


@app.route("/user_profile/<int:user_id>", methods=["GET", "POST"])
def user_account_actions(user_id):

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = g.user
    form = EditUserForm(obj=user)
    posts = Post.query.filter_by(user_id=user_id).all()

    if form.validate_on_submit():
        if User.authenticate(user.username, form.password.data):
            user.username = form.username.data
            user.email = form.email.data

            db.session.commit()
            return redirect(f"/user_profile/{user.id}")

        flash("Wrong password, please try again.", 'danger')
        return redirect(f"/user_profile/{user.id}")

    return render_template("/users/user_profile.html", posts=posts, user_id=user_id, form=form)


@app.route('/delete_account', methods=["GET", "POST"])
def delete_user():
    """Delete user."""

    if not g.user:
        flash("Access unauthorized.", "danger")

        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()
    flash("Account deleted succesfully", "success")

    return redirect("/signup")


@app.route('/delete_post/<int:post_id>', methods=["GET", "POST"])
def delete_post(post_id):

    if not g.user:
        flash("Access unauthorized.", "danger")

        return redirect("/")

    post = Post.query.get(post_id)
    Vote.query.filter_by(post_id=post_id).delete()
    db.session.delete(post)
    db.session.commit()
    flash("Post successfully delete", "success")

    return redirect(f"/user_profile/{g.user.id}")


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

# API ENDPOINTS TO ACCESS DATA VIA FRONTEND ~~~~~~~~~~~~~~~~~~~~~ #

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #


@app.route('/create/userpost', methods=["GET", "POST"])
def create_city_post():
    place_url = request.json["placeUrl"]
    title = request.json['title']
    content = request.json['content']

    if request.method == "POST":

        post = Post(title=title, content=content,
                    place_city_url=place_url, user_id=g.user.id)
        db.session.add(post)
        db.session.commit()
        resp = jsonify(post=post.serialize())
        return (resp, 201)


@app.route('/<int:post_id>', methods=['GET'])
def get_city_posts(post_id):

    post = Post.query.get_or_404(post_id)

    post_dict = {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "place_city_url": post.place_city_url,
        "user_id": post.user_id,
        "created_at": post.created_at.isoformat(),
        "place": {
            "city": post.place.city,
            "state": post.place.state
        },
        "user": {
            "id": post.user.id,
            "username": post.user.username
        },
        "num_votes": post.num_votes
    }

    return jsonify(post=post_dict)


@app.route('/post/upvote', methods=["POST"])
def handle_vote_post_req():
    post_id = request.json["postId"]

    user = g.user
    post = Post.query.get_or_404(post_id)

    if post.user_id == g.user.id:
        data = {"error": "User can't like their own post"}, 200
        return jsonify(data)

    # if the post is in user's likes then remove the "like"
    if post in user.votes:
        user.votes.remove(post)
        db.session.commit()
        vote_count = len(post.votes)
        data = {"success": True, "message": "vote removed",
                "upvotes": vote_count}, 200
        return jsonify(data)

    # else like the post
    user.votes.append(post)
    db.session.commit()
    vote_count = len(post.votes)
    data = {"success": True, "message": "post upvoted",
            "upvotes": vote_count}, 200

    return jsonify(data)


@app.route('/get/upvote', methods=['GET'])
def handle_vote_get_req():
    post_id = request.args.get("postId")
    post = Post.query.get_or_404(post_id)

    vote_count = len(post.votes)

    data = {"upvotes": vote_count}, 200
    return jsonify(data)


@app.route('/get_crime_data', methods=["GET"])
def get_crimes():
    crimes = session.get('crimes')
    city = session.get("city")
    ai_resp = generate_ai_response(crimes, city)

    if crimes:
        session.pop("crimes")
        session.pop("city")
        return jsonify(data=ai_resp)

    return jsonify({'error': 'Crime data not found in session'})
