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

    def test_homepage(self):
        """Test login with valid credentials."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = c.get('/')
            self.assertEqual(resp.status_code, 200)

    def test_show_crime_data(self):

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = c.get('/atlanta-fulton-ga/Town/Atlanta')
            self.assertEqual(resp.status_code, 200)

    def test_user_account_actions(self):

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = c.get('/user_profile/1')
            self.assertEqual(resp.status_code, 200)

    def test_delete_user(self):

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = c.get('/delete_account')
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, '/signup')

            deleted_user = User.query.get(self.user1.id)
            self.assertIsNone(deleted_user)

    def test_delete_post(self):

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = c.get("/delete_post/1")
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'/user_profile/{self.user1.id}')

            post = Post.query.get(1)

            self.assertIsNone(post)

    def test_create_city_post(self):
        # Create a new post to add
        new_post = {
            "placeUrl": f"{self.place2.city_url}",
            "title": "test title",
            "content": "This is a test post"
        }

        # Log in as a user
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

                # Send a POST request to create a new post
            resp = c.post('/create/userpost', json=new_post)

            # Check that the response is successful and the post is added to the database
            self.assertEqual(resp.status_code, 201)
            self.assertIn("post", resp.json)

            # Retrieve the newly created post from the database
            post_id = resp.json["post"]["id"]
            post = Post.query.get(post_id)

            # Check that the post is stored correctly in the database
            self.assertEqual(post.title, new_post["title"])
            self.assertEqual(post.content, new_post["content"])
            self.assertEqual(post.place_city_url, new_post["placeUrl"])
            self.assertEqual(post.user_id, self.user1.id)

    def test_get_city_posts(self):

        # Make a request to the route using the post ID
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = c.get(f'/{self.post2.id}')
            data = resp.get_json()

            # Check that the response is successful
            self.assertEqual(resp.status_code, 200)

            # Check that the returned data matches the expected data
            self.assertEqual(data['post']['id'], self.post2.id)
            self.assertEqual(data['post']['title'], self.post2.title)
            self.assertEqual(data['post']['content'], self.post2.content)
            self.assertEqual(
                data['post']['place_city_url'], self.post2.place_city_url)
            self.assertEqual(data['post']['user_id'], self.post2.user_id)
            self.assertEqual(data['post']['created_at'],
                             self.post2.created_at.isoformat())
            self.assertEqual(data['post']['place']['city'], self.place2.city)
            self.assertEqual(data['post']['place']['state'], self.place2.state)
            self.assertEqual(data['post']['user']['id'], self.user2.id)
            self.assertEqual(data['post']['user']
                             ['username'], self.user2.username)
            self.assertEqual(data['post']['num_votes'], self.post2.num_votes)

    def test_handle_vote_post_req_upvote(self):

        # login the user
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user2.id

        # upvote the post
            resp = c.post('/post/upvote', json={"postId": self.post1.id})
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()

            self.assertTrue(data[0]["success"])
            self.assertEqual(data[0]["message"], "Post upvoted")
            self.assertEqual(data[0]["upvotes"], 1)

    def test_handle_vote_post_req_remove_vote(self):

        # login the user
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user2.id

            resp = c.post('/post/upvote', json={"postId": self.post1.id})
            self.assertEqual(resp.status_code, 200)

            # remove the upvote
            resp = c.post('/post/upvote', json={"postId": self.post1.id})
            self.assertEqual(resp.status_code, 200)
            data = resp.json
            self.assertTrue(data[0]["success"])
            self.assertEqual(data[0]["message"], "Vote removed")
            self.assertEqual(data[0]["upvotes"], 0)

    def test_handle_vote_post_req_user_likes_own_post(self):

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = c.post('/post/upvote', json={"postId": self.post1.id})
            self.assertEqual(resp.status_code, 200)
            data = resp.json
            self.assertEqual(data[0]["message"],
                             "User can't like their own post")
