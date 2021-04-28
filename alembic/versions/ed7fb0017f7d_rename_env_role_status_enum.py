"""rename env role status enum

Change state that represents a successfull creation of an environment role from
"COMPLETED" to "ACTIVE" to match the wording of other status roles.

Revision ID: ed7fb0017f7d
Revises: ce9983b781fa
Create Date: 2020-07-07 11:38:08.238693

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ed7fb0017f7d"  # pragma: allowlist secret
down_revision = "ce9983b781fa"  # pragma: allowlist secret
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "environment_roles",
        "status",
        type_=sa.Enum(
            "ACTIVE", "PENDING", "DISABLED", name="status", native_enum=False,
        ),
        existing_type=sa.Enum(
            "PENDING", "COMPLETED", "DISABLED", name="status", native_enum=False
        ),
    )
    conn = op.get_bind()
    conn.execute(
        """
        UPDATE environment_roles
        SET status = (CASE WHEN status = 'COMPLETED' THEN 'ACTIVE' ELSE status END)
        """
    )


def downgrade():
    conn = op.get_bind()
    conn.execute(
        """
        UPDATE environment_roles
        SET status = (CASE WHEN status = 'ACTIVE' THEN 'COMPLETED' ELSE status END)
        """
    )
    op.alter_column(
        "environment_roles",
        "status",
        type_=sa.Enum(
            "PENDING", "COMPLETED", "DISABLED", name="status", native_enum=False
        ),
        existing_type=sa.Enum(
            "ACTIVE", "PENDING", "DISABLED", name="status", native_enum=False,
        ),
    )
