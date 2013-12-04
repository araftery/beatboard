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
@app.route('/', methods = ['GET', 'POST'])
@app.route('/index', methods = ['GET', 'POST'])
@app.route('/index/<int:page>', methods = ['GET', 'POST'])
@login_required
def index(page = 1):
    posts = Post.query.outerjoin(Upvote).group_by(Post.id).order_by(db.func.count(Upvote.id).desc(), Post.timestamp.desc()).paginate(page, POSTS_PER_PAGE, False)

    if request.method == 'GET':
        return render_template('first.html',
            method = request.method,
            template_to_load = 'index.html',
            title = 'Home',
            posts = posts,
            posts_per_page = POSTS_PER_PAGE)
    else:
        return render_template('index.html',
            method = request.method,
            title = 'Home',
            posts = posts,
            posts_per_page = POSTS_PER_PAGE)



##############
# New view #
##############
@app.route('/new', methods = ['GET', 'POST'])
@login_required
def new(page = 1):
    posts = Post.query.outerjoin(Upvote).group_by(Post.id).order_by(Post.timestamp.desc()).paginate(page, POSTS_PER_PAGE, False)
    if request.method == 'GET':
        return render_template('first.html', method = request.method, template_to_load = 'new.html', title = 'New', posts = posts, posts_per_page = POSTS_PER_PAGE)
    else:
        return render_template('new.html', method = request.method, title = 'New', posts = posts, posts_per_page = POSTS_PER_PAGE)


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
        flash('Invalid login. Please try again.', 'danger')
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
@app.route('/user/<nickname>/<int:page>', methods = ['GET', 'POST'])
@app.route('/user/<nickname>', methods = ['GET', 'POST'])
@login_required
def user(nickname, page = 1):
    user = User.query.filter_by(nickname = nickname).first()
    if user == None:
        flash('User ' + nickname + ' not found.', 'danger')
        return redirect(url_for('index'), code=307)

    posts = Post.query.outerjoin(Upvote).group_by(Post.id).filter(Post.author_id == user.id).order_by(Post.timestamp.desc()).paginate(page, POSTS_PER_PAGE, False)

    if request.method == 'GET':
        return render_template('first.html',
            template_to_load = 'user.html',
            user = user,
            no_show_rank = True,
            posts = posts)
    else:
        return render_template('user.html',
            user = user,
            no_show_rank = True,
            posts = posts)

#####################
# Edit Profile Page #
#####################
@app.route('/edit', methods = ['POST'])
@login_required
def edit():
    form = EditForm()
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash('Your changes have been saved.', 'success')
        return redirect(url_for('user', nickname = g.user.nickname), code=307)
#    else:
#      form.nickname.data = g.user.nickname
#        form.about_me.data = g.user.about_me
#        return render_template('edit.html', form = form)



##########
# Search #
##########
@app.route('/search/<query>/<int:page>', methods = ['GET', 'POST'])
@app.route('/search/<query>', methods = ['GET', 'POST'])
@login_required
def search(query = '', page = 1):
        if query == '':
            flash('Sorry, you cannot enter a blank search query.', 'danger')
            if request.method == 'GET':
                return redirect(url_for('index'), code=307)
            else:
                return redirect(url_for('index'), code=307)
        query_show = query
        query = '%{0}%'.format(query)
        posts = Post.query.outerjoin(Upvote).group_by(Post.id).filter(Post.title.ilike(query)).order_by(db.func.count(Upvote.id).desc(), Post.timestamp.desc()).paginate(page, POSTS_PER_PAGE, False)
        
        if request.method == 'GET':
            return render_template('first.html',
                template_to_load = 'search.html',
                no_show_rank = True,
                posts = posts,
                query = query_show,
                page = page,
                posts_per_page = POSTS_PER_PAGE)
        else:
            return render_template('search.html',
                no_show_rank = True,
                posts = posts,
                query = query_show,
                page = page,
                posts_per_page = POSTS_PER_PAGE)  




###############
# Submit View #
###############
@app.route('/submit', methods = ['GET', 'POST'])
@app.route('/submit/<title>/<path:url>', methods = ['GET', 'POST'])
@login_required
def submit(title = '', url = ''):
    if (url.find('://') == -1):
        if (url.find('https') == -1):
            url = url.replace('http:/', 'http://')
        else:
            url = url.replace('https:/', 'https://')
            
    form = PostForm()
    
    if form.validate_on_submit():
        existing_post = Post.query.filter(Post.song_url.ilike('%{0}%'.format(form.data['song_url']))).first()
        if (existing_post is not None):
            if not existing_post.is_upvoted_by(g.user.id):
                upvote = Upvote(voter = g.user, post_id = existing_post.id)
                db.session.add(upvote)
                db.session.commit()

                flash("A duplicate post exists. An upvote has automatically been added to the post.", 'info')
                return redirect(url_for('index'), code=307)
            else:
                flash("You have already upvoted a duplicate post.", 'danger')
                return redirect(url_for('index'), code=307)
        else:
            post = Post(title = form.data['title'], content = form.data['content'], song_url = form.data['song_url'], timestamp = int(datetime.utcnow().strftime("%s")), author = g.user)
            db.session.add(post)

            upvote = Upvote(voter = g.user, post = post)
            db.session.add(upvote)

            db.session.commit()

            flash('Your post is now live!', 'success')
            return redirect(url_for('index'), code=307)
    elif request.method == 'GET':
        return render_template('first.html', template_to_load = 'submit.html', form = form, title = title, url = url)
    else:

        # if it was POST, but not a submit, don't show errors
        try:
            if form.data['submitted_field'] == 'true':
                hide_errors = False
            else:
                hide_errors = True
        except KeyError:
            hide_errors = True

        return render_template('submit.html', form = form, title = title, url = url, hide_errors = hide_errors)


################
# Vote Handler #
################
@app.route('/vote/<int:post_id>/<int:upvoted>/<int:starred>', methods = ['GET', 'POST'])
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
                db.session.delete(existing_upvote)
            
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
                db.session.delete(existing_star)

            result_starred = 0
        db.session.commit()
        return jsonify({'id': post_id, 'upvoted': result_upvoted, 'starred': result_starred})

@app.route('/comments/<int:post_id>', methods = ['GET', 'POST'])
@login_required
def comments(post_id):
    post = Post.query.get(post_id)
    if request.method == 'GET':
        return render_template('first.html', template_to_load = 'comments.html', post = post)
    else:
        return render_template('comments.html', post = post)