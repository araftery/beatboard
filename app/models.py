from app import db
import datetime
import utilities
from sqlalchemy.orm import relationship
from hashlib import md5

# constants for the number that denotes different user types
# for support for a potential future admin panel 
ROLE_USER = 0
ROLE_ADMIN = 1

##############
# User Model #
##############
class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nickname = db.Column(db.String(64), unique = True)
    email = db.Column(db.String(120), index = True, unique = True)
    role = db.Column(db.SmallInteger, default = ROLE_USER)
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.Integer)
    time_registered = db.Column(db.Integer)
    posts = db.relationship('Post', backref = 'author', lazy = 'dynamic')
    stars = db.relationship('Star', backref = 'user', lazy = 'dynamic')
    upvote = db.relationship('Upvote', backref = 'voter', lazy = 'dynamic')
    comments  = db.relationship('Comment', backref='author', lazy = 'dynamic')

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    ##
    # Gets number of upvotes on the user's posts
    ##
    def num_upvotes(self):
        num_upvotes = 0
        for post in self.posts:
            num_upvotes += post.upvotes.count()
        return num_upvotes

    ##
    # Average upvotes per post for user
    ##
    def avg_karma(self):
        return round(self.num_upvotes()/self.posts.count(), 2)

    def get_id(self):
        return unicode(self.id)

    ##
    # Get the user's avatar from Gravatar
    ##
    def avatar(self, size):
        return 'https://s.gravatar.com/avatar/' + md5(self.email).hexdigest() + '?d=mm&s=' + str(size)

    ##
    # Creates a unique nickname for the user
    # Source: http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-vii-unit-testing
    ##
    @staticmethod
    def make_unique_nickname(nickname):

        # if the nickname is already unique, just return it
        if User.query.filter_by(nickname = nickname).first() == None:
            return nickname

        # otherwise, append a 2 and check, and continuing incrementing and checking until a unique nickname is found
        version = 2
        while True:
            new_nickname = nickname + str(version)
            if User.query.filter_by(nickname = new_nickname).first() == None:
                break
            version += 1
        return new_nickname

    def __repr__(self):
        return '<User %r>' % (self.nickname)


##############
# Post Model #
##############
class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(250))
    content = db.Column(db.String(5000))
    song_url = db.Column(db.String(2000))
    timestamp = db.Column(db.Integer)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    upvotes = db.relationship('Upvote', backref = 'post', lazy = 'dynamic')
    stars = db.relationship('Star', backref = 'post', lazy = 'dynamic')
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    ##
    # checks to see if the post is upvoted by a given user
    ##
    def is_upvoted_by(self, user_id):
        if self.upvotes.filter(Upvote.voter_id == user_id).count() > 0:
            return 1
        else:
            return 0
    ##
    # checks to see if the post is starred by a given user
    ##
    def is_starred_by(self, user_id):
        if self.stars.filter(Star.user_id == user_id).count() > 0:
            return 1
        else:
            return 0

    def __repr__(self):
        return '<Post %r>' % (self.id)

##################
# Comments Model #
##################
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.String(5000))
    timestamp = db.Column(db.Integer)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    parent_id = db.Column(db.Integer)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Comment %r>' % (self.content)

###############
# Stars Model #
###############
class Star(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

#################
# Upvotes Model #
#################
class Upvote(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    voter_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))