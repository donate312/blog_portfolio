"""Add BlogPost model

Revision ID: f9ecb6cd8ece
Revises: 40a7301690c6
Create Date: 2025-04-19 03:34:36.553990

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f9ecb6cd8ece'
down_revision = '40a7301690c6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('blog_post')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('blog_post',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('title', sa.VARCHAR(length=150), nullable=False),
    sa.Column('content', sa.TEXT(), nullable=False),
    sa.Column('author', sa.VARCHAR(length=150), nullable=False),
    sa.Column('date_posted', sa.DATETIME(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
