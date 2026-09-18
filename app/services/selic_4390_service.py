from decimal import Decimal
from typing import List, Dict
from datetime import datetime, timezone
import logging
import requests
from requests.adapters import HTTPAdapter, Retry
from run import db
from app.models.selic_mensal_4390 import SelicMensal4390

# Service to fetch SELIC series from SGS/Bacen and upsert into a database using SQLAlchemy.

logger = logging.getLogger(__name__)
DEFAULT_TIMEOUT = 30  # seconds

class Selic4390Service:
    def __init__(self, timeout: int = DEFAULT_TIMEOUT, max_retries: int = 3):
        self.timeout = timeout
        self.session = requests.Session()
        retries = Retry(
            total=max_retries,
            connect=max_retries,
            read=max_retries,
            status=max_retries,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset({"GET"}),
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def fetch_selic_4390(self, mes_inicial: str, mes_final: str):
        try:
            # api BCB para valores mensais da SELIC (código 4390) no formato JSON retorno: 01/mm/YYYY e valor com 2 casas decimais
            API_TEMPLATE = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.4390/dados?formato=json&dataInicial=01/{mesInicial}&dataFinal=01/{mesFinal}"
            url = API_TEMPLATE.format(
                mesInicial=Selic4390Service._api_month(mes_inicial),
                mesFinal=Selic4390Service._api_month(mes_final),
            )
            print(f"Fetching SELIC data from URL: {url}")
            logger.debug("Fetching SELIC data from URL: %s", url)
            resp = self.session.get(url, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            values = []

            for item in data:
                if "data" not in item or "valor" not in item:
                    raise ValueError(f"Unexpected item format from SGS API: {item}")

                values.append({
                    "competencia": item["data"],
                    "taxa": item["valor"]
                })

            self.upsert_selic_4390(values=values)
            return
            
        except requests.RequestException as e:
            logger.error("Error fetching SELIC data from SGS 4390 API: %s", e)
            raise

    @staticmethod
    def upsert_selic_4390(values: List[Dict[str, str]]):

        _table = SelicMensal4390
        db_session = db.session
        
        for item in values:

            raw_competencia = item.get("competencia")
            if not raw_competencia:
                raise ValueError("A competência SELIC é obrigatória")
            raw_taxa = float(str(item.get("taxa") or 0.0).replace(",", "."))

            existing = (
                db_session.query(_table)
                .filter(_table.competencia == raw_competencia)
                .first()
            )

            if existing:
                # update only if different
                current_obj = getattr(existing, "taxa", None)
                if current_obj != raw_taxa:
                    setattr(existing, "taxa", raw_taxa)
                    setattr(existing, "updated_at", datetime.now(timezone.utc))
                    db_session.add(existing)
            else:
                # create new instance
                new_obj = SelicMensal4390(
                    competencia=raw_competencia,
                    taxa=raw_taxa,
                    updated_at=datetime.now(timezone.utc)
                )
                db_session.add(new_obj)

        try:
            db_session.commit()
            return
        except Exception:
            db_session.rollback()
            logger.exception("Failed to commit SELIC upsert transaction")
            raise

    def check_selic_4390_exists(self, mes_inicial: str, mes_final: str):
        """Check if a SELIC entry exists for the given competencia."""
        db_session = db.session
        _table = SelicMensal4390

        try:
            entries = db_session.query(_table).all()
            competencias = {
                self._normalize_competencia(entry.competencia) for entry in entries
            }
            exists_inicial = self._normalize_competencia(mes_inicial) in competencias
            exists_final = self._normalize_competencia(mes_final) in competencias
        
        except Exception as e:
            logger.exception("Error checking SELIC 4390 existence in database: %s", e)
            raise

        if exists_inicial and exists_final:
            return

        try:
            self.fetch_selic_4390(mes_inicial=mes_inicial, mes_final=mes_final)
            return
        except Exception as e:
            logger.exception("Error fetching and upserting SELIC 4390 data: %s", e)
            raise    

    def get_selic_4390(self, mes_inicial: str, mes_final: str) -> List[SelicMensal4390]:
        """Retrieve the SELIC rate for a given competencia."""
        db_session = db.session
        _table = SelicMensal4390
        inicial = self._normalize_competencia(mes_inicial)
        final = self._normalize_competencia(mes_final)
        if inicial > final:
            raise ValueError("A competência inicial não pode ser posterior à final")

        try:
            entries = db_session.query(_table).all()
            return [
                entry
                for entry in entries
                if inicial <= self._normalize_competencia(entry.competencia) <= final
            ]
        
        except Exception as e:
            logger.exception("Error retrieving SELIC 4390 data from database: %s", e)
            raise    

    @staticmethod
    def calcular_selic_acumulada_RFB(values: List[SelicMensal4390], mes_final: str) -> Dict[str, Decimal]:
        """Calcula o fator SELIC composto de cada competência até ``mes_final``.

        Pela regra da RFB, a taxa do mês da competência inicial não entra no
        cálculo. O resultado é o fator final, já começando em ``1``; portanto,
        uma competência sem meses posteriores retorna ``Decimal("1")``.
        """
        if not values:
            raise ValueError("A lista de valores SELIC não pode estar vazia.")

        acumulado_mes = {}
        sorted_values = sorted(values, key=lambda x: Selic4390Service._normalize_competencia(x.competencia))
        reversed_values = list(reversed(sorted_values))
        final = Selic4390Service._normalize_competencia(mes_final)

        for entry in reversed_values:

            competencia = Selic4390Service._normalize_competencia(entry.competencia)

            if competencia > final:
                continue

            acumulado = 0.00
            
            for item in reversed_values:

                comp = Selic4390Service._normalize_competencia(item.competencia)

                # Se a competência do item for maior ou igual à competência final, não deve ser incluída no cálculo.
                if comp >= final:
                    continue               
                elif comp > competencia:
                   acumulado += item.taxa
                elif comp == competencia:
                    acumulado += 1.00
                else:
                    break
                    
            acumulado_mes[competencia] = acumulado
        
        return acumulado_mes

    @staticmethod
    def _normalize_competencia(value: str) -> str:
        """Normaliza competência para YYYY-MM."""
        value = (value or "").strip()
        for pattern in ("%Y-%m", "%m-%Y", "%d/%m/%Y", "%d/%m/%y"):
            try:
                return datetime.strptime(value, pattern).strftime("%Y-%m")
            except ValueError:
                continue
        raise ValueError(f"Competência SELIC inválida: {value}")

    @staticmethod
    def _api_month(value: str) -> str:
        """Converte competência para o formato mensal aceito pelo BACEN (MM/YYYY)."""
        normalized = Selic4390Service._normalize_competencia(value)
        year, month = normalized.split("-")
        return f"{month}/{year}"