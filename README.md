# Qualidade do Ar Inadequada — Mogi das Cruzes/SP

**Disciplina:** Ciência de Dados e Aprendizado de Máquina
**Título: Previsão da Qualidade do Ar Inadequada em Na Região da Faculdade UBC

**Trilha:** B — Qualidade do ar inadequada

**Equipe:** Davi Gama dos Santos (33121079) · Diogo Gomes Barbosa (35866276) · Eudenis de Souza Vieira (32751621) · Gabriel Januário Alves (35609991) · João Pedro Barreto da Silva (33297185)

**Repositório:** [DiogoGomesB/Ciencia-de-Dados-e-Aprendizagem-de-Maquina](https://github.com/DiogoGomesB/Ciencia-de-Dados-e-Aprendizagem-de-Maquina)

**Licença:** MIT (arquivo `LICENSE` no repositório)

---

## Status da Sprint 1 (17/08/2026 a 17/09/2026)

Conforme o cronograma do projeto, a Sprint 1 tem como entregas obrigatórias o RFC, a coleta bruta, o merge das duas fontes e a organização de `data/raw`. Limpeza, análise exploratória e engenharia de atributos são objeto da Sprint 2 e não são antecipadas nesta etapa.

| Entrega | Status | Observação |
|---|---|---|
| RFC | Concluída | `RFC_Proposta_de_Projeto_Template.md` |
| Dicionário de dados v0.1 | Concluída | `docs/Dicionario_de_Dados.md`, conforme `SPRINT1_TRILHA.md` |
| Coleta bruta das duas fontes | Concluída | `Coleta_Dados.py` |
| Armazenamento em `data/raw` | Concluída, com ressalva | Arquivos gerados ainda correspondem ao período de teste (01/01/2025 a 31/01/2025), não ao período oficial do projeto |
| Merge das duas fontes | Pendente | Depende da recoleta com o período oficial; é a pendência crítica da sprint |
| Configuração externa ao código | Concluída | — |
| `requirements.txt` | Concluída | — |
| `LICENSE` | Concluída | MIT |

**Pendência crítica:** o período histórico oficial do projeto foi definido em **31/08/2022 a 31/08/2026** (ver seção [Dados](#dados)), mas a coleta registrada em `data/raw/` ainda corresponde ao período de teste inicial (01/01/2025 a 31/01/2025, 744 registros por fonte). É necessário executar novamente `Coleta_Dados.py` com o período oficial antes de considerar a Sprint 1 encerrada.

**Estrutura de pastas:** o repositório já contém `data/raw/`, `docs/`, `src/` e `notebooks/`, conforme `SPRINT1_TRILHA.md`. Permanecem pendentes a criação de `config/params.yaml` (a configuração ainda está definida dentro de `Coleta_Dados.py`), o preenchimento de `notebooks/` e a criação de `docs/sprints/`.

---

## Problema

| Item | Definição |
|---|---|
| Evento a prever | A qualidade do ar em Mogi das Cruzes/SP estará inadequada na próxima hora. |
| Usuário da decisão | A definir no RFC (proposta: gestor de saúde pública ou indivíduo que decide restringir atividade externa). |
| Horizonte | Uma hora à frente — a previsão realizada no instante *t* utiliza dados disponíveis até *t* para estimar a condição em *t+1h*. |
| Classe positiva | Definida pela ultrapassagem dos padrões legais de qualidade do ar, consolidados no Índice de Qualidade do Ar (IQAr) [1, 2]. Classe 0: qualidade do ar adequada (IQAr até 100). Classe 1: qualidade do ar inadequada (IQAr entre 101 e 199, categoria "Inadequada" do IQAr). |
| Custo priorizado | Falso negativo — o modelo prever "adequada" quando a condição real na hora seguinte é inadequada. Considerado o erro mais grave, pois compromete a antecipação de uma piora real da qualidade do ar. |

Status: evento, horizonte, classe positiva e custo de falso negativo já estão formalizados no RFC (`RFC_Proposta_de_Projeto_Template.md`). Permanecem pendentes a definição do usuário da decisão e o desenvolvimento em texto corrido da discussão sobre o custo do falso negativo, hoje apenas enunciado.

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

O arquivo `requirements.txt` já está no repositório e cobre as dependências de coleta (`requests`), configuração (`PyYAML`), transformação (`pandas`, `numpy`), visualização (`matplotlib`, `seaborn`) e o notebook do guia (`jupyter`).

Configuração: prevista em `config/params.yaml`, de modo que nenhuma coordenada, cidade ou data fique fixada diretamente no código. Atualmente essa configuração ainda está definida dentro de `Coleta_Dados.py`; a migração para `config/params.yaml` permanece pendente.

Notebooks: a pasta `notebooks/` já foi criada no repositório, mas está vazia. O preenchimento com os notebooks 01 a 05 está pendente (ver [Estrutura do repositório](#estrutura-do-repositório)).

---

## Dados

| Fonte | Papel | Resolução | Natureza do dado | Período |
|---|---|---|---|---|
| Open-Meteo Air Quality API ([documentação](https://open-meteo.com/en/docs/air-quality-api)) | Qualidade do ar | Horária (dado nativo do domínio global a cada 3 horas, interpolado pela API) | Modelado (CAMS Global, para localidades fora da Europa) | 31/08/2022 a 31/08/2026 |
| Open-Meteo Historical Weather API ([documentação](https://open-meteo.com/en/docs/historical-weather-api)) | Clima | Horária | Reanálise (ERA5 / ERA5-Land / ECMWF IFS) | 31/08/2022 a 31/08/2026 |

O período foi definido pela cobertura da fonte mais restritiva: a Air Quality API só oferece dado consistente para localidades fora da Europa (domínio CAMS Global) a partir de agosto de 2022. A Historical Weather API cobre desde 1940 e não é o fator limitante. Permanece pendente a validação empírica de que a Air Quality API retorna dado não nulo em todo o intervalo definido, antes da execução da recoleta oficial.

**Limitações identificadas na coleta** (segundo `SPRINT1_TRILHA.md`):
- As APIs retornam a coordenada da célula de grade do modelo, que pode diferir ligeiramente da coordenada solicitada (-23.514561, -46.186832). Essa diferença é esperada em dado modelado ou de reanálise e não constitui erro de coleta, mas deve ser considerada na interpretação dos resultados.
- A validação inicial, referente ao período de teste (janeiro de 2025), não identificou valores nulos e confirmou compatibilidade das unidades com a documentação oficial. Essa validação cobre apenas o mês de teste, não o período oficial ainda a ser coletado.

### Documentação oficial das APIs

**Open-Meteo Air Quality API**
- Endpoint: `GET https://air-quality-api.open-meteo.com/v1/air-quality`
- Parâmetros obrigatórios: `latitude`, `longitude`
- Parâmetros utilizados pelo projeto: `hourly` (lista de poluentes), `start_date`, `end_date`, `timezone=America/Sao_Paulo`
- Resolução temporal: a série é entregue como horária, mas para coordenadas fora da Europa o dado é originado do domínio CAMS Global, cuja resolução nativa do modelo é de 3 em 3 horas. Os valores horários intermediários são interpolados pela API e não constituem observações independentes.
- Período histórico disponível na fonte: domínio global (fora da Europa), a partir de agosto de 2022; domínio europeu possui reanálise desde 2013, não aplicável a este projeto.
- Limitações: dado modelado (CAMS), não corresponde a medição direta de estação; resolução espacial de aproximadamente 45 km fora da Europa; o uso de `start_date` além do intervalo documentado para o parâmetro `past_days` (0 a 92 dias) não é oficialmente garantido pela documentação, ainda que a tabela de fontes de dados confirme cobertura desde agosto de 2022.

**Open-Meteo Historical Weather API**
- Endpoint: `GET https://archive-api.open-meteo.com/v1/archive`
- Parâmetros obrigatórios: `latitude`, `longitude`, `start_date`, `end_date`
- Parâmetros utilizados pelo projeto: `hourly` (lista de variáveis meteorológicas), `timezone=America/Sao_Paulo`
- Resolução temporal: horária, nativa.
- Período histórico disponível na fonte: reanálise ERA5 desde 1940 (resolução de 0,25°); ERA5-Land desde 1950 (resolução de 0,1°); ECMWF IFS desde 2017 (resolução de 9 km). Não constitui fator limitante para este projeto.
- Limitações: dado de reanálise, combinando estações, satélite, radar e modelo; não corresponde a medição direta pontual e pode divergir de estação local em eventos de curta duração, como chuva convectiva isolada.

**Unidade de análise:** cada linha corresponde a uma observação horária no ponto de coleta (-23.514561, -46.186832, Mogi das Cruzes/SP, fuso horário `America/Sao_Paulo`), conforme definido no RFC.

**N após o merge:** pendente — o merge das duas fontes ainda não foi realizado.

**Split:** pendente — será temporal, com definição prevista para a Sprint 2; o conjunto de teste corresponderá ao período mais recente.

**Dicionário de dados:** `docs/Dicionario_de_Dados.md`, já criado conforme `SPRINT1_TRILHA.md`. Recomenda-se conferir se o conteúdo do arquivo corresponde à tabela de variáveis apresentada a seguir.

### Variáveis coletadas

O critério adotado para a classe positiva é o IQAr consolidado, calculado como o maior sub-índice entre os seis poluentes coletados (metodologia CETESB), com a faixa de 101 a 199 correspondendo à classificação de qualidade do ar inadequada.

| Variável | Fonte | Unidade | Justificativa | Papel |
|---|---|---|---|---|
| `pm10` | Air Quality | µg/m³ | Poluente regulado pelo IQAr; indicador de material particulado grosso, associado a queimadas e poeira urbana. | Feature (valor no instante *t*) e base do alvo (valor em *t+1h*, via deslocamento temporal) |
| `pm2_5` | Air Quality | µg/m³ | Poluente regulado pelo IQAr; partícula fina com maior impacto respiratório, frequentemente responsável pelo sub-índice mais crítico em áreas urbanas. | Feature (t) e base do alvo (t+1h) |
| `carbon_monoxide` | Air Quality | µg/m³ | Poluente regulado pelo IQAr; indicador de queima incompleta, associado a tráfego e queimadas. | Feature (t) e base do alvo (t+1h) |
| `nitrogen_dioxide` | Air Quality | µg/m³ | Poluente regulado pelo IQAr; associado a emissões veiculares. | Feature (t) e base do alvo (t+1h) |
| `sulphur_dioxide` | Air Quality | µg/m³ | Poluente regulado pelo IQAr; associado à queima de combustíveis fósseis industriais. | Feature (t) e base do alvo (t+1h) |
| `ozone` | Air Quality | µg/m³ | Poluente regulado pelo IQAr; formado fotoquimicamente, sensível a temperatura e radiação solar. | Feature (t) e base do alvo (t+1h) |
| `temperature_2m` | Historical Weather | °C | Influencia a formação de ozônio e a dispersão vertical dos poluentes. | Feature |
| `relative_humidity_2m` | Historical Weather | % | Afeta a permanência de material particulado em suspensão. | Feature |
| `precipitation` | Historical Weather | mm | A chuva remove particulados da atmosfera por lavagem úmida, explicando quedas súbitas de concentração. | Feature |
| `wind_speed_10m` | Historical Weather | km/h | O vento dispersa poluentes; velocidades baixas favorecem acúmulo e picos de concentração. | Feature |
| `pressure_msl` | Historical Weather | hPa | Associada à estabilidade atmosférica; pressão alta e vento fraco favorecem inversões térmicas e acúmulo de poluentes. | Feature |

**Atenção ao risco de vazamento:** os seis poluentes desempenham dupla função no projeto — como feature, no valor observado em *t*, disponível no instante da previsão; e como insumo do alvo, no valor em *t+1h*, deslocado para o cálculo do IQAr da hora seguinte. Trata-se da mesma coluna em dois momentos distintos: a versão em *t+1h*, utilizada para compor o alvo, não deve integrar a lista de features do modelo — apenas a versão em *t*. A implementação formal do deslocamento temporal e da exclusão de variáveis por vazamento está prevista para a Sprint 2; o critério e a justificativa já estão consolidados neste documento.

---

## Modelo

Nenhum destes itens é esperado antes da Sprint 3; estão registrados aqui como referência do contrato entre sprints.

| Item | Status |
|---|---|
| Baseline | A definir na Sprint 3 (Dummy `most_frequent` e Persistência) |
| Modelo final | A definir na Sprint 5, no pipeline final |
| Limiar de decisão | A definir na validação; não deve ser otimizado no conjunto de teste |
| Métrica principal | A definir — provavelmente recall ou F1 da classe positiva, em conformidade com o custo de falso negativo definido no RFC |

---

## Estrutura do repositório

Arquitetura de referência do projeto, com indicação do que já está implementado:

```text
Ciencia-de-Dados-e-Aprendizagem-de-Maquina/
├── README.md
├── LICENSE                           # concluído (MIT)
├── requirements.txt                  # concluído
├── config/
│   └── params.yaml                   # pendente (configuração ainda em Coleta_Dados.py)
├── data/
│   ├── raw/                          # concluído: air_quality_raw.json, weather_raw.json
│   │                                 # (período de teste; recoleta com o período oficial pendente)
│   ├── interim/                      # pendente (Sprint 2)
│   └── processed/                    # pendente (Sprints 3 a 5)
├── notebooks/                        # criada, ainda vazia
├── src/
│   └── coleta/
│       └── Coleta_Dados.py           # concluído
├── models/                           # pendente (Sprint 5)
├── docs/
│   ├── RFC.md                        # concluído — RFC_Proposta_de_Projeto_Template.md
│   ├── Dicionario_de_Dados.md        # concluído — conforme SPRINT1_TRILHA.md
│   └── sprints/                      # pendente — deve receber o SPRINT1_TRILHA.md
└── reports/                          # pendente
```

A pasta `data/` não deve ser versionada integralmente no Git; recomenda-se manter um `data/README.md` com o comando de recoleta (a criar).

---

## Trabalho realizado

- Configuração centralizada (local, latitude, longitude, datas, fuso horário), sem valores fixados diretamente no código de coleta.
- Requisições às duas fontes exigidas pela Trilha B (qualidade do ar e clima), com `timeout=30` e `raise_for_status()`.
- Dados brutos preservados sem transformação em `data/raw/` (`air_quality_raw.json`, `weather_raw.json`).
- RFC formalizado, com evento, horizonte, classe positiva, custo de falso negativo, documentação das APIs e tabela de variáveis.
- Dicionário de dados v0.1 criado.
- `requirements.txt` e `LICENSE` (MIT) adicionados ao repositório.

## Pendências para o encerramento da Sprint 1

| Pendência | Prioridade |
|---|---|
| Recoletar os dados com o período oficial (31/08/2022 a 31/08/2026) | Crítica — bloqueia as demais pendências desta lista |
| Validar empiricamente a cobertura da Air Quality API no período oficial, antes da recoleta | Alta |
| Realizar o merge das duas fontes, com `how` e `validate` explicitados e justificados, e registrar o N resultante | Alta — depende da recoleta |
| Adicionar tratamento de exceções de rede (`try/except requests.RequestException`) e inspeção completa da resposta (`status_code`, `headers`, `Content-Type`, `resposta.url`) antes de qualquer transformação | Alta |
| Migrar a configuração para `config/params.yaml` | Média |
| Criar `docs/sprints/` e mover `SPRINT1_TRILHA.md` para essa pasta | Média |
| Popular a pasta `notebooks/` | Média |
| Registrar a contribuição individual de Eudenis, Gabriel e João Pedro (commits próprios ou diário de sprint) | Média |
| Nomear o usuário da decisão e desenvolver em texto corrido a discussão do custo de falso negativo no RFC | Baixa |

Observação: limpeza, análise exploratória e engenharia de atributos não fazem parte do escopo da Sprint 1; essas atividades estão previstas para a Sprint 2, a partir do dado já tratado.

---

## Documentação

- RFC: `docs/RFC.md` (`RFC_Proposta_de_Projeto_Template.md`)
- Dicionário de dados: `docs/Dicionario_de_Dados.md`
- Relatório da Sprint 1: `SPRINT1_TRILHA.md` (a mover para `docs/sprints/`)
- Model card: previsto no diário da Sprint 5
