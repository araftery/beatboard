from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
post = Table('post', pre_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('title', String),
    Column('content', String),
    Column('song_url', String),
    Column('timestamp', Integer),
    Column('author_id', Integer),
    Column('upvotes', Integer),
)

post = Table('post', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('title', String(length=250)),
    Column('content', String(length=5000)),
    Column('song_url', String(length=2000)),
    Column('timestamp', Integer),
    Column('author_id', Integer),
    Column('num_upvotes', Integer, default=ColumnDefault(1)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['post'].columns['upvotes'].drop()
    post_meta.tables['post'].columns['num_upvotes'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['post'].columns['upvotes'].create()
    post_meta.tables['post'].columns['num_upvotes'].drop()
