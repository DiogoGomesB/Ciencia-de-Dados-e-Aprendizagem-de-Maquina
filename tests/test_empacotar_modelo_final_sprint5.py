import io
import unittest

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline

from src.modelagem.Avaliar_Baselines import FEATURES_SPRINT4
from src.modelagem.Empacotar_Modelo_Final_Sprint5 import treinar_modelo_final
from src.transformacao.Calcular_Alvo_IQAr import COLUNA_ALVO, COLUNA_IQAR


class TestEmpacotarModeloFinalSprint5(unittest.TestCase):
    def test_pacote_contem_pipeline_treinado_features_e_limiar(self) -> None:
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

        artefato = treinar_modelo_final(
            dados,
            "2025-01-01T00:00:00",
            "2025-02-01T00:00:00",
        )
        arquivo = io.BytesIO()
        joblib.dump(artefato, arquivo)
        arquivo.seek(0)
        recarregado = joblib.load(arquivo)

        self.assertIsInstance(recarregado["pipeline"], Pipeline)
        self.assertIsInstance(
            recarregado["pipeline"].named_steps["classificador"],
            RandomForestClassifier,
        )
        self.assertEqual(recarregado["features"], list(FEATURES_SPRINT4))
        self.assertEqual(recarregado["decision_threshold"], 0.3)
        self.assertEqual(recarregado["training_rows"], 743)


if __name__ == "__main__":
    unittest.main()
