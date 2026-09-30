"""001_initial_schema: Create foundational tables for FamilyNest

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-30 17:00:00.000000

Creates:
- users
- people
- families
- family_members
- relationships
- invitations
- audit_logs

Includes UUID primary keys, check constraints, foreign keys with historical protection,
indexes, and timezone-aware timestamps.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. USERS table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.Text(), nullable=True),
        sa.Column('display_name', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.UniqueConstraint('email', name='uq_users_email'),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # 2. PEOPLE table
    op.create_table(
        'people',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('claimed_by_user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('middle_name', sa.String(length=100), nullable=True),
        sa.Column('last_name', sa.String(length=100), nullable=True),
        sa.Column('nickname', sa.String(length=100), nullable=True),
        sa.Column('gender', sa.String(length=50), nullable=True),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('date_of_death', sa.Date(), nullable=True),
        sa.Column('birth_place', sa.String(length=255), nullable=True),
        sa.Column('current_city', sa.String(length=255), nullable=True),
        sa.Column('occupation', sa.String(length=255), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('profile_photo_url', sa.Text(), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('is_deceased', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('is_minor', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('profile_status', sa.String(length=50), nullable=False, server_default=sa.text("'unclaimed'")),
        sa.Column('created_by_user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.UniqueConstraint('claimed_by_user_id', name='uq_people_claimed_by_user_id'),
        sa.CheckConstraint("profile_status IN ('unclaimed', 'invited', 'claimed', 'deceased')", name='ck_people_profile_status'),
    )
    op.create_index('ix_people_claimed_by_user_id', 'people', ['claimed_by_user_id'])
    op.create_index('ix_people_created_by_user_id', 'people', ['created_by_user_id'])
    op.create_index('ix_people_last_name', 'people', ['last_name'])
    op.create_index('ix_people_date_of_birth', 'people', ['date_of_birth'])

    # 3. FAMILIES table
    op.create_table(
        'families',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_by_user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
    )

    # 4. FAMILY_MEMBERS table
    op.create_table(
        'family_members',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('family_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('families.id', ondelete='CASCADE'), nullable=False),
        sa.Column('person_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('people.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('joined_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.UniqueConstraint('family_id', 'person_id', name='uq_family_members_family_person'),
        sa.CheckConstraint("role IN ('owner', 'admin', 'member', 'invited')", name='ck_family_members_role'),
    )
    op.create_index('ix_family_members_family_id', 'family_members', ['family_id'])
    op.create_index('ix_family_members_person_id', 'family_members', ['person_id'])

    # 5. RELATIONSHIPS table
    op.create_table(
        'relationships',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('person_a_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('people.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('person_b_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('people.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('relationship_type', sa.String(length=50), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('is_current', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_by_user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.CheckConstraint('person_a_id != person_b_id', name='ck_relationships_no_self_relationship'),
        sa.CheckConstraint(
            "relationship_type IN ('parent', 'child', 'spouse', 'divorced_spouse', 'sibling', 'guardian')",
            name='ck_relationships_type'
        ),
    )
    op.create_index('ix_relationships_person_a_id', 'relationships', ['person_a_id'])
    op.create_index('ix_relationships_person_b_id', 'relationships', ['person_b_id'])
    op.create_index('ix_relationships_relationship_type', 'relationships', ['relationship_type'])

    # 6. INVITATIONS table
    op.create_table(
        'invitations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('family_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('families.id', ondelete='SET NULL'), nullable=True),
        sa.Column('person_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('people.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('invited_by_user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('invited_email', sa.String(length=255), nullable=True),
        sa.Column('invited_phone', sa.String(length=50), nullable=True),
        sa.Column('invitation_token', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default=sa.text("'pending'")),
        sa.Column('expires_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.UniqueConstraint('invitation_token', name='uq_invitations_invitation_token'),
        sa.CheckConstraint("status IN ('pending', 'accepted', 'expired', 'cancelled')", name='ck_invitations_status'),
    )
    op.create_index('ix_invitations_person_id', 'invitations', ['person_id'])
    op.create_index('ix_invitations_status', 'invitations', ['status'])

    # 7. AUDIT_LOGS table
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('actor_user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('entity_type', sa.String(length=100), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_audit_logs_entity_type', 'audit_logs', ['entity_type'])
    op.create_index('ix_audit_logs_entity_id', 'audit_logs', ['entity_id'])


def downgrade() -> None:
    # Drop in reverse dependency order
    op.drop_table('audit_logs')
    op.drop_table('invitations')
    op.drop_table('relationships')
    op.drop_table('family_members')
    op.drop_table('families')
    op.drop_table('people')
    op.drop_table('users')
