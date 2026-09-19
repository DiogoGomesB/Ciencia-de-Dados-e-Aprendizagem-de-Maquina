import json
import pandas as pd
import os


# ============================================================
# 1. CARREGAR DADOS BRUTOS
# ============================================================

print("=" * 60)
print("MERGE DOS DADOS - QUALIDADE DO AR + CLIMA")
print("=" * 60)

caminho_air_quality = os.path.join("data", "raw", "air_quality_raw.json")
caminho_weather = os.path.join("data", "raw", "weather_raw.json")

with open(caminho_air_quality, "r", encoding="utf-8") as f:
    dados_air_quality = json.load(f)

with open(caminho_weather, "r", encoding="utf-8") as f:
    dados_weather = json.load(f)

print(f"Dados de qualidade do ar carregados: {caminho_air_quality}")
print(f"Dados meteorológicos carregados: {caminho_weather}")


# ============================================================
# 2. CONVERTER PARA DATAFRAME
# ============================================================

df_air_quality = pd.DataFrame(dados_air_quality["hourly"])
df_weather = pd.DataFrame(dados_weather["hourly"])

print(f"\nRegistros qualidade do ar: {len(df_air_quality)}")
print(f"Registros meteorológicos: {len(df_weather)}")
print(f"Colunas qualidade do ar: {list(df_air_quality.columns)}")
print(f"Colunas meteorológicas: {list(df_weather.columns)}")


# ============================================================
# 3. REALIZAR MERGE PELA COLUNA 'time'
# ============================================================

print("\n" + "=" * 60)
print("REALIZANDO MERGE")
print("=" * 60)

df_merged = pd.merge(df_air_quality, df_weather, on="time", how="inner")

print(f"Registros após merge: {len(df_merged)}")
print(f"Colunas após merge: {list(df_merged.columns)}")


# ============================================================
# 4. VERIFICAR INCONSISTÊNCIAS
# ============================================================

print("\n" + "=" * 60)
print("VERIFICAÇÃO DE INCONSISTÊNCIAS")
print("=" * 60)

# Verificar se há valores nulos
nulos = df_merged.isnull().sum()
if nulos.sum() > 0:
    print("\nValores nulos encontrados:")
    print(nulos[nulos > 0])
else:
    print("\nNenhum valor nulo encontrado.")

# Verificar duplicatas
duplicatas = df_merged.duplicated(subset=["time"]).sum()
if duplicatas > 0:
    print(f"\nATENÇÃO: {duplicatas} registros duplicados encontrados na coluna 'time'")
else:
    print("\nNenhuma duplicata encontrada na coluna 'time'.")


# ============================================================
# 5. CRIAR DIRETÓRIO data/interim
# ============================================================

pasta_interim = os.path.join("data", "interim")
os.makedirs(pasta_interim, exist_ok=True)


# ============================================================
# 6. SALVAR DADOS MERGED
# ============================================================

print("\n" + "=" * 60)
print("SALVANDO DADOS MERGED")
print("=" * 60)

caminho_saida = os.path.join(pasta_interim, "dados_merged.csv")

df_merged.to_csv(caminho_saida, index=False, encoding="utf-8")

print(f"Dados salvos em: {caminho_saida}")
print(f"Total de registros: {len(df_merged)}")
print(f"Total de colunas: {len(df_merged.columns)}")


# ============================================================
# 7. FINALIZAÇÃO
# ============================================================

print("\n" + "=" * 60)
print("MERGE CONCLUÍDO")
print("=" * 60)

print("\nResumo:")
print(f"- Registros qualidade do ar: {len(df_air_quality)}")
print(f"- Registros meteorológicos: {len(df_weather)}")
print(f"- Registros após merge: {len(df_merged)}")
print(f"- Arquivo de saída: {caminho_saida}")
