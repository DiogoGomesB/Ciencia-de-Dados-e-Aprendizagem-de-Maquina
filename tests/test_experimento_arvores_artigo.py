from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import requests

from src.coleta.Coleta_Dados import requisitar_api_com_retry
from src.modelagem.Experimento_Arvores_Artigo import garantir_dados_processados


def test_requisitar_api_com_retry_recupera_apos_falha() -> None:
    resposta_ok = MagicMock()
    resposta_ok.status_code = 200
    resposta_ok.json.return_value = {"hourly": {"time": ["2026-01-01T00:00"]}}
    resposta_ok.raise_for_status.return_value = None

    with patch("src.coleta.Coleta_Dados.requests.get") as mock_get, patch(
        "src.coleta.Coleta_Dados.time.sleep"
    ):
        mock_get.side_effect = [
            requests.ConnectionError("Falha temporária"),
            resposta_ok,
        ]
        dados = requisitar_api_com_retry(
            "https://example.com/api",
            params={"latitude": -23.5},
            timeout=5,
            max_tentativas=3,
            espera_inicial_s=0.01,
        )
        assert dados == {"hourly": {"time": ["2026-01-01T00:00"]}}
        assert mock_get.call_count == 2


def test_artefatos_do_artigo_e_dados_processados_existem() -> None:
    caminho_proc = garantir_dados_processados()
    assert caminho_proc.exists()

    caminho_comp = Path("reports/modeling/artigo_comparativo_modelos.csv")
    caminho_prof = Path("reports/modeling/artigo_profundidade_arvore.csv")
    assert caminho_comp.exists()
    assert caminho_prof.exists()

    df_comp = pd.read_csv(caminho_comp)
    modelos_esperados = {
        "dummy_prior",
        "persistencia_iqar_atual",
        "gaussian_naive_bayes",
        "arvore_decisao_cart",
        "random_forest_balanced",
        "xgboost_balanced",
    }
    assert modelos_esperados.issubset(set(df_comp["modelo"].unique()))
    assert "tempo_treino_s" in df_comp.columns
    assert "tempo_predicao_ms" in df_comp.columns

    assert Path("docs/index.html").exists()
    assert Path("streamlit_app.py").exists()
    assert Path("DIARIO.md").exists()
    assert Path(".env.example").exists()

