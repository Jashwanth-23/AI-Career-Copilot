"""create interview tables

Revision ID: 7a8f9e0b1c2d
Revises: 0eff5d86f61d
Create Date: 2026-08-13 00:03:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7a8f9e0b1c2d'
down_revision: Union[str, Sequence[str], None] = '0eff5d86f61d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create interview_sessions table
    op.create_table(
        'interview_sessions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('resume_id', sa.Integer(), nullable=False),
        sa.Column('target_role', sa.String(length=255), nullable=False),
        sa.Column('interview_type', sa.String(length=50), nullable=False),
        sa.Column('difficulty', sa.String(length=50), nullable=False),
        sa.Column('total_questions', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('current_question_number', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='active'),
        sa.Column('overall_score', sa.Integer(), nullable=True),
        sa.Column('performance_rating', sa.String(length=50), nullable=True),
        sa.Column('final_report', sa.JSON(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['resume_id'], ['resumes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_interview_sessions_user_id'), 'interview_sessions', ['user_id'], unique=False)
    op.create_index(op.f('ix_interview_sessions_resume_id'), 'interview_sessions', ['resume_id'], unique=False)

    # Create interview_questions table
    op.create_table(
        'interview_questions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('question_number', sa.Integer(), nullable=False),
        sa.Column('question_type', sa.String(length=50), nullable=False),
        sa.Column('difficulty', sa.String(length=50), nullable=False),
        sa.Column('topic', sa.String(length=255), nullable=True),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('resume_reference', sa.String(length=255), nullable=True),
        sa.Column('user_answer', sa.Text(), nullable=True),
        sa.Column('score', sa.Integer(), nullable=True),
        sa.Column('evaluation', sa.JSON(), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('missing_key_points', sa.JSON(), nullable=True),
        sa.Column('ideal_answer', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['interview_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_interview_questions_session_id'), 'interview_questions', ['session_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_interview_questions_session_id'), table_name='interview_questions')
    op.drop_table('interview_questions')
    op.drop_index(op.f('ix_interview_sessions_resume_id'), table_name='interview_sessions')
    op.drop_index(op.f('ix_interview_sessions_user_id'), table_name='interview_sessions')
    op.drop_table('interview_sessions')
