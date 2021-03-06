# Copyright (C) 2013 Google Inc., authors, and contributors <see AUTHORS file>
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
# Created By: dan@reciprocitylabs.com
# Maintained By: dan@reciprocitylabs.com

"""Add context_id column for fulltext search

Revision ID: f36bd5f6b5d
Revises: 4b22d3a098c7
Create Date: 2013-06-20 17:35:22.446015

"""

# revision identifiers, used by Alembic.
revision = 'f36bd5f6b5d'
down_revision = '4b22d3a098c7'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('fulltext_record_properties', sa.Column('context_id', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('fulltext_record_properties', 'context_id')
    ### end Alembic commands ###
