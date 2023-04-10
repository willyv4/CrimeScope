from turtle import pos
from app import app
import os
from sqlalchemy.exc import IntegrityError
from unittest import TestCase
from models import db, User, Place, Post, Vote


db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        user1 = User.signup("USER1",  "EMAIL@EMAIL.COM", "PASSWORD",)
        user2 = User.signup("USER2", "EMAIL@EMAIL.COM", "PASSWORD")

        p1 = Place(city_url="atlanta-fulton-ga",
                   city="Atlanta-Fulton", state="GA")

        db.session.add(p1)
        db.session.commit()

        post1 = Post(title="post",
                     content="test post", place_city_url="atlanta-fulton-ga", user_id=user2.id)

        db.session.add(post1)
        db.session.commit()

        self.user1 = user1
        self.user2 = user2
        self.p1 = p1
        self.post1 = post1

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_signup(self):

        user3 = User.signup("USER3",  "EMAIL@EMAIL.COM", "PASSWORD")
        db.session.commit()

        U3 = User.query.get(3)
        username = U3.username
        email = U3.email

        self.assertIsNotNone(U3)
        self.assertEqual("USER3", username)
        self.assertEqual("EMAIL@EMAIL.COM", email)

    def test_bad_signup(self):

        with self.assertRaises(IntegrityError):
            User.signup(username=self.user1.username, password="password",
                        email="email@test.com")
            db.session.commit()

    def test_user_authenticate(self):

        u = User.authenticate(self.user1.username, "PASSWORD")
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.user1.id)

    def test_invalid_username(self):
        self.assertFalse(User.authenticate("badusername", "password"))

    def test_wrong_password(self):
        self.assertFalse(User.authenticate(self.user1.username, "badpassword"))

    def test_create_place(self):

        p2 = Place(city_url="ivins-washington-ga", city="Ivins", state="UT")
        db.session.add(p2)
        db.session.commit()

        place = Place.query.filter_by(city="Ivins").first()

        self.assertEqual(place.city_url, "ivins-washington-ga")
        self.assertEqual(place.city, "Ivins")
        self.assertEqual(place.state, "UT")

    def test_post(self):

        post = Post(title="this is a post",
                    content="TESTTEST", place_city_url="atlanta-fulton-ga", user_id=self.user2.id)
        db.session.add(post)
        db.session.commit()

        self.assertIsNotNone(post)
        self.assertEqual(post.title, "this is a post")
        self.assertEqual(post.user_id, self.user2.id)
        self.assertEqual(post.content, "TESTTEST")

    def test_vote(self):

        post = Post.query.get(1)

        self.user1.votes.append(post)
        db.session.commit()

        vote = Vote.query.get(1)

        self.assertEqual(len(post.votes), 1)
        self.assertEqual(vote.user_id, self.user1.id)
