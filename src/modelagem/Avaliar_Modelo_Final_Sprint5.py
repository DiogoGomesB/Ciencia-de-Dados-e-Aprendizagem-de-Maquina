"""Avalia uma vez o modelo/limiar congelado e os baselines no holdout final."""

from pathlib import Path
from typing import Any

import pandas as pd
import yaml
from sklearn.dummy import DummyClassifier

from src.modelagem.Avaliar_Baselines import (
    FEATURES_SPRINT4,
    _calcular_metricas,
    _validar_persistencia,
    criar_pipeline_naive_bayes,
    criar_pipeline_sprint4,
)
from src.modelagem.Avaliar_Features_Temporais import _resumir_carga_semanal
from src.modelagem.Comparar_Modelos_Sprint5 import _classificadores_novos
from src.transformacao.Calcular_Alvo_IQAr import COLUNA_ALVO
from src.transformacao.Features_Temporais import adicionar_resumos_curto_prazo
from src.validacao.Separacao_Temporal import separar_teste_final

COLUNAS_CONTEXTO_CURTO_PRAZO = ("ozone", "pm2_5")
LIMIAR_FINAL_CONGELADO = 0.3
MODELO_FINAL_CONGELADO = "random_forest_balanced"


def avaliar_holdout_final(
    dados: pd.DataFrame,
    inicio_teste: str,
    fim_teste: str,
    horizonte_horas: int = 1,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Faz uma avaliação sem otimização sobre o período final configurado."""
    dados_temporais = adicionar_resumos_curto_prazo(
        dados,
        COLUNAS_CONTEXTO_CURTO_PRAZO,
    )
    dados_temporais["event_time"] = pd.to_datetime(
        dados_temporais["time"],
        errors="raise",
    ) + pd.Timedelta(hours=horizonte_horas)
    treino, teste = separar_teste_final(
        dados_temporais,
        inicio_teste,
        fim_teste,
        horizonte_horas,
    )
    y_treino = treino[COLUNA_ALVO].astype(int)
    y_teste = teste[COLUNA_ALVO].astype(int)
    previsoes: list[pd.DataFrame] = []
    cargas: list[pd.DataFrame] = []
    metricas: list[dict[str, Any]] = []

    dummy = DummyClassifier(strategy="prior")
    dummy.fit(pd.DataFrame(index=treino.index), y_treino)
    predicoes_modelos: dict[str, tuple[Any, Any]] = {
        "dummy_prior": (
            dummy.predict(pd.DataFrame(index=teste.index)),
            None,
        ),
        "persistencia_iqar_atual": (
            _validar_persistencia(teste, "teste_final"),
            None,
        ),
    }
    modelos = {
        "gaussian_naive_bayes": criar_pipeline_naive_bayes(FEATURES_SPRINT4),
        **{
            nome: criar_pipeline_sprint4(classificador)
            for nome, classificador in _classificadores_novos().items()
        },
    }
    for nome, pipeline in modelos.items():
        pipeline.fit(treino[list(FEATURES_SPRINT4)], y_treino)
        features_teste = teste[list(FEATURES_SPRINT4)]
        probabilidades = pipeline.predict_proba(features_teste)[:, 1]
        predicoes_modelos[nome] = (pipeline.predict(features_teste), probabilidades)

    for nome, (y_previsto, probabilidades) in predicoes_modelos.items():
        grupo = (
            "referencia_independente_de_features"
            if nome in {"dummy_prior", "persistencia_iqar_atual"}
            else "features_sprint4"
        )
        variantes = [("predict_padrao", y_previsto)]
        if nome == MODELO_FINAL_CONGELADO:
            if probabilidades is None:
                raise RuntimeError("O modelo final não produziu probabilidades.")
            variantes.append(
                (
                    f"limiar_{LIMIAR_FINAL_CONGELADO:.1f}",
                    (probabilidades >= LIMIAR_FINAL_CONGELADO).astype(int),
                )
            )

        for limiar, previsao in variantes:
            metricas.append(
                _calcular_metricas(
                    y_teste,
                    previsao,
                    fold="teste_final",
                    modelo=nome,
                    grupo_features=grupo,
                    n_treino=len(treino),
                )
                | {"limiar": limiar}
            )
            nome_variante = f"{nome}:{limiar}"
            previsoes_teste = pd.DataFrame(
                {
                    "variante": nome_variante,
                    "modelo": nome,
                    "limiar": limiar,
                    "time": teste["time"].to_numpy(),
                    "event_time": teste["event_time"].to_numpy(),
                    "y_real": y_teste.to_numpy(),
                    "y_previsto": previsao,
                },
                index=teste.index,
            )
            if probabilidades is not None:
                previsoes_teste["probabilidade_classe_1"] = probabilidades
            previsoes.append(previsoes_teste.reset_index(drop=True))
            cargas.append(
                previsoes_teste[["variante", "event_time", "y_previsto"]]
            )

    previsoes_df = pd.concat(previsoes, ignore_index=True)
    erros = previsoes_df.loc[
        previsoes_df["y_real"].ne(previsoes_df["y_previsto"])
    ].copy()
    carga_semanal = _resumir_carga_semanal(
        pd.concat(cargas, ignore_index=True)
    )
    return pd.DataFrame(metricas), previsoes_df, erros, carga_semanal


def main() -> None:
    with Path("config/params.yaml").open("r", encoding="utf-8") as arquivo:
        config = yaml.safe_load(arquivo)
    evaluation = config["evaluation"]
    horizonte_horas = evaluation["target_horizon_hours"]
    periodo = {
        "start_date": config["collection"]["start_date"],
        "end_date": config["collection"]["end_date"],
    }
    caminho_dados = (
        Path(config["paths"]["interim_data"])
        / config["paths"]["labeled_filename"].format(**periodo)
    )
    dados = pd.read_csv(caminho_dados, parse_dates=["time"])
    metricas, previsoes, erros, carga_semanal = avaliar_holdout_final(
        dados,
        evaluation["final_test"]["start"],
        evaluation["final_test"]["end"],
        horizonte_horas,
    )
    pasta_saida = Path("reports/modeling")
    pasta_saida.mkdir(parents=True, exist_ok=True)
    metricas.to_csv(
        pasta_saida / "sprint5_final_test_metrics.csv",
        index=False,
        encoding="utf-8",
    )
    previsoes.to_csv(
        pasta_saida / "sprint5_final_test_predictions.csv",
        index=False,
        encoding="utf-8",
    )
    erros.to_csv(
        pasta_saida / "sprint5_final_test_misclassified_cases.csv",
        index=False,
        encoding="utf-8",
    )
    carga_semanal.to_csv(
        pasta_saida / "sprint5_final_test_alert_burden_by_week.csv",
        index=False,
        encoding="utf-8",
    )
    print("Avaliação final — modelo e limiar congelados antes do teste:")
    print(metricas.to_string(index=False))


if __name__ == "__main__":
    main()
