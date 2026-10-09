import unittest

import pandas as pd

from src.modelagem.Comparar_Modelos_Sprint5 import (
    THRESHOLDS,
    comparar_modelos_validacao,
)
from src.transformacao.Calcular_Alvo_IQAr import COLUNA_ALVO, COLUNA_IQAR
from src.modelagem.Avaliar_Baselines import FEATURES_SPRINT4


class TestCompararModelosSprint5(unittest.TestCase):
    def test_compara_modelos_e_limites_somente_no_fold_2024_q4(self) -> None:
        periodos = 24 * 365 * 3
        tempos = pd.date_range("2022-01-01", periods=periodos, freq="h")
        dados = pd.DataFrame({"time": tempos})
        for deslocamento, coluna in enumerate(FEATURES_SPRINT4):
            dados[coluna] = [
                float((indice + deslocamento * 7) % 43)
                for indice in range(periodos)
            ]
        dados["ozone"] = [float(indice % 31) for indice in range(periodos)]
        dados["pm2_5"] = [float(indice % 23) for indice in range(periodos)]
        dados[COLUNA_IQAR] = [float(indice % 150) for indice in range(periodos)]
        dados[COLUNA_ALVO] = pd.array(
            [int((indice // 13) % 7 == 0) for indice in range(periodos)],
            dtype="Int64",
        )
        folds = [
            {
                "name": "2024-Q3",
                "start": "2024-07-01T00:00:00",
                "end": "2024-10-01T00:00:00",
            },
            {
                "name": "2024-Q4",
                "start": "2024-10-01T00:00:00",
                "end": "2025-01-01T00:00:00",
            },
        ]

        resultados, tradeoffs, previsoes, carga_semanal = comparar_modelos_validacao(
            dados,
            folds,
        )

        self.assertEqual(
            set(resultados["modelo"]),
            {
                "dummy_prior",
                "persistencia_iqar_atual",
                "gaussian_naive_bayes",
                "regressao_logistica_balanced",
                "random_forest_balanced",
            },
        )
        self.assertEqual(set(resultados["fold"]), {"2024-Q4"})
        self.assertEqual(
            set(tradeoffs["limiar"]),
            set(THRESHOLDS),
        )
        self.assertEqual(set(tradeoffs["modelo"]), set(resultados["modelo"]) - {
            "dummy_prior",
            "persistencia_iqar_atual",
        })
        self.assertEqual(set(previsoes["fold"]), {"2024-Q4"})
        self.assertTrue(
            carga_semanal["variante"].str.contains("limiar_0.7").any()
        )
        self.assertEqual(
            set(previsoes.loc[previsoes["modelo"].eq("random_forest_balanced"), "time"]),
            set(
                dados.loc[
                    dados["time"].ge("2024-09-30T23:00:00")
                    & dados["time"].lt("2024-12-31T23:00:00"),
                    "time",
                ]
            ),
        )

    def test_rejeita_config_sem_validacao_q4(self) -> None:
        dados = pd.DataFrame()

        with self.assertRaisesRegex(ValueError, "2024-Q4"):
            comparar_modelos_validacao(dados, [])


if __name__ == "__main__":
    unittest.main()
