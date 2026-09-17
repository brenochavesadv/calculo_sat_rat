from datetime import date, datetime
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest
from flask import Flask

from run import db
from app.services import apuracao_service


def _calcula_cs_model(**values):
    return SimpleNamespace(
        fap_aplicado=values["fap_aplicado"],
        aliq_rat_aplicada=values["aliq_rat_aplicada"],
        aliq_rat_ajustada=values["aliq_rat_ajustada"],
        fap_devido=values["fap_devido"],
        aliq_rat_corrigida=values["aliq_rat_corrigida"],
        aliq_rat_corrigida_ajustada=values["aliq_rat_corrigida_ajustada"],
        vr_bc_consolidada=values["vr_bc_consolidada"],
        vl_total_apur_corrigido=values["vl_total_apur_corrigido"],
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("01-2025", "2025-01"),
        ("2025-01", "2025-01"),
        (" 12-2024 ", "2024-12"),
    ],
)
def test_normalize_comp_accepts_supported_formats(value, expected):
    assert apuracao_service._normalize_comp(value) == expected


@pytest.mark.parametrize("value", [None, "", "2025", "2025-1", "13-2025", "00-2025"])
def test_normalize_comp_rejects_invalid_values(value):
    with pytest.raises(ValueError):
        apuracao_service._normalize_comp(value)


def test_parse_format_and_end_of_month():
    parsed = apuracao_service._parse_comp("2024-02")

    assert parsed == datetime(2024, 2, 1)
    assert apuracao_service._fmt_comp(parsed) == "2024-02"
    assert apuracao_service._end_of_month(parsed) == datetime(2024, 2, 29)


@pytest.mark.parametrize(
    ("comp", "expected"),
    [
        ("2025-01", True),
        ("2025-03", True),
        ("2025-04", False),
        ("2024-12", False),
    ],
)
def test_vigente_checks_month_boundaries(comp, expected):
    establishment = SimpleNamespace(
        iniValidEstab=date(2025, 1, 15),
        fimValidEstab=date(2025, 3, 31),
    )

    assert apuracao_service._vigente(establishment, comp) is expected


def test_selic_factor_applies_rates_from_month_after_start():
    rates = {
        "2025-02": SimpleNamespace(taxa=1.0),
        "2025-03": SimpleNamespace(taxa=2.0),
    }

    with patch.object(
        apuracao_service.db.session,
        "get",
        side_effect=lambda model, competencia: rates.get(competencia),
    ) as session_get:
        factor = apuracao_service._selic_factor("2025-01", "2025-03")

    assert factor == pytest.approx(1.01 * 1.02)
    assert [call.args[1] for call in session_get.call_args_list] == ["2025-02", "2025-03"]


def test_apurar_rat_normalizes_inputs_refreshes_selic_and_delegates():
    expected = {"total_periodo": 10.0, "por_competencia": []}

    with (
        patch.object(apuracao_service, "calcula_cs", return_value=expected) as calcula,
        patch(
            "app.services.selic_services.fetch_and_upsert_selic_from_bacen"
        ) as refresh_selic,
    ):
        result = apuracao_service.apurar_rat("01-2025", "02-2025", "123", 0.03)

    assert result == expected
    refresh_selic.assert_called_once_with()
    calcula.assert_called_once_with(
        comp_ini="2025-01",
        comp_fim="2025-02",
        cnpj="123",
        aliq_rat_corrigida=0.03,
    )


def test_apurar_rat_continues_when_selic_refresh_fails():
    expected = {"total_periodo": 0.0, "por_competencia": []}

    with (
        patch.object(apuracao_service, "calcula_cs", return_value=expected) as calcula,
        patch(
            "app.services.selic_services.fetch_and_upsert_selic_from_bacen",
            side_effect=RuntimeError("BACEN indisponível"),
        ),
    ):
        result = apuracao_service.apurar_rat("2025-01", "2025-01", "123", 0.03)

    assert result == expected
    calcula.assert_called_once()


def test_calcula_cs_returns_zero_report_when_no_establishment_matches():
    query = Mock()
    query.filter.return_value.all.return_value = []
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        with (
            patch.object(apuracao_service.ESocialS1005EvtTabEstab, "query", query),
            patch.object(
                apuracao_service,
                "CalculaCs",
                side_effect=_calcula_cs_model,
            ) as calcula_model,
        ):
            result = apuracao_service.calcula_cs("2025-01", "2025-02", "123", 1.0)

    assert result["total_rat_periodo_corrigido"] == 0.0
    assert [item["competencia"] for item in result["por_competencia"]] == [
        "2025-01",
        "2025-02",
    ]
    assert all(item["soma_basesCp"] == 0.0 for item in result["por_competencia"])
    assert calcula_model.call_count == 0


def test_calcula_cs_sums_bases_and_gilrat_contribution():
    establishment = SimpleNamespace(
        nrInsc="123",
        nrInscEstab="12345678901234",
        iniValidEstab=date(2025, 1, 1),
        fimValidEstab=None,
    )
    base = SimpleNamespace(
        indIncid="11",
        codCateg="101",
        vrBcCp00=1000.0,
        vrBcCp15=None,
        vrBcCp20=200.0,
        vrBcCp25=None,
        vrSuspBcCp00=None,
        vrSuspBcCp15=None,
        vrSuspBcCp20=None,
        vrSuspBcCp25=None,
        vrDescSest=None,
        vrCalcSest=None,
        vrDescSenat=None,
        vrCalcSenat=None,
        vrSalFam=None,
        vrSalMat=None,
    )
    contribution = SimpleNamespace(tpCR=164601, vrCR=36.0, vrCRSusp=None)
    event = SimpleNamespace(
        evtCsId="event-1",
        aliqRat=0.03,
        fap=1.2,
        aliqRatAjust=0.036,
        bases_remun=[base],
        info_cr_contrib=[contribution],
    )
    establishment_query = Mock()
    establishment_query.filter.return_value.all.return_value = [establishment]
    event_query = Mock()
    event_query.join.return_value = event_query
    event_query.filter.return_value = event_query
    event_query.order_by.return_value = event_query
    event_query.first.return_value = event
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        with (
            patch.object(
                apuracao_service.ESocialS1005EvtTabEstab,
                "query",
                establishment_query,
            ),
            patch.object(apuracao_service.ESocialS5011EvtCs, "query", event_query),
            patch.object(
                apuracao_service,
                "CalculaCs",
                side_effect=_calcula_cs_model,
            ) as calcula_model,
        ):
            result = apuracao_service.calcula_cs(
                "2025-01", "2025-01", "123", aliq_rat_corrigida=1.04
            )

    report = result["por_competencia"][0]
    assert result["total_rat_periodo_corrigido"] == pytest.approx(14.976)
    assert report["soma_basesCp"] == 1200.0
    assert report["rat_corrigido_devido"] == pytest.approx(14.976)
    assert report["aliq_rat_corrigida_ajustada"] == pytest.approx(1.248)
    calcula_model.assert_not_called()
