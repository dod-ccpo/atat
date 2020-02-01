"""add application_role.cloud_id

Revision ID: 17da2a475429
Revises: 50979d8ef680
Create Date: 2020-02-01 10:43:03.073539

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '17da2a475429' # pragma: allowlist secret
down_revision = '50979d8ef680' # pragma: allowlist secret
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('application_roles', sa.Column('cloud_id', sa.String(), nullable=True))
    op.add_column('application_roles', sa.Column('claimed_until', sa.TIMESTAMP(timezone=True), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('application_roles', 'cloud_id')
    op.drop_column('application_roles', 'claimed_until')
    # ### end Alembic commands ###
