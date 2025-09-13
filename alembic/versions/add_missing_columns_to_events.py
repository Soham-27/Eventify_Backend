"""add default_price and is_active columns to events

Revision ID: add_missing_columns
Revises: c2ec76179934
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_missing_columns'
down_revision = 'c2ec76179934'
branch_labels = None
depends_on = None


def upgrade():
    # Step 1: Add default_price column as nullable first
    op.add_column('events', sa.Column('default_price', sa.Integer(), nullable=True))
    
    # Step 2: Update all existing rows to have default_price = 100 (or any default value)
    op.execute("UPDATE events SET default_price = 100 WHERE default_price IS NULL")
    
    # Step 3: Make default_price NOT NULL
    op.alter_column('events', 'default_price', nullable=False)
    
    # Step 4: Add is_active column as nullable first
    op.add_column('events', sa.Column('is_active', sa.Boolean(), nullable=True))
    
    # Step 5: Update all existing rows to have is_active = True
    op.execute("UPDATE events SET is_active = true WHERE is_active IS NULL")
    
    # Step 6: Make is_active NOT NULL
    op.alter_column('events', 'is_active', nullable=False)


def downgrade():
    op.drop_column('events', 'is_active')
    op.drop_column('events', 'default_price')
