from turtle import pos
from app import app, CURR_USER_KEY
import os
from sqlalchemy.exc import IntegrityError
from unittest import TestCase
from models import db, User, Place, Post, Vote
from forms import UserAddForm

db.drop_all()
db.create_all()


class UserViews(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        # Add fake users
        user1 = User.signup(
            username='user1',
            password='password1',
            email='user1@example.com',
        )
        user2 = User.signup(
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

    def test_create_post_and_post_views(self):
        # Log in as a user
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

        # Create a new post
        new_post = {
            "placeUrl": "atlanta-fulton-ga",
            "title": "Test post",
            "content": "This is a test post"
        }

        resp = c.post("/create/userpost", json=new_post)
        self.assertEqual(resp.status_code, 201)
        self.assertIn(b'"place_city_url": "atlanta-fulton-ga"', resp.data)

        # Check that the new post appears on the homepage
        resp = self.client.get("/atlanta-fulton-ga/Town/atlanta")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Test post", resp.data)
        self.assertIn(b"This is a test post", resp.data)

        # check that user's post is on account page
        resp = c.post(f"/user_profile/{self.user1.id}")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Test post", resp.data)
        self.assertIn(b"This is a test post", resp.data)

        # check that user post is not on
        resp = c.post("/delete_post/3")
        self.assertEqual(resp.status_code, 302)
        self.assertNotIn(b"Test post", resp.data)
        self.assertNotIn(b"This is a test post", resp.data)

        resp = c.post(f"/user_profile/{self.user1.id}")
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn(b"Test post", resp.data)
        self.assertNotIn(b"This is a test post", resp.data)
        post = Post.query.get(3)
        self.assertIsNone(post)
