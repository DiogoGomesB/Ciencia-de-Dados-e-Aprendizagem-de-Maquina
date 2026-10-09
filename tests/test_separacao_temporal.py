import unittest

import pandas as pd

from src.transformacao.Calcular_Alvo_IQAr import COLUNA_ALVO
from src.validacao.Separacao_Temporal import (
    criar_folds_temporais,
    separar_teste_final,
)


def criar_dados(
    inicio: str,
    rotulos: list[int | None],
) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "time": pd.date_range(inicio, periods=len(rotulos), freq="h"),
            "feature": range(len(rotulos)),
            COLUNA_ALVO: pd.array(rotulos, dtype="Int64"),
        }
    )


class TestSeparacaoTemporal(unittest.TestCase):
    def test_fold_usa_horario_do_rotulo_e_ignora_rotulos_indefinidos(self) -> None:
        dados = criar_dados(
            "2023-12-31 21:00",
            [0, 0, 1, 1, 0, 1, None],
        )

        folds = criar_folds_temporais(
            dados,
            [
                {
                    "name": "2024-Q1",
                    "start": "2024-01-01T00:00:00",
                    "end": "2024-01-01T03:00:00",
                }
            ],
        )
        treino, validacao = folds["2024-Q1"]

        self.assertEqual(len(treino), 2)
        self.assertEqual(treino["time"].iloc[-1], pd.Timestamp("2023-12-31 22:00"))
        self.assertEqual(len(validacao), 3)
        self.assertEqual(validacao["time"].iloc[0], pd.Timestamp("2023-12-31 23:00"))
        self.assertEqual(validacao[COLUNA_ALVO].tolist(), [1, 1, 0])

    def test_treino_expande_incluindo_validacoes_anteriores(self) -> None:
        dados = criar_dados(
            "2023-12-31 21:00",
            [0, 0, 1, 1, 0, 1, 0],
        )

        folds = criar_folds_temporais(
            dados,
            [
                {
                    "name": "2024-Q1",
                    "start": "2024-01-01T00:00:00",
                    "end": "2024-01-01T03:00:00",
                },
                {
                    "name": "2024-Q2",
                    "start": "2024-01-01T03:00:00",
                    "end": "2024-01-01T06:00:00",
                },
            ],
        )

        treino_1, validacao_1 = folds["2024-Q1"]
        treino_2, validacao_2 = folds["2024-Q2"]
        self.assertEqual(len(treino_1), 2)
        self.assertEqual(len(validacao_1), 3)
        self.assertEqual(len(treino_2), 5)
        self.assertEqual(len(validacao_2), 2)
        self.assertTrue(set(validacao_1.index).issubset(set(treino_2.index)))

    def test_teste_final_separa_pelo_instante_previsto(self) -> None:
        dados = criar_dados(
            "2023-12-31 21:00",
            [0, 0, 1, 1, 0, 1, None],
        )

        treino, teste = separar_teste_final(
            dados,
            "2024-01-01T00:00:00",
            "2024-01-01T04:00:00",
        )

        self.assertEqual(len(treino), 2)
        self.assertEqual(len(teste), 4)
        self.assertEqual(teste["time"].iloc[0], pd.Timestamp("2023-12-31 23:00"))

    def test_rejeita_folds_sobrepostos(self) -> None:
        dados = criar_dados("2023-12-31 21:00", [0, 0, 1, 1, 0, 1])
        folds = [
            {
                "name": "fold-1",
                "start": "2024-01-01T00:00:00",
                "end": "2024-01-01T03:00:00",
            },
            {
                "name": "fold-2",
                "start": "2024-01-01T02:00:00",
                "end": "2024-01-01T04:00:00",
            },
        ]

        with self.assertRaisesRegex(ValueError, "ordenados e não sobrepostos"):
            criar_folds_temporais(dados, folds)


if __name__ == "__main__":
    unittest.main()
