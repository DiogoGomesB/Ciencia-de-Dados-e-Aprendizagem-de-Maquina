import numpy as np
import pandas as pd


def adicionar_hora_ciclica(dados: pd.DataFrame) -> pd.DataFrame:
    """Codifica a hora local do registro como duas coordenadas periódicas."""
    if "time" not in dados.columns:
        raise ValueError("A coluna 'time' é necessária para codificar a hora.")

    tempos = pd.to_datetime(dados["time"], errors="raise")
    if tempos.isna().any():
        raise ValueError("A coluna 'time' contém timestamps ausentes.")

    hora = (
        tempos.dt.hour
        + tempos.dt.minute / 60
        + tempos.dt.second / 3600
    )
    angulo = 2 * np.pi * hora / 24
    resultado = dados.copy()
    resultado["hora_dia_seno"] = np.sin(angulo)
    resultado["hora_dia_cosseno"] = np.cos(angulo)
    return resultado


def adicionar_diferencas_horarias(
    dados: pd.DataFrame,
    colunas: tuple[str, ...],
) -> pd.DataFrame:
    """Adiciona diferenças entre o valor de cada hora e o da hora anterior."""
    colunas_necessarias = {"time", *colunas}
    ausentes = colunas_necessarias.difference(dados.columns)
    if ausentes:
        raise ValueError(
            f"Colunas necessárias ausentes para diferenças horárias: {sorted(ausentes)}"
        )
    if not colunas:
        raise ValueError("É necessário informar ao menos uma coluna para diferenciar.")
    if len(set(colunas)) != len(colunas):
        raise ValueError("A lista de colunas não pode conter duplicatas.")

    tempos = pd.to_datetime(dados["time"], errors="raise")
    if tempos.isna().any() or tempos.duplicated().any():
        raise ValueError("A coluna 'time' contém timestamps ausentes ou duplicados.")
    if not tempos.is_monotonic_increasing:
        raise ValueError("Os timestamps devem estar em ordem cronológica crescente.")
    if not tempos.diff().iloc[1:].eq(pd.Timedelta(hours=1)).all():
        raise ValueError(
            "As diferenças horárias exigem timestamps consecutivos, "
            "com intervalo de 1 hora."
        )

    resultado = dados.copy()
    for coluna in colunas:
        valores = pd.to_numeric(resultado[coluna], errors="raise")
        resultado[f"delta_1h_{coluna}"] = valores.diff()
    return resultado


def adicionar_resumos_curto_prazo(
    dados: pd.DataFrame,
    colunas: tuple[str, ...],
) -> pd.DataFrame:
    """Adiciona média dos últimos 3 registros e mudança entre t e t-2h."""
    colunas_necessarias = {"time", *colunas}
    ausentes = colunas_necessarias.difference(dados.columns)
    if ausentes:
        raise ValueError(
            f"Colunas necessárias ausentes para resumos temporais: {sorted(ausentes)}"
        )
    if not colunas:
        raise ValueError("É necessário informar ao menos uma coluna para resumir.")
    if len(set(colunas)) != len(colunas):
        raise ValueError("A lista de colunas não pode conter duplicatas.")

    tempos = pd.to_datetime(dados["time"], errors="raise")
    if tempos.isna().any() or tempos.duplicated().any():
        raise ValueError("A coluna 'time' contém timestamps ausentes ou duplicados.")
    if not tempos.is_monotonic_increasing:
        raise ValueError("Os timestamps devem estar em ordem cronológica crescente.")
    if not tempos.diff().iloc[1:].eq(pd.Timedelta(hours=1)).all():
        raise ValueError(
            "Os resumos temporais exigem timestamps consecutivos, "
            "com intervalo de 1 hora."
        )

    resultado = dados.copy()
    for coluna in colunas:
        valores = pd.to_numeric(resultado[coluna], errors="raise")
        resultado[f"media_3h_{coluna}"] = valores.rolling(
            window=3,
            min_periods=3,
        ).mean()
        resultado[f"delta_2h_{coluna}"] = valores.diff(periods=2)
    return resultado
