from flask import render_template, flash, redirect, session, url_for, request, g, jsonify
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid
from forms import *
from models import *
from config import POSTS_PER_PAGE
import pprint
import collections

##
# Helper function that selects the top x posts
##

def select_top(limit = None):
    posts = Post.query.outerjoin(Upvote).group_by(Post.id).order_by(db.func.count(Upvote.id).desc(), Post.timestamp.desc())

    if limit != None:
        posts = posts.limit(limit)

    return posts

####################
# Index Controller #
####################

@app.route('/', methods = ['GET', 'POST'])
@app.route('/index', methods = ['GET', 'POST'])
@app.route('/index/<int:page>', methods = ['GET', 'POST'])
def index(page = 1):

    # get the posts ordered by upvotes, and paginate them
    posts = select_top()
    posts = posts.paginate(page, POSTS_PER_PAGE, False)

    # check the request type and render accordingly
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



##################
# New Controller #
##################
@app.route('/new', methods = ['GET', 'POST'])
def new(page = 1):

    # get the posts in order of age, ascending (i.e., time posted descending), and paginate them
    posts = Post.query.outerjoin(Upvote).group_by(Post.id).order_by(Post.timestamp.desc()).paginate(page, POSTS_PER_PAGE, False)
    
    # check the request type and render accordingly
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

    # if the user is already authenticated, load the homepage and skip the login page
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'), code=307)

    # load the login WTForm
    form = LoginForm()

    # if the form was submitted, validate submission and try to login using OpenID
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for = ['nickname', 'email'])

    # otherwise, the user needs to be shown the login form
    # check the request type and render accordingly
    if request.method == 'GET':
        return render_template('first.html',
            template_to_load = 'login.html', 
            title = 'Sign In',
            form = form,
            providers = app.config['OPENID_PROVIDERS'])
    else:
        return render_template('login.html',
            title = 'Sign In',
            form = form,
            providers = app.config['OPENID_PROVIDERS'])

# runs after the user has logged in with an OpenID provider
@oid.after_login
def after_login(resp):

    # validate the information given by the OpenID provider
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.', 'danger')
        return redirect(url_for('login'), code=307)

    # check to see if this is uer is in the database
    user = User.query.filter_by(email = resp.email).first()

    # if not, create a record for them
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        
        # make sure the nickname is unique
        nickname = User.make_unique_nickname(nickname)
        
        # insert into db
        user = User(nickname = nickname, email = resp.email, role = ROLE_USER, time_registered = int(datetime.datetime.utcnow().strftime("%s")))
        db.session.add(user)
        db.session.commit()

    # check to see if remember me is set, and handle accordingly
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember = remember_me)

    # the user is all set, so load the page originally requested, or load the index page
    return redirect(request.args.get('next') or url_for('index'), code=307)


##
# Runs before every request
##
@app.before_request
def before_request():

    # set the user in a global variable and update the last_seen time
    g.user = current_user
    if g.user.is_authenticated():
        g.user.last_seen = int(datetime.datetime.utcnow().strftime("%s"))
        db.session.add(g.user)
        db.session.commit()

    # get the top 20 posts from a SoundCloud domain and put into a string
    # this essentially creates a default playlist for the stratus player
    # that will play if a selected song by the user ends
    posts = Post.query.outerjoin(Upvote).group_by(Post.id).filter(Post.song_url.ilike('%soundcloud.com%')).order_by(db.func.count(Upvote.id).desc(), Post.timestamp.desc()).limit(20)
    post_string = ''
    for (index, post) in enumerate(posts):
        if index == 0:
            post_string += post.song_url
        else:
            post_string += ',' + post.song_url
    g.top_20_list = post_string


##########
# Logout #
##########
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

################################
# User Profile Page Controller #
################################
@app.route('/user/<nickname>/<page_name>/<int:page>', methods = ['GET', 'POST'])
@app.route('/user/<nickname>/<page_name>/<int:page>', methods = ['GET', 'POST'])
@app.route('/user/<nickname>/<page_name>', methods = ['GET', 'POST'])
@app.route('/user/<nickname>', methods = ['GET', 'POST'])
def user(nickname, page_name = 'none', page = 1):
    
    # get the requested user from db
    user = User.query.filter_by(nickname = nickname).first()
    if user == None:
        flash('User ' + nickname + ' not found.', 'danger')
        return redirect(url_for('index'), code=307)

    posts = None

    # if the page is set to posts, get and display the user's posts
    # if favorites, get and show their favorites
    if page_name == 'posts':
        posts = Post.query.outerjoin(Upvote).group_by(Post.id).filter(Post.author_id == user.id).order_by(Post.timestamp.desc()).paginate(page, POSTS_PER_PAGE, False)
    elif page_name == 'favorites':
        posts = Post.query.outerjoin(Star).group_by(Post.id).filter(Star.user_id == user.id).order_by(Post.timestamp.desc()).paginate(page, POSTS_PER_PAGE, False)

    if request.method == 'GET':
        return render_template('first.html',
            template_to_load = 'user.html',
            user = user,
            no_show_rank = True,
            posts = posts,
            page_name = page_name)
    else:
        return render_template('user.html',
            user = user,
            no_show_rank = True,
            posts = posts,
            page_name = page_name)

#####################
# Search Controller #
#####################
@app.route('/search/<query>/<int:page>', methods = ['GET', 'POST'])
@app.route('/search/<query>', methods = ['GET', 'POST'])
def search(query = '', page = 1):

        # validate input
        if query == '':
            flash('Sorry, you cannot enter a blank search query.', 'danger')
            if request.method == 'GET':
                return redirect(url_for('index'), code=307)
            else:
                return redirect(url_for('index'), code=307)
        query_show = query
        query = '%{0}%'.format(query)
        
        # search using a wildcard ilike query (basically, searches for titles that contain the query, case-insensitive)
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




#####################
# Submit Controller #
#####################
@app.route('/submit', methods = ['GET', 'POST'])
@app.route('/submit/<title>/<path:url>', methods = ['GET', 'POST'])
@login_required
def submit(title = '', url = ''):

    # fixes bookmarklet glitch where the protocol is reported
    # with one rather than two slashes
    if (url.find('://') == -1):
        if (url.find('https') == -1):
            url = url.replace('http:/', 'http://')
        else:
            url = url.replace('https:/', 'https://')
    
    # initialize the submit form
    form = PostForm()
    
    # if it was submitted, validate
    if form.validate_on_submit():

        # make sure the song wasn't already submitted
        existing_post = Post.query.filter(Post.song_url.ilike('%{0}%'.format(form.data['song_url']))).first()
        if (existing_post is not None):
            # if it has been submitted, upvote the existing instance as long as the current user
            # has not already upvoted that instance
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
            # otherwise, insert the post into the database
            post = Post(title = form.data['title'], content = form.data['content'], song_url = form.data['song_url'], timestamp = int(datetime.datetime.utcnow().strftime("%s")), author = g.user)
            db.session.add(post)

            upvote = Upvote(voter = g.user, post = post)
            db.session.add(upvote)

            db.session.commit()

            flash('Your post is now live!', 'success')
            return redirect(url_for('index'), code=307)

    elif request.method == 'GET':
        # if the request method was GET, load the submit form
        return render_template('first.html', template_to_load = 'submit.html', form = form, title = title, url = url)
    else:

        # if it was POST, but not a submit, don't show errors, and show the submit form
        try:
            if form.data['submitted_field'] == 'true':
                hide_errors = False
            else:
                hide_errors = True
        except KeyError:
            hide_errors = True

        return render_template('submit.html', form = form, title = title, url = url, hide_errors = hide_errors)


###################
# Vote Controller #
###################
@app.route('/vote/<int:post_id>/<int:upvoted>/<int:starred>', methods = ['GET', 'POST'])
@login_required
def vote(post_id, upvoted, starred):
    # takes AJAX requests from the upvote and star buttons next to posts

    if post_id == None or upvoted == None or starred == None:
        return jsonify({ 'error': 'data missing' })
    else:
        # get the post id, and check if the user has already upvoted to starred it
        post = Post.query.filter(Post.id == post_id).first()
        existing_upvote = post.upvotes.filter(Upvote.voter_id == g.user.id).first()
        existing_star = post.stars.filter(Star.user_id == g.user.id).first()

        result_upvoted = 0
        result_star = 0

        if upvoted:
            # if this user has not already upvoted, add an upvote
            if existing_upvote is None:
                upvote = Upvote(post_id = post_id, voter_id = g.user.id)
                post.upvotes.append(upvote)
            
            result_upvoted = 1
        else:
            # if this user has already upvoted, delete it
            if existing_upvote is not None:
                db.session.delete(existing_upvote)
            
            result_upvoted = 0

        if starred:
            # if this user has not already starred, add one
            if existing_star is None:
                star = Star(post_id = post_id, user_id = g.user.id)
                post.stars.append(star)
            
            result_starred = 1
        else:
            # if this user has already starred, delete it
            if existing_star is not None:
                db.session.delete(existing_star)

            result_starred = 0
        db.session.commit()
        return jsonify({'id': post_id, 'upvoted': result_upvoted, 'starred': result_starred})

##
# Builds the comment tree of a thread recursively given the root comment
##
def build_comment_tree(root):
    current_tree = {'root': root, 'children': []}

    # get children
    children = Comment.query.filter(Comment.parent_id == root.id).order_by(Comment.id.asc()).all()
    
    for child in children:
        current_tree['children'].append(build_comment_tree(child))

    return current_tree

#######################
# Comments Controller #
#######################
@app.route('/comments/<int:post_id>', methods = ['GET', 'POST'])
def comments(post_id):
    post = Post.query.get(post_id)

    # get root nodes
    roots = Comment.query.filter(Comment.post_id == post_id, Comment.parent_id == 0).order_by(Comment.id.asc()).all()
    comments = []
    
    # for each root node, build its comment tree
    for root in roots:
        comments.append(build_comment_tree(root))

    if request.method == 'GET':
        return render_template('first.html', template_to_load = 'comments.html', post = post, threads = comments)
    else:
        # if it was POST, but not a submit, don't show errors
        try:
            # verify input
            if request.form['comment'] == '' or request.form['parent_id'] == '' or not g.user.is_authenticated():
                    if not g.user.is_authenticated():
                        flash('You must be logged in to post a comment!', 'danger')
                        return redirect(url_for('login', code=307))
                    else:
                        flash('You left a field blank!', 'danger')
                        return render_template('comments.html', post = post, threads = comments)
            else:
                # post comment
                comment = Comment(post_id = post.id, parent_id = request.form['parent_id'], author = g.user, timestamp = int(datetime.datetime.utcnow().strftime("%s")), content = request.form['comment'])
                db.session.add(comment)
                db.session.commit()
                flash('Your comment has been posted!', 'success')
                roots = Comment.query.filter(Comment.post_id == post_id, Comment.parent_id == 0).order_by(Comment.id.asc()).all()
                comments = []

                # rebuild the comment threads with the new comment inserted
                for root in roots:
                    comments.append(build_comment_tree(root))
                return render_template('comments.html', post = post, threads = comments)
        except:
            pass

        return render_template('comments.html', post = post, threads = comments)