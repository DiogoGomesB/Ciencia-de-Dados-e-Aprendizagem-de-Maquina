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
| Como será definida a classe positiva? | Classe 0: IQAr <= 100. Classe 1: IQAr > 100. O IQAr será o maior subíndice CETESB entre os seis poluentes, calculados nas janelas de exposição da Tabela 2.7. Se faltar algum valor necessário nas janelas que terminam em t+1h, o rótulo será indefinido e a linha ficará fora da modelagem. |
| Qual é o horizonte da previsão? |1 hora à frente. |
| Qual é a unidade de análise (o que representa cada linha do dataset)?  |Cada linha representa uma observação horária do ponto geográfico de referência da Universidade Braz Cubas, contendo dados de qualidade do ar e variáveis meteorológicas correspondentes àquele horário. |

---

## 4. Escopo

| Pergunta | Resposta |
|---|---|
| Recorte geográfico (cidade/região) ou cultura e municípios (Trilha C) |O projeto será delimitado ao município de Mogi das Cruzes/SP, utilizando como referência um único ponto geográfico localizado na Universidade Braz Cubas, nas coordenadas aproximadas de latitude -23.514561 e longitude -46.186832. O ponto será utilizado como referência para as observações e não terá como objetivo representar toda a cidade.|
| Período histórico considerado |**04/08/2022 a 31/08/2026.** O período de janeiro/2025 foi preservado como teste inicial. Em 08/10/2026, as duas APIs foram coletadas para o intervalo ampliado: 35.736 horários por fonte, sem valores ausentes e com timestamps alinhados; os arquivos foram persistidos em nomes separados pelo intervalo. Em agosto/2022, a qualidade do ar começou a retornar valores em 03/08 às 21h; 04/08 foi o primeiro dia completo observado. Datas de referência anteriores retornaram horários sem valores de poluentes.|
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

O projeto utilizará duas fontes principais da Open-Meteo, consultadas para o período de **04/08/2022 a 31/08/2026**. A primeira fornece dados horários relacionados à qualidade do ar e à concentração de poluentes. A segunda fornece dados meteorológicos horários que serão utilizados para caracterizar as condições atmosféricas associadas às observações.

| Fonte | O que fornece | Papel no projeto (feature / alvo / ambos) |
|---|---|---|
|Open-Meteo Air Quality API |Dados horários de qualidade do ar, incluindo concentrações de poluentes como PM10, PM2.5, monóxido de carbono, dióxido de nitrogênio, dióxido de enxofre e ozônio.|Features e base para definição do alvo|
|Open-Meteo Weather API |Dados meteorológicos horários, como temperatura, umidade relativa, precipitação, velocidade do vento e pressão atmosférica. |Features|

### Definição operacional do alvo

O relatório CETESB de 2025 define o índice de cada poluente por interpolação linear e o IQAr consolidado como o maior subíndice. Para o alvo em t+1h, cada concentração será calculada na janela móvel que termina nesse horário: 24h para PM10, PM2,5 e SO2; 8h para O3 e CO; e 1h para NO2. Como a API fornece CO em µg/m³ e a tabela CETESB usa ppm, a conversão segue a lei dos gases ideais a 25 °C e 1 atm. Se faltar algum valor necessário em qualquer janela, o IQAr e o rótulo não são imputados. O critério positivo continua sendo IQAr > 100.

Metodologia: CETESB (2025), seção 2.3 e Tabela 2.7, pp. 18–20 ([relatório oficial](https://www.cetesb.sp.gov.br/dx/api/dam/v1/collections/186909e9-ab59-4641-abba-c5c465793216/items/3adb602d-77ec-4de5-b378-5fa141e80614/renditions/5a0e5f05-41aa-4e9c-9b00-69165ab36963/versions/1?binary=true)).

*Link para o dicionário de dados do projeto: [docs/Dicionario_de_Dados.md](Dicionario_de_Dados.md)*

---

## 7. Custo dos erros

| Tipo de erro | O que significa no contexto do projeto | Custo/consequência |
|---|---|---|
| Falso negativo |O modelo prevê que a qualidade do ar estará adequada, mas uma hora depois a condição é inadequada. |Pode deixar de identificar antecipadamente uma possível piora da qualidade do ar, reduzindo a utilidade do alerta e dificultando uma ação preventiva. |
| Falso positivo |O modelo prevê que a qualidade do ar estará inadequada, mas uma hora depois a condição permanece adequada. |Pode gerar um alerta desnecessário, causando preocupação ou ações que não seriam necessárias. |

Qual erro é mais grave para este problema, e por quê? Isso orienta a métrica da classe positiva (em geral recall) *e o limiar de decisão da Sprint 5* — o modelo devolve probabilidade; o ponto de corte é decisão de produto.

**Prioridade confirmada pela equipe:** evitar falsos negativos, aceitando a possibilidade de mais falsos alertas. Por esse motivo, a avaliação dará atenção especial ao recall e à taxa de falsos negativos da classe positiva, sem deixar de reportar precisão, falsos positivos e a carga de alertas resultante. Para contagem operacional exploratória, horas positivas consecutivas formam um episódio de alerta; uma hora prevista como negativa encerra o episódio. A equipe definiu como critério de carga no máximo três episódios iniciados por semana; um episódio que atravessa a virada da semana é contado somente na semana em que começou. Ainda falta decidir se haverá também um teto de horas de alerta por semana. Nenhum modelo ou limiar final foi selecionado. A escolha futura de limiar deverá usar somente dados de treino/validação interna temporal; o fold externo correspondente e o holdout não podem participar dessa seleção.

Uma análise exploratória de 101 limiares em janelas internas anteriores aos folds externos foi executada e documentada no relatório de desenvolvimento. Para o grupo de subíndices sem `iqar`, nenhum limiar entre 0,01 e 0,99 respeitou o teto de três episódios em todas as semanas observadas. Os cenários ilustrativos 0,25 e 0,50 excederam o teto em 21 das 52 semanas completas, com máximos de seis e sete episódios, respectivamente. Os extremos da varredura não são soluções operacionais: em 0,00, o modelo alertou por todas as 8.784 horas (8.340 falsos positivos); em 1,00, deixou de detectar 384 dos 444 positivos. Portanto, o critério semanal precisa ser avaliado em conjunto com a carga em horas e a prioridade de evitar falsos negativos; esses resultados não selecionam um limiar.

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

Não foi fixado um valor mínimo numérico de desempenho antes dos experimentos. Na Sprint 5, a escolha foi feita na validação temporal priorizando a redução de falsos negativos e respeitando o critério semanal de episódios; a avaliação final reporta também que uma semana do holdout excedeu esse teto.

---

## 11. Alternativas consideradas (opcional)

Não preenchido nesta versão.

---

## 12. Perguntas de pesquisa e decisões respondidas

As perguntas abaixo foram registradas no planejamento e respondidas progressivamente nas Sprints 2–5.

~~Qual será o período histórico final utilizado?~~ **Respondida:** 04/08/2022 a 31/08/2026; coletado, integrado e rotulado em arquivos próprios em 08/10/2026, preservando os arquivos de janeiro/2025.
~~Qual será a definição da classe positiva?~~ **Respondida:** classe 1 quando IQAr > 100; classe 0 quando IQAr <= 100. O IQAr é o maior subíndice CETESB entre os seis poluentes, com as janelas de exposição da Tabela 2.7, e o alvo de t+1h usa janelas terminando nesse horário. CO é convertido de µg/m³ para ppm a 25 °C e 1 atm. Se faltar algum valor necessário nas janelas, o rótulo ficará indefinido e a observação não será usada na modelagem.
~~Como ficará a distribuição entre as classes 0 e 1 após a definição do alvo?~~ **Respondida:** no período completo, 904 positivos e 34.809 negativos entre 35.713 rótulos definidos (2,53% positivos). A prevalência varia por ano (4,41% em 2024; 1,24% em 2025; 0,89% em 2026), reforçando a necessidade de avaliação temporal.
~~Qual estratégia de split e validação será utilizada?~~ **Respondida:** folds expansivos por trimestre em 2024; treino em cada fold usa apenas rótulos anteriores ao trimestre validado, com a validação anterior incorporada nos folds seguintes. O holdout temporal final abrange 2025 a 2026. Antes de fixar o split, a série completa foi examinada descritivamente (taxas e médias por classe); não houve ajuste/avaliação de modelo ou limiar, mas o holdout não é totalmente cego. A partir da decisão, ele não será usado para seleção. As partições usam o horário do evento previsto (`time + 1h`), evitando atribuir ao treino um rótulo cujo evento pertence à validação/teste. Os limites estão em `config/params.yaml` e a implementação em `src/validacao/Separacao_Temporal.py`.
~~Quais variáveis e características apresentam maior associação inicial com o alvo?~~ **Respondida inicialmente:** no desenvolvimento, Spearman foi maior para `iqar_ozone` e `iqar` (0,317), ozônio bruto (0,297), `iqar_pm2_5` (0,215) e PM2,5 (0,211). Os índices em *t* são candidatos disponíveis na previsão, mas as associações podem refletir janelas sobrepostas; não são causais nem substituem comparação nos folds.
~~Como comparar variáveis brutas com os subíndices derivados?~~ **Respondida (09/10/2026):** comparar nos mesmos folds temporais três conjuntos candidatos: seis poluentes brutos + cinco variáveis meteorológicas; seis subíndices e o `iqar` consolidado + as mesmas variáveis meteorológicas; e a combinação dos dois grupos de qualidade do ar + meteorologia. Os subíndices e `iqar` são calculados até *t*. A comparação formal da Sprint 3 com a Sprint 4 registrou a escolha do conjunto S4 e seus trade-offs em `docs/sprints/Sprint4_TrilhaB.md`.
**Resultado preliminar dos baselines (09/10/2026):** nos quatro folds de 2024, a persistência (classe do IQAr em *t*) obteve F1 médio 0,8196; Gaussian Naive Bayes obteve F1 médio 0,4134 com poluentes brutos, 0,6175 com subíndices/IQAr e 0,5914 com ambos. O modelo de subíndices/IQAr teve recall médio 0,9985, mas gerou 476 falsos positivos agregados. O Dummy prior previu sempre a classe negativa. As taxas de falso positivo do Naive Bayes com subíndices foram 5,7%, 2,5%, 11,0% e 3,7% nos quatro trimestres, com maior incidência em Q3. Os 114 falsos negativos do modelo com poluentes brutos foram todos positivos segundo a persistência em IQAr(t), o que evidencia complementaridade entre as referências, mas não determina regra combinada. Essas métricas são referências descritivas da Sprint 3; naquele estágio, nenhum limiar final havia sido escolhido e o holdout ainda não havia sido avaliado.
~~Será necessário utilizar janelas ou defasagens temporais para melhorar a representação das condições anteriores?~~ **Respondida na Sprint 4:** foram adicionadas médias móveis de 3 horas e deltas de 2 horas para ozônio e PM2,5, usando medições disponíveis até *t*. O protocolo temporal e as limitações estão registrados em `docs/sprints/Sprint4_TrilhaB.md`.
~~Quais características poderão ser utilizadas sem causar vazamento de informações futuras?~~ **Respondida:** o conjunto S4 usa variáveis disponíveis até *t* para prever o evento em *t+1h*; imputação e padronização são ajustadas dentro do treino. A lista congelada e o pipeline estão registrados em `docs/sprints/Sprint4_TrilhaB.md`.
~~Quais abordagens de modelagem apresentarão melhor desempenho e qual será o ganho obtido em relação aos modelos de referência?~~ **Respondida na Sprint 5:** a equipe congelou Random Forest balanceada com limiar 0,3 com base na validação temporal de 2024-Q4. No teste temporal final, avaliado uma única vez após congelar a escolha, obteve recall 0,9814, precisão 0,7822 e F1 0,8705 (158 TP, 44 FP, 3 FN, 14.387 TN). Uma das 86 semanas completas excedeu o teto de três episódios, com máximo de cinco episódios e 31 horas de alerta. A regressão logística padrão teve recall e F1 maiores no mesmo holdout, mas não substituiu a escolha congelada; o teste não foi reutilizado para seleção ou ajuste. Resultados, limitações e artefato estão documentados em `docs/sprints/Sprint5_TrilhaB.md`.

As perguntas de planejamento acima foram respondidas; pendências operacionais de equipe e integração opcional com banco de dados não alteram os resultados experimentais registrados.

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
| v0.3 |08/10/2026 | Equipe | Cobertura das APIs validada para 04/08/2022–31/08/2026; classe positiva definida como IQAr > 100 e política para alvos ausentes registrada. |
| v0.4 |08/10/2026 | Equipe | Metodologia CETESB, janelas, conversão de CO e alvo aplicados ao período ampliado; distribuição por classe documentada. |
| v0.5 |08/10/2026 | Equipe | EDA inicial e estratégia de validação temporal/teste final definidas e implementadas. |
| v0.4 |08/10/2026 | Equipe | Metodologia CETESB 2025 conferida; janelas de exposição, conversão de CO e cálculo do alvo em t+1h definidos e implementados. |
| v0.6 |09/10/2026 | Equipe | EDA gráfica no desenvolvimento e protocolo aprovado para comparar os grupos de features. |
| v0.7 |09/10/2026 | Equipe | Primeiros baselines e análise out-of-fold dos erros registrados; holdout não avaliado. |
| v0.6 |09/10/2026 | Equipe | EDA gráfica no desenvolvimento concluída e protocolo de comparação dos grupos de features aprovado. |
| v0.5 |08/10/2026 | Equipe | Período ampliado coletado, integrado e rotulado em arquivos próprios, preservando os dados de teste de janeiro/2025. |
| v0.8 | Sprint 4 | Equipe | Conjunto de features temporais comparado e congelado; resultados e trade-offs documentados. |
| v0.9 | Sprint 5 | Equipe | Seleção pré-teste, avaliação única do holdout e pipeline final documentados. |
