from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import yaml

COLUNA_ALVO = "qualidade_ar_inadequada_1h"
COLUNAS_POLUENTES = (
    "pm10",
    "pm2_5",
    "carbon_monoxide",
    "nitrogen_dioxide",
    "sulphur_dioxide",
    "ozone",
)
COLUNAS_EXTREMOS = ("carbon_monoxide", "pm10", "pm2_5")
COLUNAS_FEATURES = (
    *COLUNAS_POLUENTES,
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "wind_speed_10m",
    "pressure_msl",
    "iqar_pm10",
    "iqar_pm2_5",
    "iqar_carbon_monoxide",
    "iqar_nitrogen_dioxide",
    "iqar_sulphur_dioxide",
    "iqar_ozone",
    "iqar",
)
ROTULOS_FEATURES = {
    "carbon_monoxide": "CO (µg/m³)",
    "pm10": "PM10 (µg/m³)",
    "pm2_5": "PM2,5 (µg/m³)",
}


def _carregar_desenvolvimento() -> pd.DataFrame:
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
    limite_teste = pd.Timestamp(config["evaluation"]["final_test"]["start"])

    colunas_necessarias = {"time", COLUNA_ALVO, *COLUNAS_FEATURES}
    ausentes = colunas_necessarias.difference(dados.columns)
    if ausentes:
        raise ValueError(
            f"Colunas necessárias ausentes na base rotulada: {sorted(ausentes)}"
        )
    if dados["time"].isna().any() or dados["time"].duplicated().any():
        raise ValueError("A coluna 'time' contém timestamps ausentes ou duplicados.")
    if not dados["time"].is_monotonic_increasing:
        raise ValueError("Os timestamps devem estar em ordem cronológica crescente.")

    dados["event_time"] = dados["time"] + pd.Timedelta(
        hours=config["evaluation"]["target_horizon_hours"]
    )
    desenvolvimento = dados.loc[
        dados["event_time"].lt(limite_teste)
        & dados[COLUNA_ALVO].notna()
    ].copy()
    desenvolvimento[COLUNA_ALVO] = pd.to_numeric(
        desenvolvimento[COLUNA_ALVO],
        errors="raise",
    )
    if not desenvolvimento[COLUNA_ALVO].isin((0, 1)).all():
        raise ValueError(f"A coluna '{COLUNA_ALVO}' deve conter apenas 0 ou 1.")
    if desenvolvimento.empty:
        raise ValueError("A partição de desenvolvimento não contém rótulos definidos.")

    return desenvolvimento


def _plotar_prevalencia_mensal(dados: pd.DataFrame, pasta_saida: Path) -> Path:
    mensal = (
        dados.assign(mes=dados["event_time"].dt.to_period("M"))
        .groupby("mes")[COLUNA_ALVO]
        .agg(taxa="mean", positivos="sum", total="count")
    )
    datas = mensal.index.to_timestamp()
    figura, (eixo_taxa, eixo_contagem) = plt.subplots(
        2,
        1,
        figsize=(13, 8),
        sharex=True,
        layout="constrained",
    )
    eixo_taxa.plot(datas, mensal["taxa"] * 100, marker="o", markersize=3)
    eixo_taxa.axhline(
        dados[COLUNA_ALVO].mean() * 100,
        color="tab:red",
        linestyle="--",
        label="Média do desenvolvimento",
    )
    eixo_taxa.set_ylabel("Alvos positivos (%)")
    eixo_taxa.set_title("Prevalência mensal do evento previsto")
    eixo_taxa.legend()
    eixo_contagem.bar(datas, mensal["positivos"], width=24, color="tab:blue")
    eixo_contagem.set_ylabel("Eventos positivos")
    eixo_contagem.set_xlabel("Mês do evento previsto")
    eixo_contagem.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    eixo_contagem.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    eixo_contagem.tick_params(axis="x", rotation=35)

    caminho = pasta_saida / "prevalencia_mensal.png"
    figura.savefig(caminho, dpi=160)
    plt.close(figura)
    return caminho


def _plotar_boxplots(dados: pd.DataFrame, pasta_saida: Path) -> Path:
    figura, eixos = plt.subplots(
        1,
        len(COLUNAS_EXTREMOS),
        figsize=(13, 5),
        layout="constrained",
    )
    dados_plot = dados[[COLUNA_ALVO, *COLUNAS_EXTREMOS]].copy()
    dados_plot[COLUNA_ALVO] = dados_plot[COLUNA_ALVO].astype(int).astype(str)

    for eixo, coluna in zip(eixos, COLUNAS_EXTREMOS, strict=True):
        coluna_log = f"{coluna}_log1p"
        dados_plot[coluna_log] = np.log1p(dados_plot[coluna])
        sns.boxplot(
            data=dados_plot,
            x=COLUNA_ALVO,
            y=coluna_log,
            showfliers=True,
            flierprops={"marker": ".", "markersize": 1.5, "alpha": 0.18},
            ax=eixo,
        )
        eixo.set_xlabel("Classe do evento previsto")
        eixo.set_ylabel("log(1 + concentração)")
        eixo.set_title(ROTULOS_FEATURES[coluna])

    figura.suptitle("Distribuição das concentrações com cauda longa")
    caminho = pasta_saida / "boxplots_concentracoes_log1p.png"
    figura.savefig(caminho, dpi=160)
    plt.close(figura)
    return caminho


def _plotar_correlacoes(dados: pd.DataFrame, pasta_saida: Path) -> Path:
    correlacoes = dados[list(COLUNAS_FEATURES)].corr(method="spearman")
    figura, eixo = plt.subplots(figsize=(15, 13), layout="constrained")
    sns.heatmap(
        correlacoes,
        cmap="vlag",
        center=0,
        vmin=-1,
        vmax=1,
        square=True,
        linewidths=0.25,
        cbar_kws={"label": "Correlação de Spearman"},
        ax=eixo,
    )
    eixo.set_title("Associação entre features candidatas (desenvolvimento)")
    eixo.tick_params(axis="x", rotation=70)
    eixo.tick_params(axis="y", rotation=0)
    caminho = pasta_saida / "correlacao_spearman_features.png"
    figura.savefig(caminho, dpi=160)
    plt.close(figura)
    return caminho


def _limite_superior_iqr(valores: pd.Series) -> float:
    primeiro_quartil, terceiro_quartil = valores.quantile([0.25, 0.75])
    return float(terceiro_quartil + 1.5 * (terceiro_quartil - primeiro_quartil))


def _resumir_extremos(dados: pd.DataFrame) -> None:
    print("\nTriagem de extremos (cerca superior Q3 + 1,5 × IQR):")
    for coluna in COLUNAS_EXTREMOS:
        valores = dados[coluna].astype(float)
        limite_iqr = _limite_superior_iqr(valores)
        mascara = valores.gt(limite_iqr)
        dias = dados.loc[mascara, "event_time"].dt.date.nunique()
        taxa_positiva = dados.loc[mascara, COLUNA_ALVO].mean()
        quantis = valores.quantile([0.5, 0.9, 0.99, 0.999])
        print(
            f"{coluna}: mediana={quantis.loc[0.5]:.2f}; "
            f"p90={quantis.loc[0.9]:.2f}; p99={quantis.loc[0.99]:.2f}; "
            f"p99,9={quantis.loc[0.999]:.2f}; max={valores.max():.2f}; "
            f"cerca_IQR={limite_iqr:.2f}; excedências={int(mascara.sum())} "
            f"({mascara.mean():.2%}) em {dias} dias; "
            f"taxa positiva entre excedências={taxa_positiva:.2%}"
        )
        dias_extremos = (
            dados.loc[mascara]
            .groupby(dados.loc[mascara, "event_time"].dt.date)
            .agg(
                horas=(coluna, "size"),
                maximo=(coluna, "max"),
                positivos=(COLUNA_ALVO, "sum"),
            )
            .sort_values("maximo", ascending=False)
            .head(5)
        )
        print("  Dias com os maiores máximos:")
        print(dias_extremos.to_string())

    flags = pd.DataFrame(
        {
            coluna: dados[coluna].gt(_limite_superior_iqr(dados[coluna]))
            for coluna in COLUNAS_EXTREMOS
        }
    )
    print(
        "Excedências simultâneas de 0/1/2/3 cercas IQR: "
        f"{flags.sum(axis=1).value_counts().sort_index().to_dict()}"
    )


def _plotar_extremos(dados: pd.DataFrame, pasta_saida: Path) -> Path:
    figura, eixos = plt.subplots(
        len(COLUNAS_EXTREMOS),
        1,
        figsize=(13, 10),
        sharex=True,
        layout="constrained",
    )
    for eixo, coluna in zip(eixos, COLUNAS_EXTREMOS, strict=True):
        serie_diaria = (
            dados.set_index("event_time")[coluna]
            .resample("D")
            .max()
            .dropna()
        )
        valores = dados[coluna].astype(float)
        limite_p99 = float(valores.quantile(0.99))
        limite_iqr = _limite_superior_iqr(valores)
        eixo.plot(serie_diaria.index, serie_diaria, linewidth=0.8)
        eixo.axhline(
            limite_p99,
            color="tab:orange",
            linestyle="--",
            label=f"P99 horário = {limite_p99:.1f}",
        )
        eixo.axhline(
            limite_iqr,
            color="tab:red",
            linestyle=":",
            label=f"Cerca IQR = {limite_iqr:.1f}",
        )
        eixo.set_ylabel(ROTULOS_FEATURES[coluna])
        eixo.legend(loc="upper right")

    eixos[-1].set_xlabel("Instante do evento previsto (time + horizonte)")
    eixos[-1].xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    eixos[-1].xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    eixos[-1].tick_params(axis="x", rotation=35)
    figura.suptitle("Máximo diário das concentrações e limiares de triagem")
    caminho = pasta_saida / "extremos_concentracoes_tempo.png"
    figura.savefig(caminho, dpi=160)
    plt.close(figura)
    return caminho


def main() -> None:
    sns.set_theme(style="whitegrid")
    dados = _carregar_desenvolvimento()
    pasta_saida = Path("reports/figures/eda_desenvolvimento")
    pasta_saida.mkdir(parents=True, exist_ok=True)

    positivos = int(dados[COLUNA_ALVO].sum())
    print(
        f"Desenvolvimento: {len(dados)} rótulos definidos; "
        f"{positivos} positivos ({dados[COLUNA_ALVO].mean():.2%}); "
        f"eventos {dados['event_time'].min()} a {dados['event_time'].max()}."
    )
    _resumir_extremos(dados)

    caminhos = (
        _plotar_prevalencia_mensal(dados, pasta_saida),
        _plotar_boxplots(dados, pasta_saida),
        _plotar_correlacoes(dados, pasta_saida),
        _plotar_extremos(dados, pasta_saida),
    )
    print("\nGráficos gerados:")
    for caminho in caminhos:
        print(caminho)


if __name__ == "__main__":
    main()
