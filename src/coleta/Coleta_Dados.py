import json
import logging
import os
import time
from typing import Any

import requests
import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def requisitar_api_com_retry(
    url: str,
    params: dict[str, Any],
    timeout: int = 30,
    max_tentativas: int = 3,
    espera_inicial_s: float = 2.0,
) -> dict[str, Any]:
    """Executa requisição HTTP GET com timeout, try/except, retry exponencial e log."""
    ultima_excecao: Exception | None = None
    for tentativa in range(1, max_tentativas + 1):
        try:
            logger.info(
                "Requisitando %s (tentativa %d/%d, timeout=%ds)",
                url,
                tentativa,
                max_tentativas,
                timeout,
            )
            response = requests.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            logger.info("Resposta recebida com sucesso (HTTP %d).", response.status_code)
            return response.json()
        except requests.RequestException as erro:
            ultima_excecao = erro
            logger.warning(
                "Falha na tentativa %d/%d para %s: %s",
                tentativa,
                max_tentativas,
                url,
                erro,
            )
            if tentativa < max_tentativas:
                tempo_espera = espera_inicial_s * (2 ** (tentativa - 1))
                logger.info("Aguardando %.1fs antes da próxima tentativa...", tempo_espera)
                time.sleep(tempo_espera)
    logger.error("Todas as %d tentativas falharam para %s.", max_tentativas, url)
    assert ultima_excecao is not None
    raise ultima_excecao


def main() -> None:
    # ============================================================
    # 1. CARREGAR CONFIGURAÇÃO
    # ============================================================
    config_path = os.path.join("config", "params.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    location = config["location"]
    collection = config["collection"]
    air_quality_vars = config["air_quality_variables"]
    weather_vars = config["weather_variables"]
    apis = config["apis"]
    paths = config["paths"]

    # ============================================================
    # 2. CONFIGURAÇÃO DAS APIs E VERIFICAÇÃO DE IDEMPOTÊNCIA
    # ============================================================
    url_air_quality = os.getenv("OPENMETEO_AIR_QUALITY_URL", apis["air_quality"]["url"])
    url_weather = os.getenv("OPENMETEO_WEATHER_ARCHIVE_URL", apis["weather"]["url"])
    timeout = int(os.getenv("OPENMETEO_TIMEOUT_SECONDS", apis["air_quality"]["timeout"]))
    periodo = {
        "start_date": collection["start_date"],
        "end_date": collection["end_date"],
    }
    pasta_raw = os.getenv("RAW_DATA_DIR", paths["raw_data"])
    arquivo_air_quality = os.path.join(
        pasta_raw,
        paths["air_quality_raw_filename"].format(**periodo),
    )
    arquivo_weather = os.path.join(
        pasta_raw,
        paths["weather_raw_filename"].format(**periodo),
    )

    if os.path.exists(arquivo_air_quality) or os.path.exists(arquivo_weather):
        raise FileExistsError(
            "Já existe pelo menos um arquivo bruto para o período configurado. "
            f"Os arquivos não serão sobrescritos: {arquivo_air_quality}, {arquivo_weather}"
        )

    # ============================================================
    # 3. PARÂMETROS - QUALIDADE DO AR E CLIMA
    # ============================================================
    params_air_quality = {
        "latitude": float(os.getenv("OPENMETEO_LATITUDE", location["latitude"])),
        "longitude": float(os.getenv("OPENMETEO_LONGITUDE", location["longitude"])),
        "start_date": collection["start_date"],
        "end_date": collection["end_date"],
        "hourly": air_quality_vars,
        "timezone": os.getenv("OPENMETEO_TIMEZONE", location["timezone"]),
    }

    params_weather = {
        "latitude": float(os.getenv("OPENMETEO_LATITUDE", location["latitude"])),
        "longitude": float(os.getenv("OPENMETEO_LONGITUDE", location["longitude"])),
        "start_date": collection["start_date"],
        "end_date": collection["end_date"],
        "hourly": weather_vars,
        "timezone": os.getenv("OPENMETEO_TIMEZONE", location["timezone"]),
    }

    # ============================================================
    # 4. COLETA COM RETRY E LOG
    # ============================================================
    print("=" * 60)
    print("COLETA DE DADOS - QUALIDADE DO AR")
    print("=" * 60)
    dados_air_quality = requisitar_api_com_retry(
        url_air_quality,
        params=params_air_quality,
        timeout=timeout,
    )
    print("Coleta de qualidade do ar realizada com sucesso!")

    print("\n" + "=" * 60)
    print("COLETA DE DADOS - CLIMA")
    print("=" * 60)
    dados_weather = requisitar_api_com_retry(
        url_weather,
        params=params_weather,
        timeout=timeout,
    )
    print("Coleta meteorológica realizada com sucesso!")

    # ============================================================
    # 5. SALVAMENTO DOS DADOS BRUTOS
    # ============================================================
    os.makedirs(pasta_raw, exist_ok=True)

    with open(arquivo_air_quality, "w", encoding="utf-8") as arquivo:
        json.dump(dados_air_quality, arquivo, ensure_ascii=False, indent=4)

    with open(arquivo_weather, "w", encoding="utf-8") as arquivo:
        json.dump(dados_weather, arquivo, ensure_ascii=False, indent=4)

    print("\n" + "=" * 60)
    print("COLETA FINALIZADA")
    print("=" * 60)
    print("\nDados brutos salvos em:")
    print(f"- {arquivo_air_quality}")
    print(f"- {arquivo_weather}")
    print("\nNenhuma limpeza ou transformação foi realizada.")
    print("Os dados originais das APIs foram preservados.")


if __name__ == "__main__":
    main()
