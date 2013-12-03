from app import app, db
from app.models import Post, User, Upvote, Star, Comment

posts = Post.query.all()
users = User.query.all()
upvotes = Upvote.query.all()
stars = Star.query.all()
comments = Comment.query.all()

for post in posts:
	db.session.delete(post)

for user in users:
	db.session.delete(user)

for upvote in upvotes:
	db.session.delete(upvote)

for star in stars:
	db.session.delete(star)

for comment in comments:
	db.session.delete(comment)

db.session.commit()