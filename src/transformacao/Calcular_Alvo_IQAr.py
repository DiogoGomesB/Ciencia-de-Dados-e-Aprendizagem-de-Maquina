from pathlib import Path

import numpy as np
import pandas as pd
import yaml


COLUNAS_POLUENTES = (
    "pm10",
    "pm2_5",
    "carbon_monoxide",
    "nitrogen_dioxide",
    "sulphur_dioxide",
    "ozone",
)

JANELAS_HORAS = {
    "pm10": 24,
    "pm2_5": 24,
    "carbon_monoxide": 8,
    "nitrogen_dioxide": 1,
    "sulphur_dioxide": 24,
    "ozone": 8,
}

COLUNAS_SUBINDICE = {
    "pm10": "iqar_pm10",
    "pm2_5": "iqar_pm2_5",
    "carbon_monoxide": "iqar_carbon_monoxide",
    "nitrogen_dioxide": "iqar_nitrogen_dioxide",
    "sulphur_dioxide": "iqar_sulphur_dioxide",
    "ozone": "iqar_ozone",
}

# Pontos da Tabela 2.7 do relatório CETESB 2025, pareados aos índices 0, 40, 80, 120 e 200.
PONTOS_IQAR = np.array([0.0, 40.0, 80.0, 120.0, 200.0])
PONTOS_CONCENTRACAO = {
    "pm10": np.array([0.0, 50.0, 100.0, 150.0, 250.0]),
    "pm2_5": np.array([0.0, 25.0, 50.0, 75.0, 125.0]),
    "carbon_monoxide": np.array([0.0, 9.0, 11.0, 13.0, 15.0]),
    "nitrogen_dioxide": np.array([0.0, 200.0, 240.0, 320.0, 1130.0]),
    "sulphur_dioxide": np.array([0.0, 20.0, 40.0, 365.0, 800.0]),
    "ozone": np.array([0.0, 100.0, 130.0, 160.0, 200.0]),
}

TEMPERATURA_CO_K = 298.15
PRESSAO_CO_PA = 101325.0
MASSA_MOLAR_CO_G_MOL = 28.01
CONSTANTE_GAS = 8.314462618
FATOR_CO_UG_M3_PARA_PPM = (
    CONSTANTE_GAS * TEMPERATURA_CO_K
    / (MASSA_MOLAR_CO_G_MOL * PRESSAO_CO_PA)
)

COLUNA_IQAR = "iqar"
COLUNA_ALVO = "qualidade_ar_inadequada_1h"
LIMIAR_IQAR = 100.0


def _calcular_subindice(
    concentracao: pd.Series,
    poluente: str,
) -> pd.Series:
    valores = concentracao.to_numpy(dtype=float)
    pontos_concentracao = PONTOS_CONCENTRACAO[poluente]
    indices = np.full(valores.shape, np.nan, dtype=float)
    validos = np.isfinite(valores)

    indices[validos] = np.interp(
        valores[validos],
        pontos_concentracao,
        PONTOS_IQAR,
    )

    acima_do_ultimo_ponto = validos & (valores > pontos_concentracao[-1])
    indices[acima_do_ultimo_ponto] = PONTOS_IQAR[-1] + (
        valores[acima_do_ultimo_ponto] - pontos_concentracao[-1]
    ) * (
        (PONTOS_IQAR[-1] - PONTOS_IQAR[-2])
        / (pontos_concentracao[-1] - pontos_concentracao[-2])
    )

    return pd.Series(indices, index=concentracao.index)


def calcular_iqar(df: pd.DataFrame) -> pd.DataFrame:
    """Acrescenta o IQAr CETESB por horário, exigindo janelas completas."""
    colunas_necessarias = {"time", *COLUNAS_POLUENTES}
    ausentes = colunas_necessarias.difference(df.columns)
    if ausentes:
        raise ValueError(
            f"Colunas necessárias ausentes para calcular o IQAr: {sorted(ausentes)}"
        )

    resultado = df.copy().reset_index(drop=True)
    tempos = pd.to_datetime(resultado["time"], errors="raise")
    if tempos.isna().any():
        raise ValueError("A coluna 'time' contém timestamps ausentes.")
    if tempos.duplicated().any():
        raise ValueError("A coluna 'time' contém timestamps duplicados.")
    if not tempos.is_monotonic_increasing:
        raise ValueError("Os timestamps devem estar em ordem cronológica crescente.")
    if not tempos.diff().iloc[1:].eq(pd.Timedelta(hours=1)).all():
        raise ValueError("A série deve conter timestamps consecutivos, com intervalo de 1 hora.")

    for poluente in COLUNAS_POLUENTES:
        valores = pd.to_numeric(resultado[poluente], errors="raise").astype(float)
        nao_finitos = valores.notna() & ~np.isfinite(valores)
        if nao_finitos.any():
            raise ValueError(f"A coluna '{poluente}' contém valores não finitos.")
        if valores.lt(0).any():
            raise ValueError(f"A coluna '{poluente}' contém concentrações negativas.")

        janela = JANELAS_HORAS[poluente]
        media_movel = valores.rolling(window=janela, min_periods=janela).mean()
        if poluente == "carbon_monoxide":
            media_movel = media_movel * FATOR_CO_UG_M3_PARA_PPM

        resultado[COLUNAS_SUBINDICE[poluente]] = _calcular_subindice(
            media_movel,
            poluente,
        )

    resultado[COLUNA_IQAR] = resultado[list(COLUNAS_SUBINDICE.values())].max(
        axis=1,
        skipna=False,
    )
    return resultado


def adicionar_alvo_iqar(df: pd.DataFrame) -> pd.DataFrame:
    """Cria o rótulo binário de IQAr > 100 uma hora após cada instante."""
    resultado = calcular_iqar(df)
    iqar_futuro = resultado[COLUNA_IQAR].shift(-1)

    alvo = pd.Series(pd.NA, index=resultado.index, dtype="Int64")
    iqar_disponivel = iqar_futuro.notna()
    alvo.loc[iqar_disponivel] = (
        iqar_futuro.loc[iqar_disponivel]
        .gt(LIMIAR_IQAR)
        .astype("int64")
    )
    resultado[COLUNA_ALVO] = alvo
    return resultado


def main() -> None:
    caminho_config = Path("config/params.yaml")
    with caminho_config.open("r", encoding="utf-8") as arquivo:
        config = yaml.safe_load(arquivo)

    periodo = {
        "start_date": config["collection"]["start_date"],
        "end_date": config["collection"]["end_date"],
    }
    paths = config["paths"]
    pasta_interim = Path(paths["interim_data"])
    caminho_entrada = pasta_interim / paths["merged_filename"].format(**periodo)
    caminho_saida = pasta_interim / paths["labeled_filename"].format(**periodo)

    dados = pd.read_csv(caminho_entrada)
    dados_com_alvo = adicionar_alvo_iqar(dados)
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    if caminho_saida.exists():
        raise FileExistsError(
            f"O arquivo com alvo já existe e não será sobrescrito: {caminho_saida}"
        )
    dados_com_alvo.to_csv(caminho_saida, index=False, encoding="utf-8")

    alvo = dados_com_alvo[COLUNA_ALVO]
    print(f"Dados lidos de: {caminho_entrada}")
    print(f"Dados com alvo salvos em: {caminho_saida}")
    print(f"Registros totais: {len(dados_com_alvo)}")
    print(f"Rótulos definidos: {alvo.notna().sum()}")
    print(f"Classe positiva (IQAr > 100): {alvo.eq(1).sum()}")
    print(f"Rótulos indefinidos: {alvo.isna().sum()}")


if __name__ == "__main__":
    main()
