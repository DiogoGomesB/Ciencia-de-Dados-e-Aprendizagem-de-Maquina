from collections.abc import Mapping, Sequence
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from sklearn.base import BaseEstimator
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.transformacao.Calcular_Alvo_IQAr import COLUNA_ALVO, COLUNA_IQAR
from src.validacao.Separacao_Temporal import criar_folds_temporais

COLUNAS_POLUENTES = (
    "pm10",
    "pm2_5",
    "carbon_monoxide",
    "nitrogen_dioxide",
    "sulphur_dioxide",
    "ozone",
)
COLUNAS_METEOROLOGICAS = (
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "wind_speed_10m",
    "pressure_msl",
)
COLUNAS_SUBINDICES = (
    "iqar_pm10",
    "iqar_pm2_5",
    "iqar_carbon_monoxide",
    "iqar_nitrogen_dioxide",
    "iqar_sulphur_dioxide",
    "iqar_ozone",
    COLUNA_IQAR,
)
GRUPOS_FEATURES = {
    "poluentes_brutos_meteorologia": (
        *COLUNAS_POLUENTES,
        *COLUNAS_METEOROLOGICAS,
    ),
    "subindices_meteorologia": (
        *COLUNAS_SUBINDICES,
        *COLUNAS_METEOROLOGICAS,
    ),
    "poluentes_subindices_meteorologia": (
        *COLUNAS_POLUENTES,
        *COLUNAS_SUBINDICES,
        *COLUNAS_METEOROLOGICAS,
    ),
}
GRUPOS_ABLACAO_IQAR = {
    "subindices_sem_iqar_meteorologia": tuple(
        coluna
        for coluna in GRUPOS_FEATURES["subindices_meteorologia"]
        if coluna != COLUNA_IQAR
    ),
    "poluentes_subindices_sem_iqar_meteorologia": tuple(
        coluna
        for coluna in GRUPOS_FEATURES["poluentes_subindices_meteorologia"]
        if coluna != COLUNA_IQAR
    ),
}
GRUPOS_EXPERIMENTOS = {**GRUPOS_FEATURES, **GRUPOS_ABLACAO_IQAR}
FEATURES_SPRINT4 = (
    *GRUPOS_ABLACAO_IQAR["subindices_sem_iqar_meteorologia"],
    "media_3h_ozone",
    "media_3h_pm2_5",
    "delta_2h_ozone",
    "delta_2h_pm2_5",
)
GRUPO_REFERENCIA_INDEPENDENTE = "referencia_independente_de_features"
ROTULOS = (0, 1)
LIMIARES_ANALISE = tuple(float(valor) for valor in np.linspace(0, 1, 101))
MAX_EPISODIOS_ALERTA_SEMANA = 3


def _carregar_desenvolvimento() -> tuple[pd.DataFrame, dict, int]:
    with Path("config/params.yaml").open("r", encoding="utf-8") as arquivo:
        config = yaml.safe_load(arquivo)

    periodo = {
        "start_date": config["collection"]["start_date"],
        "end_date": config["collection"]["end_date"],
    }
    paths = config["paths"]
    caminho_dados = (
        Path(paths["interim_data"])
        / paths["labeled_filename"].format(**periodo)
    )
    dados = pd.read_csv(caminho_dados, parse_dates=["time"])
    evaluation = config["evaluation"]
    horizonte_horas = evaluation["target_horizon_hours"]
    inicio_teste = pd.Timestamp(evaluation["final_test"]["start"])

    colunas_necessarias = {
        "time",
        COLUNA_ALVO,
        COLUNA_IQAR,
        *(coluna for colunas in GRUPOS_FEATURES.values() for coluna in colunas),
    }
    ausentes = colunas_necessarias.difference(dados.columns)
    if ausentes:
        raise ValueError(
            f"Colunas necessárias ausentes na base rotulada: {sorted(ausentes)}"
        )
    tempos = pd.to_datetime(dados["time"], errors="raise")
    if tempos.isna().any() or tempos.duplicated().any():
        raise ValueError("A coluna 'time' contém timestamps ausentes ou duplicados.")
    if not tempos.is_monotonic_increasing:
        raise ValueError("Os timestamps devem estar em ordem cronológica crescente.")

    dados = dados.copy()
    dados["time"] = tempos
    dados["event_time"] = tempos + pd.Timedelta(hours=horizonte_horas)
    desenvolvimento = dados.loc[dados["event_time"].lt(inicio_teste)].copy()
    desenvolvimento[COLUNA_ALVO] = pd.to_numeric(
        desenvolvimento[COLUNA_ALVO],
        errors="raise",
    )
    rotulos_definidos = desenvolvimento[COLUNA_ALVO].notna()
    if not desenvolvimento.loc[rotulos_definidos, COLUNA_ALVO].isin(ROTULOS).all():
        raise ValueError(f"A coluna '{COLUNA_ALVO}' deve conter apenas 0 ou 1.")
    if desenvolvimento.empty or not rotulos_definidos.any():
        raise ValueError("O desenvolvimento não contém rótulos definidos.")

    return desenvolvimento, evaluation, horizonte_horas


def criar_pipeline_com_preprocessamento(
    colunas: Sequence[str],
    classificador: BaseEstimator,
) -> Pipeline:
    """Cria o pipeline numérico com pré-processamento ajustado somente no treino."""
    if not colunas or len(set(colunas)) != len(colunas):
        raise ValueError("A lista de features deve ser não vazia e sem duplicatas.")

    pre_processador = ColumnTransformer(
        transformers=[
            (
                "numericas",
                Pipeline(
                    steps=[
                        ("imputador", SimpleImputer(strategy="median")),
                        ("escalador", StandardScaler()),
                    ]
                ),
                list(colunas),
            )
        ],
        remainder="drop",
    )
    return Pipeline(
        steps=[
            ("pre_processamento", pre_processador),
            ("classificador", classificador),
        ]
    )


def criar_pipeline_naive_bayes(colunas: Sequence[str]) -> Pipeline:
    """Cria o pipeline de Naive Bayes usado nos baselines."""
    return criar_pipeline_com_preprocessamento(colunas, GaussianNB())


def criar_pipeline_sprint4(classificador: BaseEstimator) -> Pipeline:
    """Cria um classificador usando as features e o pré-processamento congelados."""
    return criar_pipeline_com_preprocessamento(FEATURES_SPRINT4, classificador)


def _calcular_metricas(
    y_real: Sequence[int],
    y_previsto: Sequence[int],
    *,
    fold: str,
    modelo: str,
    grupo_features: str,
    n_treino: int,
) -> dict[str, int | float | str]:
    precisao, recall, f1, suporte = precision_recall_fscore_support(
        y_real,
        y_previsto,
        labels=list(ROTULOS),
        zero_division=0,
    )
    tn, fp, fn, tp = confusion_matrix(
        y_real,
        y_previsto,
        labels=list(ROTULOS),
    ).ravel()

    return {
        "fold": fold,
        "modelo": modelo,
        "grupo_features": grupo_features,
        "n_treino": n_treino,
        "n_validacao": len(y_real),
        "positivos_validacao": int(suporte[1]),
        "precisao_classe_0": float(precisao[0]),
        "recall_classe_0": float(recall[0]),
        "f1_classe_0": float(f1[0]),
        "suporte_classe_0": int(suporte[0]),
        "precisao_classe_1": float(precisao[1]),
        "recall_classe_1": float(recall[1]),
        "f1_classe_1": float(f1[1]),
        "suporte_classe_1": int(suporte[1]),
        "f1_macro": float((f1[0] + f1[1]) / 2),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
    }


def _validar_persistencia(dados: pd.DataFrame, fold: str) -> pd.Series:
    iqar_atual = pd.to_numeric(dados[COLUNA_IQAR], errors="raise")
    if iqar_atual.isna().any():
        raise ValueError(
            f"O IQAr em t está ausente na validação do fold '{fold}'; "
            "não é possível calcular o baseline de persistência."
        )
    return iqar_atual.gt(100).astype(int)


def _registrar_previsoes(
    validacao: pd.DataFrame,
    y_real: pd.Series,
    y_previsto: Sequence[int],
    *,
    fold: str,
    modelo: str,
    grupo_features: str,
) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "fold": fold,
            "modelo": modelo,
            "grupo_features": grupo_features,
            "time": validacao["time"],
            "event_time": validacao["event_time"],
            "y_real": y_real.astype(int),
            "y_previsto": y_previsto,
        },
        index=validacao.index,
    ).reset_index(drop=True)


def executar_experimentos(
    dados: pd.DataFrame,
    folds_config: Sequence[Mapping[str, str]],
    horizonte_horas: int = 1,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Avalia baselines e guarda previsões out-of-fold, sem acessar o holdout."""
    folds = criar_folds_temporais(dados, folds_config, horizonte_horas)
    resultados: list[dict[str, int | float | str]] = []
    previsoes_por_fold: list[pd.DataFrame] = []

    for nome_fold, (treino, validacao) in folds.items():
        y_treino = treino[COLUNA_ALVO].astype(int)
        y_validacao = validacao[COLUNA_ALVO].astype(int)
        n_treino = len(treino)

        dummy = DummyClassifier(strategy="prior")
        dummy.fit(pd.DataFrame(index=treino.index), y_treino)
        y_dummy = dummy.predict(pd.DataFrame(index=validacao.index))
        resultados.append(
            _calcular_metricas(
                y_validacao,
                y_dummy,
                fold=nome_fold,
                modelo="dummy_prior",
                grupo_features=GRUPO_REFERENCIA_INDEPENDENTE,
                n_treino=n_treino,
            )
        )
        previsoes_por_fold.append(
            _registrar_previsoes(
                validacao,
                y_validacao,
                y_dummy,
                fold=nome_fold,
                modelo="dummy_prior",
                grupo_features=GRUPO_REFERENCIA_INDEPENDENTE,
            )
        )

        y_persistencia = _validar_persistencia(validacao, nome_fold)
        resultados.append(
            _calcular_metricas(
                y_validacao,
                y_persistencia,
                fold=nome_fold,
                modelo="persistencia_iqar_atual",
                grupo_features=GRUPO_REFERENCIA_INDEPENDENTE,
                n_treino=n_treino,
            )
        )
        previsoes_por_fold.append(
            _registrar_previsoes(
                validacao,
                y_validacao,
                y_persistencia,
                fold=nome_fold,
                modelo="persistencia_iqar_atual",
                grupo_features=GRUPO_REFERENCIA_INDEPENDENTE,
            )
        )

        for nome_grupo, colunas in GRUPOS_EXPERIMENTOS.items():
            pipeline = criar_pipeline_naive_bayes(colunas)
            pipeline.fit(treino[list(colunas)], y_treino)
            y_naive_bayes = pipeline.predict(validacao[list(colunas)])
            resultados.append(
                _calcular_metricas(
                    y_validacao,
                    y_naive_bayes,
                    fold=nome_fold,
                    modelo="gaussian_naive_bayes",
                    grupo_features=nome_grupo,
                    n_treino=n_treino,
                )
            )
            previsoes_por_fold.append(
                _registrar_previsoes(
                    validacao,
                    y_validacao,
                    y_naive_bayes,
                    fold=nome_fold,
                    modelo="gaussian_naive_bayes",
                    grupo_features=nome_grupo,
                )
            )

    return pd.DataFrame(resultados), pd.concat(previsoes_por_fold, ignore_index=True)


def criar_folds_internos_limiar(
    folds_config: Sequence[Mapping[str, str]],
) -> list[dict[str, str]]:
    """Usa o trimestre imediatamente anterior como validação interna de cada fold."""
    folds_internos = []
    for fold in folds_config:
        inicio_externo = pd.Timestamp(fold["start"])
        fim_externo = pd.Timestamp(fold["end"])
        duracao = fim_externo - inicio_externo
        if duracao <= pd.Timedelta(0):
            raise ValueError(
                f"O fold '{fold['name']}' deve ter início anterior ao fim."
            )
        meses = (
            (fim_externo.year - inicio_externo.year) * 12
            + fim_externo.month
            - inicio_externo.month
        )
        if meses > 0 and inicio_externo + pd.DateOffset(months=meses) == fim_externo:
            inicio_interno = inicio_externo - pd.DateOffset(months=meses)
        else:
            inicio_interno = inicio_externo - duracao
        folds_internos.append(
            {
                "name": fold["name"],
                "start": inicio_interno.isoformat(),
                "end": inicio_externo.isoformat(),
            }
        )
    return folds_internos


def _mascara_inicio_episodios_alerta(
    y_previsto: Sequence[int],
    event_time: Sequence[pd.Timestamp],
) -> np.ndarray:
    """Identifica o início de cada sequência positiva horária."""
    previsoes = np.asarray(y_previsto, dtype=int)
    tempos = pd.DatetimeIndex(event_time)
    if len(previsoes) != len(tempos):
        raise ValueError("Previsões e horários devem ter o mesmo comprimento.")
    if not np.isin(previsoes, ROTULOS).all():
        raise ValueError("As previsões devem conter apenas as classes 0 e 1.")
    if tempos.hasnans or not tempos.is_monotonic_increasing or tempos.has_duplicates:
        raise ValueError("Os horários devem estar ordenados, definidos e sem duplicatas.")
    if not len(previsoes):
        return np.zeros(0, dtype=bool)

    hora_consecutiva = np.zeros(len(tempos), dtype=bool)
    if len(tempos) > 1:
        hora_consecutiva[1:] = (
            np.diff(tempos.as_unit("ns").asi8)
            == pd.Timedelta(hours=1).value
        )
    inicio_episodio = (previsoes == 1) & np.r_[
        True,
        ~((previsoes[:-1] == 1) & hora_consecutiva[1:]),
    ]
    return inicio_episodio


def contar_episodios_alerta(
    y_previsto: Sequence[int],
    event_time: Sequence[pd.Timestamp],
) -> int:
    """Conta sequências positivas; uma hora negativa ou lacuna encerra o episódio."""
    return int(_mascara_inicio_episodios_alerta(y_previsto, event_time).sum())


def analisar_tradeoff_limiares(
    dados: pd.DataFrame,
    folds_config: Sequence[Mapping[str, str]],
    horizonte_horas: int = 1,
    limiares: Sequence[float] = LIMIARES_ANALISE,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Avalia uma grade de limiares em trimestres anteriores aos folds externos."""
    limiares_validos = tuple(float(limiar) for limiar in limiares)
    if (
        not limiares_validos
        or any(not np.isfinite(limiar) or not 0 <= limiar <= 1 for limiar in limiares_validos)
        or len(set(limiares_validos)) != len(limiares_validos)
    ):
        raise ValueError("Os limiares devem ser únicos, não vazios e estar entre 0 e 1.")

    folds_internos = criar_folds_internos_limiar(folds_config)
    divisao_interna = criar_folds_temporais(
        dados,
        folds_internos,
        horizonte_horas,
    )
    limites_internos = {
        fold["name"]: (fold["start"], fold["end"])
        for fold in folds_internos
    }
    resultados = []
    previsoes_por_limiar = []

    for fold_externo, (treino, validacao_interna) in divisao_interna.items():
        y_treino = treino[COLUNA_ALVO].astype(int)
        y_validacao = validacao_interna[COLUNA_ALVO].astype(int)
        for nome_grupo, colunas in GRUPOS_EXPERIMENTOS.items():
            pipeline = criar_pipeline_naive_bayes(colunas)
            pipeline.fit(treino[list(colunas)], y_treino)
            probabilidades = pipeline.predict_proba(
                validacao_interna[list(colunas)]
            )
            indice_classe_positiva = list(pipeline.classes_).index(1)
            probabilidade_positiva = probabilidades[:, indice_classe_positiva]

            for limiar in limiares_validos:
                y_previsto = (probabilidade_positiva >= limiar).astype(int)
                metricas = _calcular_metricas(
                    y_validacao,
                    y_previsto,
                    fold=fold_externo,
                    modelo="gaussian_naive_bayes",
                    grupo_features=nome_grupo,
                    n_treino=len(treino),
                )
                metricas["limiar"] = limiar
                inicio_interno, fim_interno = limites_internos[fold_externo]
                metricas["validacao_interna_inicio"] = inicio_interno
                metricas["validacao_interna_fim_exclusivo"] = fim_interno
                metricas["n_validacao_interna"] = len(validacao_interna)
                metricas["alertas"] = int(y_previsto.sum())
                metricas["episodios_alerta"] = contar_episodios_alerta(
                    y_previsto,
                    validacao_interna["event_time"],
                )
                metricas["alertas_por_1000_horas"] = (
                    float(y_previsto.mean() * 1000)
                )
                metricas["episodios_alerta_por_1000_horas"] = (
                    float(metricas["episodios_alerta"] / len(y_previsto) * 1000)
                )
                metricas["proporcao_falsos_alertas"] = (
                    float(metricas["fp"] / metricas["alertas"])
                    if metricas["alertas"]
                    else 0.0
                )
                previsoes_por_limiar.append(
                    pd.DataFrame(
                        {
                            "event_time": validacao_interna["event_time"],
                            "y_previsto": y_previsto,
                            "fold": fold_externo,
                            "modelo": "gaussian_naive_bayes",
                            "grupo_features": nome_grupo,
                            "limiar": limiar,
                        }
                    )
                )
                resultados.append(metricas)

    resumo_limiares = pd.DataFrame(resultados).sort_values(
        ["fold", "grupo_features", "limiar"]
    ).reset_index(drop=True)
    dados_previsoes = pd.concat(previsoes_por_limiar, ignore_index=True)
    dados_previsoes = dados_previsoes.sort_values(
        ["grupo_features", "limiar", "event_time"]
    ).reset_index(drop=True)
    dados_previsoes["inicio_episodio"] = False
    for _, indices in dados_previsoes.groupby(
        ["grupo_features", "limiar"],
        sort=False,
    ).groups.items():
        trecho = dados_previsoes.loc[indices]
        dados_previsoes.loc[indices, "inicio_episodio"] = (
            _mascara_inicio_episodios_alerta(
                trecho["y_previsto"],
                trecho["event_time"],
            )
        )
    dados_previsoes["semana_inicio"] = (
        dados_previsoes["event_time"].dt.normalize()
        - pd.to_timedelta(dados_previsoes["event_time"].dt.weekday, unit="D")
    )
    resumo_semanal = (
        dados_previsoes.groupby(
            ["modelo", "grupo_features", "limiar", "semana_inicio"],
            as_index=False,
        )
        .agg(
            horas_validacao=("y_previsto", "size"),
            horas_alerta=("y_previsto", "sum"),
            episodios_iniciados=("inicio_episodio", "sum"),
            folds_na_semana=("fold", "nunique"),
        )
    )
    resumo_semanal["semana_completa"] = resumo_semanal["horas_validacao"].eq(
        24 * 7
    )
    resumo_semanal = resumo_semanal.sort_values(
        ["grupo_features", "limiar", "semana_inicio"]
    ).reset_index(drop=True)
    return resumo_limiares, resumo_semanal


def resumir_tradeoff_limiares(
    resultados: pd.DataFrame,
    resultados_semanais: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Resume o trade-off por limiar, agregando contagens e médias entre janelas."""
    resumo = (
        resultados.groupby(
            ["modelo", "grupo_features", "limiar"],
            as_index=False,
        )
        .agg(
            folds=("fold", "nunique"),
            media_precisao_classe_1=("precisao_classe_1", "mean"),
            media_recall_classe_1=("recall_classe_1", "mean"),
            media_f1_classe_1=("f1_classe_1", "mean"),
            tn_total=("tn", "sum"),
            fp_total=("fp", "sum"),
            fn_total=("fn", "sum"),
            tp_total=("tp", "sum"),
            alertas_total=("alertas", "sum"),
            episodios_alerta_total=("episodios_alerta", "sum"),
            negativos_validacao=("suporte_classe_0", "sum"),
            positivos_validacao=("suporte_classe_1", "sum"),
            horas_validacao=("n_validacao", "sum"),
        )
        .sort_values(["modelo", "grupo_features", "limiar"])
        .reset_index(drop=True)
    )
    resumo["taxa_falso_positivo_agregada"] = (
        resumo["fp_total"] / resumo["negativos_validacao"]
    ).where(resumo["negativos_validacao"].gt(0))
    resumo["taxa_falso_negativo_agregada"] = (
        resumo["fn_total"] / resumo["positivos_validacao"]
    ).where(resumo["positivos_validacao"].gt(0))
    resumo["alertas_por_1000_horas"] = (
        resumo["alertas_total"] / resumo["horas_validacao"] * 1000
    )
    resumo["episodios_alerta_por_1000_horas"] = (
        resumo["episodios_alerta_total"] / resumo["horas_validacao"] * 1000
    )
    resumo["proporcao_falsos_alertas"] = (
        resumo["fp_total"] / resumo["alertas_total"]
    ).where(resumo["alertas_total"].gt(0), 0.0)
    if resultados_semanais is not None:
        resumo_semanal = (
            resultados_semanais.groupby(
                ["modelo", "grupo_features", "limiar"],
                as_index=False,
            )
            .agg(
                semanas_com_validacao=("semana_inicio", "nunique"),
                episodios_alerta_total=("episodios_iniciados", "sum"),
                max_episodios_em_uma_semana=("episodios_iniciados", "max"),
                max_horas_alerta_em_uma_semana=("horas_alerta", "max"),
                semanas_com_mais_de_3_episodios=(
                    "episodios_iniciados",
                    lambda episodios: int(
                        episodios.gt(MAX_EPISODIOS_ALERTA_SEMANA).sum()
                    ),
                ),
            )
        )
        resumo = resumo.drop(columns="episodios_alerta_total").merge(
            resumo_semanal,
            on=["modelo", "grupo_features", "limiar"],
            how="left",
            validate="one_to_one",
        )
        resumo["episodios_alerta_por_1000_horas"] = (
            resumo["episodios_alerta_total"] / resumo["horas_validacao"] * 1000
        )
        resumo["episodios_por_semana_media"] = (
            resumo["episodios_alerta_total"] / resumo["semanas_com_validacao"]
        )
    metricas_media = (
        "media_precisao_classe_1",
        "media_recall_classe_1",
        "media_f1_classe_1",
        "taxa_falso_positivo_agregada",
        "taxa_falso_negativo_agregada",
        "alertas_por_1000_horas",
        "episodios_alerta_por_1000_horas",
        "proporcao_falsos_alertas",
    )
    if resultados_semanais is not None:
        metricas_media += ("episodios_por_semana_media",)
    resumo[list(metricas_media)] = resumo[list(metricas_media)].round(4)
    return resumo


def executar_avaliacao(
    dados: pd.DataFrame,
    folds_config: Sequence[Mapping[str, str]],
    horizonte_horas: int = 1,
) -> pd.DataFrame:
    """Retorna métricas dos baselines sem acessar o holdout."""
    resultados, _ = executar_experimentos(dados, folds_config, horizonte_horas)
    return resultados


def criar_tabela_erros(
    dados: pd.DataFrame,
    previsoes: pd.DataFrame,
) -> pd.DataFrame:
    """Anexa as features em t aos falsos positivos e falsos negativos."""
    colunas_features = sorted(
        {coluna for grupo in GRUPOS_FEATURES.values() for coluna in grupo}
    )
    erros = previsoes.loc[previsoes["y_real"].ne(previsoes["y_previsto"])].copy()
    erros["tipo_erro"] = erros["y_previsto"].map(
        {0: "falso_negativo", 1: "falso_positivo"}
    )
    contexto = dados[["time", "event_time", *colunas_features]]
    return erros.merge(
        contexto,
        on=["time", "event_time"],
        how="left",
        validate="many_to_one",
    )


def resumir_erros_temporais(
    previsoes: pd.DataFrame,
    granularidade: str,
) -> pd.DataFrame:
    """Calcula taxas de erro por mês ou hora do evento de validação."""
    if granularidade not in {"mes", "hora"}:
        raise ValueError("A granularidade deve ser 'mes' ou 'hora'.")

    dados = previsoes.copy()
    if granularidade == "mes":
        dados["periodo"] = dados["event_time"].dt.strftime("%Y-%m")
    else:
        dados["periodo"] = dados["event_time"].dt.hour.map(
            lambda hora: f"{hora:02d}"
        )
    dados["eh_falso_positivo"] = dados["y_real"].eq(0) & dados[
        "y_previsto"
    ].eq(1)
    dados["eh_falso_negativo"] = dados["y_real"].eq(1) & dados[
        "y_previsto"
    ].eq(0)
    colunas_grupo = ["fold", "modelo", "grupo_features", "periodo"]

    resumo = (
        dados.groupby(colunas_grupo, as_index=False)
        .agg(
            n_validacao=("y_real", "size"),
            positivos=("y_real", "sum"),
            falsos_positivos=("eh_falso_positivo", "sum"),
            falsos_negativos=("eh_falso_negativo", "sum"),
        )
        .sort_values(colunas_grupo)
        .reset_index(drop=True)
    )
    resumo["negativos"] = resumo["n_validacao"] - resumo["positivos"]
    resumo["taxa_falso_positivo"] = (
        resumo["falsos_positivos"] / resumo["negativos"]
    ).where(resumo["negativos"].gt(0))
    resumo["taxa_falso_negativo"] = (
        resumo["falsos_negativos"] / resumo["positivos"]
    ).where(resumo["positivos"].gt(0))
    return resumo


def resumir_resultados(resultados: pd.DataFrame) -> pd.DataFrame:
    """Resume métricas por fold sem ocultar a matriz de confusão agregada."""
    metricas = (
        "precisao_classe_1",
        "recall_classe_1",
        "f1_classe_1",
        "f1_macro",
    )
    resumo = (
        resultados.groupby(["modelo", "grupo_features"], as_index=False)
        .agg(
            folds=("fold", "count"),
            media_precisao_classe_1=("precisao_classe_1", "mean"),
            media_recall_classe_1=("recall_classe_1", "mean"),
            media_f1_classe_1=("f1_classe_1", "mean"),
            media_f1_macro=("f1_macro", "mean"),
            tn_total=("tn", "sum"),
            fp_total=("fp", "sum"),
            fn_total=("fn", "sum"),
            tp_total=("tp", "sum"),
            positivos_validacao=("positivos_validacao", "sum"),
        )
        .sort_values(["modelo", "grupo_features"])
        .reset_index(drop=True)
    )
    resumo[list(f"media_{metrica}" for metrica in metricas)] = resumo[
        list(f"media_{metrica}" for metrica in metricas)
    ].round(4)
    return resumo


def main() -> None:
    dados, evaluation, horizonte_horas = _carregar_desenvolvimento()
    resultados, previsoes = executar_experimentos(
        dados,
        evaluation["validation_folds"],
        horizonte_horas,
    )
    resumo = resumir_resultados(resultados)
    erros = criar_tabela_erros(dados, previsoes)
    erros_por_mes = resumir_erros_temporais(previsoes, "mes")
    erros_por_hora = resumir_erros_temporais(previsoes, "hora")
    tradeoff_limiares = analisar_tradeoff_limiares(
        dados,
        evaluation["validation_folds"],
        horizonte_horas,
    )
    tradeoff_por_limiar, tradeoff_semanal = tradeoff_limiares
    resumo_tradeoff_limiares = resumir_tradeoff_limiares(
        tradeoff_por_limiar,
        tradeoff_semanal,
    )

    pasta_saida = Path("reports/modeling")
    pasta_saida.mkdir(parents=True, exist_ok=True)
    caminho_detalhado = pasta_saida / "baseline_metrics_by_fold.csv"
    caminho_resumo = pasta_saida / "baseline_metrics_summary.csv"
    caminho_previsoes = pasta_saida / "baseline_predictions_by_fold.csv"
    caminho_erros = pasta_saida / "baseline_misclassified_cases.csv"
    caminho_erros_mes = pasta_saida / "baseline_error_rates_by_month.csv"
    caminho_erros_hora = pasta_saida / "baseline_error_rates_by_hour.csv"
    resultados.to_csv(caminho_detalhado, index=False, encoding="utf-8")
    resumo.to_csv(caminho_resumo, index=False, encoding="utf-8")
    previsoes.to_csv(caminho_previsoes, index=False, encoding="utf-8")
    erros.to_csv(caminho_erros, index=False, encoding="utf-8")
    erros_por_mes.to_csv(caminho_erros_mes, index=False, encoding="utf-8")
    erros_por_hora.to_csv(caminho_erros_hora, index=False, encoding="utf-8")
    grupos_ablation = set(GRUPOS_ABLACAO_IQAR) | {
        "subindices_meteorologia",
        "poluentes_subindices_meteorologia",
    }
    resultados_ablation = resultados.loc[
        resultados["grupo_features"].isin(grupos_ablation)
        & resultados["modelo"].eq("gaussian_naive_bayes")
    ]
    resumo_ablation = resumo.loc[
        resumo["grupo_features"].isin(grupos_ablation)
        & resumo["modelo"].eq("gaussian_naive_bayes")
    ]
    resultados_ablation.to_csv(
        pasta_saida / "baseline_iqar_ablation_by_fold.csv",
        index=False,
        encoding="utf-8",
    )
    resumo_ablation.to_csv(
        pasta_saida / "baseline_iqar_ablation_summary.csv",
        index=False,
        encoding="utf-8",
    )
    tradeoff_por_limiar.to_csv(
        pasta_saida / "baseline_threshold_tradeoff_by_inner_fold.csv",
        index=False,
        encoding="utf-8",
    )
    tradeoff_semanal.to_csv(
        pasta_saida / "baseline_threshold_alert_episodes_by_week.csv",
        index=False,
        encoding="utf-8",
    )
    resumo_tradeoff_limiares.to_csv(
        pasta_saida / "baseline_threshold_tradeoff_summary.csv",
        index=False,
        encoding="utf-8",
    )

    print(
        f"Desenvolvimento usado: "
        f"{int(dados[COLUNA_ALVO].notna().sum())} rótulos definidos "
        f"({len(dados)} horários antes de excluir rótulos indefinidos), "
        f"com evento previsto antes de {evaluation['final_test']['start']}."
    )
    print("\nMétricas por fold:")
    print(
        resultados[
            [
                "fold",
                "modelo",
                "grupo_features",
                "positivos_validacao",
                "precisao_classe_1",
                "recall_classe_1",
                "f1_classe_1",
                "tn",
                "fp",
                "fn",
                "tp",
            ]
        ].to_string(index=False, float_format=lambda valor: f"{valor:.3f}")
    )
    print("\nMédia simples das métricas por fold e confusão agregada:")
    print(resumo.to_string(index=False))
    print("\nCasos classificados incorretamente por modelo e fold:")
    print(
        erros.groupby(
            ["fold", "modelo", "grupo_features", "tipo_erro"],
            as_index=False,
        )
        .size()
        .to_string(index=False)
    )
    print(f"\nResultados detalhados salvos em: {caminho_detalhado}")
    print(f"Resumo salvo em: {caminho_resumo}")
    print(f"Previsões por fold salvas em: {caminho_previsoes}")
    print(f"Casos incorretos com features em t salvos em: {caminho_erros}")
    print(f"Taxas de erro por mês salvas em: {caminho_erros_mes}")
    print(    f"Taxas de erro por hora salvas em: {caminho_erros_hora}"
    )
    print(
    "Comparação da ablação de IQAr consolidado salva em: "
    f"{pasta_saida / 'baseline_iqar_ablation_by_fold.csv'} e "
    f"{pasta_saida / 'baseline_iqar_ablation_summary.csv'}")
    print(
        "Trade-off de limiares nas validações internas salvo em: "
        f"{pasta_saida / 'baseline_threshold_tradeoff_by_inner_fold.csv'} e "
        f"{pasta_saida / 'baseline_threshold_tradeoff_summary.csv'}"
    )
    print(
        f"Episódios por semana salvos em: "
        f"{pasta_saida / 'baseline_threshold_alert_episodes_by_week.csv'}"
    )


if __name__ == "__main__":
    main()
