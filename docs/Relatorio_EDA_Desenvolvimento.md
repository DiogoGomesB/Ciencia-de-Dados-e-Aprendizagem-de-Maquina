# Relatório auxiliar — exploração dos dados de qualidade do ar

Este documento explica, em linguagem acessível, o objetivo do projeto, os dados usados, o que foi calculado na análise exploratória (EDA), o que os gráficos mostram e quais conclusões podem ou não ser tiradas. Também orienta uma pessoa que não participou do desenvolvimento a abrir a demonstração, executar o fluxo seguro e interpretar a saída. Foi escrito para leitores que não acompanharam as etapas anteriores.

## 1. Em poucas palavras: qual é o projeto?

O projeto investiga se é possível estimar, com uma hora de antecedência, se a qualidade do ar estará inadequada em um ponto de referência da região da Universidade Braz Cubas, em Mogi das Cruzes/SP. **Ele não é um sensor nem uma estação de medição:** usa séries históricas estimadas por modelos atmosféricos e de reanálise, disponibilizadas por APIs.

Para transformar essa pergunta em uma tarefa de ciência de dados, cada observação tem:

- **Informações disponíveis no instante `t`**: concentrações de poluentes e variáveis meteorológicas.
- **Um resultado a prever**: se o IQAr calculado para o evento em `t + 1 hora` será maior que 100.

O índice de qualidade do ar (IQAr) usado aqui segue a metodologia CETESB documentada para os seis poluentes. O projeto é acadêmico: os resultados **não são alertas oficiais**, não substituem medições de uma estação CETESB nem devem ser usados como orientação médica.

## 2. De onde vêm os dados e o que foi coletado?

As séries horárias foram consultadas em duas fontes da Open-Meteo para as coordenadas configuradas do projeto:

1. **Air Quality API**: PM10, PM2,5, monóxido de carbono (CO), dióxido de nitrogênio (NO2), dióxido de enxofre (SO2) e ozônio (O3).
2. **Historical Weather API**: temperatura, umidade relativa, precipitação, velocidade do vento e pressão ao nível médio do mar.

O intervalo ampliado vai de **04/08/2022 a 31/08/2026**, totalizando 35.736 horários por fonte. Os timestamps das fontes foram integrados em uma tabela. Os arquivos brutos são preservados em `data/raw/`; os dados integrados e rotulados ficam em `data/interim/`. Os arquivos de janeiro de 2025 anteriores à ampliação foram mantidos.

**Importante sobre a origem:** para esta região, a série de qualidade do ar é baseada em modelagem atmosférica CAMS Global, com valores horários intermediários interpolados pela API. A série meteorológica também vem de dados de arquivo/reanálise. Portanto, os dados representam estimativas para uma grade espacial, não medições diretas naquele endereço. O ponto de grade retornado pela API pode diferir um pouco das coordenadas solicitadas.

### 2.1 O que significa cada dado coletado?

Cada linha da base representa um horário (`time`) no ponto configurado. Os nomes abaixo são os nomes técnicos que aparecem nos arquivos CSV e no código. As unidades são as fornecidas pelas fontes nesta coleta.

| Nome no arquivo | Nome simples | Unidade | O que representa / por que foi incluído |
|---|---|---|---|
| `time` | Data e hora | Data/hora local | Identifica quando valem as demais informações. É usado para manter a ordem da série, montar janelas passadas e separar treino, validação e teste. Não é uma medição de poluente. |
| `pm10` | Partículas PM10 | µg/m³ | Massa estimada de partículas inaláveis de até cerca de 10 micrômetros por volume de ar. É um dos poluentes considerados no cálculo do IQAr. |
| `pm2_5` | Partículas PM2,5 | µg/m³ | Partículas finas de até cerca de 2,5 micrômetros por volume de ar. É um insumo do IQAr e também gera atributos de tendência recente usados pelo modelo. |
| `carbon_monoxide` | Monóxido de carbono (CO) | µg/m³ | Concentração estimada de CO. Entra no cálculo do subíndice após a conversão prevista no código para a unidade exigida pela tabela CETESB. |
| `nitrogen_dioxide` | Dióxido de nitrogênio (NO₂) | µg/m³ | Concentração estimada de NO₂; entra no cálculo do respectivo subíndice do IQAr. |
| `sulphur_dioxide` | Dióxido de enxofre (SO₂) | µg/m³ | Concentração estimada de SO₂; entra no cálculo do respectivo subíndice do IQAr. |
| `ozone` | Ozônio (O₃) | µg/m³ | Concentração estimada de ozônio; entra no IQAr e gera atributos de média e variação recente usados pelo modelo. |
| `temperature_2m` | Temperatura a 2 m | °C | Temperatura do ar estimada a dois metros de altura. É uma variável meteorológica de contexto. |
| `relative_humidity_2m` | Umidade relativa a 2 m | % | Umidade relativa do ar estimada a dois metros de altura. É contexto meteorológico. |
| `precipitation` | Precipitação | mm | Quantidade de precipitação no intervalo horário segundo a fonte. É contexto meteorológico. |
| `wind_speed_10m` | Velocidade do vento a 10 m | km/h | Velocidade estimada do vento a dez metros. É contexto meteorológico que pode acompanhar diferentes condições de dispersão. |
| `pressure_msl` | Pressão ao nível médio do mar | hPa | Pressão atmosférica estimada e ajustada ao nível médio do mar. É contexto meteorológico. |

**Atenção:** as descrições explicam o significado geral das variáveis, não provam que uma delas cause a piora do IQAr. As fontes são modeladas/reanalisadas e a resolução espacial não equivale a uma estação local. As features finais do modelo são um subconjunto dessas colunas mais quatro atributos derivados; a lista exata está em `FEATURES_SPRINT4` no código e no [Dicionário de Dados](Dicionario_de_Dados.md).

### 2.2 O que acontece com os dados em cada etapa?

| Etapa | O que entra | O que o programa faz | Arquivo/resultado |
|---|---|---|---|
| Coleta | Respostas das APIs Open-Meteo para datas, coordenadas e variáveis da configuração | Salva a resposta original de qualidade do ar e a resposta de clima sem misturar as fontes | Dois arquivos JSON em `data/raw/` |
| Integração (*merge*) | Os dois JSONs | Junta as tabelas pelo horário comum e verifica a quantidade de linhas, ausências e duplicatas | CSV integrado em `data/interim/` |
| Construção do alvo | CSV integrado e concentrações dos seis poluentes | Calcula subíndices pelas janelas CETESB, forma o IQAr como o maior subíndice e marca se o IQAr futuro em `t+1h` passa de 100 | CSV rotulado em `data/interim/`; contém features e também colunas calculadas para análise/alvo |
| Treino e validação | Features retrospectivas e rótulos do desenvolvimento | Ajusta o pipeline e compara modelos/limiares usando períodos temporais de validação | Métricas e previsões CSV em `reports/modeling/` |
| Empacotamento | Dados anteriores ao início do holdout e decisão já congelada | Ajusta o pipeline escolhido e guarda classificador, features e limiar para reutilização | `models/modelo_final_sprint5.joblib` |
| Demonstração | Artefato empacotado e features históricas anteriores ao holdout | Calcula features temporais, estima probabilidade e aplica o limiar salvo | Tabela mostrada no notebook; não é avaliação nem previsão atual |

Os arquivos `JSON` conservam a resposta original estruturada da API. Os arquivos `CSV` são tabelas: cada linha corresponde a um horário e cada coluna a uma variável ou resultado calculado. Os relatórios CSV contêm resultados de experimentos; não são dados brutos nem previsões oficiais.

## 3. Como foi construído o resultado que se quer prever?

Para cada poluente, a concentração é convertida em um subíndice conforme os pontos de concentração e a interpolação linear da metodologia CETESB. São usadas estas janelas, terminando no horário que está sendo avaliado:

| Poluente | Janela usada no subíndice |
|---|---:|
| PM10 | Média móvel de 24 horas |
| PM2,5 | Média móvel de 24 horas |
| CO | Média móvel de 8 horas |
| NO2 | Valor horário |
| SO2 | Média móvel de 24 horas |
| O3 | Média móvel de 8 horas |

O IQAr consolidado de cada horário é o **maior dos seis subíndices**. A classe-alvo é:

- **1 — inadequada**: IQAr maior que 100;
- **0 — não inadequada segundo este critério**: IQAr menor ou igual a 100.

O CO chega da API em µg/m³, enquanto a tabela CETESB usa ppm; por isso, sua média móvel é convertida antes do cálculo do subíndice, usando a hipótese de 25 °C e 1 atm. O rótulo associado à linha em `t` é o resultado calculado em `t + 1 hora`.

Se faltar informação para completar uma janela, o índice e o rótulo dependentes dela ficam indefinidos; esses valores não são inventados por imputação. No conjunto ampliado, há **35.713 rótulos definidos** (904 positivos e 34.809 negativos) e 23 indefinidos, principalmente por aquecimento das janelas no início da série e pela falta de uma hora futura na última linha.

### 3.1 O que significam as colunas calculadas?

Além das colunas recebidas das APIs, o CSV rotulado contém resultados construídos pelo projeto. Eles não são novas medições:

| Coluna ou grupo | Significado em linguagem simples | Uso |
|---|---|---|
| `iqar_pm10`, `iqar_pm2_5`, `iqar_carbon_monoxide`, `iqar_nitrogen_dioxide`, `iqar_sulphur_dioxide`, `iqar_ozone` | Subíndice de qualidade do ar calculado separadamente para cada poluente, conforme a tabela CETESB e a janela indicada acima. | Descrevem o nível relativo atribuído a cada poluente no horário avaliado. |
| `iqar` | O maior valor entre os seis subíndices daquele horário. | Resume qual poluente determina o IQAr consolidado. |
| `qualidade_ar_inadequada_1h` | Resultado futuro associado à linha: `1` se o IQAr de `t+1h` for maior que 100; `0` se for menor ou igual a 100; vazio se não for possível calcular o resultado. | É o alvo usado durante o treinamento e na avaliação. **Não é uma entrada permitida para gerar a previsão.** |
| `media_3h_ozone`, `media_3h_pm2_5` | Média dos valores horários do respectivo poluente em `t`, `t−1h` e `t−2h`. | Resume o nível recente de ozônio e PM2,5 usando o instante atual e passado, sem olhar adiante. |
| `delta_2h_ozone`, `delta_2h_pm2_5` | Valor do poluente em `t` menos seu valor em `t−2h`. Um número positivo indica valor maior em `t` do que duas horas antes; negativo indica valor menor. | Representa mudança ao longo de duas horas; não é uma taxa por hora nem prova causa. |
| `event_time` | Horário do evento que corresponde ao alvo, calculado como `time + 1 hora`. | Ajuda a atribuir corretamente linhas a treino, validação ou teste. É metadado de avaliação, não uma medição nem uma feature do modelo. |

O modelo final usa subíndices individuais, variáveis meteorológicas e as quatro features retrospectivas da tabela, conforme a lista congelada da Sprint 4. A coluna consolidada `iqar` e o alvo `qualidade_ar_inadequada_1h` não fazem parte das features finais. Os nomes e a lista exata podem ser conferidos no [Dicionário de Dados](Dicionario_de_Dados.md) e em `FEATURES_SPRINT4` no código.

## 4. Qual parte dos dados entrou nesta EDA?

A EDA foi feita somente no **desenvolvimento**, com rótulos cujo evento previsto (`time + 1h`) ocorre antes de 01/01/2025:

- **21.121 observações**;
- **743 eventos positivos**;
- **20.378 eventos negativos**;
- **prevalência positiva de 3,52%**.

O período de teste final, 2025–2026, não foi usado para gerar estes gráficos nem para orientar a investigação de extremos desta EDA. Há, contudo, uma ressalva metodológica: antes da definição final do corte, a série completa tinha sido examinada descritivamente, incluindo taxas e médias por classe em 2025–2026; por isso, o holdout não é totalmente cego. Posteriormente, após congelar modelo e limiar na validação, o holdout foi avaliado uma única vez na Sprint 5. Ele não deve ser reaberto para seleção ou ajuste.

## 5. O que foi analisado e para que serve cada gráfico?

O script reproduzível é [`src/analise/EDA_Desenvolvimento.py`](../src/analise/EDA_Desenvolvimento.py). Ele lê os caminhos e os limites temporais da configuração, valida timestamps e colunas necessárias e seleciona o desenvolvimento pela data do evento previsto. Os gráficos são salvos em `reports/figures/eda_desenvolvimento/`.

### Prevalência mensal

[Abrir gráfico de prevalência mensal](../reports/figures/eda_desenvolvimento/prevalencia_mensal.png)

Mostra a proporção e a contagem de eventos positivos em cada mês. Serve para visualizar mudanças temporais e períodos com poucos exemplos; não estabelece que um mês causou pior qualidade do ar. Na EDA, a taxa positiva foi mais alta em setembro (6,62%) e março (5,65%), e mais baixa em junho (1,04%). As taxas variaram por ano: 2,38% em 2022 e 4,41% em 2024.

### Boxplots de CO, PM10 e PM2,5 por classe

[Abrir boxplots das concentrações](../reports/figures/eda_desenvolvimento/boxplots_concentracoes_log1p.png)

Compara as distribuições dos valores brutos em cada classe. A escala `log1p` comprime a cauda longa para tornar visíveis tanto os valores comuns quanto os extremos; ela é apenas uma transformação visual do gráfico, não altera os dados armazenados.

As medianas das três concentrações são mais altas na classe positiva do que na negativa, mas há sobreposição. Isso é compatível com as janelas e o alvo serem derivados dos mesmos poluentes, e não demonstra causalidade nem desempenho preditivo independente.

### Correlação entre features candidatas

[Abrir matriz de correlação de Spearman](../reports/figures/eda_desenvolvimento/correlacao_spearman_features.png)

Mostra associações monotônicas entre as variáveis brutas, meteorológicas e índices calculados em `t`. O método de Spearman é baseado na ordenação dos valores e pode revelar associações mesmo quando a relação não é linear.

A matriz não inclui o alvo. Ela mostra associações altas entre alguns poluentes e seus índices porque os índices são transformações determinísticas das concentrações; PM10 e PM2,5 também variam em conjunto. Essa redundância é uma razão para comparar grupos de features nos folds, não uma justificativa automática para remover variáveis.

Em uma análise separada de associação com o alvo, os maiores coeficientes de Spearman observados foram `iqar_ozone` e `iqar` (0,317), ozônio bruto (0,297), `iqar_pm2_5` (0,215) e PM2,5 (0,211). Esses coeficientes são exploratórios: não medem causalidade, não são importância de modelo e podem refletir janelas sobrepostas e autocorrelação temporal.

### Extremos ao longo do tempo

[Abrir gráfico dos extremos no tempo](../reports/figures/eda_desenvolvimento/extremos_concentracoes_tempo.png)

Mostra o máximo diário de cada concentração, com duas linhas de referência: o percentil 99 (P99) horário e a cerca superior `Q3 + 1,5 × IQR`. O P99 indica um valor alto da distribuição; a cerca de IQR é uma regra exploratória convencional de triagem. Nenhuma das duas define, por si só, um erro de coleta ou um limite regulatório.

Os máximos observados foram:

| Variável bruta | Máximo | Percentil 99 | Cerca `Q3 + 1,5 × IQR` | Horas acima da cerca |
|---|---:|---:|---:|---:|
| CO | 3.838 µg/m³ | 981,40 µg/m³ | 533,50 µg/m³ | 1.118 (5,29%) |
| PM10 | 152,7 µg/m³ | 63,3 µg/m³ | 39,50 µg/m³ | 1.132 (5,36%) |
| PM2,5 | 106,9 µg/m³ | 44,1 µg/m³ | 27,65 µg/m³ | 1.120 (5,30%) |

Os três máximos ocorreram em 05/06/2023. Os valores elevados aparecem em sequências de horas, não apenas como um ponto isolado. Em 669 horas, as três concentrações excederam simultaneamente suas cercas. Isso sugere episódios conjuntos na série modelada, mas não permite confirmar se representam um evento atmosférico real no ponto de interesse.

Entre horas acima da cerca, a proporção de rótulos positivos foi 3,13% para CO, 14,49% para PM10 e 13,57% para PM2,5, comparada com 3,52% no desenvolvimento completo. Essas observações são horárias e autocorrelacionadas, então não devem ser tratadas como amostras independentes nem usadas para afirmar que um poluente isolado explica o evento.

O episódio ilustra por que é necessário respeitar a definição do alvo: os máximos brutos matinais tiveram rótulos negativos; mais tarde, o subíndice de ozônio elevou o IQAr acima de 100, com eventos positivos previstos entre 16h e 22h. O rótulo depende de janelas e do instante `t+1h`, não de um único valor bruto em `t`.

## 6. Conclusões e decisões desta etapa

1. A classe positiva é rara no desenvolvimento (3,52%), e sua prevalência varia no tempo. A validação deve preservar a ordem temporal.
2. Concentrações e índices derivados podem ser candidatos a features, desde que sejam calculados apenas com dados disponíveis em `t`.
3. CO, PM10 e PM2,5 têm distribuições assimétricas e episódios de valores elevados. Como não existe medição local independente para validar esses pontos, a decisão foi **preservar todos os valores**, sem exclusão, imputação ou clipping.
4. Poluentes brutos e índices derivados carregam informação relacionada. Foi aprovado comparar, nos mesmos folds de 2024, três conjuntos: (a) poluentes brutos + meteorologia; (b) subíndices/IQAr + meteorologia; (c) os dois grupos + meteorologia.
5. A EDA não selecionou modelo nem limiar. As etapas seguintes compararam features (Sprint 4) e modelos/limiares (Sprint 5) usando validação temporal; a seleção final foi congelada antes da única avaliação do holdout.

## 7. Primeiros baselines nos folds de 2024 — resultado histórico da Sprint 3

Após a EDA, os três grupos aprovados foram comparados nos mesmos quatro trimestres de validação de 2024. Na Sprint 3, os dados de 2025–2026 não entraram no treinamento, na validação nem nesta comparação. Esses resultados são o baseline histórico da etapa, não a decisão final do projeto.

Foram usados três pontos de referência:

- **Dummy prior**: sempre prevê a classe mais frequente no treino. Como há poucos positivos, previu todos os casos como negativos.
- **Persistência pelo IQAr atual**: prevê que a condição de `t` continua na hora seguinte. Em termos operacionais, prevê positivo quando `iqar` em `t` é maior que 100.
- **Gaussian Naive Bayes**: classificador simples executado com cada um dos três grupos de features. O tratamento de ausências por mediana e a padronização ficaram dentro do pipeline e foram ajustados apenas com o treino de cada fold.

Nenhum limiar foi ajustado e nenhum balanceamento artificial foi aplicado. A tabela apresenta a média simples das métricas dos quatro folds. As contagens TN/FP/FN/TP são somas dos folds, não médias.

| Modelo | Features | Precisão positiva média | Recall positivo médio | F1 positivo médio | TN | FP | FN | TP |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Dummy prior | Independente de features | 0,0000 | 0,0000 | 0,0000 | 8.397 | 0 | 387 | 0 |
| Persistência pelo IQAr em `t` | Independente de features | 0,8196 | 0,8196 | 0,8196 | 8.329 | 68 | 68 | 319 |
| Gaussian Naive Bayes | Poluentes brutos + meteorologia | 0,2996 | 0,6882 | 0,4134 | 7.814 | 583 | 114 | 273 |
| Gaussian Naive Bayes | Subíndices/IQAr + meteorologia | 0,4491 | 0,9985 | 0,6175 | 7.921 | 476 | 1 | 386 |
| Gaussian Naive Bayes | Brutos + subíndices/IQAr + meteorologia | 0,4217 | 0,9985 | 0,5914 | 7.860 | 537 | 1 | 386 |
| Gaussian Naive Bayes (ablação) | Subíndices individuais + meteorologia, sem `iqar` | 0,5057 | 0,9949 | 0,6669 | 7.995 | 402 | 3 | 384 |
| Gaussian Naive Bayes (ablação) | Brutos + subíndices individuais + meteorologia, sem `iqar` | 0,4254 | 0,9956 | 0,5942 | 7.855 | 542 | 3 | 384 |

O modelo com subíndices/IQAr identificou quase todos os positivos dos folds, mas previu positivo em muitos casos negativos. A persistência apresentou F1 médio mais alto entre estes modelos. O Dummy é útil como referência mínima, mas falha em encontrar positivos. Isso não conclui que a persistência será o modelo final: as médias resumem somente quatro períodos, as taxas variam com o tempo e o Naive Bayes supõe independência condicional entre as variáveis, hipótese pouco plausível para poluentes correlacionados. Além disso, os índices em `t` e o alvo derivam de poluentes e janelas relacionados; o horizonte está respeitado, mas essa dependência deve ser considerada ao interpretar o recall quase perfeito. Q4/2024 tem somente 46 positivos e requer cautela especial.

### O que os erros mostram

O fold 2024-Q3 concentrou o maior número de falsos positivos do Naive Bayes. Para o grupo de subíndices/IQAr, houve 224 falsos positivos no trimestre; para o grupo combinado, 260. Setembro/2024 teve o maior número mensal para ambos: 133 e 147, respectivamente. No grupo apenas com subíndices/IQAr, 181 dos 476 falsos positivos se concentraram entre 18h e 21h. São contagens brutas: sem comparar o número de previsões e eventos de cada mês/hora, não demonstram que esses períodos tenham maior taxa de erro.

Ao comparar as previsões de modelos nas mesmas linhas, 409 dos 476 falsos positivos do Naive Bayes com subíndices ocorreram quando a persistência do IQAr atual previa classe 0 (IQAr em `t` <= 100). Isso sugere que o Naive Bayes prevê diversos eventos positivos além daqueles em que a condição já era inadequada em `t`. Já os 114 falsos negativos do modelo treinado apenas com poluentes brutos foram todos previstos como positivos pela persistência. Esse contraste sugere que a representação do estado atual por IQAr pode ser útil, mas não determina qual modelo ou regra deve ser adotado.

No Q3, a taxa de falso positivo do modelo com subíndices subiu de 6,8% em julho e 6,1% em agosto para 21,2% em setembro; no grupo combinado, de 7,1% e 8,9% para 23,4%. O denominador de cada taxa é o número de negativos reais daquele mês. Os erros também se agrupam no tempo: 206 dos 224 falsos positivos do grupo de subíndices e 251 dos 260 do grupo combinado ocorreram em sequências com pelo menos duas horas consecutivas classificadas incorretamente. A maior sequência foi de 21 horas (subíndices) e 19 horas (grupo combinado). Por isso, os erros contíguos não devem ser interpretados como ocorrências independentes.

Entre os negativos Q3 que o grupo de subíndices marcou incorretamente, a mediana do IQAr em `t` foi 76,23, contra 30,15 nos negativos corretamente classificados; o subíndice de ozônio teve medianas 72,67 e 25,95, e a concentração de ozônio bruto 111,5 e 62 µg/m³. O classificador, portanto, costuma prever positivo em situações nas quais as features disponíveis em `t` estão relativamente elevadas, mas o IQAr-alvo em `t+1h` não cruza o limiar. Isso ajuda a caracterizar o erro, mas não valida nem invalida os dados.

Foi executada uma ablação removendo somente `iqar` dos dois grupos com subíndices, mantendo os subíndices individuais, meteorologia, folds, pipeline e limiar padrão. No grupo somente de subíndices, os falsos positivos caíram de 476 para 402 e o F1 médio subiu de 0,6175 para 0,6669; o recall médio caiu de 0,9985 para 0,9949 e os falsos negativos aumentaram de 1 para 3. No grupo combinado, os falsos positivos aumentaram de 537 para 542; o F1 mudou de 0,5914 para 0,5942 e o recall caiu para 0,9956. Portanto, o efeito varia de acordo com o grupo e não demonstra que a feature seja, por si só, a causa dos erros.

No Q3, o grupo somente de subíndices passou de 224 para 216 falsos positivos, mas sua taxa de setembro permaneceu em 21,2% (133 FP). No grupo combinado, os falsos positivos do trimestre aumentaram de 260 para 280; a taxa de setembro aumentou de 23,4% (147 FP) para 25,0% (157 FP). A ablação não resolveu a elevação de setembro. Todos os números são exploratórios, dependem da hipótese de independência condicional do Naive Bayes e não selecionam um modelo final.

### Exploração preliminar do limiar

Para explorar o custo relativo entre falsos negativos e falsos positivos, foi avaliada uma grade de 101 limiares (0,00 a 1,00, passo 0,01) em janelas internas temporais: para cada fold trimestral de 2024, a validação interna é o trimestre imediatamente anterior e o modelo é ajustado apenas com dados ainda anteriores. As janelas vão de 2023-Q4 a 2024-Q3; somadas, contêm 8.340 negativos e 444 positivos. Nenhuma dessas medições usa 2025–2026, e o fold externo correspondente não participa da análise do limiar.

Exemplo ilustrativo para o Gaussian Naive Bayes com subíndices individuais e meteorologia, sem `iqar`: nas janelas internas, o limiar 0,50 produziu 4 falsos negativos e 428 falsos positivos (recall agregado de 0,9925); o limiar 0,25 produziu 2 falsos negativos e 543 falsos positivos (recall agregado de 0,9971). A redução de dois falsos negativos veio acompanhada de 115 falsos positivos adicionais. Contando a classe prevista positiva por hora, foram 868 horas de alerta (98,8 por mil horas de validação) no limiar 0,50 e 985 (112,1 por mil) no limiar 0,25. Pela regra acordada com a equipe — uma hora negativa encerra o episódio — essas previsões formaram 141 e 146 episódios, respectivamente (16,1 e 16,6 por mil horas). Entre as horas previstas como positivas, 49,3% e 55,1%, respectivamente, eram falsos alertas. A contagem de episódios resume previsões consecutivas; não mede se o episódio real foi detectado nem representa por si só o número de ações operacionais. O limiar 0,25 é apenas um exemplo da exploração histórica da Sprint 3, não a escolha final. A decisão posterior da Sprint 5 está descrita na seção seguinte.

Os CSVs [`baseline_threshold_tradeoff_by_inner_fold.csv`](../reports/modeling/baseline_threshold_tradeoff_by_inner_fold.csv) e [`baseline_threshold_tradeoff_summary.csv`](../reports/modeling/baseline_threshold_tradeoff_summary.csv) trazem os valores por janela e o resumo, incluindo horas e episódios previstos como alerta por mil horas e proporção de falsos alertas entre previsões positivas. A contagem de episódios usa a regra confirmada pela equipe: uma hora negativa encerra a sequência. Ela conta episódios previstos, não acertos de detecção de episódios reais. Os demais artefatos de erros e ablação continuam em [`baseline_misclassified_cases.csv`](../reports/modeling/baseline_misclassified_cases.csv), [`baseline_error_rates_by_month.csv`](../reports/modeling/baseline_error_rates_by_month.csv), [`baseline_error_rates_by_hour.csv`](../reports/modeling/baseline_error_rates_by_hour.csv), [`baseline_iqar_ablation_by_fold.csv`](../reports/modeling/baseline_iqar_ablation_by_fold.csv) e [`baseline_iqar_ablation_summary.csv`](../reports/modeling/baseline_iqar_ablation_summary.csv). Eles se referem ao desenvolvimento/validações internas de 2023-Q4–2024; não incluem o holdout.

Resultados detalhados por trimestre, grupo e matriz de confusão estão em [`reports/modeling/baseline_metrics_by_fold.csv`](../reports/modeling/baseline_metrics_by_fold.csv) e [`reports/modeling/baseline_metrics_summary.csv`](../reports/modeling/baseline_metrics_summary.csv). Para reproduzir a avaliação, execute `python -m src.modelagem.Avaliar_Baselines` na raiz do repositório.

## 8. Resultados das Sprints 4 e 5

### Sprint 4 — features temporais e comparação S3→S4

Foram avaliados atributos retrospectivos de ozônio e PM2,5 nos mesmos folds temporais de 2024, sem consultar o holdout. A variante congelada para a etapa seguinte acrescentou médias móveis de 3 horas e deltas de 2 horas, todos calculáveis com observações disponíveis até *t*. No comparativo formal, o Gaussian Naive Bayes S4 teve recall médio 1,0000 contra 0,9949 do grupo-base S3, 0 FN contra 3 e pico semanal de 6 contra 7 episódios. Em contrapartida, passou de 402 para 471 falsos positivos, reduziu F1 de 0,6669 para 0,6261 e manteve 19 semanas acima do teto semanal de três episódios. É um trade-off, não uma melhoria global. A escolha das features e sua limitação por viés de seleção nos folds de desenvolvimento estão documentadas em [`Sprint4_TrilhaB.md`](sprints/Sprint4_TrilhaB.md).

### Sprint 5 — seleção pré-teste e avaliação final única

Na validação temporal 2024-Q4 havia 2.208 observações e 46 positivos. Foram comparados Dummy, persistência, Gaussian Naive Bayes, regressão logística balanceada e Random Forest balanceada. A equipe congelou Random Forest com `class_weight="balanced"`, 300 árvores, `min_samples_leaf=2`, `random_state=42` e limiar 0,3: recall 1,0000, precisão 0,7797, F1 0,8440, 13 falsos positivos e no máximo três episódios em cada uma das 12 semanas completas da validação (máximo de 15 horas de alerta na semana de maior carga). A janela curta e o número reduzido de positivos limitam a confiança na escolha.

Depois de congelada a decisão, o holdout temporal de 01/01/2025 a 31/08/2026 foi avaliado uma única vez: 14.592 observações, 161 positivas. A variante escolhida obteve recall 0,9814, precisão 0,7822 e F1 0,8705, com 158 verdadeiros positivos (TP), 44 falsos positivos (FP), 3 falsos negativos (FN) e 14.387 verdadeiros negativos (TN). Uma das 86 semanas completas excedeu o teto de episódios; o máximo foi cinco episódios e 31 horas de alerta. Os três eventos FN registrados foram 27/12/2025 às 14h, 28/12/2025 às 13h e 31/12/2025 às 15h. A regressão logística `predict` padrão apresentou recall 1,0000 e F1 0,8846 no mesmo holdout, mas não substituiu a escolha congelada, pois o teste não pode ser reutilizado para seleção.

O pipeline treinado somente com o período anterior ao teste foi empacotado em [`modelo_final_sprint5.joblib`](../models/modelo_final_sprint5.joblib). O notebook [`03_Demonstracao_Modelo_Final.ipynb`](../notebooks/03_Demonstracao_Modelo_Final.ipynb) demonstra carregamento e inferência sobre uma linha histórica anterior ao holdout. Como o artefato foi treinado no período usado pelo exemplo, essa previsão é *in-sample*: demonstra o fluxo técnico, mas não estima desempenho nem representa uma previsão atual.

## 9. Como executar e validar, passo a passo

Execute os comandos a partir da raiz do repositório. No Windows, os comandos abaixo usam o Python do ambiente virtual local.

### 9.0 Quero apenas abrir a demonstração e ver o resultado

Se os arquivos do projeto já estão na sua máquina, **não comece pelos notebooks de coleta**. Eles consultam serviços externos e tentam criar arquivos que já existem; o notebook de demonstração usa a base e o modelo que foram preparados anteriormente.

1. Abra a pasta do repositório no VS Code.
2. Abra o terminal do VS Code (`Terminal` → `Novo Terminal`) e confirme que o terminal está na pasta principal do projeto, onde aparecem `README.md`, `config`, `data`, `models` e `notebooks`.
3. No Windows, crie o ambiente virtual e instale as dependências uma vez:

   ```powershell
   py -3.13 -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

   Se a pasta `.venv` já existir, não precisa recriá-la; execute apenas a linha de instalação. O projeto foi validado com Python 3.13.7. Se `py -3.13` não for reconhecido, instale Python 3.13 e habilite o launcher `py`, ou selecione o interpretador instalado no VS Code.

4. Abra `notebooks/03_Demonstracao_Modelo_Final.ipynb`. Se o VS Code pedir um kernel, selecione o Python dentro de `.venv`.
5. Execute as células na ordem, usando **Run All**. Alternativamente, no terminal, abra o notebook no Jupyter:

   ```powershell
   .\.venv\Scripts\python.exe -m jupyter lab notebooks\03_Demonstracao_Modelo_Final.ipynb
   ```

6. Vá à última tabela, chamada `resumo`, e leia as colunas explicadas na seção 9.6.

O notebook **não consulta a internet**, não coleta dados, não recalcula o alvo, não treina modelos e não abre o período de teste. Ele depende de `data/interim/dados_com_alvo_2022-08-04_2026-08-31.csv` e `models/modelo_final_sprint5.joblib`. Se algum deles estiver ausente, a execução para com uma mensagem de arquivo necessário não encontrado; não tente recriá-los sem confirmar com a equipe qual versão de dados e artefato deve ser usada.

Na execução de referência, a amostra didática é de 31/12/2024 às 22h, com previsão do evento das 23h, e o texto do resultado é **“Sem alerta pela regra”**. O notebook imprime a probabilidade junto da tabela; o valor exato pode variar se o CSV ou o artefato local tiver sido substituído. Essa amostra faz parte do período de treinamento e serve somente para aprender a ler a saída.

### 9.1 Preparar o ambiente

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install pytest
```

No VS Code, selecione `.venv\Scripts\python.exe` como interpretador e instale/ative a extensão Jupyter para abrir notebooks. `pytest` é necessário apenas para executar a suíte de testes.

### 9.2 Conferir os arquivos necessários antes de rodar

Verifique a existência de:

- `config/params.yaml`;
- `data/interim/dados_com_alvo_2022-08-04_2026-08-31.csv`;
- `models/modelo_final_sprint5.joblib`;
- a pasta `reports/` com os resultados listados nas seções anteriores.

Os scripts de coleta, merge e cálculo do alvo se recusam a sobrescrever saídas já existentes. Como os dados deste projeto já foram coletados e processados, **não é necessário refazer chamadas às APIs** para validar os resultados atuais. Se estiver montando uma cópia limpa sem os arquivos intermediários, siga a ordem documentada no [`README.md`](../README.md): coleta, merge e cálculo do alvo; confira os caminhos e o período em `config/params.yaml` antes de executar. Não apague nem sobrescreva os arquivos existentes.

### 9.3 Reproduzir a EDA

```powershell
python -m src.analise.EDA_Desenvolvimento
```

O comando lê a base rotulada, separa o desenvolvimento pelo horário do evento (`time + horizonte`) e recria os gráficos em `reports/figures/eda_desenvolvimento/`. Valide que o resumo mostre 21.121 observações, 743 positivos, 20.378 negativos e prevalência de 3,52%; confira se os quatro PNGs foram gerados. Essa EDA não é a avaliação final do modelo.

### 9.4 Reproduzir validações de desenvolvimento (opcional)

Os comandos abaixo ajustam modelos e reescrevem relatórios de validação/desenvolvimento em `reports/modeling/`. Use-os quando precisar reproduzir essas análises; eles não são necessários para abrir os relatórios já gerados:

```powershell
python -m src.modelagem.Avaliar_Baselines
python -m src.modelagem.Avaliar_Features_Temporais
python -m src.modelagem.Comparar_Modelos_Sprint5
```

Confira os CSVs correspondentes ao comando e compare as métricas, contagens FP/FN e carga semanal com as tabelas das Sprints 3–5. A comparação Sprint 5 usa somente o fold de validação 2024-Q4. Não trate métricas históricas de S3 como resultados finais.

### 9.5 Validar o artefato sem reavaliar o holdout

Para reproduzir a demonstração de inferência, abra `notebooks/03_Demonstracao_Modelo_Final.ipynb` e execute as células em ordem. Ela verifica a existência/configuração do modelo, carrega apenas colunas de features e `time` até antes do holdout, calcula as quatro features de curto prazo e aplica o limiar salvo. O último `event_time` mostrado deve ser anterior a `2025-01-01 00:00:00`. A inferência é *in-sample* e não pode ser usada como métrica de desempenho.

Para repetir os testes automatizados, que usam dados sintéticos:

```powershell
python -m pytest tests
```

Os testes cobrem cálculo do alvo, separação temporal, criação de features, comparativos e empacotamento. A aprovação dos testes confirma o comportamento coberto por eles, mas não substitui a conferência dos artefatos e resultados do experimento real.

### 9.6 Como ler a tabela final da demonstração

| Coluna apresentada | Como interpretar |
|---|---|
| `horário dos dados até t` | Último horário de entrada usado. Por exemplo, `22:00` significa que as informações disponíveis até as 22h foram usadas; não significa que a qualidade do ar tenha sido medida por este projeto naquele endereço. |
| `horário do evento previsto` | Horário estimado para a condição futura. Como o horizonte configurado é uma hora, dados até 22h correspondem ao evento previsto para 23h. |
| `probabilidade estimada de IQAr > 100` | Saída numérica da classe positiva pelo pipeline. É um escore probabilístico do modelo, não uma garantia de que o evento ocorrerá e não uma probabilidade calibrada para uso clínico ou oficial. |
| `limiar congelado` | Corte usado para transformar o escore em uma classe. Neste projeto é `0.3`, escolhido na validação temporal de 2024-Q4 antes da avaliação final. Não significa que 30% seja um nível universal de risco. |
| `resultado da regra` | Se o escore for maior ou igual a 0,3, aparece `ALERTA (regra experimental)`; se for menor, aparece `Sem alerta pela regra`. O texto é apenas uma saída didática e não deve ser publicado como aviso oficial. |

**O que o notebook não mostra:** ele não exibe o rótulo real da amostra, porque isso não é necessário para a demonstração; não calcula acerto/erro; não mede qualidade do modelo; não consulta as APIs; não usa dados posteriores ao corte; e não representa a situação atual do ar. Para conhecer as métricas reais do experimento, consulte as tabelas de validação e teste na [Sprint 5](sprints/Sprint5_TrilhaB.md) e os relatórios já salvos em `reports/modeling/`. A avaliação do holdout foi feita uma única vez; não rode o script de avaliação final novamente.

### 9.7 Se aparecer um erro

| Sintoma | O que verificar |
|---|---|
| `FileNotFoundError` para `config/params.yaml` | O notebook/terminal não está aberto dentro desta cópia do repositório ou não foi encontrado o diretório raiz. Abra a pasta principal do projeto. |
| `FileNotFoundError` para o CSV ou o arquivo `.joblib` | O arquivo de dados ou modelo não está presente. Confirme que os arquivos da entrega foram obtidos; não rode avaliação final nem gere um modelo novo apenas para eliminar o erro. |
| `ModuleNotFoundError` para pandas, sklearn, yaml, joblib ou Jupyter | O kernel selecionado não é o `.venv` do projeto ou as dependências não foram instaladas. Repita a instalação do passo 9.0 e selecione o interpretador correto. |
| A saída é diferente do exemplo | Confira que a configuração, o CSV e o artefato são os da mesma versão. Uma probabilidade diferente não é necessariamente um erro se o arquivo foi atualizado; não compare a saída didática como métrica. |
| O notebook diz que o horário alcança o holdout | Pare a execução e não altere o corte para “fazer passar”. Confira `evaluation.final_test.start` e `target_horizon_hours` em `config/params.yaml`, além da ordem e do conteúdo do CSV. |

O script `python -m src.modelagem.Empacotar_Modelo_Final_Sprint5` retreina o modelo no período de treino e grava o mesmo caminho do artefato. Execute-o somente se houver uma solicitação explícita para regenerar esse pacote e após confirmar o split e a versão dos dados; não é necessário para a demonstração.

> **Não executar novamente:** `python -m src.modelagem.Avaliar_Modelo_Final_Sprint5`. Esse script consulta o holdout e grava relatórios do teste. A avaliação final já foi realizada uma única vez; não use os resultados para selecionar outro modelo, ajustar limiar ou repetir a avaliação.

## 10. Arquivos relacionados

- [`README.md`](../README.md): visão geral e estado do projeto.
- [`docs/Dicionario_de_Dados.md`](Dicionario_de_Dados.md): definições e contrato das colunas.
- [`docs/RFC.md`](RFC.md): problema, decisões metodológicas e limitações.
- [`docs/sprints/Sprint2_TrilhaB.md`](sprints/Sprint2_TrilhaB.md): registro da preparação e EDA.
- [`docs/sprints/Sprint3_TrilhaB.md`](sprints/Sprint3_TrilhaB.md): protocolo para comparar features e iniciar os baselines.
- [`docs/sprints/Sprint4_TrilhaB.md`](sprints/Sprint4_TrilhaB.md): features temporais, comparação S3→S4 e trade-offs.
- [`docs/sprints/Sprint5_TrilhaB.md`](sprints/Sprint5_TrilhaB.md): comparação de modelos, escolha pré-teste, avaliação final e model card.
- [`src/transformacao/Calcular_Alvo_IQAr.py`](../src/transformacao/Calcular_Alvo_IQAr.py): cálculo dos subíndices, IQAr e rótulo.
- [`src/transformacao/Features_Temporais.py`](../src/transformacao/Features_Temporais.py): construção retrospectiva das features temporais.
- [`src/validacao/Separacao_Temporal.py`](../src/validacao/Separacao_Temporal.py): definição dos folds e do holdout temporal.
- [`src/modelagem/Empacotar_Modelo_Final_Sprint5.py`](../src/modelagem/Empacotar_Modelo_Final_Sprint5.py): treinamento pré-teste e serialização do pipeline final.
- [`notebooks/03_Demonstracao_Modelo_Final.ipynb`](../notebooks/03_Demonstracao_Modelo_Final.ipynb): demonstração segura de inferência histórica sem rótulos.
