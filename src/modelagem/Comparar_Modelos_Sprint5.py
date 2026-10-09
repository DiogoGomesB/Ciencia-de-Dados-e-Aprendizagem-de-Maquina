"""Compara classificadores na validação temporal da Sprint 5 sem usar o holdout."""

from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from src.modelagem.Avaliar_Baselines import (
    FEATURES_SPRINT4,
    _calcular_metricas,
    _carregar_desenvolvimento,
    _validar_persistencia,
    criar_pipeline_naive_bayes,
    criar_pipeline_sprint4,
)
from src.modelagem.Avaliar_Features_Temporais import _resumir_carga_semanal
from src.transformacao.Calcular_Alvo_IQAr import COLUNA_ALVO
from src.transformacao.Features_Temporais import adicionar_resumos_curto_prazo
from src.validacao.Separacao_Temporal import criar_folds_temporais

THRESHOLDS = (0.3, 0.5, 0.7)
FOLD_VALIDACAO_SPRINT5 = "2024-Q4"
COLUNAS_CONTEXTO_CURTO_PRAZO = ("ozone", "pm2_5")


def _classificadores_novos() -> dict[str, Any]:
    return {
        "regressao_logistica_balanced": LogisticRegression(
            class_weight="balanced",
            max_iter=1000,
            random_state=42,
        ),
        "random_forest_balanced": RandomForestClassifier(
            n_estimators=300,
            class_weight="balanced",
            min_samples_leaf=2,
            n_jobs=-1,
            random_state=42,
        ),
    }


def comparar_modelos_validacao(
    dados: pd.DataFrame,
    folds_config: list[dict[str, str]],
    horizonte_horas: int = 1,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Avalia três referências e dois modelos novos em um fold temporal final."""
    folds = [fold for fold in folds_config if fold["name"] == FOLD_VALIDACAO_SPRINT5]
    if len(folds) != 1:
        raise ValueError(
            f"É necessário configurar exatamente um fold '{FOLD_VALIDACAO_SPRINT5}'."
        )
    dados_temporais = adicionar_resumos_curto_prazo(
        dados,
        COLUNAS_CONTEXTO_CURTO_PRAZO,
    )
    dados_temporais["event_time"] = pd.to_datetime(
        dados_temporais["time"],
        errors="raise",
    ) + pd.Timedelta(hours=horizonte_horas)
    treino, validacao = criar_folds_temporais(
        dados_temporais,
        folds,
        horizonte_horas,
    )[FOLD_VALIDACAO_SPRINT5]
    y_treino = treino[COLUNA_ALVO].astype(int)
    y_validacao = validacao[COLUNA_ALVO].astype(int)
    resultados: list[dict[str, int | float | str]] = []
    tradeoffs: list[dict[str, int | float | str]] = []
    previsoes: list[pd.DataFrame] = []
    previsoes_carga: list[pd.DataFrame] = []

    dummy = DummyClassifier(strategy="prior")
    dummy.fit(pd.DataFrame(index=treino.index), y_treino)
    previsoes_modelos: dict[str, tuple[Any, Any]] = {
        "dummy_prior": (
            dummy.predict(pd.DataFrame(index=validacao.index)),
            None,
        ),
        "persistencia_iqar_atual": (
            _validar_persistencia(validacao, FOLD_VALIDACAO_SPRINT5),
            None,
        ),
    }

    modelos: dict[str, Any] = {
        "gaussian_naive_bayes": criar_pipeline_naive_bayes(FEATURES_SPRINT4),
        **{
            nome: criar_pipeline_sprint4(classificador)
            for nome, classificador in _classificadores_novos().items()
        },
    }
    for nome, pipeline in modelos.items():
        pipeline.fit(treino[list(FEATURES_SPRINT4)], y_treino)
        probabilidades = pipeline.predict_proba(
            validacao[list(FEATURES_SPRINT4)]
        )[:, 1]
        previsoes_modelos[nome] = (
            pipeline.predict(validacao[list(FEATURES_SPRINT4)]),
            probabilidades,
        )

        for limiar in THRESHOLDS:
            y_limiar = (probabilidades >= limiar).astype(int)
            tradeoffs.append(
                _calcular_metricas(
                    y_validacao,
                    y_limiar,
                    fold=FOLD_VALIDACAO_SPRINT5,
                    modelo=nome,
                    grupo_features="features_sprint4",
                    n_treino=len(treino),
                )
                | {"limiar": limiar}
            )

    for nome, (y_previsto, probabilidades) in previsoes_modelos.items():
        metricas = _calcular_metricas(
            y_validacao,
            y_previsto,
            fold=FOLD_VALIDACAO_SPRINT5,
            modelo=nome,
            grupo_features=(
                "referencia_independente_de_features"
                if nome in {"dummy_prior", "persistencia_iqar_atual"}
                else "features_sprint4"
            ),
            n_treino=len(treino),
        )
        resultados.append(metricas | {"limiar": "predict_padrao"})
        previsoes_fold = pd.DataFrame(
            {
                "fold": FOLD_VALIDACAO_SPRINT5,
                "modelo": nome,
                "time": validacao["time"].to_numpy(),
                "event_time": validacao["event_time"].to_numpy(),
                "y_real": y_validacao.to_numpy(),
                "y_previsto": y_previsto,
            },
            index=validacao.index,
        )
        if probabilidades is not None:
            previsoes_fold["probabilidade_classe_1"] = probabilidades
        previsoes.append(previsoes_fold.reset_index(drop=True))
        previsoes_carga.append(
            pd.DataFrame(
                {
                    "variante": f"{nome}:predict_padrao",
                    "event_time": validacao["event_time"].to_numpy(),
                    "y_previsto": y_previsto,
                }
            )
        )
        if probabilidades is not None:
            for limiar in THRESHOLDS:
                previsoes_carga.append(
                    pd.DataFrame(
                        {
                            "variante": f"{nome}:limiar_{limiar:.1f}",
                            "event_time": validacao["event_time"].to_numpy(),
                            "y_previsto": (probabilidades >= limiar).astype(int),
                        }
                    )
                )

    return (
        pd.DataFrame(resultados),
        pd.DataFrame(tradeoffs),
        pd.concat(previsoes, ignore_index=True),
        _resumir_carga_semanal(pd.concat(previsoes_carga, ignore_index=True)),
    )


def main() -> None:
    dados, evaluation, horizonte_horas = _carregar_desenvolvimento()
    resultados, tradeoffs, previsoes, carga_semanal = comparar_modelos_validacao(
        dados,
        evaluation["validation_folds"],
        horizonte_horas,
    )
    pasta_saida = Path("reports/modeling")
    pasta_saida.mkdir(parents=True, exist_ok=True)
    resultados.to_csv(
        pasta_saida / "sprint5_validation_metrics.csv",
        index=False,
        encoding="utf-8",
    )
    tradeoffs.to_csv(
        pasta_saida / "sprint5_validation_threshold_tradeoff.csv",
        index=False,
        encoding="utf-8",
    )
    previsoes.to_csv(
        pasta_saida / "sprint5_validation_predictions.csv",
        index=False,
        encoding="utf-8",
    )
    carga_semanal.to_csv(
        pasta_saida / "sprint5_validation_alert_burden_by_week.csv",
        index=False,
        encoding="utf-8",
    )
    print("Métricas na validação temporal 2024-Q4:")
    print(resultados.to_string(index=False))
    print("\nTrade-off de limiares (validação somente):")
    print(tradeoffs.to_string(index=False))


if __name__ == "__main__":
    main()
