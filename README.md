# Qualidade do Ar Inadequada — Mogi das Cruzes/SP

**Disciplina:** Ciência de Dados e Aprendizado de Máquina
**Trilha:** B — Qualidade do ar inadequada
**Equipe:** Davi Gama dos Santos (33121079) · Diogo Gomes Barbosa (35866276) · Eudenis de Souza Vieira (32751621) · Gabriel Januário Alves (35609991) · João Pedro Barreto da Silva (33297185)
**Repositório / board:** [DiogoGomesB/Ciencia-de-Dados-e-Aprendizagem-de-Maquina](https://github.com/DiogoGomesB/Ciencia-de-Dados-e-Aprendizagem-de-Maquina)

> ⚠️ Até o momento, os commits partiram apenas de Diogo Gomes Barbosa e Davi Gama dos Santos. A contribuição individual dos demais integrantes precisa ficar registrada (commits próprios e/ou diário de sprint).

---

## Status atual — Sprint 1 (17/08–17/09)

Segundo o cronograma oficial do projeto, a Sprint 1 entrega **RFC, coleta bruta, merge e `data/raw`** (limpeza, EDA e features ficam para a Sprint 2 — não se antecipa nada disso aqui).

| Entrega da Sprint 1 | Situação |
|---|---|
| RFC (`docs/RFC.md`) | ☐ Não iniciado |
| Dicionário de dados v0.1 | ☐ Não iniciado |
| Coleta bruta das duas fontes | ☒ Feito (`Coleta_Dados.py`) |
| `data/raw` com o bruto de cada API | ☒ Feito (`air_quality_raw.json`, `weather_raw.json`) |
| Merge das duas fontes | ☐ **Não feito** — pendência crítica antes do fim da Sprint 1 |
| `config` fora do código | ☒ Feito |

⚠️ **Repositório ainda não migrado para a arquitetura mínima do projeto** (seção [Estrutura do repositório](#estrutura-do-repositório)): faltam `config/params.yaml`, `notebooks/`, `docs/RFC.md`, `docs/Dicionario_de_Dados.md`, `docs/sprints/`, `requirements.txt` e a pasta `data/` com `raw/interim/processed`.

---

## Problema

* **Evento a prever:** ocorrência de condição de qualidade do ar inadequada em Mogi das Cruzes/SP.
* **Usuário da decisão:** *(a definir no RFC — ex.: gestor de saúde pública / cidadão que decide restringir atividade externa)*.
* **Horizonte:** *(a definir — ex.: prever condição inadequada em D+1, a partir dos dados disponíveis até o instante da previsão)*.

**Classe positiva:** definida pela ultrapassagem dos padrões legais de qualidade do ar, consolidados no **Índice de Qualidade do Ar (IQAr)** [1, 2]. Neste projeto:
- `0` — qualidade do ar **adequada** (IQAr até 100)
- `1` — qualidade do ar **inadequada** (IQAr na faixa **101–199**, categoria "Inadequada" do IQAr)

**Custo priorizado (FN ou FP):** falso negativo (FN) — o modelo prever "adequada" quando a hora seguinte é, de fato, inadequada. É o erro mais crítico porque o modelo deixaria de antecipar uma piora real da qualidade do ar. *(discussão completa a detalhar no RFC)*

> Horizonte, evento e unidade de análise já definidos (ver acima). Falta apenas formalizar tudo isso em `docs/RFC.md`, que ainda não existe no repositório — sem RFC formal, a Sprint 1 não está encerrada.

**Referências**
[1] FURG — Dissertação/monografia sobre padrões de qualidade do ar: https://sistemas.furg.br/sistemas/sab/arquivos/bdtd/0000010377.pdf
[2] SANTOS, C. M. dos. UnB, 2011 — Índice de Qualidade do Ar: https://repositorio.unb.br/bitstream/10482/10977/1/2011_CleideMouradosSantos.pdf

---

## Como reproduzir

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

⚠️ `requirements.txt` ainda não existe no repositório — precisa ser criado com as dependências atuais (`requests`; e, a partir da Sprint 2, `pandas`, etc.).

Configuração: `config/params.yaml` — nada de coordenadas, cidade ou datas hard-coded no código. *(Hoje o `config` está montado dentro do próprio `Coleta_Dados.py`; precisa migrar para `config/params.yaml`.)*

Notebooks: 01 → 05 *(ainda não criados — ver [Estrutura do repositório](#estrutura-do-repositório))*.

---

## Dados

| Fonte | Papel | Resolução | Medido ou modelado | Período |
|---|---|---|---|---|
| Open-Meteo Air Quality API ([docs](https://open-meteo.com/en/docs/air-quality-api)) | Qualidade do ar | Horária (dado nativo global 3/3h, interpolado) | Modelado (CAMS Global, fora da Europa) | 31/08/2022 – 31/08/2026 |
| Open-Meteo Historical Weather API ([docs](https://open-meteo.com/en/docs/historical-weather-api)) | Clima | Horária | Reanálise (ERA5/ERA5-Land/ECMWF IFS) | 31/08/2022 – 31/08/2026 |

⚠️ O período foi definido pela cobertura da fonte mais restritiva (Air Quality, domínio global disponível só a partir de agosto/2022). A Historical Weather API cobre desde 1940, mas o período foi igualado ao da qualidade do ar para manter as duas fontes no mesmo intervalo. **Pendente:** validar empiricamente que a Air Quality API retorna dado não nulo em todo esse intervalo para as coordenadas do projeto, antes da recoleta oficial (Etapa 3).

* **Unidade de análise:** 1 linha = 1 hora, no ponto de coleta (-23.514561, -46.186832 · Mogi das Cruzes/SP · `America/Sao_Paulo`). *(proposta — confirmar no RFC)*
* **N após o merge:** *(pendente — merge ainda não foi feito)*
* **Split:** *(pendente — será temporal, definido na Sprint 2; teste = período mais recente)*
* **Dicionário:** `docs/Dicionario_de_Dados.md` *(a criar; v0.1 deve cobrir as variáveis abaixo)*

### Variáveis coletadas (bruto)

| Variável | Fonte | Unidade | Justificativa | Papel (feature / alvo) |
|---|---|---|---|---|
| `pm10` | Air Quality | µg/m³ | *(a preencher no dicionário)* | *(a definir)* |
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

Nenhuma dessas colunas é, ainda, formalmente marcada como alvo ou excluída por vazamento — isso é trabalho da Sprint 2 (formação do alvo) e deve ser refletido no dicionário v0.2.

---

## Modelo

*(Nada disto é esperado antes da Sprint 3 — registrado aqui apenas como lembrete do contrato entre sprints.)*

* **Baseline:** *(Dummy `most_frequent` + Persistência — Sprint 3)*
* **Modelo final:** *(a definir na Sprint 5, no pipeline final)*
* **Limiar (escolhido na validação) e por quê:** *(a definir — nunca otimizado no teste)*
* **Métrica principal na classe positiva (teste, uma vez):** *(a definir — provavelmente recall/F1, conforme custo de FN do RFC)*

---

## Estrutura do repositório

Arquitetura-alvo (conforme padrão do projeto) — **ainda não implementada integralmente**:

```text
projeto-trilha-b/
├── README.md
├── requirements.txt                 
├── config/
│   └── params.yaml                  # a criar (hoje: dentro do .py de coleta)
├── data/
│   ├── raw/                         # ok: air_quality_raw.json, weather_raw.json
│   ├── interim/                     # a criar (Sprint 2)
│   └── processed/                   # a criar (Sprints 3–5)
├── notebooks/                       # a criar
│   ├── 01_ingestao.ipynb
│   ├── 02_limpeza_eda_features.ipynb
│   ├── 03_baseline.ipynb
│   ├── 04_features_iteracao.ipynb
│   └── 05_modelos.ipynb
├── src/                             # opcional — hoje contém a coleta atual
│   └── coleta/
│       └── Coleta_Dados.py
├── models/                          # a criar (Sprint 5)
├── docs/
│   ├── RFC.md                       # a criar
│   ├── Dicionario_de_Dados.md       # a criar
│   └── sprints/                     # a criar
└── reports/                         # a criar
```

`data/` não sobe para o Git além de um `data/README.md` com o comando de recoleta *(a criar)*.

---

## O que já foi feito

* `config` único (local, latitude, longitude, datas, timezone) — nada hard-coded no meio do código de coleta.
* Requisições às duas fontes exigidas pela Trilha B (qualidade do ar + clima), com `timeout=30` e `raise_for_status()`.
* JSON bruto preservado sem transformação em `data/raw/` (`air_quality_raw.json`, `weather_raw.json`).

## Pendências para fechar a Sprint 1

* [ ] Escrever o RFC (`docs/RFC.md`): evento, usuário, horizonte, classe positiva, custo de FN/FP.
* [ ] Criar o dicionário de dados v0.1 (`docs/Dicionario_de_Dados.md`).
* [ ] Fazer o **merge** das duas fontes e registrar o `how`/`validate` usados e o N resultante.
* [ ] Migrar a estrutura de pastas para o padrão (`config/params.yaml`, `data/raw|interim|processed`, `notebooks/`, `docs/`).
* [ ] Criar `requirements.txt`.
* [ ] Tratar exceções de rede (`try/except requests.RequestException`) e inspecionar `status_code`/`headers`/`Content-Type`/`resposta.url` antes de qualquer transformação.
* [ ] Nomear a cidade e o recorte geográfico no RFC (feito neste README: Mogi das Cruzes/SP).
* [ ] Validar empiricamente a cobertura real da Air Quality API no novo período (31/08/2022–31/08/2026) antes da recoleta oficial — histórico anterior era 01/01/2025–31/01/2025, insuficiente.
* [ ] Garantir contribuição individual de todos os integrantes registrada (commits e/ou diário de sprint).

**Lembrete:** limpeza, EDA e engenharia de atributos **não** entram na Sprint 1 — só a partir da Sprint 2, sobre dado já limpo.

---

## Documentação

- RFC: `docs/RFC.md` *(a criar)*
- Sprints: `docs/sprints/` *(a criar — `Sprint1_TrilhaB.md`, diário e evidências)*
- Model card: no diário da Sprint 5
