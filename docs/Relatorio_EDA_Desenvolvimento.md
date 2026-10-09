# Relatório auxiliar — exploração dos dados de qualidade do ar

Este documento explica, em linguagem acessível, o objetivo do projeto, os dados usados, o que foi calculado na análise exploratória (EDA), o que os gráficos mostram e quais conclusões podem ou não ser tiradas. Foi escrito para leitores que não acompanharam as etapas anteriores.

## 1. Em poucas palavras: qual é o projeto?

O projeto investiga se é possível estimar, com uma hora de antecedência, se a qualidade do ar estará inadequada em um ponto de referência da região da Universidade Braz Cubas, em Mogi das Cruzes/SP.

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

## 4. Qual parte dos dados entrou nesta EDA?

A EDA foi feita somente no **desenvolvimento**, com rótulos cujo evento previsto (`time + 1h`) ocorre antes de 01/01/2025:

- **21.121 observações**;
- **743 eventos positivos**;
- **20.378 eventos negativos**;
- **prevalência positiva de 3,52%**.

O período de teste final, 2025–2026, não foi usado para gerar estes gráficos ou orientar a investigação de extremos. Há, contudo, uma ressalva metodológica: antes da definição final do corte, a série completa tinha sido examinada descritivamente, incluindo taxas e médias por classe em 2025–2026. Não houve treino de modelos nem ajuste de limiar com o holdout, mas ele não é totalmente cego. As decisões futuras de features e modelos devem ficar restritas ao desenvolvimento e aos folds temporais de 2024.

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
5. A EDA em si não selecionou modelo nem limiar. A seção seguinte registra a primeira comparação de baselines nos folds; modelo, features e limiar finais continuam sem seleção, mantendo 2025–2026 reservado.

## 7. Primeiros baselines nos folds de 2024

Após a EDA, os três grupos aprovados foram comparados nos mesmos quatro trimestres de validação de 2024. Os dados de 2025–2026 não entraram no treinamento, na validação nem nesta comparação.

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

Exemplo ilustrativo para o Gaussian Naive Bayes com subíndices individuais e meteorologia, sem `iqar`: nas janelas internas, o limiar 0,50 produziu 4 falsos negativos e 428 falsos positivos (recall agregado de 0,9925); o limiar 0,25 produziu 2 falsos negativos e 543 falsos positivos (recall agregado de 0,9971). A redução de dois falsos negativos veio acompanhada de 115 falsos positivos adicionais. Contando a classe prevista positiva por hora, foram 868 horas de alerta (98,8 por mil horas de validação) no limiar 0,50 e 985 (112,1 por mil) no limiar 0,25. Pela regra acordada com a equipe — uma hora negativa encerra o episódio — essas previsões formaram 141 e 146 episódios, respectivamente (16,1 e 16,6 por mil horas). Entre as horas previstas como positivas, 49,3% e 55,1%, respectivamente, eram falsos alertas. A contagem de episódios resume previsões consecutivas; não mede se o episódio real foi detectado nem representa por si só o número de ações operacionais. Isso mostra o trade-off, mas não escolhe o ponto operacional: a equipe ainda precisa decidir a carga aceitável. O limiar 0,25 é apenas um exemplo de leitura da curva, não uma recomendação nem um valor selecionado.

Os CSVs [`baseline_threshold_tradeoff_by_inner_fold.csv`](../reports/modeling/baseline_threshold_tradeoff_by_inner_fold.csv) e [`baseline_threshold_tradeoff_summary.csv`](../reports/modeling/baseline_threshold_tradeoff_summary.csv) trazem os valores por janela e o resumo, incluindo horas e episódios previstos como alerta por mil horas e proporção de falsos alertas entre previsões positivas. A contagem de episódios usa a regra confirmada pela equipe: uma hora negativa encerra a sequência. Ela conta episódios previstos, não acertos de detecção de episódios reais. Os demais artefatos de erros e ablação continuam em [`baseline_misclassified_cases.csv`](../reports/modeling/baseline_misclassified_cases.csv), [`baseline_error_rates_by_month.csv`](../reports/modeling/baseline_error_rates_by_month.csv), [`baseline_error_rates_by_hour.csv`](../reports/modeling/baseline_error_rates_by_hour.csv), [`baseline_iqar_ablation_by_fold.csv`](../reports/modeling/baseline_iqar_ablation_by_fold.csv) e [`baseline_iqar_ablation_summary.csv`](../reports/modeling/baseline_iqar_ablation_summary.csv). Eles se referem ao desenvolvimento/validações internas de 2023-Q4–2024; não incluem o holdout.

Resultados detalhados por trimestre, grupo e matriz de confusão estão em [`reports/modeling/baseline_metrics_by_fold.csv`](../reports/modeling/baseline_metrics_by_fold.csv) e [`reports/modeling/baseline_metrics_summary.csv`](../reports/modeling/baseline_metrics_summary.csv). Para reproduzir a avaliação, execute `python -m src.modelagem.Avaliar_Baselines` na raiz do repositório.

## 8. Como reproduzir

Na raiz do repositório, com as dependências de `requirements.txt` instaladas:

```bash
python -m src.analise.EDA_Desenvolvimento
```

O comando imprime a contagem de observações e o resumo de extremos e recria os quatro gráficos. Ele lê `data/interim/dados_com_alvo_2022-08-04_2026-08-31.csv`; não altera os arquivos de dados. Os resultados baseline podem ser recalculados com `python -m src.modelagem.Avaliar_Baselines`.

## 9. Arquivos relacionados

- [`README.md`](../README.md): visão geral e estado do projeto.
- [`docs/Dicionario_de_Dados.md`](Dicionario_de_Dados.md): definições e contrato das colunas.
- [`docs/RFC.md`](RFC.md): problema, decisões metodológicas e limitações.
- [`docs/sprints/Sprint2_TrilhaB.md`](sprints/Sprint2_TrilhaB.md): registro da preparação e EDA.
- [`docs/sprints/Sprint3_TrilhaB.md`](sprints/Sprint3_TrilhaB.md): protocolo para comparar features e iniciar os baselines.
- [`src/transformacao/Calcular_Alvo_IQAr.py`](../src/transformacao/Calcular_Alvo_IQAr.py): cálculo dos subíndices, IQAr e rótulo.
- [`src/validacao/Separacao_Temporal.py`](../src/validacao/Separacao_Temporal.py): definição dos folds e do holdout temporal.
