from app import db
import datetime
import utilities
from sqlalchemy.orm import relationship

##############
# User Model #
##############
ROLE_USER = 0
ROLE_ADMIN = 1

def create_test_posts(start_num, num):
    for i in range(start_num, num):
        num = str(i)
        post = Post(title = "test title " + num, content = "test content " + num, song_url = "http://www.google.com/test/url/" + num, timestamp = int(datetime.datetime.utcnow().strftime("%s")), author_id = 1)
        db.session.add(post)

        upvote = Upvote(voter_id = 1, post = post)
        db.session.add(upvote)

    db.session.commit()

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
    #num_upvotes = upvotes.count()

    #upvotes = db.relationship('Upvote', backref = 'author', lazy = 'dynamic')
    #posts = db.relationship('Post', backref = 'author', lazy = 'dynamic')

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def num_upvotes(self):
        num_upvotes = Upvote.query.filter(self.id == Upvote.post_author_id).count()
        return num_upvotes

    def get_id(self):
        return unicode(self.id)


    # Source: 
    @staticmethod
    def make_unique_nickname(nickname):
        if User.query.filter_by(nickname = nickname).first() == None:
            return nickname
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
    num_upvotes = db.Column(db.Integer, default = 1)
    upvotes = db.relationship('Upvote', backref = 'post', lazy = 'dynamic')
    stars = db.relationship('Star', backref = 'post', lazy = 'dynamic')
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    def is_upvoted_by(self, user_id):
        return self.upvotes.filter(Upvote.voter_id == user_id).count()

    def is_starred_by(self, user_id):
        return self.stars.filter(Star.user_id == user_id).count()

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
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Comment %r>' % (self.body)

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
    post_author_id = db.Column(db.Integer, db.ForeignKey('user.id'))