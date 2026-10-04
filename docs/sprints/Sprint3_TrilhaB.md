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

**Status:** Pendente - aguardando conclusão da Sprint 2.

---

## 2. Preparação para modelagem

A modelagem desta sprint deverá utilizar **o mesmo split temporal definido na Sprint 2** e as **mesmas features disponibilizadas nessa sprint**, sem criação de um novo split aleatório.

O pré-processamento deverá ser realizado dentro de um `Pipeline` do scikit-learn, utilizando um `ColumnTransformer` em conjunto com o classificador. O ajuste (`fit`) das transformações deverá ocorrer somente utilizando os dados de treino.

Imputação residual, normalização ou outras transformações necessárias deverão permanecer dentro do pipeline, evitando o ajuste de transformações utilizando informações do conjunto de teste.

Também deverá ser reconfirmada a ausência de vazamento nas features temporais já construídas na Sprint 2.

**Descrição da estratégia de split e do ColumnTransformer:**
Pendente - aguardando conclusão da Sprint 2 (split temporal e features ainda não definidos).

---

## 3. Modelagem baseline

A Sprint 3 terá como objetivo estabelecer referências iniciais de desempenho utilizando três abordagens:

1. **DummyClassifier**, representando um baseline simples baseado na classe majoritária;
2. **Persistência temporal**, utilizando a informação disponível no instante da previsão como referência para o próximo estado;
3. **Naive Bayes**, treinado no mesmo split e utilizando as mesmas features dos demais baselines.

Os três baselines deverão ser avaliados utilizando o mesmo conjunto de treino e teste, permitindo uma comparação consistente.

Serão analisadas métricas como **recall, precisão, F1 e matriz de confusão para cada classe**, com atenção especial à classe positiva, devido ao maior custo associado aos falsos negativos definido na RFC.

O Naive Bayes será tratado como um baseline pedagógico. Sua hipótese de independência condicional pode não representar adequadamente a relação entre variáveis de qualidade do ar e meteorológicas, que podem apresentar correlação entre si. Dessa forma, o objetivo nesta etapa é estabelecer uma referência de desempenho, e não assumir que o modelo represente uma relação física entre os fenômenos.

Nesta sprint não será realizado ajuste fino do limiar de decisão. Será utilizado o comportamento padrão dos modelos, deixando a definição de limiar como etapa posterior do projeto.

Também não será utilizado SMOTE ou oversampling aleatório, considerando a natureza temporal dos dados.

**Resultados (Dummy vs. persistência vs. Naive Bayes):**
Pendente - aguardando conclusão da Sprint 2.

**Evidências:**
Pendente - aguardando conclusão da Sprint 2.

---

## 4. Scrum

As atualizações da sprint devem registrar o andamento das atividades, dificuldades encontradas e decisões tomadas ao longo do período.

O board da equipe deverá refletir o estado real das tarefas realizadas durante a Sprint 3.

**Status:** Pendente.

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

A Sprint 3 tem como foco fortalecer a ingestão dos dados e estabelecer os primeiros baselines de modelagem utilizando os artefatos definidos na Sprint 2. Os experimentos deverão manter o mesmo split temporal e as mesmas features iniciais, permitindo que os resultados obtidos sirvam como referência para a evolução das features e dos modelos nas próximas sprints.

**Status atual:** A Sprint 3 **não pode ser iniciada** até que a Sprint 2 seja completada. Os artefatos necessários ainda não foram criados:
- ❌ Split temporal não definido
- ❌ Variável-alvo não formalizada
- ❌ Features iniciais não criadas
- ❌ EDA não realizada

**Próximos passos:**
1. Completar a Sprint 2 (split, EDA, alvo, features)
2. Atualizar o dicionário de dados para v0.2
3. Iniciar a Sprint 3 após conclusão da Sprint 2
