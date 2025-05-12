"""Add user preferences table

Revision ID: a89b45f2d123
Revises: previous_revision
Create Date: 2023-06-05 13:45:23.487293

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a89b45f2d123'
down_revision = 'previous_revision'  # Replace with actual previous revision ID
branch_labels = None
depends_on = None


def upgrade():
    # Create user preferences table
    op.create_table('user_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=50), nullable=False),
        sa.Column('value', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'key', name='_user_preference_uc')
    )
    
    # Add index for faster lookups by user
    op.create_index('idx_user_preferences_user_id', 'user_preferences', ['user_id'], unique=False)
    
    # Add index for faster lookups by key
    op.create_index('idx_user_preferences_key', 'user_preferences', ['key'], unique=False)


def downgrade():
    # Drop user preferences table
    op.drop_index('idx_user_preferences_key', table_name='user_preferences')
    op.drop_index('idx_user_preferences_user_id', table_name='user_preferences')
    op.drop_table('user_preferences') 