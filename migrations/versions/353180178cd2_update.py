"""update

Revision ID: 353180178cd2
Revises: b8e8d2a4f1c2
Create Date: 2026-08-07 09:54:48.875749

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '353180178cd2'
down_revision = 'b8e8d2a4f1c2'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table('calcula_cs'):
        op.create_table(
            'calcula_cs',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('nrInsc', sa.String(length=14), nullable=False),
            sa.Column('per_apur', sa.String(length=7), nullable=True),
            sa.Column('vr_bc_consolidada', sa.Float(), nullable=True, comment='Valor da base de cálculo consolidada somatorio basesRemun do S-5011'),
            sa.Column('aliq_rat_aplicado', sa.Numeric(precision=5, scale=4), nullable=True, comment='Alíquota RAT informada no s5011_evtCs'),
            sa.Column('fap_aplicado', sa.Numeric(precision=5, scale=4), nullable=True, comment='FAP aplicado no s5011_evtCs'),
            sa.Column('aliq_rat_corrigida', sa.Numeric(precision=5, scale=4), nullable=True, comment='Alíquota RAT ajustada (RAT × FAP)'),
            sa.Column('aliq_rat_ajustada', sa.Numeric(precision=5, scale=4), nullable=True, comment='Alíquota RAT ajustada (RAT × FAP) limitada a 0,5% e 3%'),
            sa.Column('vl_total_apur_aplicado', sa.Numeric(precision=14, scale=2), nullable=True, comment='Valor total apurado de contribuição devida no s5011_evtCs'),
            sa.Column('vl_total_calculado_ajuste', sa.Numeric(precision=14, scale=2), nullable=True, comment='Valor total calculado conforme ajuste da aliquota ajustada'),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index(op.f('ix_calcula_cs_per_apur'), 'calcula_cs', ['per_apur'], unique=False)

    if not inspector.has_table('esocial_s5011_evt_cs_bases_remun'):
        op.create_table(
            'esocial_s5011_evt_cs_bases_remun',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('evtCsId', sa.String(length=36), nullable=False, comment='Identificador do evento S-5011'),
            sa.Column('tpInscEstab', sa.String(length=2), nullable=True, comment='Tipo de inscrição do estabelecimento'),
            sa.Column('nrInscEstab', sa.String(length=14), nullable=True, comment='Número de inscrição do estabelecimento'),
            sa.Column('indIncid', sa.String(length=1), nullable=True, comment='Indicativo de incidência'),
            sa.Column('codCateg', sa.String(length=5), nullable=True, comment='Código da categoria do trabalhador'),
            sa.Column('vrBcCp00', sa.Numeric(precision=14, scale=2), nullable=True, comment='Base de cálculo da contribuição previdenciária sobre remuneração'),
            sa.Column('vrBcCp15', sa.Numeric(precision=14, scale=2), nullable=True, comment='Base de cálculo adicional após 15 anos'),
            sa.Column('vrBcCp20', sa.Numeric(precision=14, scale=2), nullable=True, comment='Base de cálculo adicional após 20 anos'),
            sa.Column('vrBcCp25', sa.Numeric(precision=14, scale=2), nullable=True, comment='Base de cálculo adicional após 25 anos'),
            sa.Column('vrSuspBcCp00', sa.Numeric(precision=14, scale=2), nullable=True, comment='BC com incidência suspensa'),
            sa.Column('vrSuspBcCp15', sa.Numeric(precision=14, scale=2), nullable=True, comment='BC suspensa após 15 anos'),
            sa.Column('vrSuspBcCp20', sa.Numeric(precision=14, scale=2), nullable=True, comment='BC suspensa após 20 anos'),
            sa.Column('vrSuspBcCp25', sa.Numeric(precision=14, scale=2), nullable=True, comment='BC suspensa após 25 anos'),
            sa.Column('vrDescSest', sa.Numeric(precision=14, scale=2), nullable=True, comment='Valor descontado para SEST'),
            sa.Column('vrCalcSest', sa.Numeric(precision=14, scale=2), nullable=True, comment='Valor calculado para SEST'),
            sa.Column('vrDescSenat', sa.Numeric(precision=14, scale=2), nullable=True, comment='Valor descontado para SENAT'),
            sa.Column('vrCalcSenat', sa.Numeric(precision=14, scale=2), nullable=True, comment='Valor calculado para SENAT'),
            sa.Column('vrSalFam', sa.Numeric(precision=14, scale=2), nullable=True, comment='Valor total do salário-família'),
            sa.Column('vrSalMat', sa.Numeric(precision=14, scale=2), nullable=True, comment='Valor total do salário-maternidade'),
            sa.Column('arquivo_origem', sa.String(length=255), nullable=True, comment='Nome do arquivo de origem do qual o registro foi importado'),
            sa.ForeignKeyConstraint(['evtCsId'], ['esocial_s5011_evt_cs.evtCsId']),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_esocial_s5011_bases_remun_evt_estab', 'esocial_s5011_evt_cs_bases_remun', ['evtCsId', 'nrInscEstab', 'codCateg'], unique=False)
        op.create_index(op.f('ix_esocial_s5011_evt_cs_bases_remun_evtCsId'), 'esocial_s5011_evt_cs_bases_remun', ['evtCsId'], unique=False)

    if not inspector.has_table('esocial_s5011_evt_cs_info_cr_contrib'):
        op.create_table(
            'esocial_s5011_evt_cs_info_cr_contrib',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('evtCsId', sa.String(length=36), nullable=False, comment='Identificador do evento S-5011'),
            sa.Column('tpCR', sa.Integer(), nullable=True, comment='Código de Receita'),
            sa.Column('vrCR', sa.Numeric(precision=14, scale=2), nullable=True, comment='Valor do crédito'),
            sa.Column('vrCRSusp', sa.Numeric(precision=14, scale=2), nullable=True, comment='Valor do tributo com exigibilidade suspensa.'),
            sa.Column('arquivo_origem', sa.String(length=255), nullable=True, comment='Nome do arquivo de origem do qual o registro foi importado'),
            sa.ForeignKeyConstraint(['evtCsId'], ['esocial_s5011_evt_cs.evtCsId']),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index(op.f('ix_esocial_s5011_evt_cs_info_cr_contrib_evtCsId'), 'esocial_s5011_evt_cs_info_cr_contrib', ['evtCsId'], unique=False)
        op.create_index('ix_esocial_s5011_info_cr_contrib_evt_tpcr', 'esocial_s5011_evt_cs_info_cr_contrib', ['evtCsId', 'tpCR'], unique=False)

    if inspector.has_table('esocial_s5011_bases_remun'):
        op.drop_table('esocial_s5011_bases_remun')


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table('esocial_s5011_bases_remun'):
        op.create_table(
            'esocial_s5011_bases_remun',
            sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
            sa.Column('evtCsId', mysql.VARCHAR(length=36), nullable=False),
            sa.Column('tpInscEstab', mysql.VARCHAR(length=2), nullable=True),
            sa.Column('nrInscEstab', mysql.VARCHAR(length=14), nullable=True),
            sa.Column('indIncid', mysql.VARCHAR(length=1), nullable=True),
            sa.Column('codCateg', mysql.VARCHAR(length=5), nullable=True),
            sa.Column('vrBcCp00', mysql.DECIMAL(precision=14, scale=2), nullable=True),
            sa.Column('vrBcCp15', mysql.DECIMAL(precision=14, scale=2), nullable=True),
            sa.Column('vrBcCp20', mysql.DECIMAL(precision=14, scale=2), nullable=True),
            sa.Column('vrBcCp25', mysql.DECIMAL(precision=14, scale=2), nullable=True),
            sa.Column('vrSuspBcCp00', mysql.DECIMAL(precision=14, scale=2), nullable=True),
            sa.Column('vrSuspBcCp15', mysql.DECIMAL(precision=14, scale=2), nullable=True),
            sa.Column('vrSuspBcCp20', mysql.DECIMAL(precision=14, scale=2), nullable=True),
            sa.Column('vrSuspBcCp25', mysql.DECIMAL(precision=14, scale=2), nullable=True),
            sa.Column('vrDescSest', mysql.DECIMAL(precision=14, scale=2), nullable=True),
            sa.Column('vrCalcSest', mysql.DECIMAL(precision=14, scale=2), nullable=True),
            sa.Column('vrDescSenat', mysql.DECIMAL(precision=14, scale=2), nullable=True),
            sa.Column('vrCalcSenat', mysql.DECIMAL(precision=14, scale=2), nullable=True),
            sa.Column('vrSalFam', mysql.DECIMAL(precision=14, scale=2), nullable=True),
            sa.Column('vrSalMat', mysql.DECIMAL(precision=14, scale=2), nullable=True),
            sa.Column('arquivo_origem', mysql.VARCHAR(length=255), nullable=True),
            sa.ForeignKeyConstraint(['evtCsId'], ['esocial_s5011_evt_cs.evtCsId'], name=op.f('1')),
            sa.PrimaryKeyConstraint('id'),
            mysql_collate='utf8mb4_uca1400_ai_ci',
            mysql_default_charset='utf8mb4',
            mysql_engine='InnoDB'
        )
        op.create_index('ix_esocial_s5011_bases_remun_evt_estab', 'esocial_s5011_bases_remun', ['evtCsId', 'nrInscEstab', 'codCateg'], unique=False)

    if inspector.has_table('esocial_s5011_evt_cs_info_cr_contrib'):
        op.drop_index('ix_esocial_s5011_info_cr_contrib_evt_tpcr', table_name='esocial_s5011_evt_cs_info_cr_contrib')
        op.drop_index(op.f('ix_esocial_s5011_evt_cs_info_cr_contrib_evtCsId'), table_name='esocial_s5011_evt_cs_info_cr_contrib')
        op.drop_table('esocial_s5011_evt_cs_info_cr_contrib')

    if inspector.has_table('esocial_s5011_evt_cs_bases_remun'):
        op.drop_index(op.f('ix_esocial_s5011_evt_cs_bases_remun_evtCsId'), table_name='esocial_s5011_evt_cs_bases_remun')
        op.drop_index('ix_esocial_s5011_bases_remun_evt_estab', table_name='esocial_s5011_evt_cs_bases_remun')
        op.drop_table('esocial_s5011_evt_cs_bases_remun')

    if inspector.has_table('calcula_cs'):
        op.drop_index(op.f('ix_calcula_cs_per_apur'), table_name='calcula_cs')
        op.drop_table('calcula_cs')
