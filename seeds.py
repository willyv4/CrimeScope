from app import db
from models import User, Place, Post, Vote

db.drop_all()
db.create_all()

# Three fake users
user1 = User.signup(username="johnsmith", password="password123",
                    email="johnsmith@example.com")
user2 = User.signup(username="janesmith", password="12345password",
                    email="janesmith@example.com")
user3 = User.signup(username="bobross", password="happytrees",
                    email="bobross@example.com")

db.session.commit()

#
#
#

p1 = Place(city_url="new-york-ny", city="New York", state="NY")
p2 = Place(city_url="los-angeles-ca", city="Los Angeles", state="CA")
p3 = Place(city_url="chicago-il", city="Chicago", state="IL")
p4 = Place(city_url="miami-fl", city="Miami", state="FL")
p5 = Place(city_url="seattle-wa", city="Seattle", state="WA")

db.session.add_all([p1, p2, p3, p4, p5])

#
#
#

u1 = User.query.get(1)
u2 = User.query.get(2)
u3 = User.query.get(3)

# Create 2 posts for each user
post1 = Post(title="My first post", content="Hello world!",
             place_city_url="new-york-ny", user_id=u1.id)
post2 = Post(title="My second post", content="Goodbye world!",
             place_city_url="new-york-ny", user_id=u1.id)

post3 = Post(title="First post in LA", content="LA is awesome!",
             place_city_url="los-angeles-ca", user_id=u2.id)
post4 = Post(title="Second post in LA", content="LA is crowded!",
             place_city_url="los-angeles-ca", user_id=u2.id)

post5 = Post(title="Chicago deep dish pizza", content="The best pizza in the world!",
             place_city_url="chicago-il", user_id=u3.id)
post6 = Post(title="Chicago hot dog", content="Mustard, relish, onions, tomato, and a pickle on a poppy seed bun!",
             place_city_url="chicago-il", user_id=u3.id)

db.session.add_all([post1, post2, post3, post4, post5, post6])

post = Post.query.get(1)

for user in User.query.all():
    vote = Vote(post_id=post.id, user_id=user.id)
    db.session.add(vote)

db.session.commit()
