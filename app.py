from flask import Flask, render_template, redirect, flash, request, session, g, jsonify, url_for
from sqlalchemy.exc import IntegrityError
from models import User, Post, Place, Vote, connect_db, db
from forms import CitySearchForm, EditUserForm, LoginForm, UserAddForm
from openAI_api import generate_ai_response
from places_api import crime_data_formulated, get_city_url, get_crime_data
from sqlalchemy import desc, func
import os
import time

# use code formatter


CURR_USER_KEY = "curr_user"

app = Flask(__name__,  static_url_path='/static')
app.testing = False


if __name__ == '__main__':
    app.run(debug=True)

app.config['TIMEOUT'] = 80


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


with app.app_context():
    connect_db(app)


@app.before_request
def add_user_to_g():
    """ If a user is logged in add current user to Flask global """

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""
    session.clear()

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """
    handle user signup.

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

        flash(f"Welcome, {user.username}")
        do_login(user)
        return redirect(url_for("homepage"))
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
            return redirect(url_for("homepage"))

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()

    flash("Goodbye!", "success")
    return redirect(url_for("login"))


@app.route('/', methods=["GET", "POST"])
def homepage():
    """
    Renders the homepage and handles a city search form submission for finding and displaying information about a city.

    HTTP Methods:
    - GET: Renders the homepage with a city search form.
    - POST: Handles form submission, validates the form, gets the city and state,
    gets the city URL and its type from an external API, and redirects to the city's page.

    Returns:
    If the user is not authenticated, redirects to the signup page.
    If the request method is GET, renders the homepage with a city search form.
    If the request method is POST and the form is valid, redirects to the city's page.
    If the request method is POST and the form is invalid, renders the homepage with the form and error message.
    """

    # put whole function defintion in a file called homepage
    # make routes folder with specific routes

    place_url = None
    city = None
    place_type = None
    city_state = None

    if g.user:

        form = CitySearchForm()

        if form.validate_on_submit():
            city = form.city.data
            state = form.state.data or ''
            city_state = city.capitalize() + " " + state
            place_url, place_type = get_city_url(city_state)

            existing_place = Place.query.filter_by(city_url=place_url).first()
            if existing_place:
                return redirect(url_for("show_crime_data", place_url=place_url, place_type=place_type, city_state=city_state))
            else:
                if place_url:
                    place = Place(city_url=place_url, city=city, state=state)
                    db.session.add(place)
                    db.session.commit()

                    return redirect(url_for("show_crime_data", place_url=place_url, place_type=place_type, city_state=city_state))
                else:
                    flash("Whoops there was an error. Try another search")

        return render_template("home.html", form=form, place_url=place_url, city=city, place_type=place_type, city_state=city_state)
    else:
        return redirect("/signup")


@app.route('/<place_url>/<place_type>/<city_state>', methods=["GET", "POST"])
def show_crime_data(place_url, place_type, city_state):
    """
    Show crime data for a given place.

    Args:
    - place_url (str): The url of the place.
    - place_type (str): The type of the place (e.g. city, town, etc.).
    - city (str): The name of the city.

    Returns:
    - A rendered template of the crime data page with information on violent and property crimes for the given place,
      as well as posts related to the place.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")

        return redirect("/")

    time.sleep(1)
    crime_data = get_crime_data(place_url, place_type)

    if "error" in crime_data:
        flash("Whoops there was an error. Try another search")
        return redirect("/")

    crimes = crime_data['crime-safety']
    violent_crime_list, property_crime_list = crime_data_formulated(
        crimes)

    session["crimes"] = crimes
    session["city"] = city_state

    posts = Post.query.filter_by(place_city_url=place_url).\
        outerjoin(Vote).group_by(Post.id).\
        order_by(desc(func.count(Vote.id))).all()

    return render_template("users/show_crime_data.html", posts=posts, place_url=place_url, city=city_state, v_crime=violent_crime_list, p_crime=property_crime_list)


@app.route("/user_profile/<int:user_id>", methods=["GET", "POST"])
def user_account_actions(user_id):
    """
    Show user account actions:

    Parameters:

    user_id : int
        The id of the user account to be shown.

    Returns:

    render_template: str
        The rendered template that shows the user's account information.

    """

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
    """
    Deletes the specified post and all associated votes from the database.

    If the user is not logged in, it will redirect to the home page.

    Args:
        post_id (int): The ID of the post to be deleted.

    Returns:
        A redirect to the user's profile page.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")

        return redirect("/")

    post = Post.query.get(post_id)
    Vote.query.filter_by(post_id=post_id).delete()
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted", "success")

    return redirect(f"/user_profile/{g.user.id}")


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

# API ENDPOINTS TO ACCESS DATA VIA FRONTEND ~~~~~~~~~~~~~~~~~~~~~ #

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

# make a seperate folder apis
# make routes /api/ name of route create more of a standard


@app.route('/create/userpost', methods=["GET", "POST"])
def create_city_post():
    """
    Create a new post for a city.

    HTTP Methods:
        - POST: Create a new post for a city.

    Returns:
        - Response (json): The created post in JSON format.

    Required Parameters:
        - placeUrl (str): The URL of the city where the post will be created.
        - title (str): The title of the post.
        - content (str): The content of the post.

    Authentication:
        - The user must be logged in to create a post.
    """

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
    """
    Retrieves a post by ID and returns it as a JSON object.

    Parameters:
    - post_id (int): The ID of the post to retrieve.

    Returns:
    - A JSON object representing the post, with the following keys:
        - id (int): The ID of the post.
        - title (str): The title of the post.
        - content (str): The content of the post.
        - place_city_url (str): The URL of the city associated with the post.
        - user_id (int): The ID of the user who created the post.
        - created_at (str): The creation date of the post in ISO format.
        - place (dict): A dictionary with keys "city" and "state" representing the city and state associated with the post.
        - user (dict): A dictionary with keys "id" and "username" representing the user who created the post.
        - num_votes (int): The number of votes received by the post.
    """

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
    """
    Handles the HTTP POST request for upvoting a post.

    Returns a JSON object containing a success message, the updated vote count, and a CSS class for the vote button.
    If the user has already upvoted the post, removes the upvote and returns a message indicating that the vote was removed.
    If the post was created by the same user, returns a message indicating that the user can't like their own post.

    Raises:
        404: If the post with the given ID does not exist.

    Returns:
        A JSON object with the following properties:
        - success: A boolean indicating whether the request was successful.
        - message: A string message indicating the result of the request.
        - upvotes: An integer representing the updated number of upvotes for the post.
        - class: A string representing the CSS class for the vote button.
        - post-id: An integer representing the ID of the post that was upvoted.
    """
    post_id = request.json["postId"]

    user = g.user
    post = Post.query.get_or_404(post_id)

    if post.user_id == g.user.id:
        data = {"message": "User can't like their own post",
                "class": "bg-gray-200 rounded", "post-id": post_id}, 200

        return jsonify(data)

    # if the post is in user's votes then remove the "vote"
    if post in user.votes:
        user.votes.remove(post)
        db.session.commit()
        vote_count = len(post.votes)
        data = {"success": True, "message": "Vote removed",
                "upvotes": vote_count, "class": "bg-gray-300 rounded", "post-id": post_id}, 200

        return jsonify(data)

    # else vote the post
    user.votes.append(post)
    db.session.commit()
    vote_count = len(post.votes)
    data = {"success": True, "message": "Post upvoted",
            "upvotes": vote_count, "class": "bg-emerald-300 rounded", "post-id": post_id}, 200

    return jsonify(data)


@app.route('/get/upvote', methods=['GET'])
def handle_vote_get_req():
    """
    Handles GET request to retrieve the number of upvotes for a specific post.

    Returns:
        A JSON object containing the number of upvotes for the post.
    """

    post_id = request.args.get("postId")
    post = Post.query.get_or_404(post_id)

    vote_count = len(post.votes)

    data = {"upvotes": vote_count}, 200
    return jsonify(data)


@app.route('/generate_ai', methods=["GET"])
def generate_ai():
    """
    Generates an AI response using crime data.

    Returns a JSON response containing the generated AI response.

    Query Parameters:
        - 'crimes' (string): The crime data for the city in question.
        - 'city' (string): The name of the city for which the crime data is provided.

    Session Variables:
        - 'crimes' (string): The crime data for the city in question.
        - 'city' (string): The name of the city for which the crime data is provided.

    Returns:
        - (json): A JSON response containing the generated AI response.
    """

    # get data from front end as post request

    crimes = session.get('crimes')
    city = session.get("city")

    # Check if there is new crime data and city information in the query string
    new_crimes = request.args.get("crimes")
    new_city = request.args.get("city")
    if new_crimes and new_city:
        crimes = new_crimes
        city = new_city
        session['crimes'] = crimes
        session['city'] = city

    violent_crime_list, property_crime_list = crime_data_formulated(
        crimes)

    ai_resp = generate_ai_response(
        violent_crime_list, property_crime_list, city)

    if crimes:
        # Only pop the old data if there is new data in the query string
        if new_crimes and new_city:
            session.pop("crimes")
            session.pop("city")
        response = jsonify(data=ai_resp)
        # Replace with your frontend origin
        response.headers.add('Access-Control-Allow-Origin',
                             'http://127.0.0.1:5500')
        return response

    return jsonify({'error': 'Crime data not found in session'})


@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req
