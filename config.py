import os
basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
SECRET_KEY = 'slf3jh234fsdf'
  
SQLALCHEMY_DATABASE_URI = 'postgresql://jharvard:crimson@localhost/cs50_project'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

POSTS_PER_PAGE = 10