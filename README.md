# Ciência de Dados e Aprendizagem de Máquina

**Projeto Acadêmico** — Universidade Braz Cubas
**Turma:** Segunda Noite N1
**Trilha:** B — Qualidade do ar inadequada

## 📚 Sobre o Projeto

Projeto desenvolvido para a disciplina de Ciência de Dados e Aprendizagem de Máquina da Universidade Braz Cubas. O tema central é a **Qualidade do Ar Inadequada**, aplicando técnicas de Ciência de Dados para analisar dados ambientais e, posteriormente, desenvolver um modelo preditivo.

**Status atual (Sprint 1 — Coleta de Dados):** concluída a coleta bruta via APIs. Ainda **não iniciadas** as etapas de transformação em DataFrames, integração das fontes, verificação de qualidade e definição da variável-alvo.

---

## 🎯 Objetivo

Utilizar dados históricos de qualidade do ar e condições meteorológicas para prever a ocorrência de **condições inadequadas de qualidade do ar** em um recorte geográfico definido.

> ⚠️ **Definição do problema — pendente de detalhamento.** Os itens abaixo ainda precisam ser explicitados (atualmente apenas o tema geral está definido):
> - Evento a ser previsto (não genérico) e **classe positiva** (ex.: IQA acima de que faixa, segundo qual referência — CETESB / OMS / IQAr).
> - **Horizonte de previsão** (ex.: prever condição inadequada em D+1).
> -  (ex.: risco à saúde por não alertar uma condição inadequada real) discutido, não apenas citado.
> - **Unidade de análise** de cada linha do dataset (proposta: 1 linha = 1 hora, em uma estação/ponto).

### Recorte geográfico

* **Localização:** Mogi das Cruzes – SP
* **Coordenadas:** -23.514561, -46.186832
* **Fuso horário:** America/Sao_Paulo

### Período de estudo

* **Coletado até o momento:** 01/01/2025 a 31/01/2025 (1 mês).
* ⚠️ **Insuficiente como histórico para a Trilha B** — será estendido nas próximas sprints para cobrir um período mais representativo (ex.: 1–2 anos), permitindo variação sazonal e volume adequado para treino/validação do modelo.

### Fontes de Dados

Open-Meteo Air Quality API — dados de qualidade do ar. Documentação oficial: https://open-meteo.com/en/docs/air-quality-api
Open-Meteo Historical Weather API — dados meteorológicos históricos. Documentação oficial: https://open-meteo.com/en/docs/historical-weather-api

⚠️ Para cada API, ainda faltam registrar: link da documentação oficial, parâmetros obrigatórios, resolução temporal, período histórico disponível na fonte e limitações conhecidas. Ver tabela de variáveis abaixo (a completar).

#### Tabela de variáveis coletadas *(preenchimento em andamento)*

| Variável | API | Unidade | Justificativa | Papel (feature / alvo) |
|---|---|---|---|---|
| `pm10` | Air Quality | µg/m³ | *(a preencher)* | *(a definir)* |
| `pm2_5` | Air Quality | µg/m³ | *(a preencher)* | *(a definir)* |
| `carbon_monoxide` | Air Quality | µg/m³ | *(a preencher)* | *(a definir)* |
| `nitrogen_dioxide` | Air Quality | µg/m³ | *(a preencher)* | *(a definir)* |
| `sulphur_dioxide` | Air Quality | µg/m³ | *(a preencher)* | *(a definir)* |
| `ozone` | Air Quality | µg/m³ | *(a preencher)* | *(a definir)* |
| `temperature_2m` | Historical Weather | °C | *(a preencher)* | *(a definir)* |
| `relative_humidity_2m` | Historical Weather | % | *(a preencher)* | *(a definir)* |
| `precipitation` | Historical Weather | mm | *(a preencher)* | *(a definir)* |
| `wind_speed_10m` | Historical Weather | km/h | *(a preencher)* | *(a definir)* |
| `pressure_msl` | Historical Weather | hPa | *(a preencher)* | *(a definir)* |

As unidades acima vêm do JSON bruto retornado pela API; a coluna "Justificativa" e "Papel" ainda precisam ser preenchidas em texto (não apenas implícitas no código).

---

## 👥 Integrantes

| Nome | R.A. |
| :--- | :--- |
| Davi Gama dos Santos | 33121079 |
| Diogo Gomes Barbosa | 35866276 |
| Eudenis de Souza Vieira | 32751621 |
| Gabriel Januário Alves | 35609991 |
| João Pedro Barreto da Silva | 33297185 |

> ⚠️ Nota: até o momento, os commits no repositório partiram apenas de Diogo Gomes e Davi Gama. A contribuição individual dos demais integrantes deve ficar registrada no notebook do guia e/ou em commits próprios.

---

## 🛠️ Tecnologias Utilizadas

* **Python** (linguagem principal)
* **Requests** — chamadas HTTP às APIs
* **Pandas** *(a incorporar na etapa de transformação)*
* **APIs REST** (Open-Meteo)

---

## 📁 Estrutura do Projeto

```text
PROJETOAPI/
│
├── dados/
│   ├── processed/
│   │   └── # Dados após limpeza e processamento (pendente)
│   │
│   └── raw/
│       ├── air_quality_raw.json
│       └── weather_raw.json
│
├── src/
│   ├── coleta/
│   │   └── Coleta_Dados.py
│   │
│   ├── exploracao/
│   │   └── # Análise exploratória dos dados (pendente)
│   │
│   ├── features/
│   │   └── # Criação e seleção de variáveis (pendente)
│   │
│   ├── limpeza/
│   │   └── # Tratamento e preparação dos dados (pendente)
│   │
│   └── modelo/
│       └── # Treinamento e aplicação do modelo (pendente)
│
├── Guia_Alunos_APIs_Trilhas_B_C.ipynb   # a preencher
└── README.md
```

---

## ✅ O que já foi feito

* `config` único (local, latitude, longitude, datas, timezone) — nada hard-coded no meio do código.
* Requisições às duas APIs exigidas pela Trilha B (qualidade do ar + clima).
* `timeout=30` configurado nas chamadas.
* `raise_for_status()` chamado em toda requisição.
* JSON bruto preservado sem transformação em `dados/raw/` (`air_quality_raw.json`, `weather_raw.json`), possibilitando auditoria e reprocessamento.

## ⚠️ Limitações conhecidas desta etapa

* Requisições sem `try/except requests.RequestException` (falha de rede/API ainda não tratada).
* Inspeção da resposta limitada a `.keys()` — falta checar `status_code`, `headers`, `Content-Type` e `resposta.url` antes da transformação.
* Sem documentação formal (links oficiais, parâmetros obrigatórios, período histórico disponível, limitações) das duas APIs.
* Sem tabela de variáveis com justificativa e papel (feature/alvo) preenchida em texto.
* Cidade do recorte não estava nomeada anteriormente — corrigido acima (Mogi das Cruzes-SP).

## 🚧 Etapas ainda não iniciadas

* **Transformação em DataFrames:** conversão da chave temporal de cada fonte com `pd.to_datetime`, checagem de cardinalidade e compatibilidade de fuso horário/resolução entre as fontes.
* **Integração (`merge`):** `how` e `validate` a serem escolhidos e justificados explicitamente (não deixados como `None`).
* **Verificação de qualidade dos dados:** `.info()`, `.describe()`, contagem de ausentes, checagem de duplicatas (linha completa e chave da unidade de análise), regras de valores inválidos por variável (ex.: concentração negativa, umidade fora do intervalo) contadas e documentadas — sem remoção automática.
* **Visualização inicial** com eixo temporal, título, rótulos e unidade.
* **Variável-alvo sem vazamento:** definição de limiar justificado (IQA/CETESB/OMS), `shift` temporal coerente com o horizonte de previsão, `dropna` das linhas sem alvo após o deslocamento, `value_counts` da distribuição de classes, e exclusão explícita de colunas que vazam informação futura.
* Preenchimento do notebook `Guia_Alunos_APIs_Trilhas_B_C.ipynb`.

---

## 🔜 Próximos passos

1. Preencher o notebook do guia (`Guia_Alunos_APIs_Trilhas_B_C.ipynb`).
2. Detalhar a definição do problema: classe positiva, horizonte de previsão e custo de falso negativo.
3. Estender o histórico coletado além de 1 mês.
4. Completar a tabela de variáveis (unidade, justificativa, papel) e documentar as APIs (links oficiais, parâmetros, limitações).
5. Implementar `try/except` nas requisições e inspeção completa da resposta antes da transformação.
6. Construir os DataFrames, converter datas com `pd.to_datetime` e realizar o `merge` com `how`/`validate` justificados.
7. Rodar a verificação inicial de qualidade dos dados.
8. Definir a variável-alvo com limiar justificado, `shift` e lista de features livre de vazamento.
9. Garantir que a contribuição de todos os integrantes fique registrada (commits e/ou notebook).
