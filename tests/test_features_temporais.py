import unittest

import pandas as pd
from sklearn.naive_bayes import GaussianNB

from src.modelagem.Avaliar_Features_Temporais import (
    _resumir_carga_semanal,
    _resumir_variantes,
    avaliar_lift_sprint4,
    VARIANTE_S3_COMPARAVEL,
    VARIANTE_S4_CANDIDATA,
)
from src.modelagem.Avaliar_Baselines import (
    FEATURES_SPRINT4,
    GRUPOS_ABLACAO_IQAR,
    criar_pipeline_sprint4,
)
from src.transformacao.Calcular_Alvo_IQAr import COLUNA_ALVO, COLUNA_IQAR
from src.transformacao.Features_Temporais import (
    adicionar_diferencas_horarias,
    adicionar_hora_ciclica,
    adicionar_resumos_curto_prazo,
)


class TestFeaturesTemporais(unittest.TestCase):
    def test_pipeline_sprint4_usa_lista_de_features_congelada(self) -> None:
        pipeline = criar_pipeline_sprint4(GaussianNB())
        colunas_pre_processadas = pipeline.named_steps[
            "pre_processamento"
        ].transformers[0][2]

        self.assertEqual(tuple(colunas_pre_processadas), FEATURES_SPRINT4)
        self.assertEqual(
            FEATURES_SPRINT4[-4:],
            (
                "media_3h_ozone",
                "media_3h_pm2_5",
                "delta_2h_ozone",
                "delta_2h_pm2_5",
            ),
        )
        self.assertIsInstance(pipeline.named_steps["classificador"], GaussianNB)

    def test_lift_compara_referencias_e_s3_s4_nos_mesmos_folds(self) -> None:
        periodos = 600
        dados = pd.DataFrame(
            {"time": pd.date_range("2024-01-01", periods=periodos, freq="h")}
        )
        colunas = set(GRUPOS_ABLACAO_IQAR["subindices_sem_iqar_meteorologia"])
        colunas.update({"ozone", "pm2_5", COLUNA_IQAR})
        for deslocamento, coluna in enumerate(sorted(colunas)):
            dados[coluna] = [
                float((indice + deslocamento) % 37)
                for indice in range(periodos)
            ]
        dados[COLUNA_IQAR] = [
            120.0 if indice % 11 < 2 else 40.0
            for indice in range(periodos)
        ]
        dados[COLUNA_ALVO] = pd.array(
            [int(indice % 13 < 2) for indice in range(periodos)],
            dtype="Int64",
        )
        folds = [
            {
                "name": "teste",
                "start": "2024-01-09T08:00:00",
                "end": "2024-01-23T08:00:00",
            }
        ]

        por_fold, resumo, semanal = avaliar_lift_sprint4(dados, folds)

        self.assertEqual(
            set(por_fold["grupo_features"]),
            {
                "dummy_prior",
                "persistencia_iqar_atual",
                VARIANTE_S3_COMPARAVEL,
                VARIANTE_S4_CANDIDATA,
            },
        )
        self.assertEqual(por_fold.groupby("fold").size().to_dict(), {"teste": 4})
        base = resumo.loc[resumo["variante"].eq(VARIANTE_S3_COMPARAVEL)].iloc[0]
        s4 = resumo.loc[resumo["variante"].eq(VARIANTE_S4_CANDIDATA)].iloc[0]
        self.assertAlmostEqual(
            s4["delta_recall_vs_s3"],
            s4["media_recall_classe_1"] - base["media_recall_classe_1"],
        )
        self.assertAlmostEqual(
            s4["delta_f1_vs_s3"],
            s4["media_f1_classe_1"] - base["media_f1_classe_1"],
        )
        self.assertEqual(set(semanal["variante"]), set(resumo["variante"]))

    def test_hora_ciclica_mantem_proximidade_entre_23h_e_meia_noite(self) -> None:
        dados = pd.DataFrame(
            {
                "time": pd.to_datetime(
                    ["2024-01-01 23:00", "2024-01-02 00:00"]
                )
            }
        )

        resultado = adicionar_hora_ciclica(dados)
        diferenca = resultado.loc[0, ["hora_dia_seno", "hora_dia_cosseno"]].to_numpy(
            dtype=float
        ) - resultado.loc[1, ["hora_dia_seno", "hora_dia_cosseno"]].to_numpy(
            dtype=float
        )

        self.assertLess(float((diferenca**2).sum() ** 0.5), 0.3)

    def test_hora_ciclica_rejeita_timestamp_ausente(self) -> None:
        dados = pd.DataFrame({"time": [pd.NaT]})

        with self.assertRaisesRegex(ValueError, "ausentes"):
            adicionar_hora_ciclica(dados)

    def test_diferenca_horaria_usa_valor_atual_e_hora_anterior(self) -> None:
        dados = pd.DataFrame(
            {
                "time": pd.date_range("2024-01-01", periods=3, freq="h"),
                "ozone": [10.0, 14.0, 11.0],
            }
        )

        resultado = adicionar_diferencas_horarias(dados, ("ozone",))

        self.assertTrue(pd.isna(resultado.loc[0, "delta_1h_ozone"]))
        self.assertEqual(resultado["delta_1h_ozone"].iloc[1:].tolist(), [4.0, -3.0])
        self.assertNotIn("delta_1h_ozone", dados.columns)

    def test_rejeita_timestamp_com_lacuna(self) -> None:
        dados = pd.DataFrame(
            {
                "time": pd.to_datetime(
                    ["2024-01-01 00:00", "2024-01-01 02:00"]
                ),
                "ozone": [10.0, 11.0],
            }
        )

        with self.assertRaisesRegex(ValueError, "consecutivos"):
            adicionar_diferencas_horarias(dados, ("ozone",))

    def test_rejeita_coluna_ausente(self) -> None:
        dados = pd.DataFrame(
            {
                "time": pd.date_range("2024-01-01", periods=2, freq="h"),
            }
        )

        with self.assertRaisesRegex(ValueError, "ausentes"):
            adicionar_diferencas_horarias(dados, ("ozone",))

    def test_resumos_curto_prazo_usa_apenas_valores_ate_t(self) -> None:
        dados = pd.DataFrame(
            {
                "time": pd.date_range("2024-01-01", periods=4, freq="h"),
                "ozone": [1.0, 2.0, 4.0, 9.0],
            }
        )

        resultado = adicionar_resumos_curto_prazo(dados, ("ozone",))

        self.assertTrue(pd.isna(resultado.loc[0, "media_3h_ozone"]))
        self.assertTrue(pd.isna(resultado.loc[1, "media_3h_ozone"]))
        self.assertEqual(resultado.loc[2, "media_3h_ozone"], 7 / 3)
        self.assertEqual(resultado.loc[2, "delta_2h_ozone"], 3.0)
        self.assertEqual(resultado.loc[3, "media_3h_ozone"], 5.0)
        self.assertEqual(resultado.loc[3, "delta_2h_ozone"], 7.0)

    def test_resumos_curto_prazo_rejeitam_lacunas(self) -> None:
        dados = pd.DataFrame(
            {
                "time": pd.to_datetime(
                    ["2024-01-01 00:00", "2024-01-01 02:00"]
                ),
                "ozone": [1.0, 2.0],
            }
        )

        with self.assertRaisesRegex(ValueError, "consecutivos"):
            adicionar_resumos_curto_prazo(dados, ("ozone",))

    def test_resumo_semanal_aplica_teto_somente_a_semanas_completas(self) -> None:
        event_time = pd.date_range("2024-01-01", periods=336, freq="h")
        previsoes = pd.DataFrame(
            {
                "variante": "teste",
                "event_time": event_time,
                "y_previsto": 0,
            }
        )
        previsoes.loc[[0, 2, 4, 6], "y_previsto"] = 1
        semanal = _resumir_carga_semanal(previsoes)
        metricas = pd.DataFrame(
            [
                {
                    "grupo_features": "teste",
                    "fold": "2024-Q1",
                    "precisao_classe_1": 0.5,
                    "recall_classe_1": 0.75,
                    "f1_classe_1": 0.6,
                    "tn": 0,
                    "fp": 0,
                    "fn": 0,
                    "tp": 0,
                    "n_validacao": len(previsoes),
                }
            ]
        )

        resumo = _resumir_variantes(metricas, semanal).iloc[0]

        self.assertEqual(resumo["semanas_completas"], 2)
        self.assertEqual(resumo["episodios_alerta_total"], 4)
        self.assertEqual(resumo["max_episodios_em_uma_semana"], 4)
        self.assertEqual(resumo["semanas_com_mais_de_3_episodios"], 1)
