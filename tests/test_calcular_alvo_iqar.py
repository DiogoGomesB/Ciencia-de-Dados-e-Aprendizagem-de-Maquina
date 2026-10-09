import unittest

import numpy as np
import pandas as pd

from src.transformacao.Calcular_Alvo_IQAr import (
    COLUNA_ALVO,
    COLUNA_IQAR,
    COLUNAS_SUBINDICE,
    FATOR_CO_UG_M3_PARA_PPM,
    adicionar_alvo_iqar,
    calcular_iqar,
)


def criar_dados(horas: int = 40) -> pd.DataFrame:
    dados = {
        "time": pd.date_range("2025-01-01", periods=horas, freq="h"),
        "pm10": np.zeros(horas),
        "pm2_5": np.zeros(horas),
        "carbon_monoxide": np.zeros(horas),
        "nitrogen_dioxide": np.zeros(horas),
        "sulphur_dioxide": np.zeros(horas),
        "ozone": np.zeros(horas),
    }
    return pd.DataFrame(dados)


class TestCalcularAlvoIQAr(unittest.TestCase):
    def test_subindice_pm10_interpola_pontos_da_tabela_cetesb(self) -> None:
        dados = criar_dados(horas=24)
        for concentracao, indice in (
            (0.0, 0.0),
            (50.0, 40.0),
            (100.0, 80.0),
            (150.0, 120.0),
            (250.0, 200.0),
        ):
            dados["pm10"] = concentracao
            calculado = calcular_iqar(dados)
            self.assertAlmostEqual(calculado["iqar_pm10"].iloc[-1], indice)

    def test_cada_subindice_tem_a_fronteira_correta_para_iqar_100(self) -> None:
        limites = {
            "pm10": 125.0,
            "pm2_5": 62.5,
            "carbon_monoxide": 12.0 / FATOR_CO_UG_M3_PARA_PPM,
            "nitrogen_dioxide": 280.0,
            "sulphur_dioxide": 202.5,
            "ozone": 145.0,
        }

        for poluente, limite in limites.items():
            with self.subTest(poluente=poluente):
                dados = criar_dados(horas=24)
                dados[poluente] = limite
                calculado = calcular_iqar(dados)
                self.assertAlmostEqual(calculado[COLUNA_IQAR].iloc[-1], 100.0)

                rotulado = adicionar_alvo_iqar(dados)
                self.assertEqual(rotulado[COLUNA_ALVO].iloc[-2], 0)

                dados[poluente] = limite + 1e-6
                acima_do_limite = adicionar_alvo_iqar(dados)
                self.assertEqual(acima_do_limite[COLUNA_ALVO].iloc[-2], 1)

    def test_alvo_usa_iqar_da_hora_seguinte(self) -> None:
        dados = criar_dados()
        dados.loc[24, "nitrogen_dioxide"] = 300.0

        calculado = adicionar_alvo_iqar(dados)

        self.assertGreater(calculado[COLUNA_IQAR].iloc[24], 100.0)
        self.assertEqual(calculado[COLUNA_ALVO].iloc[23], 1)
        self.assertEqual(calculado[COLUNA_ALVO].iloc[24], 0)

    def test_janela_incompleta_ou_com_falha_deixa_alvo_indefinido(self) -> None:
        dados = criar_dados()
        dados.loc[10, "pm10"] = np.nan

        calculado = adicionar_alvo_iqar(dados)

        self.assertTrue(pd.isna(calculado[COLUNA_ALVO].iloc[22]))
        self.assertEqual(calculado[COLUNA_ALVO].iloc[34], 0)
        self.assertTrue(pd.isna(calculado[COLUNA_ALVO].iloc[-1]))

    def test_co_e_convertido_de_ug_m3_para_ppm_na_condicao_aprovada(self) -> None:
        dados = criar_dados(horas=24)
        dados["carbon_monoxide"] = 12.0 / FATOR_CO_UG_M3_PARA_PPM

        calculado = calcular_iqar(dados)

        self.assertAlmostEqual(
            calculado[COLUNAS_SUBINDICE["carbon_monoxide"]].iloc[-1],
            100.0,
        )
        rotulado = adicionar_alvo_iqar(dados)
        self.assertEqual(rotulado[COLUNA_ALVO].iloc[-2], 0)

    def test_rejeita_timestamp_nao_horario(self) -> None:
        dados = criar_dados()
        dados.loc[3, "time"] += pd.Timedelta(minutes=30)

        with self.assertRaisesRegex(ValueError, "intervalo de 1 hora"):
            calcular_iqar(dados)

    def test_rejeita_concentracoes_negativas(self) -> None:
        dados = criar_dados()
        dados.loc[3, "pm10"] = -1.0

        with self.assertRaisesRegex(ValueError, "concentrações negativas"):
            calcular_iqar(dados)


if __name__ == "__main__":
    unittest.main()
