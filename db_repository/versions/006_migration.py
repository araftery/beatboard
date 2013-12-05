from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
upvote = Table('upvote', pre_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('voter_id', Integer),
    Column('post_id', Integer),
    Column('post_author_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['upvote'].columns['post_author_id'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['upvote'].columns['post_author_id'].create()
