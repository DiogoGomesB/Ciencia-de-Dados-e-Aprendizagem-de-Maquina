import unittest

import numpy as np
import pandas as pd

from src.modelagem.Avaliar_Baselines import (
    GRUPOS_ABLACAO_IQAR,
    GRUPOS_EXPERIMENTOS,
    GRUPOS_FEATURES,
    _calcular_metricas,
    analisar_tradeoff_limiares,
    criar_folds_internos_limiar,
    contar_episodios_alerta,
    criar_tabela_erros,
    criar_pipeline_naive_bayes,
    executar_experimentos,
    resumir_erros_temporais,
    resumir_tradeoff_limiares,
)
from src.transformacao.Calcular_Alvo_IQAr import COLUNA_ALVO, COLUNA_IQAR


class TestAvaliarBaselines(unittest.TestCase):
    def test_grupos_de_features_correspondem_ao_protocolo_aprovado(self) -> None:
        self.assertEqual(len(GRUPOS_FEATURES), 3)
        self.assertEqual(len(GRUPOS_ABLACAO_IQAR), 2)
        self.assertEqual(len(GRUPOS_EXPERIMENTOS), 5)
        self.assertEqual(
            GRUPOS_ABLACAO_IQAR["subindices_sem_iqar_meteorologia"],
            tuple(
                coluna
                for coluna in GRUPOS_FEATURES["subindices_meteorologia"]
                if coluna != COLUNA_IQAR
            ),
        )
        self.assertEqual(
            GRUPOS_ABLACAO_IQAR["poluentes_subindices_sem_iqar_meteorologia"],
            tuple(
                coluna
                for coluna in GRUPOS_FEATURES["poluentes_subindices_meteorologia"]
                if coluna != COLUNA_IQAR
            ),
        )
        self.assertEqual(
            len(GRUPOS_FEATURES["poluentes_brutos_meteorologia"]),
            len(GRUPOS_FEATURES["subindices_meteorologia"]) - 1,
        )
        self.assertEqual(
            len(GRUPOS_FEATURES["poluentes_subindices_meteorologia"]),
            len(GRUPOS_FEATURES["poluentes_brutos_meteorologia"])
            + len(GRUPOS_FEATURES["subindices_meteorologia"])
            - 5,
        )
        self.assertTrue(
            set(GRUPOS_FEATURES["poluentes_brutos_meteorologia"]).isdisjoint(
                {"iqar", "iqar_ozone"}
            )
        )
        self.assertTrue(
            all(
                "time" not in colunas and COLUNA_ALVO not in colunas
                for colunas in GRUPOS_FEATURES.values()
            )
        )

    def test_pipeline_imputa_escalona_e_produz_predicoes(self) -> None:
        pipeline = criar_pipeline_naive_bayes(("feature_a", "feature_b"))
        treino = pd.DataFrame(
            {
                "feature_a": [0.0, 1.0, 2.0, 3.0],
                "feature_b": [1.0, np.nan, 3.0, 4.0],
            }
        )
        pipeline.fit(treino, [0, 0, 1, 1])

        previsoes = pipeline.predict(
            pd.DataFrame({"feature_a": [1.5], "feature_b": [np.nan]})
        )

        self.assertEqual(previsoes.shape, (1,))
        self.assertIn(previsoes[0], (0, 1))
        self.assertEqual(
            pipeline.named_steps["pre_processamento"]
            .named_transformers_["numericas"]
            .named_steps["imputador"]
            .statistics_[1],
            3.0,
        )

    def test_metricas_reportam_classes_e_matriz_de_confusao(self) -> None:
        metricas = _calcular_metricas(
            [0, 0, 1, 1],
            [0, 1, 0, 1],
            fold="2024-Q1",
            modelo="teste",
            grupo_features="teste",
            n_treino=10,
        )

        self.assertEqual(
            (metricas["tn"], metricas["fp"], metricas["fn"], metricas["tp"]),
            (1, 1, 1, 1),
        )
        self.assertEqual(metricas["recall_classe_1"], 0.5)
        self.assertEqual(metricas["precisao_classe_0"], 0.5)

    def test_resumo_temporal_calcula_taxas_com_denominadores_da_classe(self) -> None:
        previsoes = pd.DataFrame(
            {
                "fold": ["2024-Q1"] * 4,
                "modelo": ["modelo"] * 4,
                "grupo_features": ["grupo"] * 4,
                "event_time": pd.to_datetime(
                    [
                        "2024-01-01 10:00",
                        "2024-01-01 10:00",
                        "2024-02-01 10:00",
                        "2024-02-01 11:00",
                    ]
                ),
                "y_real": [0, 1, 0, 1],
                "y_previsto": [1, 0, 0, 1],
            }
        )

        resumo = resumir_erros_temporais(previsoes, "mes")

        self.assertEqual(resumo.loc[0, "negativos"], 1)
        self.assertEqual(resumo.loc[0, "falsos_positivos"], 1)
        self.assertEqual(resumo.loc[0, "taxa_falso_positivo"], 1.0)
        self.assertEqual(resumo.loc[0, "falsos_negativos"], 1)
        self.assertEqual(resumo.loc[0, "taxa_falso_negativo"], 1.0)

    def test_tradeoff_usa_somente_trimestre_anterior_ao_fold_externo(self) -> None:
        tempos = pd.date_range("2023-12-29 00:00", periods=72, freq="h")
        dados = pd.DataFrame({"time": tempos})
        colunas = {
            coluna for grupo in GRUPOS_EXPERIMENTOS.values() for coluna in grupo
        }
        for deslocamento, coluna in enumerate(sorted(colunas)):
            dados[coluna] = [
                float(indice % 12 + deslocamento)
                for indice in range(len(dados))
            ]
        dados[COLUNA_IQAR] = [float(indice % 2 * 120) for indice in range(len(dados))]
        dados[COLUNA_ALVO] = pd.array(
            [indice % 2 for indice in range(len(dados))],
            dtype="Int64",
        )
        dados["event_time"] = dados["time"] + pd.Timedelta(hours=1)

        tradeoff, semanal = analisar_tradeoff_limiares(
            dados,
            [
                {
                    "name": "fold-externo",
                    "start": "2024-01-01T00:00:00",
                    "end": "2024-01-02T00:00:00",
                }
            ],
            limiares=(0.0, 0.5, 1.0),
        )

        self.assertEqual(len(tradeoff), len(GRUPOS_EXPERIMENTOS) * 3)
        self.assertTrue(
            tradeoff["validacao_interna_fim_exclusivo"]
            .eq("2024-01-01T00:00:00")
            .all()
        )
        limiar_zero = tradeoff.loc[tradeoff["limiar"].eq(0.0)]
        self.assertTrue(limiar_zero["recall_classe_1"].eq(1.0).all())
        self.assertTrue(
            limiar_zero["fp"].eq(limiar_zero["suporte_classe_0"]).all()
        )
        self.assertIn("episodios_iniciados", semanal.columns)
        semanal_grupo = semanal.loc[
            semanal["grupo_features"].eq("poluentes_brutos_meteorologia")
            & semanal["limiar"].eq(0.5)
        ]
        self.assertEqual(semanal_grupo["horas_validacao"].sum(), 24)
        total_grupo = tradeoff.loc[
            tradeoff["grupo_features"].eq("poluentes_brutos_meteorologia")
            & tradeoff["limiar"].eq(0.5),
            "episodios_alerta",
        ].sum()
        self.assertEqual(
            semanal_grupo["episodios_iniciados"].sum(),
            total_grupo,
        )

    def test_tradeoff_rejeita_limiar_fora_do_intervalo(self) -> None:
        with self.assertRaises(ValueError):
            analisar_tradeoff_limiares(
                pd.DataFrame(),
                [],
                limiares=(-0.1,),
            )

    def test_resumo_tradeoff_inclui_carga_de_alertas(self) -> None:
        resultados = pd.DataFrame(
            [
                {
                    "fold": "2024-Q1",
                    "modelo": "modelo",
                    "grupo_features": "grupo",
                    "limiar": 0.5,
                    "precisao_classe_1": 0.5,
                    "recall_classe_1": 0.75,
                    "f1_classe_1": 0.6,
                    "tn": 2,
                    "fp": 2,
                    "fn": 1,
                    "tp": 3,
                    "suporte_classe_0": 4,
                    "suporte_classe_1": 4,
                    "alertas": 5,
                    "episodios_alerta": 2,
                    "n_validacao": 8,
                }
            ]
        )
        resultados_semanais = pd.DataFrame(
            [
                {
                    "semana_inicio": pd.Timestamp("2024-01-01"),
                    "episodios_iniciados": 2,
                    "horas_alerta": 2,
                    "fold": "2024-Q1",
                    "modelo": "modelo",
                    "grupo_features": "grupo",
                    "limiar": 0.5,
                },
                {
                    "semana_inicio": pd.Timestamp("2024-01-08"),
                    "episodios_iniciados": 4,
                    "horas_alerta": 3,
                    "fold": "2024-Q1",
                    "modelo": "modelo",
                    "grupo_features": "grupo",
                    "limiar": 0.5,
                },
            ]
        )

        resumo = resumir_tradeoff_limiares(
            resultados,
            resultados_semanais,
        ).iloc[0]

        self.assertEqual(resumo["alertas_total"], 5)
        self.assertEqual(resumo["episodios_alerta_total"], 6)
        self.assertEqual(resumo["alertas_por_1000_horas"], 625.0)
        self.assertEqual(resumo["episodios_alerta_por_1000_horas"], 750.0)
        self.assertEqual(resumo["episodios_por_semana_media"], 3.0)
        self.assertEqual(resumo["proporcao_falsos_alertas"], 0.4)
        self.assertEqual(resumo["taxa_falso_negativo_agregada"], 0.25)
        self.assertEqual(resumo["max_episodios_em_uma_semana"], 4)
        self.assertEqual(resumo["max_horas_alerta_em_uma_semana"], 3)
        self.assertEqual(resumo["semanas_com_mais_de_3_episodios"], 1)
        resumo_por_fold = resumir_tradeoff_limiares(resultados).iloc[0]
        self.assertEqual(resumo_por_fold["episodios_alerta_total"], 2)
        self.assertEqual(
            resumo_por_fold["episodios_alerta_por_1000_horas"],
            250.0,
        )

    def test_conta_episodios_positivos_separados_por_negativo_ou_lacuna(self) -> None:
        horarios = pd.date_range("2024-01-01", periods=9, freq="h").delete(6)

        episodios = contar_episodios_alerta(
            [0, 1, 1, 0, 1, 1, 1, 0],
            horarios,
        )

        self.assertEqual(episodios, 3)

    def test_folds_internos_usam_trimestres_de_calendario_sem_sobreposicao(self) -> None:
        folds_internos = criar_folds_internos_limiar(
            [
                {
                    "name": "2024-Q1",
                    "start": "2024-01-01T00:00:00",
                    "end": "2024-04-01T00:00:00",
                },
                {
                    "name": "2024-Q2",
                    "start": "2024-04-01T00:00:00",
                    "end": "2024-07-01T00:00:00",
                },
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
        )

        self.assertEqual(
            [fold["start"] for fold in folds_internos],
            [
                "2023-10-01T00:00:00",
                "2024-01-01T00:00:00",
                "2024-04-01T00:00:00",
                "2024-07-01T00:00:00",
            ],
        )
        self.assertEqual(
            [fold["end"] for fold in folds_internos],
            [
                "2024-01-01T00:00:00",
                "2024-04-01T00:00:00",
                "2024-07-01T00:00:00",
                "2024-10-01T00:00:00",
            ],
        )

    def test_avaliacao_usa_somente_janelas_de_validacao_configuradas(self) -> None:
        tempos = pd.date_range("2023-12-31 20:00", periods=9, freq="h")
        dados = pd.DataFrame({"time": tempos})
        colunas = {
            coluna for grupo in GRUPOS_EXPERIMENTOS.values() for coluna in grupo
        }
        for deslocamento, coluna in enumerate(sorted(colunas)):
            dados[coluna] = [float(indice + deslocamento) for indice in range(9)]
        dados[COLUNA_IQAR] = [0, 0, 0, 120, 120, 0, 120, 0, 120]
        dados[COLUNA_ALVO] = pd.array(
            [0, 0, 1, 1, 0, 1, 0, 1, 1],
            dtype="Int64",
        )
        dados["event_time"] = dados["time"] + pd.Timedelta(hours=1)
        resultado, previsoes = executar_experimentos(
            dados,
            [
                {
                    "name": "2024-Q1",
                    "start": "2024-01-01T00:00:00",
                    "end": "2024-01-01T04:00:00",
                }
            ],
        )

        self.assertEqual(set(resultado["modelo"]), {
            "dummy_prior",
            "persistencia_iqar_atual",
            "gaussian_naive_bayes",
        })
        self.assertEqual(len(previsoes), 4 * 7)
        self.assertLess(
            previsoes["event_time"].max(),
            pd.Timestamp("2025-01-01"),
        )
        self.assertEqual(
            set(resultado.loc[resultado["modelo"].eq("gaussian_naive_bayes"), "grupo_features"]),
            set(GRUPOS_EXPERIMENTOS),
        )
        persistencia = resultado.loc[
            resultado["modelo"].eq("persistencia_iqar_atual")
        ].iloc[0]
        self.assertEqual(
            (
                persistencia["tn"],
                persistencia["fp"],
                persistencia["fn"],
                persistencia["tp"],
            ),
            (0, 2, 1, 1),
        )
        casos_incorretos = criar_tabela_erros(dados, previsoes)
        self.assertTrue(casos_incorretos["y_real"].ne(casos_incorretos["y_previsto"]).all())
        self.assertIn("iqar", casos_incorretos.columns)
        self.assertEqual(
            set(casos_incorretos["tipo_erro"]),
            {"falso_positivo", "falso_negativo"},
        )


if __name__ == "__main__":
    unittest.main()
