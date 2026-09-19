import requests
import json
import os
import yaml


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
# 2. CONFIGURAÇÃO DAS APIs
# ============================================================

url_air_quality = apis["air_quality"]["url"]
url_weather = apis["weather"]["url"]
timeout = apis["air_quality"]["timeout"]


# ============================================================
# 3. PARÂMETROS - QUALIDADE DO AR
# ============================================================

params_air_quality = {
    "latitude": location["latitude"],
    "longitude": location["longitude"],
    "start_date": collection["start_date"],
    "end_date": collection["end_date"],
    "hourly": air_quality_vars,
    "timezone": location["timezone"]
}


# ============================================================
# 4. PARÂMETROS - CLIMA
# ============================================================

params_weather = {
    "latitude": location["latitude"],
    "longitude": location["longitude"],
    "start_date": collection["start_date"],
    "end_date": collection["end_date"],
    "hourly": weather_vars,
    "timezone": location["timezone"]
}


# ============================================================
# 5. COLETA - QUALIDADE DO AR
# ============================================================

print("=" * 60)
print("COLETA DE DADOS - QUALIDADE DO AR")
print("=" * 60)

response_air_quality = requests.get(
    url_air_quality,
    params=params_air_quality,
    timeout=timeout
)

response_air_quality.raise_for_status()

dados_air_quality = response_air_quality.json()

print("Status:", response_air_quality.status_code)
print("Coleta de qualidade do ar realizada com sucesso!")


# ============================================================
# 6. COLETA - CLIMA
# ============================================================

print("\n" + "=" * 60)
print("COLETA DE DADOS - CLIMA")
print("=" * 60)

response_weather = requests.get(
    url_weather,
    params=params_weather,
    timeout=timeout
)

response_weather.raise_for_status()

dados_weather = response_weather.json()

print("Status:", response_weather.status_code)
print("Coleta meteorológica realizada com sucesso!")


# ============================================================
# 7. INSPEÇÃO DOS DADOS
# ============================================================

print("\n" + "=" * 60)
print("INSPEÇÃO DAS RESPOSTAS")
print("=" * 60)

print("\nChaves da API de Qualidade do Ar:")
print(dados_air_quality.keys())

print("\nChaves da API Meteorológica:")
print(dados_weather.keys())


# ============================================================
# 8. CRIAÇÃO DA PASTA PARA DADOS BRUTOS
# ============================================================

pasta_raw = paths["raw_data"]

os.makedirs(pasta_raw, exist_ok=True)


# ============================================================
# 9. SALVAMENTO DOS DADOS BRUTOS
# ============================================================

arquivo_air_quality = os.path.join(
    pasta_raw,
    "air_quality_raw.json"
)

arquivo_weather = os.path.join(
    pasta_raw,
    "weather_raw.json"
)


with open(arquivo_air_quality, "w", encoding="utf-8") as arquivo:
    json.dump(
        dados_air_quality,
        arquivo,
        ensure_ascii=False,
        indent=4
    )


with open(arquivo_weather, "w", encoding="utf-8") as arquivo:
    json.dump(
        dados_weather,
        arquivo,
        ensure_ascii=False,
        indent=4
    )


# ============================================================
# 10. FINALIZAÇÃO
# ============================================================

print("\n" + "=" * 60)
print("COLETA FINALIZADA")
print("=" * 60)

print("\nDados brutos salvos em:")

print(f"- {arquivo_air_quality}")
print(f"- {arquivo_weather}")

print("\nNenhuma limpeza ou transformação foi realizada.")
print("Os dados originais das APIs foram preservados.")