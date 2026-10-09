# Dicionário de Dados

**Projeto:** Previsão da Qualidade do Ar Inadequada na Região da Faculdade UBC
**Trilha:** B — Qualidade do ar inadequada
**Equipe:** Davi Gama dos Santos - 33121079, Diogo Gomes Barbosa - 35866276, Eudenis de Souza Vieira - 32751621, Gabriel Januário Alves - 35609991, João Pedro Barreto da Silva - 33297185
**Última atualização:** 09/10/2026 — atualizar a cada sprint em que variáveis nasçam ou saiam
**Versão:** v1.0 — conjunto final de features da Random Forest S5 documentado

> Contrato das colunas entre sprints. Sprint 1: fontes e variáveis **brutas**. Sprint 2: log de limpeza, alvo formal, derivados iniciais e exclusões por vazamento. Sprint 4: features iteradas. Sprint 5: conferência com o model card — as colunas do modelo escolhido são estas.

**Unidade de análise (o que é uma linha):** Uma observação horária contendo dados de qualidade do ar e condições meteorológicas para o ponto de estudo na região da Faculdade UBC, em Mogi das Cruzes/SP.

**N após o merge (Sprint 1, período de teste):** 744 registros (01/01/2025 a 31/01/2025)

**N após o merge do período ampliado:** 35.736 registros (04/08/2022 a 31/08/2026), salvos em `data/interim/dados_merged_2022-08-04_2026-08-31.csv`.

**Validação e persistência das APIs (08/10/2026):** 35.736 horários por fonte, de 04/08/2022 a 31/08/2026; sem ausências nas variáveis solicitadas e com timestamps alinhados. Os JSONs de janeiro/2025 foram preservados; os arquivos ampliados incluem o intervalo no nome.

**N após a rotulagem:** 35.736 linhas; 35.713 rótulos definidos (904 positivos, 34.809 negativos) e 23 indefinidos pelo aquecimento das janelas e pelo horizonte na última linha. Arquivo: `data/interim/dados_com_alvo_2022-08-04_2026-08-31.csv`.

**Split temporal (Sprint 2):** intervalos definidos pelo horário do evento previsto (`time + 1h`). Validação expansiva em 2024-Q1 (2.184 linhas, 114 positivas), Q2 (2.184, 55), Q3 (2.208, 172) e Q4 (2.208, 46). Treino final até antes de 2025: 21.121 linhas (743 positivas, 20.378 negativas). Teste final, 2025–2026: 14.592 linhas (161 positivas, 14.431 negativas). Rótulos indefinidos são excluídos.

---

## 1. Fontes de dados

| Fonte | API / Endpoint | Cobertura temporal disponível | Resolução temporal | Medido ou modelado? | Limitações conhecidas |
| --- | --- | --- | --- | --- | --- |
| Open-Meteo Air Quality API | https://air-quality-api.open-meteo.com/v1/air-quality | Na validação de 08/10/2026, dados completos de 04/08/2022 a 31/08/2026; datas de referência anteriores a agosto/2022 retornaram poluentes nulos. | Horária (com valores horários interpolados pelo modelo) | Modelado — os dados de qualidade do ar são provenientes de modelos atmosféricos, não de uma estação de medição localizada exatamente no ponto do projeto. | Resolução espacial de aproximadamente 45 km para o CAMS Global fora da Europa; portanto, os valores representam uma grade/modelo atmosférico e não uma medição pontual da Universidade Braz Cubas. |
| Open-Meteo Historical Weather API | https://archive-api.open-meteo.com/v1/archive | Consulta validada de 04/08/2022 a 31/08/2026; o ERA5 tem cobertura histórica anterior, mas não amplia o período conjunto sem dados de qualidade do ar. | Horária | Modelado/reanálise — os dados históricos são obtidos a partir de modelos e conjuntos de reanálise meteorológica. | A resolução espacial depende do conjunto utilizado; para ERA5, a documentação informa aproximadamente 25 km. |

> **Trilha B:** poluentes Open-Meteo em geral são produto **modelado**, não medição de estação local — declarar na coluna acima.

> **Trilha C:** registrar códigos do IBGE (agregado, variável, classificação) e o que cada um representa. Anotar municípios e safras: N = municípios × safras.

---

## 2. Variáveis brutas (coletadas na Sprint 1)

| Nome da coluna | Fonte | Tipo | Unidade | Descrição | Observações |
| --- | --- | --- | --- | --- | --- |
| `time` | Open-Meteo Air Quality / Weather | data-hora | ISO 8601 | Data e horário correspondentes à observação e instante de origem das features. | Usada para integrar as fontes e determinar o horário do evento previsto (`time + 1h`) nas partições temporais. |
| `pm10` | Open-Meteo Air Quality | numérica contínua | μg/m³ | Concentração de material particulado com diâmetro aerodinâmico de até 10 micrômetros. | Variável bruta de qualidade do ar. |
| `pm2_5` | Open-Meteo Air Quality | numérica contínua | μg/m³ | Concentração de material particulado fino com diâmetro aerodinâmico de até 2,5 micrômetros. | Variável bruta de qualidade do ar. |
| `carbon_monoxide` | Open-Meteo Air Quality | numérica contínua | μg/m³ | Concentração de monóxido de carbono. | Variável bruta de qualidade do ar. |
| `nitrogen_dioxide` | Open-Meteo Air Quality | numérica contínua | μg/m³ | Concentração de dióxido de nitrogênio. | Variável bruta de qualidade do ar. |
| `sulphur_dioxide` | Open-Meteo Air Quality | numérica contínua | μg/m³ | Concentração de dióxido de enxofre. | Variável bruta de qualidade do ar. |
| `ozone` | Open-Meteo Air Quality | numérica contínua | μg/m³ | Concentração de ozônio. | Variável bruta de qualidade do ar. |
| `temperature_2m` | Open-Meteo Historical Weather | numérica contínua | °C | Temperatura do ar a 2 metros de altura. | Variável meteorológica bruta. |
| `relative_humidity_2m` | Open-Meteo Historical Weather | numérica contínua | % | Umidade relativa do ar a 2 metros de altura. | Variável meteorológica bruta. |
| `precipitation` | Open-Meteo Historical Weather | numérica contínua | mm | Quantidade de precipitação registrada no período horário. | Variável meteorológica bruta. |
| `wind_speed_10m` | Open-Meteo Historical Weather | numérica contínua | km/h | Velocidade do vento a 10 metros de altura. | Variável meteorológica bruta. |
| `pressure_msl` | Open-Meteo Historical Weather | numérica contínua | hPa | Pressão atmosférica reduzida ao nível médio do mar. | Variável meteorológica bruta. |

Observação: as variáveis acima são as entradas brutas das APIs. O alvo CETESB e seu deslocamento de uma hora já estão implementados; as features do modelo, defasagens e demais exclusões por vazamento serão definidas e documentadas nas etapas seguintes.

*Tipo: numérica contínua / numérica discreta / categórica / data-hora / identificador.*

---

## 2.1 Validação dos dados e valores ausentes (Sprint 2)

`data/raw/` permanece intocado. A tabela da EDA é `data/interim/`.

Não imputar com média/mediana/moda do dataset inteiro nesta etapa.

| Problema | Regra aplicada | Linhas/células afetadas | N depois | Observação |
| --- | --- | --- | --- | --- |
| Ausências nas variáveis brutas das APIs | Nenhuma imputação necessária | 0 | 35.736 | Período ampliado; ambas as fontes |
| Duplicatas na coluna `time` | Nenhuma correção necessária | 0 | 35.736 | Timestamps únicos e alinhados |
| Lacunas no intervalo horário | Nenhuma correção necessária | 0 | 35.736 | Série contínua no período ampliado |

**Valores ausentes gerados pelas janelas e pelo horizonte (não imputar):**

As janelas de 24h deixam 23 valores iniciais indefinidos nos subíndices correspondentes e no IQAr consolidado; as janelas de 8h deixam 7 valores iniciais indefinidos para CO e O3. Como o rótulo depende do IQAr em `t+1h`, 23 linhas ficam sem rótulo no total (aquecimento inicial e última hora sem futuro). Essas linhas não participam da modelagem supervisionada.

---

## 3. Alvo de classificação *(implementado no período ampliado)*

| Campo | Descrição |
| --- | --- |
| Nome da coluna | `qualidade_ar_inadequada_1h`. |
| Definição da classe positiva | Classe 1 se o IQAr consolidado em t+1h for > 100, incluindo categorias mais graves; classe 0 se for <= 100. |
| Cálculo do índice | Interpolação linear por poluente conforme a Tabela 2.7 do relatório CETESB 2025; IQAr = maior subíndice calculado entre os seis poluentes. A continuação do último trecho linear é usada acima do último ponto tabelado; isso não altera a classe binária para IQAr > 100. |
| Janelas usadas no alvo | PM10, PM2,5 e SO2: média móvel de 24h; O3 e CO: média móvel de 8h; NO2: valor horário. Todas terminam no horário avaliado, t+1h. |
| Conversão de CO | A API fornece µg/m³ e a tabela CETESB usa ppm. Converter a média móvel de CO pela lei dos gases ideais a 25 °C e 1 atm antes de interpolar. |
| Ausência no período-alvo | Se faltar qualquer concentração necessária em alguma das janelas dos seis poluentes terminando em t+1h, o IQAr/rótulo fica indefinido; não imputar o rótulo e excluir a linha da modelagem supervisionada. |
| Fonte da variável de origem | Open-Meteo Air Quality. |
| Horizonte de previsão (deslocamento aplicado) | 1h à frente: as features disponíveis até t preveem o IQAr calculado em t+1h. |
| Colunas geradas | `iqar_pm10`, `iqar_pm2_5`, `iqar_carbon_monoxide`, `iqar_nitrogen_dioxide`, `iqar_sulphur_dioxide`, `iqar_ozone`, `iqar` (no próprio horário da linha) e `qualidade_ar_inadequada_1h` (rótulo deslocado). |
| Distribuição no treino final | 743 positivos (3,52%) e 20.378 negativos entre 21.121 linhas, com horário do alvo anterior a 2025. |
| Distribuição no teste final | 161 positivos (1,10%) e 14.431 negativos entre 14.592 linhas, com horário do alvo em 2025–2026. Taxas e médias por classe desse período foram examinadas descritivamente antes de fixar o split; não usar o holdout para seleção posterior de modelo ou limiar. |
| Distribuição na validação | 2024-Q1: 114 positivos; Q2: 55; Q3: 172; Q4: 46. A variação entre folds deve ser considerada ao interpretar as métricas. |

**Pontos de concentração correspondentes aos índices CETESB:** a tabela abaixo registra os valores de concentração que correspondem aos pontos 0, 40, 80, 120 e 200 do índice, na ordem indicada. Para CO, os valores estão em ppm; os demais estão em µg/m³.

| Poluente | 0 | 40 | 80 | 120 | 200 | Janela |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| PM10 | 0 | 50 | 100 | 150 | 250 | 24h |
| PM2,5 | 0 | 25 | 50 | 75 | 125 | 24h |
| O3 | 0 | 100 | 130 | 160 | 200 | 8h |
| CO | 0 | 9 | 11 | 13 | 15 | 8h |
| NO2 | 0 | 200 | 240 | 320 | 1.130 | 1h |
| SO2 | 0 | 20 | 40 | 365 | 800 | 24h |

Fonte: CETESB (2025), *Relatório de Metodologia para Avaliação da Qualidade do Ar*, seção 2.3 e Tabela 2.7, pp. 18–20 ([PDF oficial](https://www.cetesb.sp.gov.br/dx/api/dam/v1/collections/186909e9-ab59-4641-abba-c5c465793216/items/3adb602d-77ec-4de5-b378-5fa141e80614/renditions/5a0e5f05-41aa-4e9c-9b00-69165ab36963/versions/1?binary=true)).

---

## 4. Atributos derivados (Sprints 2 e 4)

| Nome do atributo | Variável(is) de origem | Tipo de transformação | Janela/parâmetro (definido no treino) | Calculável no instante da previsão? | Justificativa | Sprint (2 ou 4) | Feature ou alvo? |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Pendente | Pendente | Pendente | Pendente | Pendente | As features derivadas serão definidas após a análise exploratória detalhada e a avaliação dos modelos de referência. | 2 | Feature |
| Pendente | Pendente | Pendente | Pendente | Pendente | Novos atributos poderão ser incluídos na Sprint 4 após avaliação das features desenvolvidas nas sprints anteriores. | 4 | Feature |
| `delta_1h_ozone`, `delta_1h_pm2_5` | `ozone`, `pm2_5` | Diferença horária | 1 hora anterior | Sim, com a medição em *t* e em *t-1h* | Candidatas a representar a direção da mudança recente; triagem não demonstrou ganho consistente de F1 e ainda não foram selecionadas para o pipeline final. | 4 | Feature candidata |
| `delta_1h_iqar_ozone`, `delta_1h_iqar_pm2_5` | `iqar_ozone`, `iqar_pm2_5` | Diferença horária | 1 hora anterior | Sim, com os subíndices disponíveis em *t* e em *t-1h* | Candidatas a representar a variação recente dos subíndices; triagem elevou os falsos positivos e não justificou seleção final. | 4 | Feature candidata |
| `delta_1h_temperature_2m`, `delta_1h_relative_humidity_2m`, `delta_1h_precipitation`, `delta_1h_wind_speed_10m`, `delta_1h_pressure_msl` | Variáveis meteorológicas correspondentes | Diferença horária | 1 hora anterior | Sim, com observações disponíveis em *t* e em *t-1h* | Candidatas a representar mudanças meteorológicas recentes; a triagem conjunta não melhorou o equilíbrio de métricas e não as selecionou para o pipeline final. | 4 | Feature candidata |
| `hora_dia_seno`, `hora_dia_cosseno` | Hora da coluna `time` | Codificação cíclica (seno/cosseno) | Período de 24 horas | Sim, o horário do registro está disponível em *t* | Candidatas a representar continuidade entre horários próximos, motivadas pela concentração temporal de falsos positivos; triagem reduziu a carga semanal máxima, mas aumentou FP e reduziu F1, portanto ainda não foram selecionadas. | 4 | Feature candidata |
| `media_3h_ozone`, `media_3h_pm2_5` | `ozone`, `pm2_5` | Média móvel retrospectiva | Três registros horários, incluindo *t* | Sim, desde que os dados de *t*, *t-1h* e *t-2h* estejam disponíveis | Integram a Random Forest final; no comparativo S3→S4, a variante combinada reduziu FN de 3 para 0, mas FP aumentaram em 69 e F1 diminuiu. Selecionadas para o modelo final da Sprint 5. | 5 | Feature do modelo final |
| `delta_2h_ozone`, `delta_2h_pm2_5` | `ozone`, `pm2_5` | Diferença entre valores | Valor em *t* menos valor em *t-2h* | Sim, com observações disponíveis em *t* e *t-2h* | Integram a Random Forest final; eliminam FN no comparativo de desenvolvimento, com aumento de FP e sem redução das semanas acima do teto. Selecionadas para o modelo final da Sprint 5. | 5 | Feature do modelo final |

As diferenças de 1h são calculadas como `valor(t) - valor(t-1h)`; as diferenças de 2h como `valor(t) - valor(t-2h)`. As médias de 3h usam as três observações em *t*, *t-1h* e *t-2h*. As transformações são retrospectivas, antes da separação dos folds; valores ausentes na borda inicial são tratados pelo imputador ajustado no treino. A codificação cíclica mapeia a hora do registro a coordenadas seno/cosseno com período de 24 horas. As triagens temporais são executadas por `python -m src.modelagem.Avaliar_Features_Temporais`; o comparativo formal S3→S4 está em `reports/modeling/sprint4_lift_by_fold.csv`, `sprint4_lift_summary.csv` e `sprint4_alert_burden_by_week.csv`. A avaliação Sprint 5 foi feita em 2024-Q4 para seleção e o teste final foi consultado uma única vez; resultados estão em `sprint5_validation_metrics.csv`, `sprint5_validation_threshold_tradeoff.csv` e `sprint5_final_test_metrics.csv`. As quatro features de contexto curto fazem parte da Random Forest final; o pipeline e limiar estão registrados em `models/modelo_final_sprint5.joblib`. O limiar 0,3 foi escolhido na validação, sem acesso ao holdout. O teste teve recall 0,9814, 3 FN, 44 FP e F1 0,8705; essa avaliação não foi reutilizada para novo ajuste ou seleção.

*Tipo de transformação: média móvel / valor defasado (lag) / agregação (soma, contagem) / variável de calendário / outro (especificar).*

> Cada linha precisa de justificativa — não copiar só o nome da coluna. Parâmetros de janela **não** se reajustam no teste. A Sprint 4 acrescenta linhas novas; não apaga as da Sprint 2 se ainda estiverem no modelo (pode marcar "descartada na seleção"). Timestamp, código IBGE e nome de município **não** entram como número; calendário (mês, safra) vale. "Calculável no instante da previsão" = sim só se os dados de origem já existiriam na hora da decisão (mesmo horizonte do RFC).

---

## 5. Variáveis excluídas das features (risco de vazamento)

| Nome da coluna | Motivo da exclusão |
| --- | --- |
| `qualidade_ar_inadequada_1h` | É o rótulo-alvo (y), não uma feature de entrada (X). |

> Incluir colunas usadas para construir o alvo e qualquer informação que só existiria depois do evento ou depois do instante de previsão. Elas **não** entram no `ColumnTransformer`.

---

## 6. Observações gerais e limitações do dataset

* Os dados de qualidade do ar utilizados pela API são provenientes de modelos atmosféricos/reanálises, não de uma estação de medição localizada exatamente no ponto do projeto.
* Os dados representam uma célula de grade/modelo atmosférico, portanto podem apresentar diferenças em relação às condições observadas especificamente na Faculdade UBC.
* As coordenadas solicitadas ao serviço e as coordenadas retornadas pelas APIs podem apresentar pequenas diferenças devido ao funcionamento da grade espacial dos modelos.
* A coleta original de janeiro/2025 foi preservada. A coleta ampliada de 04/08/2022 a 31/08/2026 foi persistida em JSONs com o período no nome: 35.736 horários por fonte, sem ausências e com timestamps alinhados.
* As variáveis brutas não apresentaram ausências, duplicatas temporais ou lacunas horárias no período ampliado; valores indefinidos nas colunas derivadas decorrem do cálculo das janelas e do horizonte, e não foram imputados.
* Os merges de janeiro/2025 (744 registros) e do período ampliado (35.736 registros) foram mantidos em arquivos separados.
* O critério, o cálculo do IQAr e o deslocamento de 1h estão implementados em `src/transformacao/Calcular_Alvo_IQAr.py`; o script grava o alvo em arquivo separado sem sobrescrever o merge.
* No período ampliado, 35.713 rótulos foram definidos: 904 positivos e 34.809 negativos (2,53% positivos). Vinte e três linhas ficaram sem rótulo por aquecimento das janelas e pelo horizonte na última linha.
* A base de janeiro/2025 teve 721 rótulos definidos: 15 positivos e 706 negativos (~2,1% positivos).
* O alvo é uma estimativa baseada em dados horários modelados/interpolados pela Open-Meteo; não representa o IQAr oficial de uma estação CETESB.
* A Sprint 2 foi parcialmente executada: coletas, merges, alvo CETESB, split temporal e EDA descritiva/gráfica do desenvolvimento foram concluídos; a Sprint 3 avançou com a comparação inicial de features e baselines.
* A EDA do desenvolvimento é reproduzida por `python -m src.analise.EDA_Desenvolvimento`; gráficos ficam em `reports/figures/eda_desenvolvimento/`. Ela usa somente rótulos com evento previsto até 31/12/2024.
* A cerca exploratória `Q3 + 1,5 × IQR` sinalizou aproximadamente 5,3% das horas em cada uma das variáveis CO, PM10 e PM2,5; as excedências formam episódios e se sobrepõem. Os dados são modelados/interpolados e não há medição local independente; nenhum extremo foi removido ou limitado.
* Os baselines Dummy prior, persistência pelo IQAr em `t` e Gaussian Naive Bayes foram avaliados nos quatro folds de validação de 2024; detalhes e matrizes de confusão ficam em `reports/modeling/`. O Gaussian Naive Bayes usa imputação por mediana e padronização ajustadas no treino de cada fold. O holdout 2025–2026 não foi usado.
* Resultados de desenvolvimento são preliminares: o maior recall médio do Naive Bayes com subíndices/IQAr (0,9985) veio acompanhado de 476 falsos positivos agregados; a persistência teve F1 médio 0,8196. Não houve ajuste de limiar nem avaliação final do holdout.
* `reports/modeling/baseline_predictions_by_fold.csv` contém previsões out-of-fold; `baseline_misclassified_cases.csv` acrescenta as features em `t` dos falsos positivos/falsos negativos para análise dos erros. Ambos abrangem apenas folds de 2024.
* `reports/modeling/baseline_error_rates_by_month.csv` e `baseline_error_rates_by_hour.csv` trazem taxas de falso positivo e falso negativo por período, com denominadores de classe. A análise de 2024-Q3 identificou uma elevação das taxas em setembro e erros em sequências de horas.
* `reports/modeling/baseline_iqar_ablation_by_fold.csv` e `baseline_iqar_ablation_summary.csv` comparam os grupos com subíndices/IQAr e suas variantes sem o IQAr consolidado nos mesmos quatro folds de 2024. No grupo só de subíndices, a ablação reduziu os falsos positivos de 476 para 402; no grupo combinado, aumentou de 537 para 542. Nenhuma variante final foi selecionada.
* `reports/modeling/baseline_threshold_tradeoff_by_inner_fold.csv` e `baseline_threshold_tradeoff_summary.csv` apresentam 101 limiares avaliados em validações temporais internas anteriores aos folds externos, incluindo falsos positivos/negativos, horas e episódios de alerta por mil horas, carga semanal e proporção de falsos alertas entre previsões positivas. `baseline_threshold_alert_episodes_by_week.csv` detalha horas alertadas e episódios iniciados por semana. Episódios são sequências de previsões positivas; uma hora negativa ou lacuna encerra a sequência, e a contagem é atribuída à semana em que o episódio começa. A equipe definiu teto de três episódios iniciados por semana, mas os cenários 0,25 e 0,50 excederam esse limite em 21 das 52 semanas completas (máximos de seis e sete episódios); nenhum limiar entre 0,01 e 0,99 o respeitou em todas as semanas no grupo de subíndices sem `iqar`. A métrica conta episódios previstos, não detecção de episódios reais. **Na análise da Sprint 3**, nenhum limiar foi escolhido e o holdout permaneceu reservado; a Sprint 5 conduziu a seleção final em validação temporal e a avaliação única registrada acima.

---

## 7. Histórico de alterações

| Versão | Sprint | Data | O que mudou |
| --- | --- | --- | --- |
| v0.1 | 1 | 17/09/2026 | Fontes, variáveis brutas, informações iniciais sobre o conjunto de dados e limitações da coleta. |
| v0.1 | 2 | 04/10/2026 | Log de limpeza atualizado (merge realizado); N em `interim` documentado. |
| v0.2 | | 08/10/2026 | Período das APIs validado e registrado; critério do alvo e política de dados ausentes definidos. |
| v0.2 | 2 | | Log de limpeza; N em `interim`; split; alvo; derivados iniciais; exclusões |
| v0.3 | 2 | 08/10/2026 | Metodologia CETESB 2025 conferida; janelas, conversão de CO, subíndices e rótulo a t+1h implementados. |
| v0.4 | 2 | 08/10/2026 | Período ampliado coletado, integrado e rotulado em arquivos separados; distribuição inicial documentada. |
| v0.5 | 2 | 08/10/2026 | EDA inicial, folds expansivos em 2024 e teste final em 2025–2026 documentados; separação temporal implementada. |
| v0.6 | 2 | 09/10/2026 | EDA gráfica e triagem de extremos reproduzíveis no desenvolvimento; sem remoção ou clipping. |
| v0.7 | 3 | 09/10/2026 | Três grupos de features e baselines comparados nos folds de 2024; holdout mantido reservado. |
| v0.8 | 4 | 09/10/2026 | Features temporais candidatas e comparativo formal S3→S4 documentados. |
| v0.9 | 4 | 09/10/2026 | Quatro features de contexto curto congeladas para o comparativo da Sprint 5. |
| v1.0 | 5 | 09/10/2026 | Features do modelo final e resultados da avaliação final única documentados. |
| v0.4 | 5 | | Conferência com o modelo final / model card |
| | | | |
