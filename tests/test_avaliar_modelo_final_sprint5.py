import unittest

import pandas as pd

from src.modelagem.Avaliar_Baselines import FEATURES_SPRINT4
from src.modelagem.Avaliar_Modelo_Final_Sprint5 import (
    LIMIAR_FINAL_CONGELADO,
    MODELO_FINAL_CONGELADO,
    avaliar_holdout_final,
)
from src.transformacao.Calcular_Alvo_IQAr import COLUNA_ALVO, COLUNA_IQAR


class TestAvaliarModeloFinalSprint5(unittest.TestCase):
    def test_avalia_baselines_e_limite_congelado_no_teste_configurado(self) -> None:
        periodos = 24 * 62
        dados = pd.DataFrame(
            {"time": pd.date_range("2024-12-01", periods=periodos, freq="h")}
        )
        for deslocamento, coluna in enumerate(FEATURES_SPRINT4):
            dados[coluna] = [
                float((indice + deslocamento * 3) % 29)
                for indice in range(periodos)
            ]
        dados["ozone"] = [float(indice % 31) for indice in range(periodos)]
        dados["pm2_5"] = [float(indice % 23) for indice in range(periodos)]
        dados[COLUNA_IQAR] = [float(indice % 150) for indice in range(periodos)]
        dados[COLUNA_ALVO] = pd.array(
            [int((indice // 7) % 4 == 0) for indice in range(periodos)],
            dtype="Int64",
        )
        dados.loc[dados.index[-1], COLUNA_ALVO] = pd.NA

        metricas, previsoes, erros, carga = avaliar_holdout_final(
            dados,
            "2025-01-01T00:00:00",
            "2025-02-01T00:00:00",
        )

        self.assertEqual(set(metricas["fold"]), {"teste_final"})
        self.assertEqual(
            set(metricas["modelo"]),
            {
                "dummy_prior",
                "persistencia_iqar_atual",
                "gaussian_naive_bayes",
                "regressao_logistica_balanced",
                MODELO_FINAL_CONGELADO,
            },
        )
        self.assertIn(
            f"limiar_{LIMIAR_FINAL_CONGELADO:.1f}",
            set(metricas["limiar"]),
        )
        previsao_selecionada = previsoes.loc[
            previsoes["variante"].eq(
                f"{MODELO_FINAL_CONGELADO}:limiar_{LIMIAR_FINAL_CONGELADO:.1f}"
            )
        ]
        self.assertEqual(previsao_selecionada["event_time"].min(), pd.Timestamp("2025-01-01"))
        self.assertLess(
            previsao_selecionada["event_time"].max(),
            pd.Timestamp("2025-02-01"),
        )
        self.assertTrue(set(erros["variante"]).issubset(set(previsoes["variante"])))
        self.assertTrue(carga["semana_completa"].any())


if __name__ == "__main__":
    unittest.main()
