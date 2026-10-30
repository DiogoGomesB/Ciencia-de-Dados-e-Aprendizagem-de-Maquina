# Diário de Bordo — Trilha B (Qualidade do Ar — Universidade Braz Cubas)

Este documento consolida o histórico evolutivo do projeto, as decisões de escopo e as retrospectivas individuais de cada Sprint ao longo do semestre (`2026/2`). Os relatórios detalhados de cada etapa também estão preservados em [`docs/sprints/`](docs/sprints/).

---

## Equipe

| Nome | RA | Papel no Projeto |
|---|---|---|
| Davi Gama dos Santos | 33121079 | Equipe de Desenvolvimento |
| Diogo Gomes Barbosa | 35866276 ([@DiogoGomesB](https://github.com/DiogoGomesB)) | Scrum Master & Equipe de Desenvolvimento |
| Eudenis de Souza Vieira | 32751621 | Equipe de Desenvolvimento |
| Gabriel Januário Alves | 35609991 | Equipe de Desenvolvimento |
| João Pedro Barreto da Silva | 33297185 | Equipe de Desenvolvimento |

---

## Registro de Evolução de Escopo e Decisões Técnicas

1. **Sprint 1 — Coleta inicial e delimitação espacial:**
   - Ponto de referência definido na Universidade Braz Cubas (`-23.514561`, `-46.186832`, fuso `America/Sao_Paulo`).
   - Coleta piloto realizada para janeiro/2025 (`744` registros horários) nas APIs *Open-Meteo Air Quality* e *Historical Weather*, preservando os JSONs originais em `data/raw/`.
2. **Sprint 2 — Ampliação histórica, Alvo CETESB e Split Temporal:**
   - Mudança de recorte temporal documentada: ampliação de janeiro/2025 para o histórico completo disponível sem lacunas de `04/08/2022` a `31/08/2026` (`35.736` horas).
   - Formalização matemática da classe positiva segundo a Tabela 2.7 da CETESB (`IQAr > 100` em $t+1\text{h}$), resultando em `35.713` rótulos válidos (`904` positivos = `2,53%`).
   - Divisão temporal estrita pelo horário do evento (`event_time`): desenvolvimento até `31/12/2024` (`21.121` horas; `743` positivos = `3,52%`) e holdout/teste recente de `01/01/2025` a `31/08/2026` (`14.592` horas; `161` positivos = `1,10%`).
3. **Sprint 3 — Baselines, Ablação do IQAr e Regra Operacional:**
   - Avaliação dos baselines (`DummyClassifier`, `Persistência` e `GaussianNB`) nos 4 folds trimestrais de 2024.
   - Estudo de ablação: retirada da variável agregada `iqar` do conjunto de entrada para evitar colinearidade com os 6 subíndices individuais, reduzindo Falsos Positivos de `476` para `402` no grupo de subíndices (elevando F1 de `0,6175` para `0,6669`, com `3 FN` nos 4 folds de 2024).
   - Definição do critério operacional semanal: teto exploratório de até `3` episódios de alerta iniciados por semana completa.
4. **Sprint 4 — Engenharia de Atributos Temporais e Pipeline Congelado:**
   - Criação de 4 features retrospectivas de curto prazo (`media_3h_ozone`, `media_3h_pm2_5`, `delta_2h_ozone`, `delta_2h_pm2_5`) calculadas estritamente até $t$.
   - Congelamento das 15 colunas em `FEATURES_SPRINT4` dentro de um `ColumnTransformer` (`SimpleImputer(strategy="median")` + `StandardScaler()`), zerando os Falsos Negativos nos folds de desenvolvimento (`FN` caiu de `3` para `0`).
5. **Sprint 5 — Experimento Comparativo de Árvores, Limiar 0,30, Dashboard e Artigo Técnico:**
   - Comparação sistemática entre Baseline (`DummyClassifier`, `Persistência`, `GaussianNB`), `Regressão Logística`, **Árvore de Decisão (`DecisionTreeClassifier`)**, **Random Forest (`RandomForestClassifier`)** e **XGBoost (`XGBClassifier`)**, avaliando métricas de risco (Recall, Precisão, F1, Matriz de Confusão) e latência de treino/inferência.
   - Congelamento do modelo final (**Random Forest Balanceada**, 300 árvores, `min_samples_leaf=2`, limiar `0,30`) antes da abertura do holdout (`Recall = 98,14%`, `F1 = 87,05%`, apenas `3 FN` em `14.592` horas).
   - Entrega do Dashboard no Streamlit (`streamlit_app.py`), módulo de previsão ao vivo (`+1h` oficial e projeções experimentais `+7h` e `+24h`) e Artigo Técnico em página web (`docs/index.html`).

---

## Retrospectivas por Sprint

### Sprint 1 — Definição do Problema e Coleta Bruta ([Relatório Completo](docs/sprints/Sprint1_TrilhaB.md))

| Integrante | O que fiz nesta Sprint | Dificuldades | O que pretendo manter/ajustar |
|---|---|---|---|
| Davi Gama dos Santos | Configurei os endpoints das APIs Open-Meteo (Air Quality e Historical Weather) e validei os parâmetros de latitude, longitude e timezone. | Compreender as limitações de grade espacial do CAMS Global e garantir que as respostas trouxessem as 744 horas de janeiro/2025. | Manter os scripts parametrizados via YAML e documentar eventuais particularidades da API. |
| Diogo Gomes Barbosa | Atuei como Scrum Master, estruturei o repositório, elaborei o RFC v0.1 inicial e implementei o script central de coleta `Coleta_Dados.py` com proteção contra sobrescrita. | Alinhar o cronograma da Trilha B e definir o horizonte estrito de 1h para orientar as próximas sprints. | Manter versionamento rigoroso e comunicação ágil com o time. |
| Eudenis de Souza Vieira | Realizei a conferência dos dados brutos em JSON, verificando formato, consistência de campos e montagem do Dicionário de Dados v0.1. | Verificar as variáveis meteorológicas necessárias para contextualizar a dispersão dos poluentes. | Aprofundar a inspeção dos dados para preparar a etapa de merge na Sprint 2. |
| Gabriel Januário Alves | Pesquisei a fundamentação teórica sobre padrões de qualidade do ar (CETESB e literatura científica) e colaborei na redação das limitações do RFC. | Mapear as resoluções temporais nativas da Open-Meteo fora da Europa. | Manter embasamento bibliográfico sólido para justificar as escolhas do projeto. |
| João Pedro Barreto da Silva | Configurei o ambiente Python, `requirements.txt` e estrutura de diretórios do projeto (`data/raw`, `src/coleta`, `config/params.yaml`). | Garantir a compatibilidade de versões e dependências do Scikit-Learn e Pandas no Windows. | Manter testes e validações automatizadas de ambiente para toda a equipe. |

---

### Sprint 2 — Limpeza, Alvo CETESB, Split Temporal e EDA ([Relatório Completo](docs/sprints/Sprint2_TrilhaB.md))

| Integrante | O que fiz nesta Sprint | Dificuldades | O que pretendo manter/ajustar |
|---|---|---|---|
| Davi Gama dos Santos | Implementei o script `Merge_Dados.py` realizando a integração das duas fontes por `time` e validando a integridade das 35.736 linhas. | Assegurar o alinhamento perfeito de fuso horário (`America/Sao_Paulo`) entre as séries. | Manter a rotina de verificação automática de timestamps. |
| Diogo Gomes Barbosa | Coordenei a sprint como Scrum Master e implementei o cálculo do alvo CETESB (subíndices, IQAr e rótulo em $t+1\text{h}$). | Aplicar corretamente as janelas de 8h e 24h e a conversão de CO de $\mu\text{g/m}^3$ para ppm. | Manter testes automatizados para cada regra do alvo e revisar o board com mais frequência. |
| Eudenis de Souza Vieira | Apoiei na codificação das janelas móveis de 24h e 8h e conversão de CO para o cálculo do alvo CETESB em `Calcular_Alvo_IQAr.py`. | Tratar as linhas iniciais de aquecimento da série temporal sem imputar rótulos inexistentes. | Manter a regra estrita de não imputação de rótulos no alvo. |
| Gabriel Januário Alves | Desenvolvi o script `EDA_Desenvolvimento.py`, gerando os gráficos de prevalência mensal, correlação de Spearman e boxplots das concentrações. | Garantir que a EDA utilizasse apenas o conjunto de desenvolvimento (2022–2024), sem tocar no holdout. | Salvar figuras padronizadas em alta resolução no diretório `reports/figures`. |
| João Pedro Barreto da Silva | Implementei e testei a lógica do split temporal expansivo em `Separacao_Temporal.py`, garantindo que os folds usassem o tempo do evento ($t+1\text{h}$). | Evitar contaminação temporal na fronteira de cada trimestre. | Reutilizar a mesma função de split nas sprints de modelagem. |

---

### Sprint 3 — Baselines, Ablação e Carga de Alertas ([Relatório Completo](docs/sprints/Sprint3_TrilhaB.md))

| Integrante | O que fiz nesta Sprint | Dificuldades | O que pretendo manter/ajustar |
|---|---|---|---|
| Davi Gama dos Santos | Validei a reprodutibilidade da ingestão e reexecução da pipeline CD, garantindo a integridade dos arquivos em `data/raw/` e `data/interim/`. | Garantir que execuções repetidas não sobrescrevessem arquivos legados. | Manter testes de carga e proteção de arquivos. |
| Diogo Gomes Barbosa | Organizei a sprint e montei o pipeline com imputação pela mediana e padronização ajustadas só no treino. | Evitar vazamento ao ajustar o pré-processamento dentro de cada fold. | Manter tudo dentro de um único `Pipeline` e documentar cada decisão. |
| Eudenis de Souza Vieira | Conduzi o estudo de ablação do IQAr consolidado no pipeline do Naive Bayes e extração dos falsos positivos out-of-fold. | Interpretar o impacto da correlação entre subíndices e a hipótese de independência condicional do Naive Bayes. | Avaliar modelos não lineares que lidem melhor com correlação na Sprint 5. |
| Gabriel Januário Alves | Realizei a análise de distribuição de erros por mês e hora do dia, identificando o pico de falsos positivos em setembro/Q3. | Isolar o efeito da sazonalidade nas taxas de falsos alertas. | Apoiar na formulação das hipóteses de contexto temporal para a Sprint 4. |
| João Pedro Barreto da Silva | Implementei o cálculo das métricas por fold e a rotina de varredura exploratória dos 101 limiares de decisão nas validações internas. | Agregar a carga semanal de alertas sem quebrar sequências nas viradas de semana. | Automatizar os relatórios em CSV em `reports/modeling/`. |

---

### Sprint 4 — Engenharia de Atributos Temporais e Lift ([Relatório Completo](docs/sprints/Sprint4_TrilhaB.md))

| Integrante | O que fiz nesta Sprint | Dificuldades | O que pretendo manter/ajustar |
|---|---|---|---|
| Davi Gama dos Santos | Apoiei na implementação das funções de defasagem e médias móveis em `Features_Temporais.py` e verifiquei o tratamento de bordas na série. | Evitar valores nulos indesejados nas primeiras horas sem criar vazamento temporal. | Manter a documentação dos parâmetros de janela no Dicionário de Dados. |
| Diogo Gomes Barbosa | Congelei o pipeline de preparação (`ColumnTransformer`) e coordenei o checkpoint da Sprint Review. | Manter o mesmo transformer para todos os modelos comparados. | Manter o congelamento antes de cada comparação e registrar a versão usada. |
| Eudenis de Souza Vieira | Participei da avaliação comparativa das variantes de deltas meteorológicos e de hora cíclica nos quatro folds de 2024. | Compreender por que a codificação cíclica da hora não reduziu consistentemente os falsos positivos. | Registrar a decisão fundamentada de descarte das variáveis não selecionadas. |
| Gabriel Januário Alves | Atualizei as tabelas de métricas de lift S3→S4 e estruturei a apresentação visual dos resultados para o checkpoint com o PO. | Sintetizar a interpretação do trade-off entre ganho de recall e custo em falsos positivos. | Manter os relatórios CSV gerados automaticamente e versionados em `reports/modeling/`. |
| João Pedro Barreto da Silva | Implementei o script `Avaliar_Features_Temporais.py` para rodar a triagem das variantes e consolidar o cálculo de episódios semanais. | Calcular o número de episódios sem quebrar sequências contínuas de alerta entre dias. | Manter o script reproduzível via linha de comando para a equipe. |

---

### Sprint 5 — Comparativo de Árvores, Holdout, Dashboard e Artigo ([Relatório Completo](docs/sprints/Sprint5_TrilhaB.md))

| Integrante | O que fiz nesta Sprint | Dificuldades | O que pretendo manter/ajustar |
|---|---|---|---|
| Davi Gama dos Santos | Apoiei na execução comparativa dos modelos (Árvore de Decisão, Random Forest e XGBoost) e na inspeção dos 3 falsos negativos do holdout. | Entender por que os 3 FN ocorreram em horas de subida abrupta de ozônio vespertino. | Manter a análise detalhada de erros por episódio nas entregas finais. |
| Diogo Gomes Barbosa | Como Scrum Master, conduzi o congelamento do modelo (Random Forest, limiar 0,30) antes de consultar o holdout, criei o fluxo de previsão (`+1h`, `+7h`, `+24h`) e o dashboard Streamlit. | Garantir que o holdout fosse avaliado uma única vez e tratar as horas futuras que as APIs devolvem. | Manter a regra de não reutilizar o teste e cobrir o fluxo com testes automatizados. |
| Eudenis de Souza Vieira | Participei da avaliação dos limiares na validação 2024-Q4, conferi o teto operacional semanal e apoiei na redação técnica sobre Bagging vs. Boosting. | Conciliar a escolha do limiar 0,30 com a carga de falsos positivos no período de verão. | Manter a escolha de limiar estritamente na validação, antes do teste final. |
| Gabriel Januário Alves | Colaborei no preenchimento do Model Card, na construção do Artigo Técnico em página web (`docs/index.html`) e nas figuras didáticas dos modelos. | Garantir consistência entre todos os números dos CSVs, Model Card, Dashboard e Artigo Web. | Manter a rastreabilidade direta entre relatórios CSV e documentação pública. |
| João Pedro Barreto da Silva | Auxiliei no empacotamento do pipeline final (`modelo_final_sprint5.joblib`), medição de latência de treino/predição e testes automatizados (`pytest`). | Garantir que os metadados do artefato preservassem exatamente o limiar e as colunas congeladas. | Manter a suíte `pytest` cobrindo tanto o pipeline histórico quanto a projeção ao vivo. |

