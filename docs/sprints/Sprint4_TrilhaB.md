# Diário de Sprint 4 — Iteração de atributos, retreino do baseline e pipeline congelado
**Período:** 05/10/2026 a 11/10/2026
**Trilha:** B — Qualidade do ar inadequada

**Equipe:**
**Scrum Master do Sprint:**
**Repositório GitHub:** (link)

> Sprint 1: coleta bruta. Sprint 2: limpeza, split, alvo e features iniciais. Sprint 3: baselines. Esta sprint **evolui** as features a partir dos erros do baseline, **retreina Dummy + persistência + Naive Bayes no mesmo split** e congela o `ColumnTransformer` para a Sprint 5. Sem lift documentado, não há evolução — só colunas novas.

### Contrato desta sprint

| | Artefato | Origem / destino |
|---|---|---|
| **Entra** | Split da Sprint 2, features da Sprint 2, erros e métricas da Sprint 3 | Sprints 2 e 3 |
| **Entra** | `ColumnTransformer` inicial da Sprint 3 | Sprint 3 |
| **Sai** | Features **novas** (além das da Sprint 2), com justificativa pelos erros da Sprint 3 | Sprint 5 |
| **Sai** | `ColumnTransformer` **congelado** (`fit` só no treino) | Sprint 5 **é obrigada a usar este** |
| **Sai** | Dummy + persistência + NB **retreinados** + tabela de lift S3→S4 | Sprint 5 (piso do comparativo; **não colar métricas da Sprint 3**) |
| **Sai** | Dicionário v0.9 | Sprint 5 |

**Não sai daqui:** seleção do modelo final entre classificadores novos, limiar de decisão, model card.

- [x] Confirmei o mesmo protocolo de folds temporais definido na Sprint 2/3 e que as features “novas” não são as da Sprint 2 renomeadas
- [x] O comparativo S3→S4 foi executado nos mesmos quatro folds temporais de 2024; o holdout 2025–2026 não foi usado.

---

## Pergunta orientadora da Sprint 4

**Que contexto disponível até o instante `t` pode melhorar os baselines da Sprint 3, especialmente na identificação de transições para IQAr > 100, sem aumentar injustificadamente os falsos alertas e sem vazamento temporal?**

Use os resultados da Sprint 3 para formular hipóteses antes de criar colunas:

- Os erros variam entre folds; Q3/2024 concentrou falsos positivos, com elevação em setembro. Verifique se uma hipótese de contexto temporal ou de regime explica esse padrão sem tratar a correlação como causalidade.
- A equipe prioriza evitar falsos negativos. Considere se atributos candidatos representam mudança ou persistência das condições em *t* e em horas anteriores; qualquer valor agregado deve usar apenas observações disponíveis até *t*.
- O teto exploratório é de três episódios previstos iniciados por semana. Nos cenários 0,25 e 0,50 do grupo de subíndices sem `iqar`, houve 21 semanas completas acima do teto, com picos de 7 e 6 episódios e cargas máximas de 85 e 90 horas, respectivamente. Não há teto de horas definido e nenhum limiar foi selecionado. Reporte ambas as dimensões, sem otimizar limiar nesta sprint.

**Roteiro de decisão:**
1. Para cada padrão de erro escolhido, registrar a evidência da Sprint 3, a hipótese e o atributo candidato que poderia representá-la.
2. Conferir disponibilidade temporal, cálculo em *t* ou com defasagens passadas, tratamento de bordas e ausência de uso de rótulos futuros.
3. Implementar somente atributos com justificativa verificável; se a hipótese não puder ser testada ou não houver ganho, registrar isso em vez de manter colunas apenas para aumentar o conjunto de features.
4. Comparar S3 e S4 nos mesmos folds e no mesmo protocolo. Além das métricas de classe positiva, analisar carga semanal de episódios e horas, mantendo separado o desenvolvimento de features da futura seleção de limiar.
5. Congelar o conjunto e o pipeline para a Sprint 5 apenas após documentar o lift, as limitações e as decisões da equipe.

**Hipóteses em triagem — ainda não congeladas como features finais:**

| Evidência da Sprint 3 | Hipótese | Atributo candidato | Decisão / justificativa |
|---|---|---|---|
| No grupo de subíndices, falsos positivos se concentraram em períodos com IQAr/ozônio elevados; Q3 e setembro tiveram taxas de FP mais altas. | A variação horária de ozônio e PM2,5 pode ajudar a distinguir nível atual de tendência recente. | Diferença entre o valor em *t* e *t-1h* de `ozone` e `pm2_5`; em separado, de `iqar_ozone` e `iqar_pm2_5`. | Triagem executada nos quatro folds de 2024, limiar padrão 0,5. Os deltas brutos deram variação pequena, sem ganho consistente de F1; ainda não selecionados. |
| A taxa de falsos positivos variou por período e condições meteorológicas podem caracterizar regimes distintos. | Mudanças meteorológicas horárias podem complementar as concentrações. | Diferenças em temperatura, umidade, precipitação, velocidade do vento e pressão. | A triagem conjunta não melhorou o equilíbrio geral; não selecionadas. |

**Triagem reproduzível de features temporais:** `python -m src.modelagem.Avaliar_Features_Temporais`. Os deltas são `valor(t) - valor(t-1h)` e a hora do dia é codificada por seno/cosseno com período de 24 horas, sempre usando informação disponível em *t*. O script usa a validação temporal de 2024 e o `predict` padrão do Gaussian Naive Bayes (sem ajuste de limiar), compara o grupo-base de subíndices sem `iqar` com cinco variantes e grava métricas por fold, resumo e carga semanal em `reports/modeling/temporal_feature_*.csv`. As semanas que cruzam fronteiras entre folds são agrupadas antes da contagem; o holdout 2025–2026 não é acessado.

**Resultado da triagem (8.784 horas, 52 semanas completas):**

| Variante | Recall médio | F1 médio | FP | FN | Semanas acima de 3 episódios | Máximo de episódios/semana | Máximo de horas de alerta/semana |
|---|---:|---:|---:|---:|---:|---:|---:|
| Grupo-base, sem deltas | 0,9949 | 0,6669 | 402 | 3 | 19 | 7 | 85 |
| Deltas brutos de ozônio e PM2,5 | 0,9971 | 0,6654 | 411 | 2 | 18 | 6 | 86 |
| Deltas de `iqar_ozone` e `iqar_pm2_5` | 0,9985 | 0,6115 | 504 | 1 | 17 | 7 | 86 |
| Deltas meteorológicos | 0,9882 | 0,6300 | 450 | 5 | 27 | 9 | 81 |
| Deltas dos subíndices e meteorologia | 0,9985 | 0,5787 | 554 | 1 | 29 | 8 | 82 |
| Hora do dia cíclica | 0,9971 | 0,6338 | 435 | 2 | 20 | 7 | 69 |

O delta bruto de ozônio/PM2,5 reduziu os FN de 3 para 2 e as semanas acima do teto de 19 para 18, mas aumentou FP de 402 para 411, reduziu ligeiramente F1 e elevou a carga semanal máxima de 85 para 86 horas. Os demais grupos aumentaram FP e/ou reduziram F1. **Conclusão provisória:** os testes não demonstram ganho consistente suficiente para congelar qualquer delta no pipeline; documentam a hipótese investigada e deixam explícita a necessidade de decisão da equipe antes de consolidar features. Resultados obtidos nos mesmos folds são exploratórios e não uma avaliação final independente.

A hora cíclica também não foi selecionada: reduziu a carga máxima por semana de 85 para 69 horas, mas elevou FP de 402 para 435, reduziu F1 de 0,6669 para 0,6338 e deixou 20 semanas acima do teto (eram 19 no grupo-base). A menor carga máxima, isoladamente, não compensa esses resultados nem demonstra melhoria geral.

**Segunda triagem — contexto curto de ozônio e PM2,5:** para representar tendências em escala maior que uma hora, foram avaliadas a média dos três valores horários até *t* e a diferença entre os valores em *t* e *t−2h*. As quatro variantes usaram os mesmos folds e o limiar padrão:

| Variante | Recall médio | F1 médio | FP | FN | Semanas acima de 3 episódios | Máximo de episódios/semana | Máximo de horas de alerta/semana |
|---|---:|---:|---:|---:|---:|---:|---:|
| Grupo-base, sem deltas | 0,9949 | 0,6669 | 402 | 3 | 19 | 7 | 85 |
| Delta de 2h em ozônio e PM2,5 | 0,9949 | 0,6666 | 410 | 3 | 18 | 7 | 85 |
| Média de 3h em ozônio e PM2,5 | 0,9985 | 0,6307 | 462 | 1 | 18 | 6 | 77 |
| Média de 3h e delta de 2h | 1,0000 | 0,6261 | 471 | 0 | 19 | 6 | 76 |

A média de 3h com delta de 2h evitou os três FN observados no grupo-base, mas aumentou FP em 69, reduziu F1 em 0,0408 e não reduziu o número de semanas acima do teto. A média de 3h sozinha teve um FN, 60 FP adicionais e uma semana a menos acima do teto. **Recomendação antes do comparativo formal:** levar a variante combinada (`media_3h_ozone`, `media_3h_pm2_5`, `delta_2h_ozone`, `delta_2h_pm2_5`) à comparação S3→S4, pois corresponde melhor à prioridade acordada de reduzir falsos negativos e também reduziu os picos semanais de episódios (7 para 6) e de horas de alerta (85 para 76). A ressalva é relevante: FP subiram de 402 para 471, o F1 caiu e o número de semanas acima de três episódios permaneceu 19. Portanto, ela foi mantida como **candidata experimental** para o comparativo e revisão da equipe, não como feature operacional definitivamente selecionada.

Essa segunda triagem é reproduzida pelo mesmo comando. As métricas detalhadas ficam em `reports/modeling/short_term_feature_metrics_by_fold.csv`, `short_term_feature_metrics_summary.csv` e `short_term_feature_alert_burden_by_week.csv`.

**Comparativo formal S3→S4:** a candidata combinada foi comparada ao grupo-base correspondente da Sprint 3 (subíndices individuais + meteorologia, sem `iqar` consolidado) nos mesmos quatro folds expansivos. Dummy e persistência também foram reavaliados como referências nos mesmos folds; para eles, as features não mudam. Todos usam `predict` padrão, sem ajuste de limiar. O resumo reproduzível está em `reports/modeling/sprint4_lift_summary.csv`; resultados por fold e carga semanal em `sprint4_lift_by_fold.csv` e `sprint4_alert_burden_by_week.csv`.

| Comparação | Recall classe 1 | F1 classe 1 | FP | FN | Semanas acima de 3 episódios | Máximo de episódios/semana | Máximo de horas de alerta/semana |
|---|---:|---:|---:|---:|---:|---:|---:|
| Dummy (referência) | 0,0000 | 0,0000 | 0 | 387 | 0 | 0 | 0 |
| Persistência (referência) | 0,8196 | 0,8196 | 68 | 68 | 4 | 5 | 32 |
| Gaussian NB S3 — grupo-base comparável | 0,9949 | 0,6669 | 402 | 3 | 19 | 7 | 85 |
| Gaussian NB S4 — candidata média 3h + delta 2h | 1,0000 | 0,6261 | 471 | 0 | 19 | 6 | 76 |

No comparativo formal, a candidata aumentou o recall médio em 0,0051, reduziu FN em 3 e reduziu o pico de episódios de 7 para 6; em contrapartida, acrescentou 69 FP e reduziu o F1 em 0,0408. O número de semanas completas acima do teto permaneceu em 19. Essa é uma troca entre custos, não uma melhoria geral. Como a prioridade acordada é evitar FN, **decisão técnica recomendada:** congelar as quatro features para o comparativo da Sprint 5, aceitando e registrando o custo medido em FP e F1. O congelamento é do conjunto de atributos para a próxima etapa, não uma seleção do modelo final nem do limiar operacional. Se o teto de três episódios por semana for tratado como requisito rígido, nenhum dos dois grupos o satisfaz (19 semanas excedidas); a decisão final deverá considerar esse conflito sem consultar o holdout antes da avaliação final.

---

## 1. Engenharia de atributos iterada

- [x] Atributos **novos** em relação à Sprint 2 (não são os mesmos com outro nome)
- [x] Motivação ligada aos erros da Sprint 3; os resumos de 3h e deltas de 2h investigam nível recente e variação de poluentes
- [ ] Seleção/redução de atributos avaliada **só no treino** (não no teste nem no dataset inteiro) e justificada — a triagem foi exploratória nos folds de validação de 2024, portanto não satisfaz esse critério estrito
- [x] Disponibilidade temporal dos atributos novos revisada; transformações usam somente valores até *t* e parâmetros do imputador/escalador são ajustados dentro do treino de cada fold
- [x] Cada atributo novo descrito e justificado individualmente
- [x] Dicionário (seção de derivados) atualizado

**Descrição dos atributos criados/selecionados, disponibilidade temporal e de quais erros da Sprint 3 eles investigam:**

Para o comparativo da Sprint 5, fica congelado o grupo-base de subíndices sem `iqar` consolidado, meteorologia e quatro atributos de contexto curto (`media_3h_ozone`, `media_3h_pm2_5`, `delta_2h_ozone`, `delta_2h_pm2_5`). A escolha segue a prioridade acordada de evitar FN e os resultados formais acima; a triagem nos folds de desenvolvimento pode introduzir viés de seleção, razão para manter o holdout temporal reservado e realizar nele apenas a avaliação final definida na Sprint 5. Os atributos de médias e deltas são calculados causalmente com dados disponíveis em *t*; lacunas iniciais são tratadas pelo imputador.

## 2. Pipeline de preparação congelado

- [x] Um `Pipeline` sklearn: `ColumnTransformer` **e** o classificador no mesmo objeto; lista de colunas congelada em `FEATURES_SPRINT4`
- [x] Estratégias justificadas: imputação pela mediana e padronização de variáveis numéricas, ambas ajustadas no treino; não há variáveis categóricas que exijam encoding
- [x] `fit` confirmado apenas no treino de cada fold
- [x] O pipeline reutilizável está em `src/modelagem/Avaliar_Baselines.py`; `criar_pipeline_sprint4` aplica a lista congelada e aceita classificadores sklearn para uso na Sprint 5. Não alterar a lista sem documentar a mudança e reavaliar os três baselines.

**Descrição da preparação final:**

O pipeline recebe o classificador como parâmetro, preservando o mesmo `ColumnTransformer` para Naive Bayes e futuros classificadores comparáveis. As features temporais são construídas antes da separação, com operações retrospectivas sem consulta a valores futuros; o imputador e o escalador são ajustados somente durante `fit` no treino de cada fold. A referência de persistência continua sendo uma regra direta baseada no IQAr em *t* e Dummy permanece independente das features.

## 3. Retreino do baseline e lift

- [x] Dummy, persistência e Naive Bayes **reavaliados** nos mesmos folds temporais da Sprint 2/3; Naive Bayes treinado com o conjunto congelado S4
- [x] Métricas por classe (recall, precisão, F1, matriz) dos modelos, por fold, em `reports/modeling/sprint4_lift_by_fold.csv`
- [x] Tabela de delta em relação ao grupo-base S3 comparável (recall e F1 da classe positiva)
- [x] Sem ganho geral: a candidata prioriza recall/FN ao custo de F1/FP; deltas de 1h, variáveis meteorológicas, hora cíclica e as variantes alternativas de contexto curto não foram incluídas no conjunto congelado.

**Tabela de lift (classe positiva; mesmos quatro folds temporais de 2024):**

| Modelo | Recall S3 | Recall S4 | F1 S3 | F1 S4 | Delta recall |
|---|---|---|---|---|---|
| Dummy | 0,0000 | 0,0000 | 0,0000 | 0,0000 | 0,0000 |
| Persistência | 0,8196 | 0,8196 | 0,8196 | 0,8196 | 0,0000 |
| Naive Bayes (grupo-base S3 sem `iqar`) | 0,9949 | 1,0000 | 0,6669 | 0,6261 | +0,0051 |

**Interpretação do lift:** a candidata S4 eliminou os três FN do grupo-base, mas adicionou 69 FP e reduziu F1 em 0,0408; o número de semanas completas acima do teto não mudou. Dummy e persistência servem como referências reavaliadas, não como modelos com features novas. O resultado é um trade-off entre FN e FP, sem evidência para declarar uma melhoria geral. As quatro features ficam congeladas para o comparativo da Sprint 5, sem constituir escolha de modelo ou limiar final.

**Carga operacional exploratória — sem seleção de limiar:**

| Modelo / grupo | Limiar do `predict` padrão | Semanas acima de 3 episódios | Máximo de episódios/semana | Máximo de horas de alerta/semana | Observações |
|---|---:|---:|---:|---:|---|
| Gaussian NB — grupo-base S3 sem `iqar` | 0,5 | 19 | 7 | 85 | 402 FP, 3 FN |
| Gaussian NB — candidata S4 | 0,5 | 19 | 6 | 76 | 471 FP, 0 FN |

Reportar os resultados semanais como diagnóstico de desenvolvimento, não como garantia de carga futura. Um episódio é contado na semana em que começa; a contagem não mede acertos na detecção de episódios reais. Não criar ou ajustar limiar nesta sprint.

## 4. Sprint Review — checkpoint intermediário

**Incremento demonstrado ao PO (docente):**
**Feedback recebido:**

## 5. Scrum

- [ ] Atualizações assíncronas semanais registradas
- [ ] Board refletindo o backlog, em andamento e concluído

## 6. Diário de bordo (retrospectiva individual)

| Integrante | O que fiz nesta Sprint | Dificuldades | O que pretendo manter/ajustar |
|---|---|---|---|
| | | | |

---

## Rubrica de avaliação — Sprint 4 (nota de 0 a 4,0)

| Critério | Peso | O que caracteriza nota máxima | Nota atribuída | Observações |
|---|---|---|---|---|
| Engenharia de atributos iterada | 1,5 | Atributos novos, justificados pelos erros da Sprint 3, seleção criteriosa, sem vazamento | | |
| Pipeline congelado | 0,5 | ColumnTransformer atualizado, `fit` só no treino, estratégias justificadas | | |
| Retreino do baseline e lift | 1,0 | Dummy/persistência/NB retreinados no mesmo split; delta de recall/F1 interpretado | | |
| Sprint Review / incremento demonstrado | 0,5 | Incremento real apresentado ao PO, com feedback registrado | | |
| Scrum + diário de bordo | 0,5 | Board atualizado semanalmente, diário reflexivo de todos os integrantes | | |
| **Nota final da Sprint 4** | **4,0** | | **___ / 4,0** | |
