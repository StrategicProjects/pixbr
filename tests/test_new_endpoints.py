"""Tests for the CnaePorteRecebedor and PixUsuariosCadastradosDICT endpoints."""

import pandas as pd
import pytest

import pixbr
from pixbr import _odata
from pixbr.client import ENDPOINTS, PixClient, _coerce_numeric


BASE = _odata.BASE_URL


def test_cnae_url():
    url = _odata.build_url(
        "CnaePorteRecebedor",
        {"Database": "202506"},
        filter="AnoMes eq 202506 and mei eq 'S'",
        top=5,
    )
    assert url == (
        f"{BASE}/CnaePorteRecebedor(Database=@Database)"
        "?$format=json&@Database='202506'"
        "&$filter=AnoMes%20eq%20202506%20and%20mei%20eq%20'S'&$top=5"
    )


def test_dict_users_url_has_no_params():
    url = _odata.build_url(
        "PixUsuariosCadastradosDICT",
        None,
        orderby="DataGraficosPix desc",
        top=12,
    )
    assert url == (
        f"{BASE}/PixUsuariosCadastradosDICT"
        "?$format=json&$orderby=DataGraficosPix%20desc&$top=12"
    )
    assert "@" not in url


def test_endpoints_registry_covers_all_six():
    assert set(ENDPOINTS) == {
        "ChavesPix",
        "TransacoesPixPorMunicipio",
        "EstatisticasTransacoesPix",
        "EstatisticasFraudesPix",
        "CnaePorteRecebedor",
        "PixUsuariosCadastradosDICT",
    }
    assert ENDPOINTS["CnaePorteRecebedor"] == ("Database", "YYYYMM")
    assert ENDPOINTS["PixUsuariosCadastradosDICT"] == (None, None)


def test_pix_endpoints_lists_six():
    df = pixbr.pix_endpoints()
    assert len(df) == 6
    assert "CnaePorteRecebedor" in set(df["endpoint"])
    assert "PixUsuariosCadastradosDICT" in set(df["endpoint"])


def test_pix_columns_new_schemas():
    assert len(pixbr.pix_columns("cnae")) == 15
    assert len(pixbr.pix_columns("dict_users")) == 4
    fraud = pixbr.pix_columns("fraud")
    assert len(fraud) == 24
    assert "QtdePixcontestados" in set(fraud["column"])


def test_cnae_stats_requires_valid_database():
    client = PixClient(verbose=False)
    with pytest.raises(ValueError, match="Invalid year_month"):
        client.cnae_stats("2025")


def test_validate_columns_warns_on_unknown_cnae_column():
    with pytest.warns(UserWarning, match="Unknown column"):
        kept = _odata.validate_columns(["porte", "nope"], ["porte", "mei"])
    assert kept == ["porte"]


def test_coerce_numeric_fraud_qtde_and_percentual():
    # The old pattern-based coercion missed Qtde*/Percentual* columns.
    df = pd.DataFrame(
        {
            "AnoMes": ["202509"],
            "QtdePixcontestados": ["123"],
            "PercentualdeDevolucao": ["42.5"],
        }
    )
    out = _coerce_numeric(
        df, ["AnoMes", "QtdePixcontestados", "PercentualdeDevolucao"]
    )
    assert out["QtdePixcontestados"].dtype.kind in "if"
    assert out["PercentualdeDevolucao"].dtype.kind in "if"


def test_dict_users_parses_dates():
    respx = pytest.importorskip("respx")
    with respx.mock(base_url=BASE) as mock:
        mock.get(url__regex=r".*PixUsuariosCadastradosDICT.*").respond(
            json={
                "value": [
                    {
                        "DataGraficosPix": "2026-09-30",
                        "qtdUsuariosPessoaFisica": 168245596,
                        "qtdUsuariosPessoaJuridica": 18729138,
                        "qtdUsuariosCadastradosDICTTotal": 186974734,
                    }
                ]
            }
        )
        with PixClient(verbose=False) as client:
            df = client.dict_users()
    assert pd.api.types.is_datetime64_any_dtype(df["DataGraficosPix"])
    assert df["qtdUsuariosCadastradosDICTTotal"].iloc[0] == 186974734


def test_cnae_stats_coerces_numeric_columns():
    respx = pytest.importorskip("respx")
    with respx.mock(base_url=BASE) as mock:
        mock.get(url__regex=r".*CnaePorteRecebedor.*").respond(
            json={
                "value": [
                    {
                        "AnoMes": 202506,
                        "porte": "Microempresa",
                        "mei": "S",
                        "qtlanliq": "12306",
                        "vllanliq": "34603287.12",
                    }
                ]
            }
        )
        with PixClient(verbose=False) as client:
            df = client.cnae_stats("202506")
    assert df["qtlanliq"].dtype.kind in "if"
    assert df["vllanliq"].dtype.kind in "if"
    assert df["porte"].iloc[0] == "Microempresa"
