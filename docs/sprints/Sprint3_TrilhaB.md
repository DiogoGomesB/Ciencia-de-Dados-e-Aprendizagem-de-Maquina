# Diário de Sprint 3 — Ingestão robusta e primeira modelagem (baseline)

**Período:** 28/09/2026 a 04/10/2026

**Trilha:** B — Qualidade do ar inadequada

**Equipe:** Davi Gama dos Santos - 33121079, Diogo Gomes Barbosa - 35866276, Eudenis de Souza Vieira - 32751621, Gabriel Januário Alves - 35609991, João Pedro Barreto da Silva - 33297185

**Scrum Master do Sprint:** A preencher conforme definição da equipe.

**Repositório GitHub:** A preencher com o link do repositório.

---

## Contrato desta sprint

A Sprint 3 parte dos resultados produzidos na Sprint 2, mantendo o mesmo recorte do problema, o mesmo split temporal, a mesma variável-alvo e as features iniciais definidas anteriormente. Nesta etapa, o foco está no fortalecimento da ingestão dos dados e na construção dos primeiros baselines para estabelecer uma referência de desempenho para as etapas posteriores.

Os dados brutos da Sprint 1 permanecem preservados como origem. Os dados tratados e o split utilizados nesta sprint devem corresponder aos artefatos produzidos na Sprint 2.

### 1. Aprofundamento da ingestão (Pipeline CD)

Nesta sprint, será avaliada a robustez do processo de coleta e armazenamento dos dados, buscando permitir a reexecução do processo sem duplicação ou perda dos dados brutos.

A coleta deverá manter a separação entre:

* `data/raw/`: dados brutos obtidos das APIs, preservados como origem;
* `data/interim/`: dados tratados e preparados na Sprint 2;
* `data/processed/`: dados com as features utilizadas na modelagem desta sprint.

Também deverá ser mantido um `requirements.txt` contendo as dependências e versões utilizadas no processo de coleta e preparação.

**Evidências:** serão registrados os links para os commits, notebooks ou arquivos que comprovem a implementação da ingestão robusta.

**Status atualizado em 09/10/2026:** coleta versionada e proteção contra sobrescrita implementadas; a avaliação baseline foi executada em desenvolvimento nos folds temporais de 2024. O holdout 2025–2026 não foi usado.

---

## 2. Preparação para modelagem

A modelagem desta sprint deverá utilizar **o mesmo split temporal definido na Sprint 2** e as features iniciais após serem especificadas, sem criação de um novo split aleatório.

O pré-processamento deverá ser realizado dentro de um `Pipeline` do scikit-learn, utilizando um `ColumnTransformer` em conjunto com o classificador. O ajuste (`fit`) das transformações deverá ocorrer somente utilizando os dados de treino.

Imputação residual, normalização ou outras transformações necessárias deverão permanecer dentro do pipeline, evitando o ajuste de transformações utilizando informações do conjunto de teste.

Também deverá ser reconfirmada a ausência de vazamento nas features temporais já construídas na Sprint 2.

**Estratégia de split:** folds expansivos por trimestre em 2024; treino crescente a partir de 04/08/2022, com períodos definidos pelo horário do rótulo (`time + 1h`). Teste final de 2025–2026, reservado para avaliação final.
**Features e pré-processamento:** os três grupos candidatos foram definidos; o Gaussian Naive Bayes usa `ColumnTransformer` e pipeline com imputação e padronização ajustadas no treino de cada fold. A escolha final de features/modelo permanece pendente.

**Protocolo de comparação aprovado em 09/10/2026:** avaliar nos mesmos folds três grupos candidatos: (1) seis poluentes brutos + meteorologia; (2) seis subíndices e `iqar` consolidado + meteorologia; (3) poluentes brutos, subíndices e `iqar` + meteorologia. Os índices candidatos usam somente valores disponíveis até *t*. O holdout 2025–2026 não participa da seleção; as transformações e os modelos ainda serão definidos.

---

## 3. Modelagem baseline

A Sprint 3 terá como objetivo estabelecer referências iniciais de desempenho utilizando três abordagens:

1. **DummyClassifier**, representando um baseline simples baseado na classe majoritária;
2. **Persistência temporal**, utilizando a informação disponível no instante da previsão como referência para o próximo estado;
3. **Naive Bayes**, treinado nos mesmos folds, com um pipeline separado para cada grupo candidato de features.

Os três baselines deverão ser avaliados nos mesmos folds expansivos de validação para permitir comparação consistente. O holdout temporal 2025–2026 não será usado para escolha de features, modelos ou limiares e será avaliado somente após congelar o pipeline. Como taxas e médias por classe desse período foram examinadas descritivamente antes da definição do split, ele não é totalmente cego; essa limitação deve acompanhar os resultados finais.

Serão analisadas métricas como **recall, precisão, F1 e matriz de confusão para cada classe**, com atenção especial à classe positiva, devido ao maior custo associado aos falsos negativos definido na RFC.

O Naive Bayes será tratado como um baseline pedagógico. Sua hipótese de independência condicional pode não representar adequadamente a relação entre variáveis de qualidade do ar e meteorológicas, que podem apresentar correlação entre si. Dessa forma, o objetivo nesta etapa é estabelecer uma referência de desempenho, e não assumir que o modelo represente uma relação física entre os fenômenos.

Nesta sprint não será realizado ajuste fino do limiar de decisão. Será utilizado o comportamento padrão dos modelos, deixando a definição de limiar como etapa posterior do projeto.

Também não será utilizado SMOTE ou oversampling aleatório, considerando a natureza temporal dos dados.

**Definição operacional dos baselines:**

- `DummyClassifier(strategy="prior")`: estima a classe majoritária somente no treino de cada fold. Como a classe positiva é rara, prevê a classe 0 em todos os registros de validação.
- Persistência: prevê classe 1 se o IQAr calculado em `t` for > 100 e classe 0 caso contrário; representa a hipótese simples de que o estado atual continua na próxima hora.
- Gaussian Naive Bayes: executado separadamente para os três grupos de features aprovados, com imputação pela mediana e padronização numérica. O `SimpleImputer`, `StandardScaler` e classificador estão no mesmo `Pipeline`/`ColumnTransformer`; são ajustados apenas no treino de cada fold.

Não houve ajuste de limiar, reamostragem ou seleção com o holdout. Métricas abaixo são médias simples das quatro métricas por fold; as contagens da matriz de confusão são somas dos quatro folds e não médias.

**Resultados iniciais (Dummy vs. persistência vs. Gaussian Naive Bayes):**

| Modelo | Grupo de features | Precisão classe 1 (média) | Recall classe 1 (média) | F1 classe 1 (média) | TN total | FP total | FN total | TP total |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Dummy prior | Independente de features | 0,0000 | 0,0000 | 0,0000 | 8.397 | 0 | 387 | 0 |
| Persistência por IQAr em `t` | Independente de features | 0,8196 | 0,8196 | 0,8196 | 8.329 | 68 | 68 | 319 |
| Gaussian Naive Bayes | Poluentes brutos + meteorologia | 0,2996 | 0,6882 | 0,4134 | 7.814 | 583 | 114 | 273 |
| Gaussian Naive Bayes | Subíndices/IQAr + meteorologia | 0,4491 | 0,9985 | 0,6175 | 7.921 | 476 | 1 | 386 |
| Gaussian Naive Bayes | Brutos + subíndices/IQAr + meteorologia | 0,4217 | 0,9985 | 0,5914 | 7.860 | 537 | 1 | 386 |
| Gaussian Naive Bayes (ablação) | Subíndices individuais + meteorologia, sem `iqar` | 0,5057 | 0,9949 | 0,6669 | 7.995 | 402 | 3 | 384 |
| Gaussian Naive Bayes (ablação) | Brutos + subíndices individuais + meteorologia, sem `iqar` | 0,4254 | 0,9956 | 0,5942 | 7.855 | 542 | 3 | 384 |

O Naive Bayes com subíndices/IQAr teve o maior recall médio entre os três grupos iniciais, mas também 476 falsos positivos agregados. A persistência teve maior F1 médio entre os baselines iniciais. Na ablação, retirar `iqar` reduziu os FP de 476 para 402 no grupo somente de subíndices, com recall descendo de 0,9985 para 0,9949 e F1 subindo de 0,6175 para 0,6669. No grupo combinado, os FP aumentaram de 537 para 542, recall caiu de 0,9985 para 0,9956 e F1 mudou de 0,5914 para 0,5942. Assim, o efeito não é consistente entre grupos e não demonstra causalidade nem seleciona o modelo. Os resultados são preliminares: a prevalência muda entre períodos e Q4/2024 tem apenas 46 positivos. O Naive Bayes pressupõe independência condicional, hipótese pouco realista para poluentes correlacionados; índices em `t` e o alvo também usam poluentes/janelas relacionados.

As métricas por fold e o resumo agregado foram salvos em:

- `reports/modeling/baseline_metrics_by_fold.csv`
- `reports/modeling/baseline_metrics_summary.csv`
- `reports/modeling/baseline_predictions_by_fold.csv`
- `reports/modeling/baseline_misclassified_cases.csv`, com cada falso positivo/falso negativo e as features disponíveis em *t*
- `reports/modeling/baseline_error_rates_by_month.csv` e `baseline_error_rates_by_hour.csv`, com os denominadores das taxas
- `reports/modeling/baseline_iqar_ablation_by_fold.csv` e `baseline_iqar_ablation_summary.csv`, comparando os grupos com subíndices antes e depois da remoção do IQAr consolidado
- `reports/modeling/baseline_threshold_tradeoff_by_inner_fold.csv` e `baseline_threshold_tradeoff_summary.csv`, com a varredura de 101 limiares em validações temporais internas anteriores aos folds externos

**Investigação dos erros:** o fold 2024-Q3 concentrou mais falsos positivos nos modelos Naive Bayes. O grupo de subíndices/IQAr teve 224 FP em Q3 e o grupo combinado 260; setembro/2024 foi o mês com mais FP para ambos (133 e 147, respectivamente). No grupo de subíndices, 181 dos 476 FP ocorreram entre 18h e 21h. Esses são totais de erros, não taxas por hora/mês; a distribuição desigual de observações e de positivos impede interpretá-los como risco relativo sem denominadores.

Como verificação por fold, a taxa de falso positivo (FP / negativos da validação) do Gaussian Naive Bayes com subíndices foi 5,7%, 2,5%, 11,0% e 3,7% em Q1, Q2, Q3 e Q4, respectivamente; no grupo combinado foi 6,4%, 2,9%, 12,8% e 3,8%. O trimestre Q3 se destaca mesmo usando o número de negativos como denominador, indicando que vale examinar mudança temporal e condições desse período nos próximos experimentos.

Dentro do Q3, a taxa de falso positivo do grupo de subíndices aumentou de 6,8% em julho e 6,1% em agosto para 21,2% em setembro. No grupo combinado, passou de 7,1% e 8,9% para 23,4%. As taxas usam os negativos de cada mês como denominador. No grupo de subíndices, 206 de 224 erros FP ocorreram em sequências de pelo menos duas horas incorretas; a sequência mais longa teve 21 horas. No grupo combinado, foram 251 de 260, com máximo de 19 horas. Portanto, essas contagens representam episódios temporalmente correlacionados, não centenas de erros independentes.

No grupo de subíndices, entre negativos da validação Q3, as medianas de IQAr em *t* foram 76,23 nos falsos positivos e 30,15 nos negativos corretamente classificados; para `iqar_ozone`, 72,67 e 25,95; para ozônio bruto, 111,5 e 62 µg/m³. Ou seja, os falsos positivos tendem a ocorrer quando algumas features em *t* estão elevadas, mas o evento rotulado em *t+1h* continua negativo. Isso descreve o que o classificador viu; não demonstra erro nos dados nem relação causal.

Dos 476 falsos positivos do Naive Bayes com subíndices/IQAr nos quatro folds, 409 ocorreram quando a persistência pelo IQAr atual previa classe 0 (IQAr em *t* <= 100). Em contrapartida, os 114 falsos negativos do Naive Bayes com poluentes brutos foram todos identificados como positivos pela regra de persistência. O achado é compatível com o valor adicional do IQAr em *t* para capturar o estado atual, mas não prova causa nem decide uma regra híbrida.

**Resultado da ablação controlada:** a variante somente de subíndices reduziu FP em 74 (15,5%) nos quatro folds, mas aumentou FN de 1 para 3. No Q3, caiu de 224 para 216 FP e aumentou de 1 para 2 FN; a taxa de setembro permaneceu em 21,2% (133 FP). Na variante combinada, os FP aumentaram de 537 para 542 no agregado e de 260 para 280 no Q3; em setembro, a taxa foi de 25,0% (157 FP), ante 23,4% (147 FP) com `iqar`. Portanto, remover a feature consolidada ajudou no agregado apenas no grupo somente de subíndices, mas não resolveu a elevação de setembro e piorou o grupo combinado. A relação entre o `iqar` consolidado e os erros depende do grupo, e o Naive Bayes pode ser sensível às dependências entre variáveis. Nenhuma das variantes foi escolhida como modelo final; não houve ajuste de limiar e o holdout permanece fechado.

**Critério de alertas definido pela equipe:** evitar falsos negativos, aceitando a possibilidade de emitir mais falsos alertas; uma hora prevista como negativa encerra o episódio e o teto é de três episódios iniciados por semana. Um episódio que atravessa a virada da semana é contado somente na semana em que começou. Ainda falta decidir se será definido um teto de horas de alerta por semana. Para contar episódios previstos, horas positivas consecutivas são agrupadas em um alerta. As comparações reportam recall/taxa de falsos negativos, precisão, contagem/taxa de falsos positivos, horas de alerta, número de episódios e estabilidade entre folds. Se houver ajuste de limiar, ele deverá ocorrer em validações temporais internas aos dados de treino de cada fold; nunca se escolhe o limiar pelo resultado do próprio fold externo ou do holdout.

**Trade-off preliminar de limiares:** para cada fold externo de 2024, foi usado como validação interna o trimestre imediatamente anterior (2023-Q4 para 2024-Q1 e Q1, Q2 e Q3/2024 para os folds seguintes). Cada modelo foi ajustado apenas nos dados anteriores a essa janela; nela foram avaliados limiares de 0,00 a 1,00, em passos de 0,01. As quatro janelas internas somam 8.784 horas, com 8.340 negativos e 444 positivos. Como exemplo, no grupo de subíndices sem `iqar`, o limiar 0,50 resultou em recall agregado de 0,9925 (4 FN), 428 FP, 868 horas previstas como alerta e 141 episódios (98,8 horas e 16,1 episódios por mil horas); o limiar 0,25 resultou em recall 0,9971 (2 FN), 543 FP, 985 horas de alerta e 146 episódios (112,1 horas e 16,6 episódios por mil horas). Ao reunir todas as janelas antes de agrupar episódios por semana, ambos os cenários ultrapassaram o teto de três episódios em 21 das 52 semanas completas: máximo de sete (0,50) e seis (0,25). As cargas máximas foram 85 e 90 horas de alerta por semana, respectivamente. Nenhum limiar entre 0,01 e 0,99 atendeu ao teto em todas as semanas. O limiar 0,00 alertou em todas as 8.784 horas (8.340 FP); o limiar 1,00 teve 384 FN. Portanto, o teto de episódios precisa ser considerado junto da duração/carga de alertas e da prioridade de evitar falsos negativos. São cenários exploratórios, não uma recomendação: nenhum limiar foi selecionado, as métricas contam episódios previstos (não acertos na detecção de episódios reais) e o holdout segue reservado. A métrica de cada janela não foi usada para avaliar o próprio fold externo correspondente.

**Evidências:**
Script reproduzível: `python -m src.modelagem.Avaliar_Baselines`. Os CSVs acima registram as métricas por classe, matrizes de confusão, ablação e trade-off preliminar de limiares.

---

## 4. Scrum

As atualizações da sprint devem registrar o andamento das atividades, dificuldades encontradas e decisões tomadas ao longo do período.

O board da equipe deverá refletir o estado real das tarefas realizadas durante a Sprint 3.

**Status:** Entregas técnicas concluídas em 09/10/2026. Permanecem pendentes apenas a atualização do board e o preenchimento das retrospectivas individuais pela equipe.

---

## 5. Diário de bordo (retrospectiva individual)

|| Integrante                  | O que fiz nesta Sprint       | Dificuldades | O que pretendo manter/ajustar |
|| --------------------------- | ---------------------------- | ------------ | ----------------------------- |
|| Davi Gama dos Santos        | A preencher pelo integrante. | A preencher. | A preencher.                  |
|| Diogo Gomes Barbosa         | A preencher pelo integrante. | A preencher. | A preencher.                  |
|| Eudenis de Souza Vieira     | A preencher pelo integrante. | A preencher. | A preencher.                  |
|| Gabriel Januário Alves      | A preencher pelo integrante. | A preencher. | A preencher.                  |
|| João Pedro Barreto da Silva | A preencher pelo integrante. | A preencher. | A preencher.                  |

---

## Conclusão da Sprint 3

A Sprint 3 estabeleceu os primeiros baselines a partir dos artefatos da Sprint 2, preservando o split temporal e o holdout. A comparação dos grupos de features, a análise de erros, a ablação do `iqar` e a varredura interna de limiares servem de evidência para orientar a engenharia de atributos da Sprint 4; não selecionam um modelo ou limiar final.

**Fechamento técnico atualizado em 09/10/2026:** as entregas de ingestão e modelagem previstas foram executadas e documentadas. O resumo semanal foi regenerado após unir as janelas internas antes de contar episódios, evitando reiniciar episódios nas fronteiras entre janelas. No grupo de subíndices sem `iqar`, os limiares ilustrativos 0,25 e 0,50 ultrapassaram o teto acordado de três episódios em 21 das 52 semanas completas; nenhum limiar de 0,01 a 0,99 respeitou o teto em todas as semanas. A equipe optou por não definir agora um limite adicional de horas de alerta: a carga semanal será reportada para apoiar decisões futuras. Nenhum limiar foi selecionado, e o holdout 2025–2026 permanece reservado.

- ✅ Ingestão e dados preparados para a modelagem disponíveis
- ✅ Split temporal implementado
- ✅ Variável-alvo formalizada e calculada
- ✅ EDA gráfica e triagem de extremos concluídas somente no desenvolvimento
- ✅ Três grupos de features comparados nos mesmos folds de 2024
- ✅ Dummy, persistência e Gaussian Naive Bayes executados e documentados
- ✅ Erros out-of-fold examinados por trimestre, mês, hora e features em t
- ✅ Ablação do `iqar` consolidado comparada nos mesmos quatro folds, sem ajuste de limiar
- ✅ Trade-off de 101 limiares examinado nas janelas temporais internas, sem selecionar limiar final
- ✅ Agrupamento semanal de episódios validado e relatórios atualizados
- ✅ Critério operacional registrado: até três episódios iniciados por semana; sem teto adicional de horas por enquanto
- ✅ Holdout 2025–2026 mantido reservado; nenhuma avaliação final realizada
- ⏳ Board da sprint e retrospectivas individuais aguardam atualização pela equipe

**Próximos passos:**
1. Atualizar o board e preencher as retrospectivas individuais para concluir os registros Scrum da Sprint 3.
2. Iniciar a Sprint 4 com as hipóteses de engenharia de atributos motivadas pelos erros e pela carga semanal aqui documentados; preservar o split da Sprint 2 e não selecionar limiar nesta etapa.
3. Manter 2025–2026 reservado até congelar pipeline e decisões; avaliar o holdout uma única vez ao final.
