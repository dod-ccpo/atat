"""User first and last name nullable

Revision ID: bfdb81e51aed
Revises: 43da0c0c3f5e
Create Date: 2020-09-14 15:11:28.888265

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "bfdb81e51aed"  # pragma: allowlist secret
down_revision = "43da0c0c3f5e"  # pragma: allowlist secret
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("users", "first_name", existing_type=sa.VARCHAR(), nullable=True)
    op.alter_column("users", "last_name", existing_type=sa.VARCHAR(), nullable=True)


def downgrade():
    op.alter_column("users", "last_name", existing_type=sa.VARCHAR(), nullable=False)
    op.alter_column("users", "first_name", existing_type=sa.VARCHAR(), nullable=False)
