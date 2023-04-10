from app import app, CURR_USER_KEY
from sqlalchemy.exc import IntegrityError
from unittest import TestCase
from models import db, User, Place, Post, Vote


db.create_all()


class UserViews(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        # Add fake users
        user1 = User(
            username='user1',
            password='password1',
            email='user1@example.com',
        )
        user2 = User(
            username='user2',
            password='password2',
            email='user2@example.com',
        )
        db.session.add_all([user1, user2])
        db.session.commit()

        # Add fake places
        place1 = Place(
            city_url='atlanta-fulton-ga',
            city='Atlanta',
            state='GA',
        )
        place2 = Place(
            city_url='new-york-ny',
            city='New York',
            state='NY',
        )
        db.session.add_all([place1, place2])
        db.session.commit()

        # Add fake posts
        post1 = Post(
            title='Post 1',
            content='Content of post 1',
            user_id=user1.id,
            place_city_url=place1.city_url,
        )
        post2 = Post(
            title='Post 2',
            content='Content of post 2',
            user_id=user2.id,
            place_city_url=place2.city_url,
        )
        db.session.add_all([post1, post2])
        db.session.commit()

        self.client = app.test_client()

        self.user1 = user1
        self.user2 = user2
        self.place1 = place1
        self.place2 = place2
        self.post1 = post1
        self.post2 = post2

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_logout(self):
        """Test login with valid credentials."""

        # Make a POST request to the login route with valid credentials
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = c.get("/logout")
            self.assertEqual(resp.status_code, 302)
            self.assertIn(
                b'<a href="/login">/login</a>', resp.data)

    def test_homepage(self):
        """Test login with valid credentials."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = c.get('/')
            self.assertEqual(resp.status_code, 200)

            self.assertIn(
                b'<label for="state-input">State</label>', resp.data)

    def test_show_crime_data(self):

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = c.get('/atlanta-fulton-ga/Town/Atlanta')
            self.assertEqual(resp.status_code, 200)

            self.assertIn(
                b'<form method="POST" class="vote-form" >\n        <input type="hidden" id="vote-id" name="vote-id" value="1" />', resp.data)
