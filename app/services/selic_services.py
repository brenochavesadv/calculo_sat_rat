from decimal import Decimal
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Type
from decimal import Decimal
from datetime import date, datetime
import logging
import requests
from requests.adapters import HTTPAdapter, Retry
from run import db
from app.models.selic import SelicMensal

"""
services/selic_services.py

Service to fetch SELIC series from SGS/Bacen and upsert into a database using SQLAlchemy.

Usage example:

from your_app.models import SelicModel  # model must have fields for codigo_serie, data, valor

service = SelicService()
service.upsert_selic(
    db_session,                     # SQLAlchemy Session
    SelicModel,                     # SQLAlchemy model class
    codigo_serie=11,                # series code
    data_inicial="01/01/2020",      # dd/mm/YYYY
    data_final="31/12/2020",        # dd/mm/YYYY
    codigo_field="codigo_serie",
    date_field="data",
    value_field="valor",
    commit=True
)
"""

logger = logging.getLogger(__name__)
DEFAULT_TIMEOUT = 10  # seconds
API_TEMPLATE = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.4390/dados?formato=json&dataInicial={dataInicial}&dataFinal={dataFinal}"


class SelicService:
    def __init__(self, timeout: int = DEFAULT_TIMEOUT, max_retries: int = 3):
        self.timeout = timeout
        self.session = requests.Session()
        retries = Retry(total=max_retries, backoff_factor=0.3, status_forcelist=(500, 502, 503, 504))
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def fetch_selic(self, data_inicial: str, data_final: str) -> List[Dict[str, Any]]:
        """
        Fetch SELIC series from Bacen SGS API.

        - data_inicial / data_final: strings in dd/mm/YYYY format

        Returns a list of dicts with keys 'data' and 'valor' as strings from the API.
        """
        url = API_TEMPLATE.format(dataInicial=data_inicial, dataFinal=data_final)
        logger.debug("Fetching SELIC data from URL: %s", url)
        resp = self.session.get(url, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()
        if not isinstance(data, list):
            raise ValueError("Unexpected response format from SGS API")
        return data

    @staticmethod
    def _parse_date(date_str: str) -> datetime.date:
        # SGS returns dates commonly in "dd/mm/YYYY"
        return datetime.strptime(date_str, "%d/%m/%Y").date()

    @staticmethod
    def _parse_value(value_str: str) -> Decimal:
        """
        Convert Brazilian number strings to Decimal.
        Examples: "1.234,56" -> Decimal("1234.56"), "0,1234" -> Decimal("0.1234")
        """
        if value_str is None:
            return Decimal("0")
        # Remove thousands separator '.' and replace decimal comma ',' with '.'
        normalized = value_str.replace(".", "").replace(",", ".").strip()
        return Decimal(normalized)

    def upsert_selic(
        self,
        db_session,
        model: Type,
        codigo_serie: int,
        data_inicial: str,
        data_final: str,
        codigo_field: str = "codigo_serie",
        date_field: str = "data",
        value_field: str = "valor",
        commit: bool = True,
    ) -> int:
        """
        Fetch SELIC series and insert/update rows in the DB.

        - db_session: SQLAlchemy Session
        - model: SQLAlchemy declarative model class
        - codigo_field/date_field/value_field: attribute names on the model
        - commit: whether to commit the session after changes

        Returns the number of inserted/updated records.
        """
        items = self.fetch_selic(codigo_serie, data_inicial, data_final)
        count = 0
        for item in items:
            # item expected like {'data': '01/01/2020', 'valor': '4,50'}
            raw_date = item.get("data")
            raw_val = item.get("valor")
            try:
                date_obj = self._parse_date(raw_date)
                val = self._parse_value(raw_val)
            except Exception as e:
                logger.warning("Skipping record with invalid data %s: %s", item, e)
                continue

            # Build filters dynamically
            model_codigo_attr = getattr(model, codigo_field)
            model_date_attr = getattr(model, date_field)

            existing = (
                db_session.query(model)
                .filter(model_codigo_attr == codigo_serie)
                .filter(model_date_attr == date_obj)
                .one_or_none()
            )

            if existing:
                # update only if different
                current_val = getattr(existing, value_field)
                if current_val != val:
                    setattr(existing, value_field, val)
                    db_session.add(existing)
                    count += 1
            else:
                # create new instance
                obj_data = {
                    codigo_field: codigo_serie,
                    date_field: date_obj,
                    value_field: val,
                }
                try:
                    new_obj = model(**obj_data)
                except TypeError:
                    # fallback: set attributes after instantiation
                    new_obj = model()
                    setattr(new_obj, codigo_field, codigo_serie)
                    setattr(new_obj, date_field, date_obj)
                    setattr(new_obj, value_field, val)
                db_session.add(new_obj)
                count += 1

        if commit:
            try:
                db_session.commit()
            except Exception:
                db_session.rollback()
                logger.exception("Failed to commit SELIC upsert transaction")
                raise

        return count

def fetch_and_upsert_selic_from_bacen():
    """Fetch monthly SELIC series from Bacen (SGS) and upsert into selic_mensal.

    Behavior:
    - Find the latest `competencia` in `selic_mensal` (format YYYY-MM).
    - Compute the next month as start (first day) and the previous month as final (end of previous month).
      If table is empty, default to 2000-01 as start.
    - Call Bacen SGS API via services.selic_services.SelicService.fetch_selic and upsert rows.
    Returns a dict with counts and the date range used.
    """

    # find last competencia
    last = SelicMensal.query.order_by(SelicMensal.competencia.desc()).first()
    if last is None:
        start_year = 2000
        start_month = 1
    else:
        try:
            y, m = last.competencia.split('-')
            y = int(y); m = int(m)
            # next month
            if m == 12:
                y += 1; m = 1
            else:
                m += 1
            start_year = y; start_month = m
        except Exception:
            # fallback
            start_year = 2000; start_month = 1

    # data_inicial is first day of start_year-start_month
    data_inicial_dt = date(start_year, start_month, 1)

    # Format as dd/mm/YYYY for SGS API
    data_inicial = data_inicial_dt.strftime("%d/%m/%Y")
    data_final = date.today().strftime("%d/%m/%Y")

    svc = SelicService()
    items = svc.fetch_selic(data_inicial, data_final)
    inserted = 0
    for item in items:
        raw_date = item.get("data")  # dd/mm/YYYY
        raw_val = item.get("valor")
        try:
            d = datetime.strptime(raw_date, "%d/%m/%Y").date()
            comp = f"{d.year:04d}-{d.month:02d}"
            taxa = float(str(raw_val).replace('.', '').replace(',', '.')) if raw_val is not None else 0.0
        except Exception:
            continue

        # upsert
        obj = SelicMensal(competencia=comp, taxa=taxa)
        db.session.merge(obj)
        inserted += 1

    db.session.commit()
    return {"ok": True, "inserted": inserted, "range": (data_inicial, data_final)}
