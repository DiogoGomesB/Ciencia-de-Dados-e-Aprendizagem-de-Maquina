# RFC: Proposta de Projeto

| Campo | Valor |
|---|---|
| **Título** | Previsão da Qualidade do Ar Inadequada em Na Região da Faculdade UBC |
| **Trilha** | B — Qualidade do ar inadequada |
| **Equipe** | Davi Gama dos Santos - 33121079, Diogo Gomes Barbosa	- 35866276, Eudenis de Souza Vieira - 32751621, Gabriel Januário Alves - 35609991, João Pedro Barreto da Silva - 33297185 |
| **Autores** | Davi Gama dos Santos, Diogo Gomes Barbosa, Eudenis de Souza Vieira, Gabriel Januário Alves e João Pedro Barreto da Silva |
| **Status** | Em revisão |
| **Data** | 15/09/2026 |
| **Sprint de referência** | 1 |

> Um RFC ("Request for Comments") é um documento curto que formaliza uma proposta antes de ela ser executada, para que o time (e quem revisa) concorde com o problema e o escopo antes de investir tempo em código. Aqui, ele reúne o canvas de kickoff numa proposta legível por alguém de fora do grupo. Algoritmo (Random Forest, XGBoost, etc.) **não** se escolhe neste documento.

---

## 1. Resumo (TL;DR)

O projeto prevê a qualidade do ar no ponto de referência da Universidade Braz Cubas, em Mogi das Cruzes/SP, com horizonte de uma hora à frente. 
A proposta é voltada principalmente ao contexto acadêmico, demonstrando como dados de qualidade do ar e meteorológicos podem ser utilizados para antecipar situações de qualidade do ar inadequada. 
O objetivo é identificar possíveis episódios de piora com antecedência, contribuindo para o acompanhamento e prevenção de impactos relacionados à qualidade do ar.

---

## 2. Contexto e motivação

A qualidade do ar é um fator relevante para o meio ambiente e para a saúde pública, pois a presença de determinados poluentes pode estar associada à piora das condições atmosféricas. A previsão de uma hora à frente pretende apoiar a identificação antecipada de possíveis situações de qualidade do ar inadequada no ponto de referência da Universidade Braz Cubas, em Mogi das Cruzes/SP. Dessa forma, o projeto busca demonstrar como dados de qualidade do ar e condições meteorológicas podem ser utilizados para acompanhar e antecipar episódios de piora da qualidade do ar.

---

## 3. Problema e evento a ser previsto

| Pergunta | Resposta |
|---|---|
| Qual evento será previsto? Prever se a qualidade do ar no ponto de referência da Universidade Braz Cubas, em Mogi das Cruzes/SP, estará inadequada uma hora à frente. | |
| Como será definida a classe positiva? *(provisória na Sprint 1; limiar formal na Sprint 2, com base no treino)* Classe 1: qualidade do ar inadequada. Classe 0: qualidade do ar adequada. O limiar que determinará formalmente quando a qualidade do ar será considerada inadequada será definido na Sprint 2, após a análise e preparação dos dados. | |
| Qual é o horizonte da previsão? 1 hora à frente. | |
| Qual é a unidade de análise (o que representa cada linha do dataset)? Cada linha representa uma observação horária do ponto geográfico de referência da Universidade Braz Cubas, contendo dados de qualidade do ar e variáveis meteorológicas correspondentes àquele horário. | |

---

## 4. Escopo

| Pergunta | Resposta |
|---|---|
| Recorte geográfico (cidade/região) ou cultura e municípios (Trilha C) | |
| Período histórico considerado | |
| O que está **dentro** do escopo deste projeto | |
| O que está **fora** de escopo (explicitamente não será feito) | |

> Trilha C: **uma única cultura** e municípios de escala comparável. Declarar também o N esperado (municípios × safras): a produtividade do IBGE é em geral anual; N pequeno limita modelos complexos.

---

## 5. Usuários e decisão apoiada

Quem usaria o alerta gerado por este projeto? Que decisão concreta essa pessoa/instituição tomaria com base nele?

---

## 6. Dados e fontes

Resumo de alto nível. O detalhe (unidade, resolução, medido vs. modelado, códigos IBGE) vai no `Dicionário de Dados`.

| Fonte | O que fornece | Papel no projeto (feature / alvo / ambos) |
|---|---|---|
| | | |
| | | |

**Link para o dicionário de dados do projeto:**

---

## 7. Custo dos erros

| Tipo de erro | O que significa no contexto do projeto | Custo/consequência |
|---|---|---|
| Falso negativo | | |
| Falso positivo | | |

Qual erro é mais grave para este problema, e por quê? Isso orienta a métrica da classe positiva (em geral recall) **e o limiar de decisão da Sprint 5** — o modelo devolve probabilidade; o ponto de corte é decisão de produto.

---

## 8. Abordagem proposta (visão de alto nível)

Caminho planejado, sem escolher algoritmo:

**ingestão bruta (Pipeline CD)** → integração do cru → **limpeza e tratamento** → **split** → imputação residual só no treino (se houver) → EDA **no treino já tratado** → alvo formal → features sem vazamento → **um `Pipeline` sklearn** (pré-processamento + classificador) → baselines → iteração de features com retreino → modelos + **limiar escolhido na validação** (teste uma vez) → model card + artefato (`joblib` do Pipeline).

Dashboard de visualização, se houver na mostra final, é extra: não há sprint numerada de deploy neste projeto.

---

## 9. Riscos e limitações conhecidas

- (ex.: dados modelados em vez de medidos, série histórica curta, N pequeno na Trilha C, desbalanceamento, API instável)

---

## 10. Critérios de sucesso

Como o grupo vai saber, ao final, que a solução é útil? (ex.: recall mínimo na classe positiva **no teste**, no limiar escolhido; model card preenchido; dicionário alinhado ao modelo)

---

## 11. Alternativas consideradas *(opcional)*

Outras definições de problema, recorte ou fonte que o grupo avaliou e descartou, com o motivo.

---

## 12. Perguntas em aberto

Pontos que dependem da EDA da Sprint 2 (limiar do alvo, janelas) ou do lift da Sprint 4.

---

## 13. Cronograma e contrato entre sprints

| Sprint | Período | Produz (sai) | A próxima sprint é obrigada a usar |
|---|---|---|---|
| 1 | 17/08/2026 – 17/09/2026 | RFC v0.1, dicionário v0.1, `data/raw`, `config`, N do merge | O bruto desta coleta |
| 2 | 18/09/2026 – 27/09/2026 | `data/interim`, split, alvo, features iniciais, dicionário v0.2 | Split, alvo e features daqui |
| 3 | 28/09/2026 – 04/10/2026 | Transformer inicial, Dummy + persistência + NB, erros | Os erros (para features novas) e o mesmo split |
| 4 | 05/10/2026 – 11/10/2026 | Features novas, transformer congelado, lift S3→S4, dicionário v0.3 | Este transformer e estes baselines retreinados |
| 5 | 12/10/2026 – 25/10/2026 | Comparativo final, limiar **na validação**, caderno, model card, dicionário v0.4, `joblib` do Pipeline | — (entrega final) |

---

## 14. Histórico de revisões

| Versão | Data | Autor | O que mudou |
|---|---|---|---|
| v0.1 | | | Primeira versão do RFC (Sprint 1) |
| | | | |
