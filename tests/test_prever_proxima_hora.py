import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

from src.aplicacao.Prever_Proxima_Hora import (
    _json_para_dataframe_hourly,
    _limitar_ate_agora,
    _preparar_linha_mais_recente,
    _projetar_janela_futura,
    prever_proxima_hora,
    projetar_proximas_horas,
)
from src.modelagem.Avaliar_Baselines import FEATURES_SPRINT4


class _PipelineStub:
    def predict_proba(self, dados: pd.DataFrame):
        return np.tile([0.25, 0.75], (len(dados), 1))


class TestPreverProximaHora(unittest.TestCase):
    def _base_horaria(self, horas: int = 72) -> pd.DataFrame:
        dados = pd.DataFrame(
            {
                "time": pd.date_range("2026-10-01", periods=horas, freq="h"),
                "pm10": [40.0 + (i % 7) for i in range(horas)],
                "pm2_5": [18.0 + (i % 5) for i in range(horas)],
                "carbon_monoxide": [700.0 + (i % 9) for i in range(horas)],
                "nitrogen_dioxide": [90.0 + (i % 11) for i in range(horas)],
                "sulphur_dioxide": [12.0 + (i % 3) for i in range(horas)],
                "ozone": [80.0 + (i % 13) for i in range(horas)],
                "temperature_2m": [22.0 + (i % 4) for i in range(horas)],
                "relative_humidity_2m": [60.0 + (i % 6) for i in range(horas)],
                "precipitation": [0.0 for _ in range(horas)],
                "wind_speed_10m": [9.0 + (i % 5) for i in range(horas)],
                "pressure_msl": [1012.0 + (i % 3) for i in range(horas)],
            }
        )
        return dados

    def test_limitar_ate_agora_remove_horas_futuras(self) -> None:
        base = self._base_horaria(48)
        agora = pd.Timestamp("2026-10-01 10:30")

        resultado = _limitar_ate_agora(base, "America/Sao_Paulo", agora)

        self.assertEqual(resultado["time"].iloc[-1], pd.Timestamp("2026-10-01 10:00"))

    def test_json_para_dataframe_hourly_rejeita_resposta_sem_hourly(self) -> None:
        with self.assertRaisesRegex(ValueError, "não contém a chave 'hourly'"):
            _json_para_dataframe_hourly({}, "air_quality")

    def test_preparar_linha_mais_recente_retorna_ultima_linha_valida(self) -> None:
        base = self._base_horaria()
        linha = _preparar_linha_mais_recente(base, list(FEATURES_SPRINT4))

        self.assertEqual(len(linha), 1)
        self.assertTrue(set(FEATURES_SPRINT4).issubset(linha.columns))
        self.assertFalse(linha[list(FEATURES_SPRINT4)].isna().any().any())

    def test_prever_proxima_hora_retorna_resumo_com_alerta(self) -> None:
        base = self._base_horaria()
        artefato = {
            "pipeline": _PipelineStub(),
            "features": list(FEATURES_SPRINT4),
            "decision_threshold": 0.3,
            "target_horizon_hours": 1,
        }

        with (
            patch("src.aplicacao.Prever_Proxima_Hora._carregar_config", return_value={}),
            patch("src.aplicacao.Prever_Proxima_Hora._carregar_artefato_modelo", return_value=artefato),
            patch("src.aplicacao.Prever_Proxima_Hora._coletar_dados_recentes", return_value=base),
        ):
            resumo = prever_proxima_hora()

        self.assertEqual(len(resumo), 1)
        self.assertAlmostEqual(
            float(resumo["probabilidade estimada de IQAr > 100"].iloc[0]),
            0.75,
            places=6,
        )
        self.assertEqual(resumo["resultado da regra"].iloc[0], "ALERTA (regra experimental)")

    def test_projetar_janela_futura_retorna_7h_e_24h(self) -> None:
        base = self._base_horaria(96)
        artefato = {
            "pipeline": _PipelineStub(),
            "features": list(FEATURES_SPRINT4),
            "decision_threshold": 0.3,
            "target_horizon_hours": 1,
        }
        horario_base = pd.Timestamp("2026-10-02 12:00:00")

        projecao_7h = _projetar_janela_futura(base, artefato, horario_base, horas_frente=7)
        projecao_24h = _projetar_janela_futura(base, artefato, horario_base, horas_frente=24)

        self.assertEqual(len(projecao_7h), 7)
        self.assertEqual(list(projecao_7h["horizonte"]), [f"+{i}h" for i in range(1, 8)])
        self.assertEqual(len(projecao_24h), 24)
        self.assertEqual(projecao_24h["horizonte"].iloc[0], "+1h")
        self.assertEqual(projecao_24h["horizonte"].iloc[-1], "+24h")
        self.assertEqual(
            projecao_24h["horário do evento previsto"].iloc[0],
            pd.Timestamp("2026-10-02 13:00:00"),
        )
        self.assertEqual(
            projecao_24h["horário do evento previsto"].iloc[-1],
            pd.Timestamp("2026-10-03 12:00:00"),
        )

    def test_projetar_proximas_horas_integra_fluxo_experimental(self) -> None:
        base = self._base_horaria(96)
        artefato = {
            "pipeline": _PipelineStub(),
            "features": list(FEATURES_SPRINT4),
            "decision_threshold": 0.3,
            "target_horizon_hours": 1,
        }
        config = {"location": {"timezone": "America/Sao_Paulo"}}
        agora = pd.Timestamp("2026-10-02 12:15:00")

        with (
            patch("src.aplicacao.Prever_Proxima_Hora._carregar_config", return_value=config),
            patch("src.aplicacao.Prever_Proxima_Hora._carregar_artefato_modelo", return_value=artefato),
            patch("src.aplicacao.Prever_Proxima_Hora._coletar_serie_com_projecao", return_value=base),
        ):
            projecao = projetar_proximas_horas(horas_frente=24, agora=agora)

        self.assertEqual(len(projecao), 24)
        self.assertTrue((projecao["resultado da regra"] == "ALERTA (projeção experimental)").all())


if __name__ == "__main__":
    unittest.main()
