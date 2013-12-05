import os
basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

OPENID_PROVIDERS = [
    { 'name': 'Google', 'url': 'https://www.google.com/accounts/o8/id', 'imgsrc': '/static/img/signin_google.png' },
    { 'name': 'Yahoo', 'url': 'https://me.yahoo.com', 'imgsrc': '/static/img/signin_yahoo.png' },
    { 'name': 'AOL', 'url': 'http://openid.aol.com/<username>', 'imgsrc': '/static/img/signin_aol.png' }]
    
SQLALCHEMY_DATABASE_URI = 'postgresql://jharvard:crimson@localhost/cs50_project'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

POSTS_PER_PAGE = 10