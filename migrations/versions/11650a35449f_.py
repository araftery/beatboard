"""empty message

Revision ID: 11650a35449f
Revises: None
Create Date: 2013-11-29 00:50:49.238689

"""

# revision identifiers, used by Alembic.
revision = '11650a35449f'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table(u'migrate_version')
    op.drop_index('user_nickname_key', 'user')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_index('user_nickname_key', 'user', [u'nickname'], unique=True)
    op.create_table(u'migrate_version',
    sa.Column(u'repository_id', sa.VARCHAR(length=250), autoincrement=False, nullable=False),
    sa.Column(u'repository_path', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column(u'version', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint(u'repository_id', name=u'migrate_version_pkey')
    )
    ### end Alembic commands ###
