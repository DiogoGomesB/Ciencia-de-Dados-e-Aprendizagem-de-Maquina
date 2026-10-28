from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import pandas as pd
import requests
import yaml

from src.modelagem.Avaliar_Baselines import FEATURES_SPRINT4
from src.transformacao.Calcular_Alvo_IQAr import calcular_iqar
from src.transformacao.Features_Temporais import adicionar_resumos_curto_prazo

COLUNAS_CONTEXTO_CURTO_PRAZO = ("ozone", "pm2_5")
MODELO_FINAL_PATH = Path("models") / "modelo_final_sprint5.joblib"


def _carregar_config() -> dict[str, Any]:
    caminho = Path("config") / "params.yaml"
    with caminho.open("r", encoding="utf-8") as arquivo:
        return yaml.safe_load(arquivo)


def _coletar_api(url: str, params: dict[str, Any], timeout: int) -> dict[str, Any]:
    resposta = requests.get(url, params=params, timeout=timeout)
    resposta.raise_for_status()
    return resposta.json()


def _json_para_dataframe_hourly(dados: dict[str, Any], nome_api: str) -> pd.DataFrame:
    if "hourly" not in dados:
        raise ValueError(f"A resposta da API '{nome_api}' não contém a chave 'hourly'.")
    quadro = pd.DataFrame(dados["hourly"])
    if "time" not in quadro.columns:
        raise ValueError(f"A resposta da API '{nome_api}' não contém a coluna 'time'.")
    return quadro


def _limitar_ate_agora(
    dados: pd.DataFrame,
    fuso_horario: str,
    agora: pd.Timestamp | None = None,
) -> pd.DataFrame:
    """Descarta horas futuras: as APIs devolvem o resto do dia como previsão."""
    if agora is None:
        agora = pd.Timestamp.now(tz=fuso_horario).tz_localize(None)
    limite = agora.floor("h")
    passado = dados.loc[pd.to_datetime(dados["time"]).le(limite)]
    if passado.empty:
        raise RuntimeError("Nenhuma hora até o momento atual foi retornada pelas APIs.")
    return passado.reset_index(drop=True)


def _coletar_serie_com_projecao(
    config: dict[str, Any],
    forecast_days: int = 2,
) -> pd.DataFrame:
    """Coleta histórico recente e projeção horária futura das APIs da Open-Meteo."""
    location = config["location"]
    apis = config["apis"]
    aplicacao = config.get("application", {})

    dias_historico = int(aplicacao.get("recent_history_days", 3))
    if dias_historico < 2:
        raise ValueError("application.recent_history_days deve ser >= 2 para formar features temporais.")
    if forecast_days < 1:
        raise ValueError("forecast_days deve ser >= 1.")

    timeout_air = int(apis["air_quality"]["timeout"])
    timeout_weather = int(
        apis.get("weather_forecast", {}).get("timeout", apis["weather"]["timeout"])
    )

    params_air = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "hourly": config["air_quality_variables"],
        "timezone": location["timezone"],
        "past_days": dias_historico,
        "forecast_days": forecast_days,
    }
    params_weather = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "hourly": config["weather_variables"],
        "timezone": location["timezone"],
        "past_days": dias_historico,
        "forecast_days": forecast_days,
    }

    dados_air = _coletar_api(
        apis["air_quality"]["url"],
        params_air,
        timeout_air,
    )
    url_weather = apis.get("weather_forecast", {}).get(
        "url",
        "https://api.open-meteo.com/v1/forecast",
    )
    dados_weather = _coletar_api(
        url_weather,
        params_weather,
        timeout_weather,
    )

    quadro_air = _json_para_dataframe_hourly(dados_air, "air_quality")
    quadro_weather = _json_para_dataframe_hourly(dados_weather, "weather_forecast")

    dados = pd.merge(quadro_air, quadro_weather, on="time", how="inner")
    if dados.empty:
        raise RuntimeError("A junção das séries horárias retornou vazia; não há dados em comum entre as APIs.")

    dados = dados.sort_values("time").reset_index(drop=True)
    dados["time"] = pd.to_datetime(dados["time"], errors="raise")
    if dados["time"].duplicated().any():
        raise RuntimeError("A junção gerou timestamps duplicados, impedindo a inferência temporal.")
    return dados


def _coletar_dados_recentes(config: dict[str, Any]) -> pd.DataFrame:
    dados = _coletar_serie_com_projecao(config, forecast_days=1)
    return _limitar_ate_agora(dados, config["location"]["timezone"])


def _carregar_artefato_modelo(caminho_modelo: Path) -> dict[str, Any]:
    if not caminho_modelo.exists():
        raise FileNotFoundError(
            f"Modelo não encontrado em '{caminho_modelo}'. Gere o arquivo antes de prever."
        )
    artefato = joblib.load(caminho_modelo)
    chaves_necessarias = {
        "pipeline",
        "features",
        "decision_threshold",
        "target_horizon_hours",
    }
    faltantes = chaves_necessarias.difference(artefato)
    if faltantes:
        raise RuntimeError(
            f"Artefato do modelo inválido; faltam chaves: {sorted(faltantes)}"
        )
    return artefato


def _preparar_linha_mais_recente(
    dados_brutos: pd.DataFrame,
    features_modelo: list[str],
) -> pd.DataFrame:
    com_iqar = calcular_iqar(dados_brutos)
    com_features = adicionar_resumos_curto_prazo(com_iqar, COLUNAS_CONTEXTO_CURTO_PRAZO)

    ausentes = set(features_modelo).difference(com_features.columns)
    if ausentes:
        raise RuntimeError(
            f"As seguintes features exigidas pelo modelo não existem na base atual: {sorted(ausentes)}"
        )

    elegiveis = com_features.dropna(subset=features_modelo)
    if elegiveis.empty:
        raise RuntimeError(
            "Não há linha elegível para inferência após calcular as features. "
            "Aumente application.recent_history_days ou verifique lacunas nos dados horários."
        )

    return elegiveis.iloc[[-1]][features_modelo + ["time"]]


def _projetar_janela_futura(
    dados_serie: pd.DataFrame,
    artefato: dict[str, Any],
    horario_base: pd.Timestamp,
    horas_frente: int = 24,
) -> pd.DataFrame:
    """Projeta experimentalmente as próximas horas (+1h até +horas_frente)."""
    if horas_frente < 1:
        raise ValueError("horas_frente deve ser >= 1.")

    features_modelo = list(artefato["features"])
    if features_modelo != list(FEATURES_SPRINT4):
        raise RuntimeError(
            "As features do artefato não correspondem às features congeladas da Sprint 4."
        )

    pipeline = artefato["pipeline"]
    if not hasattr(pipeline, "predict_proba"):
        raise TypeError("O pipeline empacotado não fornece predict_proba.")

    com_iqar = calcular_iqar(dados_serie)
    com_features = adicionar_resumos_curto_prazo(com_iqar, COLUNAS_CONTEXTO_CURTO_PRAZO)

    ausentes = set(features_modelo).difference(com_features.columns)
    if ausentes:
        raise RuntimeError(
            f"As seguintes features exigidas pelo modelo não existem na base atual: {sorted(ausentes)}"
        )

    limite_base = pd.Timestamp(horario_base).floor("h")
    elegiveis = (
        com_features.loc[pd.to_datetime(com_features["time"]).ge(limite_base)]
        .dropna(subset=features_modelo)
        .head(horas_frente)
        .copy()
    )
    if elegiveis.empty:
        raise RuntimeError(
            "Não há linhas elegíveis para projeção futura após calcular as features."
        )

    limiar = float(artefato["decision_threshold"])
    horizonte = pd.Timedelta(hours=int(artefato["target_horizon_hours"]))
    mapa_iqar = com_iqar.set_index(pd.to_datetime(com_iqar["time"]))["iqar"]

    probabilidades = pipeline.predict_proba(elegiveis[features_modelo])[:, 1]
    linhas: list[dict[str, Any]] = []
    for passo, (horario_t_raw, prob) in enumerate(
        zip(elegiveis["time"], probabilidades),
        start=1,
    ):
        horario_t = pd.Timestamp(horario_t_raw)
        horario_evento = horario_t + horizonte
        prob_float = float(prob)
        classe_alerta = int(prob_float >= limiar)
        iqar_previsto = float(mapa_iqar.get(horario_evento, float("nan")))
        linhas.append(
            {
                "horizonte": f"+{passo}h",
                "horário base da janela": horario_t,
                "horário do evento previsto": horario_evento,
                "iqar projetado (CAMS)": (
                    round(iqar_previsto, 2) if pd.notna(iqar_previsto) else float("nan")
                ),
                "probabilidade estimada de IQAr > 100": prob_float,
                "limiar congelado": limiar,
                "resultado da regra": (
                    "ALERTA (projeção experimental)"
                    if classe_alerta
                    else "Sem alerta pela regra"
                ),
            }
        )

    return pd.DataFrame(linhas)


def prever_proxima_hora() -> pd.DataFrame:
    config = _carregar_config()
    artefato = _carregar_artefato_modelo(MODELO_FINAL_PATH)

    features_modelo = list(artefato["features"])
    if features_modelo != list(FEATURES_SPRINT4):
        raise RuntimeError(
            "As features do artefato não correspondem às features congeladas da Sprint 4."
        )

    amostra = _preparar_linha_mais_recente(_coletar_dados_recentes(config), features_modelo)
    pipeline = artefato["pipeline"]
    if not hasattr(pipeline, "predict_proba"):
        raise TypeError("O pipeline empacotado não fornece predict_proba.")

    limiar = float(artefato["decision_threshold"])
    horizonte = pd.Timedelta(hours=int(artefato["target_horizon_hours"]))
    probabilidade = float(pipeline.predict_proba(amostra[features_modelo])[0, 1])
    classe_alerta = int(probabilidade >= limiar)

    horario_t = pd.Timestamp(amostra["time"].iloc[0])
    horario_evento = horario_t + horizonte
    resultado = "ALERTA (regra experimental)" if classe_alerta else "Sem alerta pela regra"

    return pd.DataFrame(
        [
            {
                "horário dos dados até t": horario_t,
                "horário do evento previsto": horario_evento,
                "probabilidade estimada de IQAr > 100": probabilidade,
                "limiar congelado": limiar,
                "resultado da regra": resultado,
            }
        ]
    )


def projetar_proximas_horas(
    horas_frente: int = 24,
    agora: pd.Timestamp | None = None,
) -> pd.DataFrame:
    """Projeta experimentalmente as próximas horas (ex.: 7h ou 24h) com dados das APIs."""
    config = _carregar_config()
    artefato = _carregar_artefato_modelo(MODELO_FINAL_PATH)
    dias_previsao = max(2, (int(horas_frente) // 24) + 2)
    serie = _coletar_serie_com_projecao(config, forecast_days=dias_previsao)
    if agora is None:
        agora = pd.Timestamp.now(tz=config["location"]["timezone"]).tz_localize(None)
    return _projetar_janela_futura(
        serie,
        artefato,
        agora.floor("h"),
        horas_frente=horas_frente,
    )


def main() -> None:
    resumo = prever_proxima_hora()
    print("=== 1. Previsão Oficial Validada (+1h à frente) ===")
    print(resumo.to_string(index=False))
    print()

    projecao_24h = projetar_proximas_horas(horas_frente=24)
    print("=== 2. Projeção Experimental — Próximas 7 Horas (Turno) ===")
    print(projecao_24h.head(7).to_string(index=False))
    print()

    print("=== 3. Projeção Experimental — Próximas 24 Horas (Dia Completo) ===")
    print(projecao_24h.to_string(index=False))
    print()
    print(
        "Previsão operacional +1h e projeção experimental (+7h / +24h) com dados recentes de API. "
        "Use como apoio experimental, não como alerta oficial de saúde."
    )


if __name__ == "__main__":
    main()
