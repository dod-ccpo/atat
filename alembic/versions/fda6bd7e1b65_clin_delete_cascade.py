"""clin delete cascade

Revision ID: fda6bd7e1b65
Revises: e0c6eb21771f
Create Date: 2019-08-07 16:37:02.451277

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "fda6bd7e1b65"
down_revision = "e0c6eb21771f"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("clins_task_order_id_fkey", "clins")
    op.create_foreign_key(
        "clins_task_order_id_fkey",
        "clins",
        "task_orders",
        ["task_order_id"],
        ["id"],
        ondelete="cascade",
    )


def downgrade():
    op.drop_constraint("clins_task_order_id_fkey", "clins")
    op.create_foreign_key(
        "clins_task_order_id_fkey",
        "clins",
        "task_orders",
        ["task_order_id"],
        ["id"],
        ondelete="no action",
    )
