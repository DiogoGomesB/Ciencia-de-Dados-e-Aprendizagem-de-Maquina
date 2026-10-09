from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.naive_bayes import GaussianNB

from src.modelagem.Avaliar_Baselines import (
    FEATURES_SPRINT4,
    GRUPOS_ABLACAO_IQAR,
    _validar_persistencia,
    _calcular_metricas,
    _carregar_desenvolvimento,
    _mascara_inicio_episodios_alerta,
    criar_pipeline_naive_bayes,
    criar_pipeline_sprint4,
)
from src.transformacao.Features_Temporais import (
    adicionar_diferencas_horarias,
    adicionar_hora_ciclica,
    adicionar_resumos_curto_prazo,
)
from src.transformacao.Calcular_Alvo_IQAr import COLUNA_ALVO
from src.validacao.Separacao_Temporal import criar_folds_temporais

COLUNAS_DELTA_SUBINDICES = ("iqar_ozone", "iqar_pm2_5")
COLUNAS_DELTA_METEOROLOGIA = (
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "wind_speed_10m",
    "pressure_msl",
)
COLUNAS_DELTA_POLUENTES_BRUTOS = ("ozone", "pm2_5")
COLUNAS_POLUENTES_CURTO_PRAZO = ("ozone", "pm2_5")
VARIANTES_DELTA = {
    "baseline_atual": (),
    "hora_dia_ciclica": (),
    "delta_subindices_ozone_pm25": COLUNAS_DELTA_SUBINDICES,
    "delta_meteorologia": COLUNAS_DELTA_METEOROLOGIA,
    "delta_subindices_e_meteorologia": (
        *COLUNAS_DELTA_SUBINDICES,
        *COLUNAS_DELTA_METEOROLOGIA,
    ),
    "delta_poluentes_brutos_ozone_pm25": COLUNAS_DELTA_POLUENTES_BRUTOS,
}
VARIANTES_CURTO_PRAZO = {
    "baseline_atual": (),
    "media_3h_poluentes_brutos_ozone_pm25": ("media",),
    "delta_2h_poluentes_brutos_ozone_pm25": ("delta",),
    "media_3h_e_delta_2h_poluentes_brutos_ozone_pm25": ("media", "delta"),
}
GRUPO_BASE = "subindices_sem_iqar_meteorologia"
VARIANTE_S3_COMPARAVEL = "naive_bayes_s3_subindices_sem_iqar"
VARIANTE_S4_CANDIDATA = "naive_bayes_s4_media3h_delta2h_ozone_pm25"
MAX_EPISODIOS_SEMANA = 3


def _preparar_features_temporais(dados: pd.DataFrame) -> pd.DataFrame:
    """Cria apenas variações de uma hora para os candidatos desta triagem."""
    colunas = tuple(
        dict.fromkeys(
            coluna
            for variante in VARIANTES_DELTA.values()
            for coluna in variante
        )
    )
    return adicionar_diferencas_horarias(dados, colunas)


def avaliar_variantes_curto_prazo(
    dados: pd.DataFrame,
    folds_config: list[dict[str, str]],
    horizonte_horas: int = 1,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Compara resumos causais de 3h em folds de desenvolvimento."""
    if not folds_config:
        raise ValueError("É necessário configurar folds temporais para avaliação.")

    dados_temporais = adicionar_resumos_curto_prazo(
        dados,
        COLUNAS_POLUENTES_CURTO_PRAZO,
    )
    dados_temporais["event_time"] = pd.to_datetime(
        dados_temporais["time"],
        errors="raise",
    ) + pd.Timedelta(hours=horizonte_horas)
    grupos = criar_folds_temporais(
        dados_temporais,
        folds_config,
        horizonte_horas,
    )
    colunas_base = GRUPOS_ABLACAO_IQAR[GRUPO_BASE]
    metricas: list[dict[str, Any]] = []
    previsoes: list[pd.DataFrame] = []

    for nome_fold, (treino, validacao) in grupos.items():
        y_treino = treino[COLUNA_ALVO].astype(int)
        y_validacao = validacao[COLUNA_ALVO].astype(int)
        for nome_variante, componentes in VARIANTES_CURTO_PRAZO.items():
            features = list(colunas_base)
            if "media" in componentes:
                features.extend(
                    f"media_3h_{coluna}"
                    for coluna in COLUNAS_POLUENTES_CURTO_PRAZO
                )
            if "delta" in componentes:
                features.extend(
                    f"delta_2h_{coluna}"
                    for coluna in COLUNAS_POLUENTES_CURTO_PRAZO
                )
            pipeline = criar_pipeline_naive_bayes(features)
            pipeline.fit(treino[features], y_treino)
            y_previsto = pipeline.predict(validacao[features])
            metricas.append(
                _calcular_metricas(
                    y_validacao,
                    y_previsto,
                    fold=nome_fold,
                    modelo="gaussian_naive_bayes",
                    grupo_features=nome_variante,
                    n_treino=len(treino),
                )
            )
            previsoes.append(
                pd.DataFrame(
                    {
                        "fold": nome_fold,
                        "variante": nome_variante,
                        "time": validacao["time"].to_numpy(),
                        "event_time": validacao["event_time"].to_numpy(),
                        "y_real": y_validacao.to_numpy(),
                        "y_previsto": y_previsto,
                    }
                )
            )

    resultados = pd.DataFrame(metricas)
    previsoes_df = pd.concat(previsoes, ignore_index=True)
    semanal = _resumir_carga_semanal(previsoes_df)
    resumo = _resumir_variantes(resultados, semanal)
    return resultados, resumo, semanal


def avaliar_lift_sprint4(
    dados: pd.DataFrame,
    folds_config: list[dict[str, str]],
    horizonte_horas: int = 1,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Compara referências da Sprint 3 e a candidata S4 nos mesmos folds."""
    if not folds_config:
        raise ValueError("É necessário configurar folds temporais para avaliação.")

    dados_temporais = adicionar_resumos_curto_prazo(
        dados,
        COLUNAS_POLUENTES_CURTO_PRAZO,
    )
    dados_temporais["event_time"] = pd.to_datetime(
        dados_temporais["time"],
        errors="raise",
    ) + pd.Timedelta(hours=horizonte_horas)
    grupos = criar_folds_temporais(
        dados_temporais,
        folds_config,
        horizonte_horas,
    )
    colunas_base = GRUPOS_ABLACAO_IQAR[GRUPO_BASE]
    features_s4 = list(FEATURES_SPRINT4)
    metricas: list[dict[str, Any]] = []
    previsoes: list[pd.DataFrame] = []

    for nome_fold, (treino, validacao) in grupos.items():
        y_treino = treino[COLUNA_ALVO].astype(int)
        y_validacao = validacao[COLUNA_ALVO].astype(int)
        modelos: list[tuple[str, Any, pd.Series | Any]] = []

        dummy = DummyClassifier(strategy="prior")
        dummy.fit(pd.DataFrame(index=treino.index), y_treino)
        y_dummy = dummy.predict(pd.DataFrame(index=validacao.index))
        modelos.append(
            (
                "dummy_prior",
                "dummy_prior",
                y_dummy,
            )
        )

        y_persistencia = _validar_persistencia(validacao, nome_fold)
        modelos.append(
            (
                "persistencia_iqar_atual",
                "persistencia_iqar_atual",
                y_persistencia,
            )
        )

        for variante, features in (
            (VARIANTE_S3_COMPARAVEL, list(colunas_base)),
            (VARIANTE_S4_CANDIDATA, features_s4),
        ):
            if variante == VARIANTE_S4_CANDIDATA:
                pipeline = criar_pipeline_sprint4(GaussianNB())
            else:
                pipeline = criar_pipeline_naive_bayes(features)
            pipeline.fit(treino[features], y_treino)
            modelos.append(
                (
                    "gaussian_naive_bayes",
                    variante,
                    pipeline.predict(validacao[features]),
                )
            )

        for modelo, variante, y_previsto in modelos:
            metricas.append(
                _calcular_metricas(
                    y_validacao,
                    y_previsto,
                    fold=nome_fold,
                    modelo=modelo,
                    grupo_features=variante,
                    n_treino=len(treino),
                )
            )
            previsoes.append(
                pd.DataFrame(
                    {
                        "fold": nome_fold,
                        "variante": variante,
                        "time": validacao["time"].to_numpy(),
                        "event_time": validacao["event_time"].to_numpy(),
                        "y_real": y_validacao.to_numpy(),
                        "y_previsto": y_previsto,
                    }
                )
            )

    resultados = pd.DataFrame(metricas)
    previsoes_df = pd.concat(previsoes, ignore_index=True)
    semanal = _resumir_carga_semanal(previsoes_df)
    resumo = _resumir_variantes(resultados, semanal)
    referencia = resumo.loc[resumo["variante"].eq(VARIANTE_S3_COMPARAVEL)].iloc[0]
    mascara_s4 = resumo["variante"].eq(VARIANTE_S4_CANDIDATA)
    resumo.loc[mascara_s4, "delta_recall_vs_s3"] = (
        resumo.loc[mascara_s4, "media_recall_classe_1"]
        - referencia["media_recall_classe_1"]
    )
    resumo.loc[mascara_s4, "delta_f1_vs_s3"] = (
        resumo.loc[mascara_s4, "media_f1_classe_1"]
        - referencia["media_f1_classe_1"]
    )
    for metrica in ("fp_total", "fn_total"):
        resumo.loc[mascara_s4, f"delta_{metrica}_vs_s3"] = (
            resumo.loc[mascara_s4, metrica] - referencia[metrica]
        )
    return resultados, resumo, semanal


def avaliar_variantes_temporais(
    dados: pd.DataFrame,
    folds_config: list[dict[str, str]],
    horizonte_horas: int = 1,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Compara deltas horários em folds de desenvolvimento com predict padrão."""
    if not folds_config:
        raise ValueError("É necessário configurar folds temporais para avaliação.")

    dados_temporais = adicionar_hora_ciclica(_preparar_features_temporais(dados))
    dados_temporais["event_time"] = pd.to_datetime(
        dados_temporais["time"],
        errors="raise",
    ) + pd.Timedelta(hours=horizonte_horas)
    grupos = criar_folds_temporais(
        dados_temporais,
        folds_config,
        horizonte_horas,
    )
    colunas_base = GRUPOS_ABLACAO_IQAR[GRUPO_BASE]
    metricas: list[dict[str, Any]] = []
    previsoes: list[pd.DataFrame] = []

    for nome_fold, (treino, validacao) in grupos.items():
        y_treino = treino[COLUNA_ALVO].astype(int)
        y_validacao = validacao[COLUNA_ALVO].astype(int)
        for nome_variante, colunas_delta in VARIANTES_DELTA.items():
            if nome_variante == "hora_dia_ciclica":
                features = [
                    *colunas_base,
                    "hora_dia_seno",
                    "hora_dia_cosseno",
                ]
            else:
                features = [
                    *colunas_base,
                    *(f"delta_1h_{coluna}" for coluna in colunas_delta),
                ]
            pipeline = criar_pipeline_naive_bayes(features)
            pipeline.fit(treino[features], y_treino)
            y_previsto = pipeline.predict(validacao[features])
            metricas.append(
                _calcular_metricas(
                    y_validacao,
                    y_previsto,
                    fold=nome_fold,
                    modelo="gaussian_naive_bayes",
                    grupo_features=nome_variante,
                    n_treino=len(treino),
                )
            )
            previsoes.append(
                pd.DataFrame(
                    {
                        "fold": nome_fold,
                        "variante": nome_variante,
                        "time": validacao["time"].to_numpy(),
                        "event_time": validacao["event_time"].to_numpy(),
                        "y_real": y_validacao.to_numpy(),
                        "y_previsto": y_previsto,
                    }
                )
            )

    resultados = pd.DataFrame(metricas)
    previsoes_df = pd.concat(previsoes, ignore_index=True)
    semanal = _resumir_carga_semanal(previsoes_df)
    resumo = _resumir_variantes(resultados, semanal)
    return resultados, resumo, semanal


def _resumir_carga_semanal(previsoes: pd.DataFrame) -> pd.DataFrame:
    dados = previsoes.sort_values(["variante", "event_time"]).copy()
    dados["inicio_episodio"] = False
    for _, indices in dados.groupby("variante").groups.items():
        mascara = _mascara_inicio_episodios_alerta(
            dados.loc[indices, "y_previsto"].to_numpy(dtype=int),
            dados.loc[indices, "event_time"],
        )
        dados.loc[indices, "inicio_episodio"] = mascara

    dados["semana_inicio"] = (
        dados["event_time"].dt.normalize()
        - pd.to_timedelta(dados["event_time"].dt.weekday, unit="D")
    )
    semanal = (
        dados.groupby(["variante", "semana_inicio"], as_index=False)
        .agg(
            horas_validacao=("y_previsto", "size"),
            horas_alerta=("y_previsto", "sum"),
            episodios_iniciados=("inicio_episodio", "sum"),
        )
        .sort_values(["variante", "semana_inicio"])
        .reset_index(drop=True)
    )
    semanal["semana_completa"] = semanal["horas_validacao"].eq(24 * 7)
    return semanal


def _resumir_variantes(
    resultados: pd.DataFrame,
    semanal: pd.DataFrame,
) -> pd.DataFrame:
    resumo = (
        resultados.groupby("grupo_features", as_index=False)
        .agg(
            folds=("fold", "nunique"),
            media_precisao_classe_1=("precisao_classe_1", "mean"),
            media_recall_classe_1=("recall_classe_1", "mean"),
            media_f1_classe_1=("f1_classe_1", "mean"),
            tn_total=("tn", "sum"),
            fp_total=("fp", "sum"),
            fn_total=("fn", "sum"),
            tp_total=("tp", "sum"),
            horas_validacao=("n_validacao", "sum"),
        )
        .rename(columns={"grupo_features": "variante"})
    )
    semanas_completas = semanal.loc[semanal["semana_completa"]]
    semanal_resumo = (
        semanas_completas.groupby("variante", as_index=False)
        .agg(
            semanas_completas=("semana_completa", "sum"),
            max_episodios_em_uma_semana=("episodios_iniciados", "max"),
            semanas_com_mais_de_3_episodios=(
                "episodios_iniciados",
                lambda episodios: int(episodios.gt(MAX_EPISODIOS_SEMANA).sum()),
            ),
            max_horas_alerta_em_uma_semana=("horas_alerta", "max"),
        )
    )
    episodios_totais = (
        semanal.groupby("variante", as_index=False)
        .agg(episodios_alerta_total=("episodios_iniciados", "sum"))
    )
    resumo = resumo.merge(
        semanal_resumo,
        on="variante",
        how="left",
        validate="one_to_one",
    )
    resumo = resumo.merge(
        episodios_totais,
        on="variante",
        how="left",
        validate="one_to_one",
    )
    metricas = (
        "media_precisao_classe_1",
        "media_recall_classe_1",
        "media_f1_classe_1",
    )
    resumo[list(metricas)] = resumo[list(metricas)].round(4)
    return resumo.sort_values("variante").reset_index(drop=True)


def main() -> None:
    dados, evaluation, horizonte_horas = _carregar_desenvolvimento()
    resultados, resumo, semanal = avaliar_variantes_temporais(
        dados,
        evaluation["validation_folds"],
        horizonte_horas,
    )
    pasta_saida = Path("reports/modeling")
    pasta_saida.mkdir(parents=True, exist_ok=True)
    resultados.to_csv(
        pasta_saida / "temporal_feature_metrics_by_fold.csv",
        index=False,
        encoding="utf-8",
    )
    resumo.to_csv(
        pasta_saida / "temporal_feature_metrics_summary.csv",
        index=False,
        encoding="utf-8",
    )
    semanal.to_csv(
        pasta_saida / "temporal_feature_alert_burden_by_week.csv",
        index=False,
        encoding="utf-8",
    )
    resultados_curto_prazo, resumo_curto_prazo, semanal_curto_prazo = (
        avaliar_variantes_curto_prazo(
            dados,
            evaluation["validation_folds"],
            horizonte_horas,
        )
    )
    resultados_curto_prazo.to_csv(
        pasta_saida / "short_term_feature_metrics_by_fold.csv",
        index=False,
        encoding="utf-8",
    )
    resumo_curto_prazo.to_csv(
        pasta_saida / "short_term_feature_metrics_summary.csv",
        index=False,
        encoding="utf-8",
    )
    semanal_curto_prazo.to_csv(
        pasta_saida / "short_term_feature_alert_burden_by_week.csv",
        index=False,
        encoding="utf-8",
    )
    resultados_lift, resumo_lift, semanal_lift = avaliar_lift_sprint4(
        dados,
        evaluation["validation_folds"],
        horizonte_horas,
    )
    resultados_lift.to_csv(
        pasta_saida / "sprint4_lift_by_fold.csv",
        index=False,
        encoding="utf-8",
    )
    resumo_lift.to_csv(
        pasta_saida / "sprint4_lift_summary.csv",
        index=False,
        encoding="utf-8",
    )
    semanal_lift.to_csv(
        pasta_saida / "sprint4_alert_burden_by_week.csv",
        index=False,
        encoding="utf-8",
    )
    print("Métricas por fold:")
    print(resultados.to_string(index=False))
    print("\nResumo por variante:")
    print(resumo.to_string(index=False))
    print("\nResumo das features de curto prazo:")
    print(resumo_curto_prazo.to_string(index=False))
    print("\nResumo formal do lift S3 para S4:")
    print(resumo_lift.to_string(index=False))


if __name__ == "__main__":
    main()
