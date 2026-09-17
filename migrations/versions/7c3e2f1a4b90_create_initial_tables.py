"""create initial tables

Revision ID: 7c3e2f1a4b90
Revises: c9b2e44acacf
Create Date: 2026-08-05 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

from run import db

# Import models so their tables are registered on db.metadata.
from app.models import ajuste  # noqa: F401
from app.models import base_apurada  # noqa: F401
from app.models import contribuicao  # noqa: F401
from app.models import import_skip  # noqa: F401
from app.models.job import Job, JobFile  # noqa: F401
from app.models.municipio import Municipio  # noqa: F401
from app.models import remuneracao  # noqa: F401
from app.models import rubrica  # noqa: F401
from app.models import selic  # noqa: F401
from app.models import user  # noqa: F401
from app.models import esocial_s1005_evtTabEstab  # noqa: F401
from app.models import esocial_s1010_evtTabRubrica  # noqa: F401
from app.models import esocial_s1200_evtRemun  # noqa: F401
from app.models import esocial_s1202_evtRmnRPPS  # noqa: F401
from app.models import esocial_s1210_evtPgtos  # noqa: F401
from app.models import esocial_s1298_evtReabreEvPer  # noqa: F401
from app.models import esocial_s1299_evtFechaEvPer  # noqa: F401
from app.models import esocial_s5001_evtBasesTrab  # noqa: F401
from app.models import esocial_s5002_evtIrrfBenef  # noqa: F401
from app.models import esocial_s5011_evtCs  # noqa: F401


# revision identifiers, used by Alembic.
revision = '7c3e2f1a4b90'
down_revision = 'c9b2e44acacf'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    for table in db.metadata.sorted_tables:
        table.create(bind=bind, checkfirst=True)


def downgrade() -> None:
    bind = op.get_bind()
    for table in reversed(db.metadata.sorted_tables):
        table.drop(bind=bind, checkfirst=True)