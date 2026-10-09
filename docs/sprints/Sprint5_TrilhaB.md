# Diário de Sprint 5 — Modelagem completa, limiar de decisão e seleção
**Período:** 12/10/2026 a 25/10/2026
**Trilha:** B — Qualidade do ar inadequada

**Equipe:**
**Scrum Master do Sprint:**
**Repositório GitHub:** (link)

> Split da Sprint 2 e `ColumnTransformer` **congelado na Sprint 4**. Use `FEATURES_SPRINT4` e `criar_pipeline_sprint4(classificador)` em `src/modelagem/Avaliar_Baselines.py` para aplicar exatamente as mesmas colunas e preparação aos classificadores comparáveis. No comparativo, Dummy, persistência e Naive Bayes são os da Sprint 4 (mesmo pipeline, exceto as referências que não dependem de features). Pode **reproduzir** esses números no notebook desta sprint; **não** colar métricas da Sprint 3 (features antigas). Classificadores novos treinam neste pipeline, na mesma partição de teste.

### Contrato desta sprint

| | Artefato | Origem / destino |
|---|---|---|
| **Entra** | Split da Sprint 2 | Sprint 2 — **não mudar o teste** |
| **Entra** | Features finais + `ColumnTransformer` congelado + baselines retreinados (lift) | Sprint 4 |
| **Entra** | RFC (custo de FN) e dicionário v0.9 | Sprints 1 e 4 |
| **Sai** | Comparativo no pipeline final (baselines S4 + ≥2 modelos novos, mesma partição) | Entrega final |
| **Sai** | Limiar de decisão justificado pelo RFC | Entrega final |
| **Sai** | Modelo escolhido + caderno de experimentos + model card + dicionário v0.4 + `joblib` do Pipeline em `models/` | Entrega final / mostra |

**Não há sprint seguinte.** Dashboard, se houver, é extra e lê estes artefatos — não gera outro split.

- [ ] Confirmei transformer da Sprint 4, split da Sprint 2 e que nenhuma métrica da Sprint 3 entrou no quadro

---

## 1. Revisão do split e da preparação

- [x] Mesmo split temporal da Sprint 2 (ou o recorte reaplicado e já usado nas Sprints 3–4)
- [x] `Pipeline`/`ColumnTransformer` da Sprint 4, usando `FEATURES_SPRINT4`, com `fit` só no treino
- [x] Vazamento temporal dos atributos S4 reconfirmado; derivados são retrospectivos e usam dados até *t*

**Recorte de validação temporal (sem acessar o teste):** treino expansivo com 18.913 linhas até antes de 01/10/2024 pelo horário do evento; validação 2024-Q4 com 2.208 linhas (46 positivas). As 12 semanas completas da validação são consideradas na carga semanal; semanas parciais são excluídas dos máximos. O teste final continua reservado. O pipeline aplica imputação mediana e padronização dentro do treino e usa `FEATURES_SPRINT4`.

## 2. Comparativo no pipeline final

- [x] Dummy, persistência e Naive Bayes do pipeline da Sprint 4 comparados na mesma validação temporal
- [x] Dois classificadores adicionais avaliados: regressão logística e Random Forest
- [x] Baselines e modelos novos avaliados na mesma partição de teste; o holdout foi consultado uma única vez
- [x] Hiperparâmetros documentados; não foi feita busca no teste
- [x] `class_weight="balanced"` nos dois classificadores novos; SMOTE / oversampling aleatório não foi usado
- [x] Independência do Naive Bayes continua tratada como hipótese pedagógica, não como fato dos dados

**Modelos no comparativo (3 baselines da Sprint 4 + ≥2 novos):**
1. Dummy
2. Persistência
3. Naive Bayes
4. Regressão logística (`class_weight="balanced"`, `max_iter=1000`, `random_state=42`)
5. Random Forest (`n_estimators=300`, `class_weight="balanced"`, `min_samples_leaf=2`, `n_jobs=-1`, `random_state=42`)

Os dois classificadores novos usam `FEATURES_SPRINT4` e o mesmo pré-processamento mediana + `StandardScaler`, ajustado somente no treino. A comparação é exploratória em 2024-Q4; não há ajuste de hiperparâmetros.

**Validação 2024-Q4 com `predict` padrão (46 positivos; FP/FN em contagem):**

| Modelo | Precisão classe 1 | Recall classe 1 | F1 classe 1 | FP | FN |
|---|---:|---:|---:|---:|---:|
| Dummy prior | 0,0000 | 0,0000 | 0,0000 | 0 | 46 |
| Persistência pelo IQAr em *t* | 0,8043 | 0,8043 | 0,8043 | 9 | 9 |
| Gaussian Naive Bayes S4 | 0,3866 | 1,0000 | 0,5576 | 73 | 0 |
| Regressão logística balanceada | 0,7797 | 1,0000 | 0,8762 | 13 | 0 |
| Random Forest balanceada | 0,9000 | 0,9783 | 0,9375 | 5 | 1 |

Relatórios reproduzíveis: `reports/modeling/sprint5_validation_metrics.csv`, `sprint5_validation_predictions.csv` e `sprint5_validation_alert_burden_by_week.csv`.

## 3. Avaliação, limiar e custo do falso negativo

- [x] Recall, precisão, F1 e matriz de confusão por classe no `predict` padrão para todos os modelos
- [x] Recorte de validação temporal no fim do treino (2024-Q4)
- [x] Trade-off de limiares 0,3 / 0,5 / 0,7 medido na validação; nenhum limiar foi ajustado com o teste
- [x] Teste medido uma vez após congelar Random Forest e limiar 0,3 na validação; o corte não foi escolhido olhando o teste
- [x] Acurácia não foi usada como critério; as métricas e contagens da classe positiva são reportadas
- [x] FN/FP também em **contagem**, não só em percentual

**Caderno de experimentos (validação e teste):**

Na validação, a regressão logística com limiar 0,7 teve 0 FN, 5 FP (precisão 0,9020; F1 0,9485), mas excedeu o teto de episódios em uma das 12 semanas completas (máximo de 4). A Random Forest com limiar 0,3 teve 0 FN, 13 FP (precisão 0,7797; F1 0,8440) e respeitou o teto nas 12 semanas completas (máximo de 3 episódios e 15 horas alertadas na semana de maior carga). **Decisão da equipe:** congelar Random Forest, limiar 0,3, priorizando evitar FN e respeitar o teto semanal na validação. A decisão foi tomada sobre uma única janela curta (46 positivos); os relatórios por limiar e semana são `reports/modeling/sprint5_validation_threshold_tradeoff.csv` e `sprint5_validation_alert_burden_by_week.csv`.

| ID | Modelo | Features (S2/S4) | Limiar | Recall val. | Recall teste | Precisão teste | F1 teste |
|---|---|---|---|---|---|---|---|
| — | Dummy prior | Referência | padrão | 0,0000 | 0,0000 | 0,0000 | 0,0000 |
| — | Persistência | Referência | — | 0,8043 | 0,7888 | 0,7888 | 0,7888 |
| — | Gaussian Naive Bayes | S4 | padrão (0,5) | 1,0000 | 1,0000 | 0,3492 | 0,5177 |
| `random_state=42` | Regressão logística balanceada | S4 | padrão (0,5) | 1,0000 | 1,0000 | 0,7931 | 0,8846 |
| `random_state=42` | Random Forest balanceada | S4 | padrão (0,5) | 0,9783 | 0,8820 | 0,9000 | 0,8847 |
| `random_state=42` | Random Forest balanceada | S4 | 0,3 (congelado) | 1,0000 | 0,9814 | 0,7822 | 0,8705 |

Anotar `random_state` na coluna ID ou numa nota abaixo. Persistência não tem limiar probabilístico — deixar “—” e avaliar só a classe persistida.

**Limiar congelado antes do teste:** Random Forest, 0,3. Na janela 2024-Q4 atingiu recall 1,0 e respeitou o limite em 12 semanas completas, ao custo de 13 FP. A equipe confirmou essa combinação para a única avaliação final; não houve ajuste posterior.

**Avaliação final única (01/01/2025 a 31/08/2026 pelo horário do evento):** treino com 21.121 linhas; holdout com 14.592 linhas e 161 positivos. Todos os resultados abaixo usam o mesmo holdout; as linhas `predict` padrão não foram usadas para ajustar o limiar. A variante Random Forest com 0,3 foi a congelada antes de abrir o conjunto.

| Modelo / regra | Limiar | Precisão classe 1 | Recall classe 1 | F1 classe 1 | FP | FN |
|---|---:|---:|---:|---:|---:|---:|
| Dummy prior | padrão | 0,0000 | 0,0000 | 0,0000 | 0 | 161 |
| Persistência pelo IQAr em *t* | — | 0,7888 | 0,7888 | 0,7888 | 34 | 34 |
| Gaussian Naive Bayes S4 | padrão (0,5) | 0,3492 | 1,0000 | 0,5177 | 300 | 0 |
| Regressão logística balanceada | padrão (0,5) | 0,7931 | 1,0000 | 0,8846 | 42 | 0 |
| Random Forest balanceada | padrão (0,5) | 0,9000 | 0,8820 | 0,8847 | 18 | 19 |
| **Random Forest balanceada — selecionada na validação** | **0,3** | **0,7822** | **0,9814** | **0,8705** | **44** | **3** |

A Random Forest com limiar 0,3 não manteve recall 1,0 no holdout: deixou três eventos sem alerta. Nas 86 semanas completas do teste, uma excedeu o teto; o máximo foi cinco episódios e 31 horas de alerta. Os três FN ocorreram nos eventos de 27/12/2025 14h, 28/12/2025 13h e 31/12/2025 15h. O relatório de casos traz as datas dos FP também. A regressão logística `predict` padrão teve zero FN e 42 FP, mas não substitui a variante previamente congelada: o teste não foi usado para trocar modelo, alterar limiar ou retreinar uma nova seleção. Os resultados indicam que a prioridade de evitar FN segue em trade-off com a carga de alertas; o holdout não será reutilizado para novas escolhas.

Relatórios da única execução: `reports/modeling/sprint5_final_test_metrics.csv`, `sprint5_final_test_predictions.csv`, `sprint5_final_test_misclassified_cases.csv` e `sprint5_final_test_alert_burden_by_week.csv`.

## 4. Seleção do modelo, análise de erros e model card mínimo

- [x] Modelo congelado antes do holdout com justificativa de recall e teto semanal; teste reportado sem reajuste. A regressão logística tem métricas de teste melhores em recall/F1 que a variante congelada; essa observação é registrada, não usada para trocar o modelo após abrir o holdout.
- [x] FN concretos identificados por data/hora; FP registrados no CSV de erros
- [x] Model card mínimo preenchido abaixo
- [x] `joblib` do pipeline inteiro em `models/modelo_final_sprint5.joblib` (pré-processamento + Random Forest; limiar registrado nos metadados)
- [x] Dicionário conferido para o conjunto de features congelado da Sprint 4

**Modelo final e justificativa:**

Random Forest balanceada, com 300 árvores, `min_samples_leaf=2`, `random_state=42`, e limiar 0,3 congelado na validação temporal. A validação encontrou recall 1,0 e respeitou o teto em 12 semanas completas. No holdout, o recall foi 0,9814 (3 FN) e o F1 0,8705; esta limitação é mantida explícita, sem nova seleção ou ajuste sobre o teste.

**Principais erros analisados (FN/FP relevantes):**

FN nos horários previstos para 27/12/2025 14h, 28/12/2025 13h e 31/12/2025 15h. Os 44 FP e todos os casos classificados incorretamente estão em `reports/modeling/sprint5_final_test_misclassified_cases.csv`.

### Model card mínimo

| Campo | Conteúdo |
|---|---|
| Problema / classe positiva | Prever se o IQAr será > 100 na hora seguinte no ponto de referência da Universidade Braz Cubas. |
| Unidade de análise e horizonte | Observação horária do ponto de referência; horizonte de 1 hora. |
| Split (treino / teste) | Treino temporal até antes de 01/01/2025 pelo horário do evento (21.121 linhas); teste de 01/01/2025 a 31/08/2026 (14.592 linhas; 161 positivos). |
| Features (link do dicionário) | `FEATURES_SPRINT4`; [dicionário de dados](../Dicionario_de_Dados.md). |
| Algoritmo, hiperparâmetros, `random_state` e limiar (origem: validação) | Random Forest `class_weight="balanced"`, 300 árvores, `min_samples_leaf=2`, `random_state=42`; limiar 0,3 congelado em validação temporal 2024-Q4. |
| Métrica principal no teste (classe positiva) | Recall 0,9814; precisão 0,7822; F1 0,8705; 158 TP, 3 FN, 44 FP, 14.387 TN. |
| O que o modelo **não** faz / limitações | Não é alerta oficial nem previsão em tempo real; usa dados modelados de um ponto; validação de limiar tem 46 positivos; no holdout houve 3 FN e uma semana excedeu o teto exploratório de episódios. |
| Como reproduzir (`requirements.txt` + notebook/script) | Instalar `requirements.txt`; `python -m src.modelagem.Comparar_Modelos_Sprint5` reproduz validação; `python -m src.modelagem.Empacotar_Modelo_Final_Sprint5` gera o artefato final. O relatório do holdout já está salvo; não executar novamente a avaliação final após inspecionar o teste. |

## 5. Integração com Banco de Dados (opcional)

- [ ] Ponto de integração avaliado com a disciplina de Banco de Dados (poluentes, clima e previsões)
- [ ] Situação atual da integração (em andamento / não viabilizada / concluída)

## 6. Scrum e diário de bordo

- [ ] Board atualizado
- [ ] Diário de bordo individual preenchido

| Integrante | O que fiz nesta Sprint | Dificuldades | O que pretendo manter/ajustar |
|---|---|---|---|
| | | | |

---

## Rubrica de avaliação — Sprint 5 (nota de 0 a 4,0)

| Critério | Peso | O que caracteriza nota máxima | Nota atribuída | Observações |
|---|---|---|---|---|
| Revisão do split e da preparação | 0,5 | Split da Sprint 2 e transformer da Sprint 4, vazamento reconfirmado | | |
| Comparativo no pipeline final | 1,0 | Baselines retreinados + ≥2 modelos novos, mesma partição, hiperparâmetros documentados | | |
| Avaliação, limiar e custo de FN | 1,0 | Métricas por classe + limiar escolhido **na validação** ligado ao RFC; teste uma vez; FN/FP em contagem | | |
| Seleção, erros e model card | 1,0 | Justificativa clara (métrica da positiva, não acurácia), casos concretos, model card, `joblib` do Pipeline; baseline vencedor é aceito | | |
| Scrum + diário de bordo (e integração opcional com BD) | 0,5 | Board e diário refletindo o processo real da Sprint | | |
| **Nota final da Sprint 5** | **4,0** | | **___ / 4,0** | |
