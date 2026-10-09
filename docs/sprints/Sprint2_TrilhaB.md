# Diário de Sprint 2 — Limpeza, tratamento, EDA e engenharia de atributos
**Período:** 18/09/2026 a 27/09/2026
**Trilha definitiva do grupo:** B — Qualidade do ar inadequada

**Equipe:** Davi Gama dos Santos - 33121079, Diogo Gomes Barbosa - 35866276, Eudenis de Souza Vieira - 32751621, Gabriel Januário Alves - 35609991, João Pedro Barreto da Silva - 33297185
**Scrum Master do Sprint:** A preencher conforme definição da equipe.
**Repositório GitHub:** A preencher com o link do repositório.
**Estado atualizado em 09/10/2026:** alvo, partições temporais e EDA descritiva/gráfica do desenvolvimento implementados; seleção/engenharia de features e modelagem continuam pendentes.

> A aula pode usar a **Trilha A (chuva intensa)** só como exemplo de método. **A entrega é nos dados brutos da Trilha B coletados na Sprint 1** (`data/raw/`).
>
> Fluxo aplicado: **inspeção/validação → definição e cálculo do alvo → split temporal pelo horário do evento → EDA inicial para entender a prevalência → EDA detalhada no desenvolvimento → features**. Não se imputam rótulos nem valores de janelas incompletas. Imputação estatística, se necessária nas features, deve ser ajustada apenas no treino. Não há modelagem (baseline na Sprint 3).

### Contrato desta sprint

| Artefato | Origem / destino |
|---|---|
| `data/raw/` + `config/` + N do merge | Sprint 1 — **não substituir por outra coleta sem versionar** |
| RFC v0.1 e dicionário v0.1 | Sprint 1 |
| `data/interim/` + log de validação (N antes/depois) | Sprint 2 — período ampliado integrado e documentado |
| Split (corte, N treino/teste) | Implementado em `src/validacao/Separacao_Temporal.py`; reutilizar o mesmo corte |
| Alvo formal (limiar, horizonte, desbalanceamento no treino) | Implementado/documentado; mantê-lo fixo nas Sprints 3–5 |
| Features iniciais justificadas + dicionário v0.2 | Sprint 3 (transformer) e 4 (base para iterar) |

**Não sai daqui:** Dummy, persistência, Naive Bayes, F1, modelo escolhido.

- [x] Confirmei que o notebook desta sprint lê o `data/raw` da Sprint 1

---

## 1. Limpeza e tratamento (antes da EDA)

`data/raw/` permanece intocado. A tabela tratada vai para `data/interim/`.

### 1.1 Inspeção (contar o sujo, ainda sem corrigir)

- [x] Estatística descritiva das colunas numéricas
- [x] Ausentes quantificados por coluna
- [x] Duplicatas (linhas e por chave de unidade de análise)
- [x] Valores inválidos de domínio (ex.: poluente negativo)
- [ ] Sentinelas específicas da API (nenhum padrão específico documentado)

**Diagnóstico (período ampliado):**
- 35.736 registros por fonte, com timestamps alinhados e sem lacunas horárias.
- Nenhum valor nulo ou concentração negativa nas variáveis de origem.
- Os 744 horários de janeiro/2025 foram preservados nos arquivos originais.

### 1.2 Regras aplicadas

Não imputar com média/mediana/moda do dataset **inteiro**. Isso vaza o teste. Imputação estatística, se precisar, é a seção 3 (depois do split).

- [x] Tipos e unidades padronizados
- [x] Duplicatas tratadas com contagem
- [ ] Sentinelas → `NaN` explícito (nenhum padrão específico documentado na resposta da API)
- [ ] Inválidos de domínio tratados com regra escrita (remover / `NaN` / correção só se a fonte tiver erro conhecido)
- [x] Log: o que foi feito, em quantas linhas/células, N depois
- [x] Tabela salva em `data/interim/`
- [x] Dicionário (log de validação) atualizado

| Problema encontrado | Regra aplicada | Linhas/células afetadas | N depois |
|---|---|---|---|
| Ausência nas variáveis brutas | Não necessária | 0 | 35.736 |
| Concentração negativa ou valor inválido | Não necessária | 0 | 35.736 |
| Duplicata ou lacuna horária | Não necessária | 0 | 35.736 |

**N após a validação:** 35.736 registros.
**Evidências:** `data/interim/dados_merged_2022-08-04_2026-08-31.csv`; valores indefinidos gerados pelas janelas do alvo são registrados na seção 5, sem imputação.

## 2. Split temporal

Sobre a tabela rotulada em `data/interim/`; os períodos são atribuídos pelo horário do evento previsto (`time + 1h`).

- [x] Treino = período mais antigo; teste = mais recente (sem embaralhar)
- [x] Data de corte explícita; N treino e N teste
- [x] Teste final reservado: não usar para seleção de modelo, limiar ou parâmetros de transformação

**Validação:** folds expansivos por trimestre em 2024. O primeiro fold treina em 04/08/2022–2023; os seguintes incorporam os trimestres de validação anteriores.
**Teste final:** horário do alvo de 01/01/2025 a 01/09/2026 (fim exclusivo).
**N treino final / N teste:** 21.121 (743 positivos) / 14.592 (161 positivos).
**Justificativa:** o recorte cronológico simula previsão futura e os folds mantêm o teste final fora da seleção. A implementação e os limites estão em `src/validacao/Separacao_Temporal.py` e `config/params.yaml`.

## 3. Tratamento estatístico residual (depois do split, antes da EDA)

Só NA que a limpeza de domínio não resolveu. Parâmetros saem **somente do treino**.

- [x] Estratégia justificada
- [x] Ausências nas variáveis brutas inexistentes; valores indefinidos nas janelas e no rótulo mantidos sem imputação

**Regra residual:** não há ausências nas variáveis brutas. Valores indefinidos gerados pelas janelas móveis/horizonte não são imputados nem usados na modelagem supervisionada. Imputação de features só será considerada após a engenharia e ajustada no treino, se necessária.

## 4. Análise exploratória (EDA) — desenvolvimento já tratado

- [x] Estatística descritiva inicial das features candidatas no desenvolvimento
- [x] Série temporal, distribuições e boxplots
- [x] Associação exploratória feature-alvo no desenvolvimento (Spearman; pode ser espúria em série temporal)
- [x] Outliers investigados e discutidos (sem remoção ou clipping)

> O desenvolvimento inclui treino e folds de validação de 2022–2024. A exploração detalhada de features não usa o período de teste 2025–2026.

**Exposição descritiva anterior ao split:** antes de fixar a janela, foram examinadas as taxas por ano e médias condicionadas à classe na série inteira, inclusive 2025–2026. Não houve ajuste/avaliação de modelo nem otimização de limiar; porém, o teste não é totalmente cego. A partir do split fixado, dados do teste não serão usados em decisões de features, modelo, parâmetros ou limiar.

**EDA no desenvolvimento (21.121 linhas, 743 positivas):** setembro teve 6,62% de positivos, março 5,65% e junho 1,04%. Por hora do evento, as taxas mais altas ocorreram às 18h (13,30%), 17h (12,84%) e 19h (11,82%); entre 7h e 11h não houve positivos neste período. Esses padrões não devem ser convertidos em regras fixas, dada a raridade e a variação temporal.

As medianas da classe 0 para a classe 1 foram: ozônio 61 → 156 µg/m³, PM2,5 9 → 18,9 µg/m³, temperatura 19,2 → 25 °C, umidade relativa 86 → 67% e IQAr em *t* 26,85 → 118,33. As associações de Spearman mais altas com o alvo foram `iqar_ozone` e `iqar` (0,317 cada), ozônio (0,297), `iqar_pm2_5` (0,215) e PM2,5 (0,211). O NO2 e seu subíndice ficaram próximos de zero; isso não basta para excluir uma variável, pois interações e desempenho nos folds ainda serão avaliados.

Os subíndices e o IQAr calculados em *t* são candidatos válidos, pois usam dados disponíveis no instante da previsão. A associação com o alvo pode refletir as mesmas concentrações e janelas móveis sobrepostas; não representa causalidade nem importância independente. Quatro dessas colunas (`iqar_pm10`, `iqar_pm2_5`, `iqar_sulphur_dioxide` e `iqar`) têm uma ausência cada no desenvolvimento, na borda inicial das janelas.

**EDA gráfica reproduzível:** `python -m src.analise.EDA_Desenvolvimento` gera [prevalência mensal](../../reports/figures/eda_desenvolvimento/prevalencia_mensal.png), [boxplots em `log1p`](../../reports/figures/eda_desenvolvimento/boxplots_concentracoes_log1p.png), [correlação de Spearman entre features](../../reports/figures/eda_desenvolvimento/correlacao_spearman_features.png) e [máximos diários no tempo](../../reports/figures/eda_desenvolvimento/extremos_concentracoes_tempo.png). A análise seleciona somente rótulos com evento previsto até 31/12/2024; 2025–2026 permanece fora dela.

O CO bruto atinge 3.838 µg/m³ (p99,9 = 2.832,04 µg/m³), PM10 152,7 µg/m³ e PM2,5 106,9 µg/m³. Os três máximos coincidem em 05/06/2023; há sequências de vários horários altos, especialmente em maio–junho/2023, e episódios de particulados em setembro/2024. A cerca superior `Q3 + 1,5 × IQR` sinaliza 1.118 horas (5,29%) para CO, 1.132 (5,36%) para PM10 e 1.120 (5,30%) para PM2,5; 669 horas cruzam as três cercas ao mesmo tempo. Isso é uma triagem estatística, não uma validação de erro. As taxas positivas nos horários acima da cerca foram 3,13% (CO), 14,49% (PM10) e 13,57% (PM2,5), contra 3,52% no desenvolvimento, mas há autocorrelação horária, sobreposição das janelas e deslocamento do alvo de uma hora.

O alvo depende de médias móveis CETESB e do maior subíndice em *t+1h*, não do valor bruto isolado. No episódio de 05/06/2023, os picos matinais de CO/PM não produziram rótulos positivos imediatos; mais tarde, o subíndice de ozônio ultrapassou 100, gerando rótulos positivos para eventos previstos entre 16h e 22h. A matriz também evidencia associação alta entre PM10/PM2,5 e índices derivados, que são transformações determinísticas. Sem medição local independente, os extremos continuam sem validação externa; não foram removidos nem limitados. A comparação de variáveis brutas e índices derivados fica para os folds, sem decisão baseada no holdout.

## 5. Definição da variável-alvo

**Classe positiva:** 1 quando IQAr > 100; classe 0 quando IQAr <= 100.
**Limiar e justificativa:** IQAr é o maior dos seis subíndices calculados conforme CETESB 2025; as janelas e a conversão de CO seguem a Tabela 2.7. A decisão foi alinhada ao custo de falso negativo do RFC.
**Horizonte / deslocamento:** 1h à frente (definido no RFC).
**Desbalanceamento no treino final:** 743 positivos (3,52%) e 20.378 negativos em 21.121 rótulos definidos.
**Teste reservado:** 161 positivos e 14.431 negativos em 14.592 rótulos definidos. As taxas e médias por classe do período completo foram vistas descritivamente antes de congelar o split; não usar o teste para seleção posterior de modelo ou limiar.

- [x] Classe positiva sem ambiguidade, ligada ao custo de FN
- [x] Desbalanceamento das classes quantificado no treino
- [x] Seção do alvo no dicionário preenchida
- [x] Rótulo e colunas calculadas em t+1h reservados à construção do alvo; valores observados até t continuam candidatos a feature

## 6. Engenharia de atributos (Feature Engineering)

- [ ] Médias móveis, lags e agregações só com informação anterior ao ponto de previsão
- [ ] Cada feature seria calculável **no momento real da previsão** (mesmo horizonte do RFC)
- [ ] Timestamp e IDs **não** entram como número; calendário (hora, dia da semana, estação) vale
- [ ] Variáveis de calendário quando pertinente (hora, dia da semana, estação)
- [ ] Parâmetros de janela definidos **no treino**, depois aplicados ao teste
- [ ] Vazamento ausente (texto + código: `.shift()` / `.rolling()` sem o instante-alvo nem o futuro)
- [ ] Cada atributo justificado um a um; dicionário atualizado

**Descrição e justificativa dos atributos:** Pendente - features ainda não foram criadas.

**Evidências (trecho de código, link do notebook):** Pendente.

## 7. Scrum

- [ ] Atualizações semanais no board
- [ ] Board refletindo o estado real

**Link do board:** Pendente.

## 8. Diário de bordo (retrospectiva individual)

| Integrante | O que fiz nesta Sprint | Dificuldades | O que pretendo manter/ajustar |
|---|---|---|---|
| Davi Gama dos Santos | A preencher pelo integrante. | A preencher. | A preencher. |
| Diogo Gomes Barbosa | A preencher pelo integrante. | A preencher. | A preencher. |
| Eudenis de Souza Vieira | A preencher pelo integrante. | A preencher. | A preencher. |
| Gabriel Januário Alves | A preencher pelo integrante. | A preencher. | A preencher. |
| João Pedro Barreto da Silva | A preencher pelo integrante. | A preencher. | A preencher. |

---

## Rubrica de avaliação — Sprint 2 (nota de 0 a 4,0)

| Critério | Peso | O que caracteriza nota máxima | Nota atribuída | Observações |
|---|---|---|---|---|
| Limpeza e tratamento | 1,0 | Inspeção numérica, regras explícitas, log com N, `interim` gerado, raw intocado, sem estatística global para imputar | Parcial | Variáveis brutas verificadas; sentinelas ainda não auditadas especificamente |
| Split temporal | 0,5 | Corte explícito na tabela limpa; teste isolado | Concluído | Folds expansivos em 2024 e teste final 2025–2026 implementados |
| EDA e variável-alvo | 1,0 | EDA no treino tratado; alvo formalizado no treino; dicionário atualizado | Parcial | EDA descritiva/gráfica e triagem de extremos documentadas; seleção de features ainda pendente |
| Engenharia de atributos | 1,0 | Janelas/lags coerentes, sem vazamento, parâmetros no treino, atributos justificados um a um | Pendente | Features ainda não criadas |
| Scrum + diário de bordo | 0,5 | Board com histórico; diário reflexivo de todos | Pendente | Diário ainda não preenchido |
| **Nota final da Sprint 2** | **4,0** | | **___ / 4,0** | |

---

## Observações

A Sprint 2 foi **parcialmente executada** e atualizada em 09/10/2026:
- ✅ Merge ampliado entre as fontes: `dados_merged_2022-08-04_2026-08-31.csv`, com 35.736 registros
- ✅ Variáveis brutas verificadas: sem ausências, valores negativos, duplicatas ou lacunas horárias
- ✅ Alvo CETESB formalizado e aplicado: 35.713 rótulos definidos, 904 positivos
- ✅ Split temporal implementado; 21.121 registros de treino final e 14.592 de teste final, separados pelo horário do rótulo
- ✅ EDA descritiva e gráfica concluída somente no desenvolvimento; teste reservado para avaliação final
- ✅ Dicionário atualizado para v0.6
- ✅ EDA detalhada e triagem estatística dos extremos documentadas; sem tratamento automático de valores
- ❌ Features derivadas e modelagem ainda não realizadas
- ❌ Diário individual e board ainda precisam ser preenchidos pela equipe

**Conclusão:** A Sprint 2 necessita ser completada antes de prosseguir para a Sprint 3. Os artefatos essenciais (split, alvo, features) ainda não foram criados.
