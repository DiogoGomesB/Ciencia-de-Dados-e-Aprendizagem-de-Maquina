| Campo | Valor |
|---|---|
| *Título* | Previsão da Qualidade do Ar Inadequada em Na Região da Faculdade UBC |
| *Trilha* | B — Qualidade do ar inadequada |
| *Equipe* | Davi Gama dos Santos - 33121079, Diogo Gomes Barbosa	- 35866276, Eudenis de Souza Vieira - 32751621, Gabriel Januário Alves - 35609991, João Pedro Barreto da Silva - 33297185 |
| *Autores* | Davi Gama dos Santos, Diogo Gomes Barbosa, Eudenis de Souza Vieira, Gabriel Januário Alves e João Pedro Barreto da Silva |
| *Status* | Em revisão |
| *Data* | 15/09/2026 |
| *Sprint de referência* | 1 |

> Um RFC ("Request for Comments") é um documento curto que formaliza uma proposta antes de ela ser executada, para que o time (e quem revisa) concorde com o problema e o escopo antes de investir tempo em código. Aqui, ele reúne o canvas de kickoff numa proposta legível por alguém de fora do grupo. Algoritmo (Random Forest, XGBoost, etc.) *não* se escolhe neste documento.

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
| Qual evento será previsto? |Prever se a qualidade do ar no ponto de referência da Universidade Braz Cubas, em Mogi das Cruzes/SP, estará inadequada uma hora à frente. |
| Como será definida a classe positiva?  |(provisória na Sprint 1; limiar formal na Sprint 2, com base no treino) Classe 1: qualidade do ar inadequada. Classe 0: qualidade do ar adequada. O limiar que determinará formalmente quando a qualidade do ar será considerada inadequada será definido na Sprint 2, após a análise e preparação dos dados. |
| Qual é o horizonte da previsão? |1 hora à frente. |
| Qual é a unidade de análise (o que representa cada linha do dataset)?  |Cada linha representa uma observação horária do ponto geográfico de referência da Universidade Braz Cubas, contendo dados de qualidade do ar e variáveis meteorológicas correspondentes àquele horário. |

---

## 4. Escopo

| Pergunta | Resposta |
|---|---|
| Recorte geográfico (cidade/região) ou cultura e municípios (Trilha C) |O projeto será delimitado ao município de Mogi das Cruzes/SP, utilizando como referência um único ponto geográfico localizado na Universidade Braz Cubas, nas coordenadas aproximadas de latitude -23.514561 e longitude -46.186832. O ponto será utilizado como referência para as observações e não terá como objetivo representar toda a cidade.|
| Período histórico considerado |**31/08/2022 a 31/08/2026.** O período inicial (01/01/2025 a 31/01/2025) foi descartado por ser insuficiente como histórico. O novo intervalo foi definido pela cobertura da fonte mais restritiva: a Open-Meteo Air Quality API só oferece dado consistente para pontos fora da Europa (domínio CAMS Global) a partir de agosto/2022; a Historical Weather API cobre desde 1940 e não é o fator limitante. **Pendente:** validar empiricamente, antes da recoleta, que a Air Quality API retorna dado não nulo em todo o intervalo para as coordenadas do projeto.|
| O que está *dentro* do escopo deste projeto |Coleta e integração de dados de qualidade do ar e meteorológicos; organização e limpeza dos dados; análise da qualidade da base; definição da variável-alvo; criação de características para a previsão de uma hora à frente; desenvolvimento, treinamento e avaliação de modelos de classificação nas etapas posteriores do projeto.|
| O que está *fora* de escopo (explicitamente não será feito) |Representar a qualidade do ar de toda a cidade por meio de vários pontos de monitoramento; realizar previsões para outras cidades ou regiões; desenvolver um sistema de monitoramento em tempo real; criar um aplicativo ou serviço de produção para emissão de alertas; realizar implantação em ambiente produtivo.|

> Trilha C: *uma única cultura* e municípios de escala comparável. Declarar também o N esperado (municípios × safras): a produtividade do IBGE é em geral anual; N pequeno limita modelos complexos.

---

## 5. Usuários e decisão apoiada

Quem usaria o alerta gerado por este projeto? Que decisão concreta essa pessoa/instituição tomaria com base nele?
Em um possível cenário de utilização, o alerta poderia ser utilizado por instituições de ensino, órgãos públicos ou equipes responsáveis pelo acompanhamento ambiental e da qualidade do ar. A partir da previsão de uma possível condição inadequada para a próxima hora, esses usuários poderiam acompanhar a situação com maior atenção e avaliar a necessidade de comunicar ou orientar a população sobre a piora prevista.
No contexto deste projeto acadêmico, o alerta será utilizado principalmente para demonstrar a aplicação de Ciência de Dados e Aprendizagem de Máquina na previsão de qualidade do ar, não constituindo um sistema oficial de alerta à população.

---

## 6. Dados e fontes

O projeto utilizará duas fontes principais da Open-Meteo, ambas cobrindo o período de **31/08/2022 a 31/08/2026**. A primeira fornece dados horários relacionados à qualidade do ar e à concentração de poluentes. A segunda fornece dados meteorológicos horários que serão utilizados para caracterizar as condições atmosféricas associadas às observações.

| Fonte | O que fornece | Papel no projeto (feature / alvo / ambos) |
|---|---|---|
|Open-Meteo Air Quality API |Dados horários de qualidade do ar, incluindo concentrações de poluentes como PM10, PM2.5, monóxido de carbono, dióxido de nitrogênio, dióxido de enxofre e ozônio.|Features e base para definição do alvo|
|Open-Meteo Weather API |Dados meteorológicos horários, como temperatura, umidade relativa, precipitação, velocidade do vento e pressão atmosférica. |Features|

*Link para o dicionário de dados do projeto: a definir*

---

## 7. Custo dos erros

| Tipo de erro | O que significa no contexto do projeto | Custo/consequência |
|---|---|---|
| Falso negativo |O modelo prevê que a qualidade do ar estará adequada, mas uma hora depois a condição é inadequada. |Pode deixar de identificar antecipadamente uma possível piora da qualidade do ar, reduzindo a utilidade do alerta e dificultando uma ação preventiva. |
| Falso positivo |O modelo prevê que a qualidade do ar estará inadequada, mas uma hora depois a condição permanece adequada. |Pode gerar um alerta desnecessário, causando preocupação ou ações que não seriam necessárias. |

Qual erro é mais grave para este problema, e por quê? Isso orienta a métrica da classe positiva (em geral recall) *e o limiar de decisão da Sprint 5* — o modelo devolve probabilidade; o ponto de corte é decisão de produto.

Erro mais grave: o falso negativo, pois significa que o modelo não identificou uma situação de qualidade do ar inadequada que deveria ser antecipada. Por esse motivo, o projeto dará atenção especial ao recall da classe positiva (1) nas etapas de avaliação. O limiar de decisão será definido posteriormente, com base nos resultados da validação.

---

## 8. Abordagem proposta (visão de alto nível)

Caminho planejado, sem escolher algoritmo:

*ingestão bruta (Pipeline CD)* → integração do cru → *limpeza e tratamento* → *split* → imputação residual só no treino (se houver) → EDA *no treino já tratado* → alvo formal → features sem vazamento → *um Pipeline sklearn* (pré-processamento + classificador) → baselines → iteração de features com retreino → modelos + *limiar escolhido na validação* (teste uma vez) → model card + artefato (joblib do Pipeline).

Dashboard de visualização, se houver na mostra final, é extra: não há sprint numerada de deploy neste projeto.

O projeto seguirá um fluxo composto pela coleta e integração dos dados de qualidade do ar e meteorológicos, seguido pelas etapas de limpeza, análise, definição da variável-alvo, criação das características e desenvolvimento de modelos de classificação. As decisões relacionadas ao processamento dos dados, features, modelos e critérios de avaliação serão definidas e refinadas nas sprints seguintes, conforme os resultados das análises realizadas.

---

## 9. Riscos e limitações conhecidas

- Os dados utilizados pela API de qualidade do ar podem ser estimados por modelos atmosféricos, não representando necessariamente uma medição realizada exatamente no ponto da Universidade Braz Cubas.
- Para o ponto do projeto (fora da Europa), a Air Quality API usa o domínio CAMS Global, cuja resolução nativa do modelo é de 3 em 3 horas; os valores horários intermediários são interpolados pela própria API, não são observações independentes.
- O histórico de qualidade do ar só está disponível de forma consistente a partir de agosto/2022 para a região do projeto — isso já define o teto do período histórico utilizável, independentemente da cobertura mais longa da API de clima (desde 1940).
- O projeto utiliza um único ponto geográfico de referência, portanto os resultados não devem ser generalizados automaticamente para todo o município de Mogi das Cruzes.
- Podem existir dados ausentes, duplicados ou valores inconsistentes, que deverão ser identificados e tratados durante as etapas de preparação e análise.
- Existe a possibilidade de desbalanceamento entre as classes adequada e inadequada após a definição do limiar, o que será verificado nas etapas seguintes.
- A disponibilidade dos dados depende do funcionamento e da estabilidade das APIs utilizadas para a coleta.
- O histórico utilizado pode não representar todas as condições atmosféricas possíveis, limitando a capacidade de generalização dos resultados.

---

## 10. Critérios de sucesso

A solução será considerada útil ao final do projeto caso seja capaz de prever situações de qualidade do ar inadequada com desempenho satisfatório no conjunto de teste, dando atenção especial à capacidade de identificar corretamente a classe positiva.

Além do desempenho do modelo, serão considerados como critérios de sucesso:

    definição e justificativa da variável-alvo e do seu limiar;
    utilização de dados corretamente integrados, tratados e documentados;
    ausência de vazamento de informações futuras;
    avaliação do modelo por métricas adequadas, com atenção especial ao recall da classe positiva;
    documentação dos resultados, limitações e decisões tomadas;
    dicionário de dados atualizado e alinhado às variáveis utilizadas pelo modelo;
    preenchimento do model card e disponibilização do artefato final do pipeline.

O valor mínimo de desempenho esperado será definido nas etapas de validação, após a análise dos dados e dos resultados dos modelos de referência.

---

## 11. Alternativas consideradas (opcional)

Não preenchido nesta versão.

---

## 12. Perguntas em aberto

Pontos que dependem da EDA da Sprint 2 (limiar do alvo, janelas) ou do lift da Sprint 4.

~~Qual será o período histórico final utilizado, considerando a cobertura compatível das APIs e a qualidade dos dados disponíveis?~~ **Respondida (Sprint 1):** 31/08/2022 a 31/08/2026, limitado pela Air Quality API. Falta apenas a validação empírica de que não há lacunas de dado nulo nesse intervalo.
Qual será o limiar utilizado para definir a classe positiva, classificando a qualidade do ar como inadequada?
Quais variáveis e características apresentarão maior relação com a ocorrência de qualidade do ar inadequada?
Será necessário utilizar janelas ou defasagens temporais para melhorar a representação das condições anteriores?
Como ficará a distribuição entre as classes 0 e 1 após a definição do alvo?
Quais características poderão ser utilizadas sem causar vazamento de informações futuras?
Quais abordagens de modelagem apresentarão melhor desempenho e qual será o ganho obtido em relação aos modelos de referência?

Essas questões serão respondidas progressivamente nas sprints seguintes, principalmente a partir da análise exploratória dos dados, dos experimentos de modelagem e da comparação dos resultados.

---

## 13. Cronograma e contrato entre sprints

| Sprint | Período | Produz (sai) | A próxima sprint é obrigada a usar |
|---|---|---|---|
| 1 | 17/08/2026 – 17/09/2026 | RFC v0.1, dicionário v0.1, data/raw, config, N do merge | O bruto desta coleta |
| 2 | 18/09/2026 – 27/09/2026 | data/interim, split, alvo, features iniciais, dicionário v0.2 | Split, alvo e features daqui |
| 3 | 28/09/2026 – 04/10/2026 | Transformer inicial, Dummy + persistência + NB, erros | Os erros (para features novas) e o mesmo split |
| 4 | 05/10/2026 – 11/10/2026 | Features novas, transformer congelado, lift S3→S4, dicionário v0.3 | Este transformer e estes baselines retreinados |
| 5 | 12/10/2026 – 25/10/2026 | Comparativo final, limiar *na validação*, caderno, model card, dicionário v0.4, joblib do Pipeline | — (entrega final) |

---

## 14. Histórico de revisões

| Versão | Data | Autor | O que mudou |
|---|---|---|---|
| v0.1 |15/09/2026 | Diogo Gomes e Davi Gama | Primeira versão do RFC (Sprint 1) |
| v0.2 |14/09/2026 | Davi Gama e Diogo Gomes | Período histórico definido: 31/08/2022–31/08/2026 (seções 4, 6, 9, 12), substituindo o intervalo provisório de 01/01/2025–31/01/2025. |
