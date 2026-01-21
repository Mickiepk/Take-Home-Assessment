"""Initial migration: create sessions and messages tables

Revision ID: f3665c33c3a6
Revises: 
Create Date: 2026-01-21 16:11:32.155145

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f3665c33c3a6'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create sessions table
    op.create_table(
        'sessions',
        sa.Column('session_id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('status', sa.String(20), default='active', nullable=False),
        sa.Column('worker_id', sa.String(255), nullable=True),
        sa.Column('vnc_port', sa.Integer, nullable=True),
        sa.Column('session_metadata', sa.JSON, default=dict, nullable=False),
    )
    
    # Create indexes for sessions table
    op.create_index('ix_sessions_session_id', 'sessions', ['session_id'])
    op.create_index('ix_sessions_status', 'sessions', ['status'])
    
    # Create messages table
    op.create_table(
        'messages',
        sa.Column('message_id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('session_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('message_metadata', sa.JSON, default=dict, nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.session_id'], ondelete='CASCADE'),
    )
    
    # Create indexes for messages table
    op.create_index('ix_messages_message_id', 'messages', ['message_id'])
    op.create_index('ix_messages_session_id', 'messages', ['session_id'])
    op.create_index('ix_messages_role', 'messages', ['role'])
    op.create_index('ix_messages_timestamp', 'messages', ['timestamp'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index('ix_messages_timestamp', 'messages')
    op.drop_index('ix_messages_role', 'messages')
    op.drop_index('ix_messages_session_id', 'messages')
    op.drop_index('ix_messages_message_id', 'messages')
    op.drop_index('ix_sessions_status', 'sessions')
    op.drop_index('ix_sessions_session_id', 'sessions')
    
    # Drop tables
    op.drop_table('messages')
    op.drop_table('sessions')
