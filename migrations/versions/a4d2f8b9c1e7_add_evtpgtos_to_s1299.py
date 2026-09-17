"""add evtPgtos to s1299

Revision ID: a4d2f8b9c1e7
Revises: 7c3e2f1a4b90
Create Date: 2026-08-05 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a4d2f8b9c1e7'
down_revision = '7c3e2f1a4b90'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'esocial_s1299_evt_fecha_ev_per',
        sa.Column('evtPgtos', sa.String(length=1), nullable=False, server_default=sa.text("'N'"), comment='Possui eventos de pagamento de rendimentos do trabalho? (S/N)'),
    )


def downgrade() -> None:
    op.drop_column('esocial_s1299_evt_fecha_ev_per', 'evtPgtos')