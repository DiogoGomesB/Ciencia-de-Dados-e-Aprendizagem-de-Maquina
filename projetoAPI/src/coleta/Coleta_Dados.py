import requests
import json
import os


# ============================================================
# 1. CONFIGURAÇÃO DA COLETA
# ============================================================

config = {
    "latitude": -23.514561,
    "longitude": -46.186832,
    "start_date": "2025-01-01",
    "end_date": "2025-01-31",
    "timezone": "America/Sao_Paulo",

    "air_quality_variables": [
        "pm10",
        "pm2_5",
        "carbon_monoxide",
        "nitrogen_dioxide",
        "sulphur_dioxide",
        "ozone"
    ],

    "weather_variables": [
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation",
        "wind_speed_10m",
        "pressure_msl"
    ]
}


# ============================================================
# 2. CONFIGURAÇÃO DAS APIs
# ============================================================

url_air_quality = "https://air-quality-api.open-meteo.com/v1/air-quality"

url_weather = "https://archive-api.open-meteo.com/v1/archive"


# ============================================================
# 3. PARÂMETROS - QUALIDADE DO AR
# ============================================================

params_air_quality = {
    "latitude": config["latitude"],
    "longitude": config["longitude"],
    "start_date": config["start_date"],
    "end_date": config["end_date"],
    "hourly": [
        "pm10",
        "pm2_5",
        "carbon_monoxide",
        "nitrogen_dioxide",
        "sulphur_dioxide",
        "ozone"
    ],
    "timezone": config["timezone"]
}


# ============================================================
# 4. PARÂMETROS - CLIMA
# ============================================================

params_weather = {
    "latitude": config["latitude"],
    "longitude": config["longitude"],
    "start_date": config["start_date"],
    "end_date": config["end_date"],
    "hourly": [
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation",
        "wind_speed_10m",
        "pressure_msl"
    ],
    "timezone": config["timezone"]
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
    timeout=30
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
    timeout=30
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

pasta_raw = os.path.join("dados", "raw")

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