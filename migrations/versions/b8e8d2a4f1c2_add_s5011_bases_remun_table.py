"""add s5011 bases remun table

Revision ID: b8e8d2a4f1c2
Revises: a4d2f8b9c1e7
Create Date: 2026-08-05 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b8e8d2a4f1c2'
down_revision = 'a4d2f8b9c1e7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'esocial_s5011_bases_remun',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('evtCsId', sa.String(length=36), nullable=False),
        sa.Column('tpInscEstab', sa.String(length=2), nullable=True),
        sa.Column('nrInscEstab', sa.String(length=14), nullable=True),
        sa.Column('indIncid', sa.String(length=1), nullable=True),
        sa.Column('codCateg', sa.String(length=5), nullable=True),
        sa.Column('vrBcCp00', sa.Numeric(14, 2), nullable=True),
        sa.Column('vrBcCp15', sa.Numeric(14, 2), nullable=True),
        sa.Column('vrBcCp20', sa.Numeric(14, 2), nullable=True),
        sa.Column('vrBcCp25', sa.Numeric(14, 2), nullable=True),
        sa.Column('vrSuspBcCp00', sa.Numeric(14, 2), nullable=True),
        sa.Column('vrSuspBcCp15', sa.Numeric(14, 2), nullable=True),
        sa.Column('vrSuspBcCp20', sa.Numeric(14, 2), nullable=True),
        sa.Column('vrSuspBcCp25', sa.Numeric(14, 2), nullable=True),
        sa.Column('vrDescSest', sa.Numeric(14, 2), nullable=True),
        sa.Column('vrCalcSest', sa.Numeric(14, 2), nullable=True),
        sa.Column('vrDescSenat', sa.Numeric(14, 2), nullable=True),
        sa.Column('vrCalcSenat', sa.Numeric(14, 2), nullable=True),
        sa.Column('vrSalFam', sa.Numeric(14, 2), nullable=True),
        sa.Column('vrSalMat', sa.Numeric(14, 2), nullable=True),
        sa.Column('arquivo_origem', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['evtCsId'], ['esocial_s5011_evt_cs.evtCsId']),
    )
    op.create_index('ix_esocial_s5011_bases_remun_evt_estab', 'esocial_s5011_bases_remun', ['evtCsId', 'nrInscEstab', 'codCateg'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_esocial_s5011_bases_remun_evt_estab', table_name='esocial_s5011_bases_remun')
    op.drop_table('esocial_s5011_bases_remun')