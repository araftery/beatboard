from flask import render_template, flash, redirect, session, url_for, request, g, jsonify
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid
from forms import LoginForm
from datetime import datetime
from forms import LoginForm, EditForm, PostForm
from models import User, ROLE_USER, ROLE_ADMIN, Post, Upvote, Star
from config import POSTS_PER_PAGE

##############
# Index view #
##############
@app.route('/', methods = ['GET'])
@app.route('/index', methods = ['GET'])
@app.route('/index/<int:page>', methods = ['GET'])
@login_required
def index(page = 1):
    posts = Post.query.outerjoin(Upvote).group_by(Post.id).order_by(db.func.count(Upvote.id).desc(), Post.timestamp.desc()).paginate(page, POSTS_PER_PAGE, False)
    return render_template('index.html',
        title = 'Home',
        posts = posts,
        posts_per_page = POSTS_PER_PAGE)

##################
# Login Handlers #
##################
@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/login', methods = ['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for = ['nickname', 'email'])
    return render_template('login.html', 
        title = 'Sign In',
        form = form,
        providers = app.config['OPENID_PROVIDERS'])

@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')
        return redirect(url_for('login'))
    user = User.query.filter_by(email = resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        nickname = User.make_unique_nickname(nickname)
        user = User(nickname = nickname, email = resp.email, role = ROLE_USER, time_registered = int(datetime.utcnow().strftime("%s")))
        db.session.add(user)
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember = remember_me)
    return redirect(request.args.get('next') or url_for('index'))

##################
# Before Request #
##################
@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated():
        g.user.last_seen = int(datetime.utcnow().strftime("%s"))
        db.session.add(g.user)
        db.session.commit()

##########
# Logout #
##########
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

#####################
# User Profile Page #
#####################
@app.route('/user/<nickname>/<int:page>')
@login_required
def user(nickname, page = 1):
    user = User.query.filter_by(nickname = nickname).first()
    if user == None:
        flash('User ' + nickname + ' not found.')
        return redirect(url_for('index'))
    posts = user.posts.paginate(page, POSTS_PER_PAGE, False)
    return render_template('user.html',
        user = user,
        posts = posts)

#####################
# Edit Profile Page #
#####################
@app.route('/edit', methods = ['GET', 'POST'])
@login_required
def edit():
    form = EditForm()
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit'))
    else:
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
        return render_template('edit.html', form = form)

###############
# Submit View #
###############
@app.route('/submit', methods = ['GET', 'POST'])
@app.route('/submit/<title>/<path:url>', methods = ['GET', 'POST'])
@login_required
def submit(title = '', url = ''):
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title = form.data['title'], content = form.data['content'], song_url = form.data['song_url'].lower(), timestamp = int(datetime.utcnow().strftime("%s")), author = g.user)
        db.session.add(post)

        upvote = Upvote(voter = g.user, post = post, post_author_id = post.author_id)
        db.session.add(upvote)

        db.session.commit()

        flash('Your post is now live!')
        return redirect(url_for('index'))
    else:
        return render_template('submit.html', form = form, title = title, url = url)

################
# Vote Handler #
################
@app.route('/vote/<int:post_id>/<int:upvoted>/<int:starred>', methods = ['GET'])
@login_required
def vote(post_id, upvoted, starred):
    if post_id == None or upvoted == None or starred == None:
        return jsonify({ 'error': 'data missing' })
    else:
        post = Post.query.filter(Post.id == post_id).first()
        existing_upvote = post.upvotes.filter(Upvote.voter_id == g.user.id).first()
        existing_star = post.stars.filter(Star.user_id == g.user.id).first()

        result_upvoted = 0
        result_star = 0

        if upvoted:
            # if this user has not already upvoted
            if existing_upvote is None:
                upvote = Upvote(post_id = post_id, voter_id = g.user.id)
                post.upvotes.append(upvote)
            
            result_upvoted = 1
        else:
            # if this user has already upvoted
            if existing_upvote is not None:
                post.upvotes.remove(existing_upvote)
            
            result_upvoted = 0

        if starred:
            # if this user has not already starred
            if existing_star is None:
                star = Star(post_id = post_id, user_id = g.user.id)
                post.stars.append(star)
            
            result_starred = 1
        else:
            # if this user has already starred
            if existing_star is not None:
                post.stars.remove(existing_star)

            result_starred = 0
        db.session.commit()
        return jsonify({'id': post_id, 'upvoted': result_upvoted, 'starred': result_starred})

@app.route('/test')
def test():
    return render_template('test.html')