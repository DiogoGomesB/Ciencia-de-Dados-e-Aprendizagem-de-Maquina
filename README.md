# Qualidade do Ar Inadequada — Mogi das Cruzes/SP

**Disciplina:** Ciência de Dados e Aprendizado de Máquina

**Título:** Previsão de Qualidade do Ar Inadequada na Região da Faculdade UBC

**Trilha:** B — Qualidade do ar inadequada

**Equipe:** Davi Gama dos Santos (33121079) · Diogo Gomes Barbosa (35866276) · Eudenis Vieira (32751621) · Gabriel Januário Alves (35609991) · João Pedro Barreto da Silva (33297185)

**Repositório:** [DiogoGomesB/Ciencia-de-Dados-e-Aprendizagem-de-Maquina](https://github.com/DiogoGomesB/Ciencia-de-Dados-e-Aprendizagem-de-Maquina)

**Licença:** MIT (arquivo `LICENSE` no repositório)

---

## Estado atual do projeto

Situação técnica verificada em 09/10/2026. O projeto percorreu coleta, integração, cálculo do alvo, EDA, validação temporal, comparação de atributos e modelos, avaliação final única e empacotamento do pipeline. O conjunto ampliado foi salvo em arquivos identificados pelo período; os arquivos legados de janeiro/2025 foram preservados. Os registros de Scrum, feedback e rubricas ainda dependem do preenchimento real pela equipe.

| Entrega | Status | Observação |
|---|---|---|
| RFC | Atualizado | `docs/RFC.md`; escopo, decisões metodológicas, resultados e limitações registrados |
| Dicionário de dados | Atualizado | `docs/Dicionario_de_Dados.md`; inclui as features congeladas e o modelo final |
| Coleta bruta das duas fontes | Concluída para o período ampliado | 35.736 horários por fonte em arquivos versionados pelo intervalo; JSONs de janeiro/2025 preservados |
| Merge das duas fontes | Concluído para o período ampliado | 35.736 linhas em `data/interim/dados_merged_2022-08-04_2026-08-31.csv`; merge de janeiro preservado |
| Alvo | Implementado e calculado | 35.713 rótulos definidos: 904 positivos (2,53%) e 34.809 negativos; 23 indefinidos |
| Split temporal | Definido e implementado | Validação expansiva nos quatro trimestres de 2024; teste final de 2025 a 2026, sem embaralhamento |
| EDA do desenvolvimento | Concluída | Séries, boxplots, correlação entre candidatas e triagem de extremos |
| Baselines e comparação de features | Concluídos | Sprints 3–4; comparação S3→S4 e trade-offs documentados nos mesmos folds |
| Seleção e avaliação do modelo final | Concluídas | Random Forest e limiar 0,3 congelados na validação; holdout avaliado uma única vez |
| Pipeline final | Empacotado | `models/modelo_final_sprint5.joblib`; inferência demonstrativa em `notebooks/03_Demonstracao_Modelo_Final.ipynb` |
| Relatórios de análise e modelagem | Gerados | `reports/`; incluem validação, teste final, erros e carga semanal |
| Testes automatizados | 35 aprovados | `tests/`; cobrem alvo, split, features, baselines, avaliação e empacotamento |
| `requirements.txt` | Concluída | — |
| `LICENSE` | Concluída | MIT |

---

## Problema

| Item | Definição |
|---|---|
| Evento a prever | A qualidade do ar em Mogi das Cruzes/SP estará inadequada na próxima hora. |
| Usuário da decisão | Contexto acadêmico; usuário operacional ainda não definido pela equipe. |
| Horizonte | Uma hora à frente — a previsão realizada no instante *t* utiliza dados disponíveis até *t* para estimar a condição em *t+1h*. |
| Classe positiva | Classe 0: IQAr <= 100. Classe 1: IQAr > 100, incluindo as categorias mais graves. O índice consolidado é o maior subíndice dos seis poluentes, conforme a metodologia CETESB 2025. |
| Custo priorizado | Falso negativo — o modelo prever "adequada" quando a condição real na hora seguinte é inadequada. Considerado o erro mais grave, pois compromete a antecipação de uma piora real da qualidade do ar. |

Status: alvo, split temporal, EDA, comparação S3→S4, pipeline de features congelado e comparação de modelos estão implementados. A Sprint 5 congelou Random Forest com limiar 0,3 na validação, avaliou o holdout uma única vez e empacotou o pipeline. A demonstração atual usa uma linha histórica in-sample; não é uma previsão atual nem uma medição do ar.

**Referências**
[1] FURG — Dissertação/monografia sobre padrões de qualidade do ar: https://sistemas.furg.br/sistemas/sab/arquivos/bdtd/0000010377.pdf
[2] SANTOS, C. M. dos. UnB, 2011 — Índice de Qualidade do Ar: https://repositorio.unb.br/bitstream/10482/10977/1/2011_CleideMouradosSantos.pdf
[3] CETESB (2025), *Relatório de Metodologia para Avaliação da Qualidade do Ar*, Tabela 2.7 e seção 2.3, pp. 18–20: [PDF oficial](https://www.cetesb.sp.gov.br/dx/api/dam/v1/collections/186909e9-ab59-4641-abba-c5c465793216/items/3adb602d-77ec-4de5-b378-5fa141e80614/renditions/5a0e5f05-41aa-4e9c-9b00-69165ab36963/versions/1?binary=true).

---

## Como reproduzir e executar

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

O projeto foi validado com Python 3.13.7. Se `.venv` já existir, não a crie novamente; execute apenas a instalação das dependências. Para os testes automatizados, instale também `pytest`:

```powershell
.\.venv\Scripts\python.exe -m pip install pytest
```

O arquivo `requirements.txt` cobre coleta (`requests`), configuração (`PyYAML`), transformação e análise (`pandas`, `numpy`, `matplotlib`, `seaborn`), modelagem (`scikit-learn`) e notebooks (`jupyter`).

Configuração: coordenadas, datas, variáveis, endpoints, timeout e nomes dos arquivos estão em `config/params.yaml`. Os arquivos do intervalo configurado são nomeados com as datas e não sobrescrevem os JSONs ou o CSV de janeiro/2025.

### Demonstração rápida do modelo já empacotado

Se os dados e o modelo finais já estiverem presentes, abra `notebooks/03_Demonstracao_Modelo_Final.ipynb` no VS Code, escolha o interpretador `.venv\Scripts\python.exe` e execute as células na ordem. Ou rode:

```powershell
.\.venv\Scripts\python.exe -m jupyter lab notebooks\03_Demonstracao_Modelo_Final.ipynb
```

O notebook carrega `models/modelo_final_sprint5.joblib`, lê apenas as features históricas anteriores ao holdout, calcula os atributos de curto prazo e mostra a probabilidade e a decisão do limiar 0,3. Não coleta dados, não carrega o alvo, não retreina e não acessa o holdout. A linha usada é histórica e in-sample; serve para demonstrar a saída, não para medir desempenho ou informar a qualidade do ar atual. Para explicação detalhada de cada variável e campo da saída, veja o [Relatório EDA](docs/Relatorio_EDA_Desenvolvimento.md).

### Reproduzir coleta e transformações

Os notebooks de coleta e integração fazem parte do fluxo para uma configuração nova. Eles podem consultar APIs externas e recusam sobrescrever arquivos já existentes. **Não os execute para simplesmente abrir a demonstração ou reproduzir as métricas já documentadas.**

Para acompanhar a coleta e integração de forma interativa, abra os notebooks em `notebooks/` com Jupyter ou a extensão Jupyter do VS Code e execute as células na ordem:

1. [`01_Coleta_Dados.ipynb`](notebooks/01_Coleta_Dados.ipynb) consulta as APIs, inspeciona as respostas e salva os JSONs brutos. A execução faz chamadas externas e recusa sobrescrever arquivos existentes.
2. [`02_Merge_Dados.ipynb`](notebooks/02_Merge_Dados.ipynb) verifica os arquivos e horários, integra as fontes e salva o CSV em `data/interim/`.
3. [`03_Demonstracao_Modelo_Final.ipynb`](notebooks/03_Demonstracao_Modelo_Final.ipynb) carrega o pipeline empacotado e demonstra uma inferência histórica. O notebook lê apenas features anteriores ao holdout; não carrega rótulos, não retreina e não reavalia o teste. A previsão demonstrada é in-sample e não mede desempenho nem representa uma previsão atual.

O cálculo do alvo e a validação temporal estão disponíveis como scripts. Em uma cópia limpa, após conferir `config/params.yaml` e garantir que os arquivos de saída ainda não existem, a sequência pelo terminal é:

```powershell
.\.venv\Scripts\python.exe src\coleta\Coleta_Dados.py
.\.venv\Scripts\python.exe src\transformacao\Merge_Dados.py
.\.venv\Scripts\python.exe src\transformacao\Calcular_Alvo_IQAr.py
.\.venv\Scripts\python.exe -m src.validacao.Separacao_Temporal
```

Essa sequência é para uma configuração nova, com os caminhos de saída ainda livres. Os scripts gravam arquivos com o período configurado no nome e recusam sobrescrever arquivos existentes. A coleta consulta serviços externos. A rotulagem exige uma série horária ordenada e usa janelas completas terminando no horário avaliado; a última linha não recebe rótulo porque não há observação para *t+1h*. Não remova arquivos para contornar a proteção contra sobrescrita.

O script de validação temporal lê as partições de `config/params.yaml`, ignora rótulos indefinidos e imprime os tamanhos/classes de cada fold e do teste. A divisão é feita pelo horário do evento previsto (`time + 1h`); os dados não são duplicados nem salvos em novos arquivos.

Os notebooks documentam coleta, integração e demonstração de inferência. Os experimentos de desenvolvimento permanecem reproduzíveis pelos scripts em `src/`. Não execute `src.modelagem.Avaliar_Modelo_Final_Sprint5` novamente: a avaliação do holdout já foi realizada uma única vez. Não use esse holdout para escolher outro modelo, limiar ou conjunto de features.

Para executar os testes automatizados (com dados sintéticos), rode na raiz:

```powershell
.\.venv\Scripts\python.exe -m pytest tests
```

---

## Dados

| Fonte | Papel | Resolução | Natureza do dado | Período |
|---|---|---|---|---|
| Open-Meteo Air Quality API ([documentação](https://open-meteo.com/en/docs/air-quality-api)) | Qualidade do ar | Horária (dado nativo do domínio global a cada 3 horas, interpolado pela API) | Modelado (CAMS Global, para localidades fora da Europa) | 04/08/2022 a 31/08/2026 |
| Open-Meteo Historical Weather API ([documentação](https://open-meteo.com/en/docs/historical-weather-api)) | Clima | Horária | Reanálise (ERA5 / ERA5-Land / ECMWF IFS) | 04/08/2022 a 31/08/2026 |

Em 08/10/2026, o intervalo completo foi coletado e salvo: 35.736 horários em cada API, sem valores ausentes nas variáveis solicitadas, sem lacunas horárias e com timestamps idênticos. Os JSONs e o CSV originais de janeiro/2025 foram preservados. Consultas a datas anteriores a agosto/2022 retornaram horários sem valores de poluentes; em agosto/2022, os dados começaram em 03/08 às 21h, e 04/08 foi o primeiro dia completo.

### EDA inicial e avaliação temporal

A análise inicial encontrou 35.713 rótulos definidos e 904 positivos (2,53%). Antes de fixar o split, a série completa foi examinada descritivamente, incluindo taxas por ano e médias condicionadas à classe; por isso, o período 2025–2026 não é um teste totalmente cego. Nenhum modelo ou limiar foi treinado/selecionado com esses dados descritivos. Depois de fixado o split, as decisões de features e modelos foram baseadas no desenvolvimento (2022–2024); o holdout foi consultado uma única vez após congelar a escolha na validação.

Para preservar essa ordem temporal, a validação expansiva foi feita nos trimestres de 2024 e a janela de teste final cobre 2025–2026. Os intervalos são atribuídos pelo horário previsto (`time + 1h`), não apenas pelo horário das features:

| Partição | Registros | Positivos | Negativos |
|---|---:|---:|---:|
| Validação 2024-Q1 | 2.184 | 114 | 2.070 |
| Validação 2024-Q2 | 2.184 | 55 | 2.129 |
| Validação 2024-Q3 | 2.208 | 172 | 2.036 |
| Validação 2024-Q4 | 2.208 | 46 | 2.162 |
| Treino final (até antes de 2025) | 21.121 | 743 | 20.378 |
| Teste final (2025–2026) | 14.592 | 161 | 14.431 |

Em cada fold, o treino contém somente rótulos anteriores ao início do trimestre de validação; os trimestres anteriores são incorporados nos folds seguintes. A seleção final de modelo e limiar ocorreu na janela temporal 2024-Q4, sem consulta ao holdout. Como os 46 positivos do Q4 são uma amostra pequena, as métricas devem ser interpretadas com cautela.

**EDA detalhada inicial no desenvolvimento (rótulos com evento até 31/12/2024):** 21.121 linhas, 743 positivas (3,52%). A taxa positiva variou de 2,38% em 2022 a 4,41% em 2024; por mês, setembro foi 6,62%, março 5,65% e junho 1,04%. Por hora do evento, os picos foram 18h (13,30%), 17h (12,84%) e 19h (11,82%). São padrões exploratórios, sujeitos a variação temporal, não regras para um classificador.

Como candidatos a feature, os subíndices e o IQAr calculados até *t* estão disponíveis no instante da previsão e não usam diretamente o rótulo futuro. No desenvolvimento, a associação de Spearman com o alvo foi maior para `iqar_ozone` e `iqar` (ambos 0,317), `ozone` (0,297), `iqar_pm2_5` (0,215) e `pm2_5` (0,211). Medianas entre classe 0 e 1: ozônio 61 e 156 µg/m³; PM2,5 9 e 18,9 µg/m³; IQAr em *t* 26,85 e 118,33. Como o alvo é construído a partir dos mesmos poluentes e de janelas sobrepostas, essas associações não são evidência causal nem importância independente.

Na Sprint 3 foram comparados três grupos nos mesmos folds: (1) seis poluentes brutos + meteorologia; (2) seis subíndices e `iqar` + meteorologia; (3) poluentes brutos, subíndices e `iqar` + meteorologia. Depois, na Sprint 4, médias e deltas retrospectivos de ozônio e PM2,5 foram comparados ao grupo-base. A seleção de features ocorreu nos folds de desenvolvimento e pode apresentar viés de seleção; essa limitação está registrada na Sprint 4. Nenhuma feature usa diretamente valores futuros em relação a *t*.

Não há ausências nas variáveis brutas no desenvolvimento; `iqar_pm10`, `iqar_pm2_5`, `iqar_sulphur_dioxide` e `iqar` têm uma ausência cada, na borda inicial das janelas. A matriz de Spearman mostra associação elevada entre PM10/PM2,5 e seus índices derivados, esperada porque estes são transformações determinísticas; `iqar` também é o máximo dos subíndices. Isso indica redundância candidata, não justifica excluir features antes da comparação nos folds.

A EDA gráfica foi reproduzida em `src/analise/EDA_Desenvolvimento.py`, usando somente rótulos com evento previsto até 31/12/2024. Os gráficos mostram prevalência mensal variável, distribuições por classe em escala `log1p`, associações entre as features candidatas e máximos diários de CO/PM. O CO bruto chega a 3.838 µg/m³ (p99,9 = 2.832,04 µg/m³), PM10 a 152,7 µg/m³ e PM2,5 a 106,9 µg/m³; os três máximos ocorreram em 05/06/2023, em um episódio com vários horários elevados simultaneamente. Também aparecem episódios de particulados em maio–junho/2023 e setembro/2024. Não há medição local independente para confirmar os valores.

A cerca exploratória `Q3 + 1,5 × IQR` marca 1.118 horas para CO (5,29%), 1.132 para PM10 (5,36%) e 1.120 para PM2,5 (5,30%); 669 horas excedem simultaneamente as três cercas. Entre essas horas, as taxas positivas foram 3,13%, 14,49% e 13,57%, respectivamente, ante 3,52% no desenvolvimento todo. Como as observações são horárias e autocorrelacionadas, essas taxas não são evidência causal nem observações independentes. A classe usa as janelas CETESB e o evento em *t+1h*, não o valor bruto isolado: no episódio de 05/06/2023, os máximos matinais de CO/PM tiveram rótulo negativo; mais tarde, o subíndice de ozônio elevou o IQAr acima de 100, produzindo rótulos positivos para eventos previstos entre 16h e 22h. As cercas são apenas triagem estatística; nenhum valor foi removido ou limitado.

Para reproduzir a análise, execute `.\.venv\Scripts\python.exe -m src.analise.EDA_Desenvolvimento` na raiz do projeto. As imagens geradas estão em [prevalência mensal](reports/figures/eda_desenvolvimento/prevalencia_mensal.png), [boxplots das concentrações](reports/figures/eda_desenvolvimento/boxplots_concentracoes_log1p.png), [correlação de Spearman](reports/figures/eda_desenvolvimento/correlacao_spearman_features.png) e [extremos no tempo](reports/figures/eda_desenvolvimento/extremos_concentracoes_tempo.png). Esta EDA usa apenas desenvolvimento; o holdout não foi usado para produzir esses gráficos.

Para uma explicação não técnica da origem e do propósito dos dados, dos cálculos, dos gráficos, dos resultados e de suas limitações, consulte o [relatório auxiliar da EDA](docs/Relatorio_EDA_Desenvolvimento.md).

**Primeiros baselines e ablação (Sprint 3):** nos folds de validação de 2024, a persistência pelo IQAr em *t* obteve F1 positivo médio 0,8196. O Gaussian Naive Bayes obteve F1 médio 0,4134 com poluentes brutos, 0,6175 com subíndices/IQAr e 0,5914 com os dois grupos. Remover o `iqar` consolidado reduziu os falsos positivos de 476 para 402 no grupo somente de subíndices, mas no grupo combinado houve aumento de 537 para 542; a ablação também não reduziu a taxa elevada de setembro em Q3. São resultados exploratórios daquele estágio, sem ajuste de limiar e sem uso do holdout; a seleção final ocorreu posteriormente na Sprint 5. O script é `.\.venv\Scripts\python.exe -m src.modelagem.Avaliar_Baselines`; consulte as [métricas por fold](reports/modeling/baseline_metrics_by_fold.csv), o [resumo](reports/modeling/baseline_metrics_summary.csv), os [casos classificados incorretamente](reports/modeling/baseline_misclassified_cases.csv), as [taxas de erro por mês](reports/modeling/baseline_error_rates_by_month.csv) e o [resumo da ablação](reports/modeling/baseline_iqar_ablation_summary.csv).

**Critério de alertas definido pela equipe:** evitar falsos negativos, aceitando a possibilidade de mais falsos alertas; uma hora prevista como negativa encerra o episódio e o limite é de até três episódios iniciados por semana. Um episódio que atravessa a virada da semana é contado na semana em que começou. Ainda não há teto definido para horas de alerta. Para a entrega final, a equipe congelou Random Forest com limiar 0,3 na validação; o teste final foi consultado uma vez e resultou em uma semana completa acima do teto, sem reutilização para ajustes.

Uma varredura exploratória de 101 limiares em trimestres internos anteriores aos folds externos está disponível em [métricas por janela](reports/modeling/baseline_threshold_tradeoff_by_inner_fold.csv), [resumo do trade-off](reports/modeling/baseline_threshold_tradeoff_summary.csv) e [carga semanal de episódios](reports/modeling/baseline_threshold_alert_episodes_by_week.csv). No grupo de subíndices sem `iqar`, os cenários 0,25 e 0,50 excederam o teto semanal em 21 das 52 semanas completas, com máximos de 6 e 7 episódios e cargas máximas de 90 e 85 horas de alerta por semana. Nenhum limiar entre 0,01 e 0,99 respeitou o teto em todas as semanas. Os extremos também não são adequados: 0,00 emitiu alerta por todas as 8.784 horas e produziu 8.340 falsos positivos; 1,00 deixou 384 dos 444 positivos sem alerta. São cenários internos exploratórios da etapa anterior à Sprint 5, não limiares selecionados nem estimativas de operação futura. A contagem semanal une as janelas internas antes de agrupar episódios e não mede acerto na detecção de episódios reais; esses relatórios não usaram o holdout. A avaliação final do holdout foi feita separadamente, uma única vez, conforme documentado na Sprint 5.

**Sprint 4 — triagem temporal:** `.\.venv\Scripts\python.exe -m src.modelagem.Avaliar_Features_Temporais` comparou, nos folds de 2024 e sem ajustar limiar, diferenças horárias de ozônio/PM2,5 e de variáveis meteorológicas, além de hora do dia cíclica, com o grupo-base de subíndices sem `iqar`. Os deltas brutos de ozônio e PM2,5 mudaram o recall de 0,9949 para 0,9971 (FN de 3 para 2), mas aumentaram FP de 402 para 411 e reduziram ligeiramente F1; a hora cíclica elevou FP para 435 e reduziu F1, embora diminuísse o pico de horas de alerta semanal de 85 para 69. Essas variantes não foram incorporadas ao conjunto final. Métricas reproduzíveis: [por fold](reports/modeling/temporal_feature_metrics_by_fold.csv), [resumo](reports/modeling/temporal_feature_metrics_summary.csv) e [carga semanal](reports/modeling/temporal_feature_alert_burden_by_week.csv). A triagem não consultou o holdout.

Uma segunda triagem adicionou médias retrospectivas de 3h e mudanças em 2h para ozônio e PM2,5. No comparativo formal S3→S4, a variante combinada teve 0 FN contra 3 no grupo-base e reduziu os picos semanais de 7 para 6 episódios e de 85 para 76 horas. A troca foi aumento de FP (471, +69), redução de F1 (0,6261 ante 0,6669) e nenhuma redução nas semanas acima do teto de três episódios (19). Como o projeto prioriza evitar falsos negativos, as quatro features foram mantidas no conjunto congelado para a Sprint 5. A triagem nos folds de desenvolvimento pode introduzir viés de seleção; os resultados do teste final e essa limitação estão descritos adiante e no diário da Sprint 5. Resultados da triagem: [métricas por fold](reports/modeling/short_term_feature_metrics_by_fold.csv), [resumo](reports/modeling/short_term_feature_metrics_summary.csv) e [carga semanal](reports/modeling/short_term_feature_alert_burden_by_week.csv). Comparativo formal: [lift por fold](reports/modeling/sprint4_lift_by_fold.csv), [resumo S3→S4](reports/modeling/sprint4_lift_summary.csv) e [carga semanal](reports/modeling/sprint4_alert_burden_by_week.csv).

**Sprint 5 — modelagem e avaliação final:** `.\.venv\Scripts\python.exe -m src.modelagem.Comparar_Modelos_Sprint5` comparou Dummy, persistência, Gaussian Naive Bayes S4, regressão logística balanceada e Random Forest balanceada em 2024-Q4. A regressão logística usa `max_iter=1000` e `random_state=42`; a Random Forest usa 300 árvores, `min_samples_leaf=2` e `random_state=42`. Na validação (2.208 horas, 46 positivos), a equipe congelou Random Forest com limiar 0,3: recall 1,0, precisão 0,7797, F1 0,8440, 13 FP e nenhuma semana completa acima do teto de três episódios (máximo de três). A avaliação final foi executada uma vez: no holdout (14.592 horas, 161 positivos), a combinação congelada teve recall 0,9814, precisão 0,7822, F1 0,8705, TN=14.387, FP=44, FN=3 e TP=158. Uma semana das 86 completas excedeu o teto: pico de cinco episódios e 31 horas de alerta. Os comparadores também foram medidos no mesmo holdout, mas não houve novo ajuste ou troca após consultá-lo; a regressão logística teve métricas superiores no teste, mas não substituiu o modelo congelado. Os três falsos negativos ocorreram em 27/12/2025 14h, 28/12/2025 13h e 31/12/2025 15h. Relatórios de validação: [métricas](reports/modeling/sprint5_validation_metrics.csv), [trade-off de limiares](reports/modeling/sprint5_validation_threshold_tradeoff.csv), [carga semanal](reports/modeling/sprint5_validation_alert_burden_by_week.csv) e [previsões](reports/modeling/sprint5_validation_predictions.csv). Relatórios finais: [métricas](reports/modeling/sprint5_final_test_metrics.csv), [erros](reports/modeling/sprint5_final_test_misclassified_cases.csv) e [carga semanal](reports/modeling/sprint5_final_test_alert_burden_by_week.csv). Pipeline empacotado em `models/modelo_final_sprint5.joblib`.

**Limitações identificadas na coleta** (segundo [Sprint 1](docs/sprints/Sprint1_TrilhaB.md)):
- As APIs retornam a coordenada da célula de grade do modelo, que pode diferir ligeiramente da coordenada solicitada (-23.514561, -46.186832). Essa diferença é esperada em dado modelado ou de reanálise e não constitui erro de coleta, mas deve ser considerada na interpretação dos resultados.
- Tanto os arquivos de janeiro/2025 quanto a coleta ampliada não apresentaram valores nulos nas variáveis solicitadas; no período ampliado, as duas fontes também têm timestamps alinhados e sem lacunas.

### Documentação oficial das APIs

**Open-Meteo Air Quality API**
- Endpoint: `GET https://air-quality-api.open-meteo.com/v1/air-quality`
- Parâmetros obrigatórios: `latitude`, `longitude`
- Parâmetros utilizados pelo projeto: `hourly` (lista de poluentes), `start_date`, `end_date`, `timezone=America/Sao_Paulo`
- Resolução temporal: a série é entregue como horária, mas para coordenadas fora da Europa o dado é originado do domínio CAMS Global, cuja resolução nativa do modelo é de 3 em 3 horas. Os valores horários intermediários são interpolados pela API e não constituem observações independentes.
- Período histórico disponível na fonte: domínio global (fora da Europa), a partir de agosto de 2022; domínio europeu possui reanálise desde 2013, não aplicável a este projeto.
- Limitações: dado modelado (CAMS), não corresponde a medição direta de estação; resolução espacial de aproximadamente 45 km fora da Europa. Embora a documentação descreva `past_days` como limitado a 0–92 dias, a consulta histórica com `start_date`/`end_date` para o intervalo deste projeto foi validada empiricamente em 08/10/2026; esse comportamento deve ser revalidado se a API mudar.

**Open-Meteo Historical Weather API**
- Endpoint: `GET https://archive-api.open-meteo.com/v1/archive`
- Parâmetros obrigatórios: `latitude`, `longitude`, `start_date`, `end_date`
- Parâmetros utilizados pelo projeto: `hourly` (lista de variáveis meteorológicas), `timezone=America/Sao_Paulo`
- Resolução temporal: horária, nativa.
- Período histórico disponível na fonte: reanálise ERA5 desde 1940 (resolução de 0,25°); ERA5-Land desde 1950 (resolução de 0,1°); ECMWF IFS desde 2017 (resolução de 9 km). Não constitui fator limitante para este projeto.
- Limitações: dado de reanálise, combinando estações, satélite, radar e modelo; não corresponde a medição direta pontual e pode divergir de estação local em eventos de curta duração, como chuva convectiva isolada.

**Unidade de análise:** cada linha corresponde a uma observação horária no ponto de coleta (-23.514561, -46.186832, Mogi das Cruzes/SP, fuso horário `America/Sao_Paulo`), conforme definido no RFC.

**N após o merge:** 744 registros no arquivo legado de janeiro/2025 e 35.736 no arquivo do período ampliado (`dados_merged_2022-08-04_2026-08-31.csv`).

**Split temporal:** implementado em `src/validacao/Separacao_Temporal.py`. Os folds expansivos de validação usam os quatro trimestres de 2024; o teste final cobre 2025–2026. Os limites são configurados em `config/params.yaml` e atribuídos pela hora do rótulo (`time + 1h`).

**Dicionário de dados:** `docs/Dicionario_de_Dados.md`.

### Variáveis coletadas

O critério de classe positiva adotado é IQAr > 100, incluindo categorias mais graves; classe 0 corresponde a IQAr <= 100. O cálculo implementado segue a Tabela 2.7 e a seção 2.3 do relatório CETESB 2025: cada poluente recebe um subíndice por interpolação linear, e o IQAr é o maior entre os seis subíndices.

| Poluente | Janela móvel terminando no horário avaliado |
|---|---:|
| `pm10`, `pm2_5`, `sulphur_dioxide` | 24 horas |
| `ozone`, `carbon_monoxide` | 8 horas |
| `nitrogen_dioxide` | 1 hora |

Como a API retorna CO em µg/m³ e a tabela CETESB usa ppm, a concentração média de CO é convertida pela lei dos gases ideais a 25 °C e 1 atm antes do cálculo do subíndice. O rótulo da linha *t* usa o IQAr calculado no horário *t+1h*. Se faltar dado necessário em qualquer janela de qualquer um dos seis poluentes, o IQAr e o rótulo daquele horário ficam indefinidos; o rótulo não é imputado. Os subíndices e o IQAr calculados no instante *t* são colunas de auditoria/características candidatas; nenhum valor posterior a *t* deve entrar nas features.

Esse alvo é uma estimativa metodológica baseada em concentrações horárias modeladas/interpoladas pela Open-Meteo; não é o IQAr oficial de uma estação CETESB. Na base completa, há 904 positivos entre 35.713 rótulos definidos (2,53%). O CSV de janeiro/2025 foi a amostra inicial preservada; a avaliação final foi definida para 2025–2026, com 161 positivos em 14.592 linhas.

| Variável | Fonte | Unidade | Justificativa | Papel |
|---|---|---|---|---|
| `pm10` | Air Quality | µg/m³ | Poluente regulado pelo IQAr; indicador de material particulado grosso, associado a queimadas e poeira urbana. | Feature em *t*; alvo usa média móvel de 24h até *t+1h* |
| `pm2_5` | Air Quality | µg/m³ | Poluente regulado pelo IQAr; partícula fina com maior impacto respiratório, frequentemente responsável pelo subíndice mais crítico em áreas urbanas. | Feature em *t*; alvo usa média móvel de 24h até *t+1h* |
| `carbon_monoxide` | Air Quality | µg/m³ | Poluente regulado pelo IQAr; indicador de queima incompleta, associado a tráfego e queimadas. | Feature em *t*; alvo usa média móvel de 8h até *t+1h* e conversão para ppm |
| `nitrogen_dioxide` | Air Quality | µg/m³ | Poluente regulado pelo IQAr; associado a emissões veiculares. | Feature em *t*; alvo usa concentração de 1h em *t+1h* |
| `sulphur_dioxide` | Air Quality | µg/m³ | Poluente regulado pelo IQAr; associado à queima de combustíveis fósseis industriais. | Feature em *t*; alvo usa média móvel de 24h até *t+1h* |
| `ozone` | Air Quality | µg/m³ | Poluente regulado pelo IQAr; formado fotoquimicamente, sensível a temperatura e radiação solar. | Feature em *t*; alvo usa média móvel de 8h até *t+1h* |
| `temperature_2m` | Historical Weather | °C | Influencia a formação de ozônio e a dispersão vertical dos poluentes. | Feature |
| `relative_humidity_2m` | Historical Weather | % | Afeta a permanência de material particulado em suspensão. | Feature |
| `precipitation` | Historical Weather | mm | A chuva remove particulados da atmosfera por lavagem úmida, explicando quedas súbitas de concentração. | Feature |
| `wind_speed_10m` | Historical Weather | km/h | O vento dispersa poluentes; velocidades baixas favorecem acúmulo e picos de concentração. | Feature |
| `pressure_msl` | Historical Weather | hPa | Associada à estabilidade atmosférica; pressão alta e vento fraco favorecem inversões térmicas e acúmulo de poluentes. | Feature |

**Atenção ao risco de vazamento:** os seis poluentes desempenham dupla função — como candidatos a feature nos valores disponíveis até *t* e como insumos do alvo nas janelas que terminam em *t+1h*. As colunas calculadas no horário *t+1h* são usadas apenas para gerar `qualidade_ar_inadequada_1h` e não integram as features do modelo. O cálculo do alvo, o split temporal e o conjunto congelado de features da Sprint 4 estão implementados; as features são retrospectivas e usam dados disponíveis até *t*. A avaliação final já foi concluída, com as limitações registradas na Sprint 5.

---

## Modelo

| Item | Status |
|---|---|
| Baseline | Dummy prior, persistência pelo IQAr em *t* e Gaussian Naive Bayes com features S4 |
| Modelo selecionado | Random Forest balanceada, 300 árvores, `min_samples_leaf=2`, `random_state=42` |
| Limiar de decisão | 0,3, congelado na validação temporal 2024-Q4 |
| Métrica principal no teste | Recall 0,9814 da classe positiva; 3 FN e 44 FP |
| Resultado da regra semanal | 1 de 86 semanas completas excedeu o teto de 3 episódios; pico de 5 episódios e 31 horas de alerta |
| Artefato | `models/modelo_final_sprint5.joblib` (pipeline, features e limiar) |

O modelo usa os sete subíndices individuais dos poluentes, cinco variáveis meteorológicas e quatro atributos retrospectivos: médias móveis de 3h e deltas de 2h de ozônio e PM2,5. Não usa o IQAr consolidado nem o alvo futuro como entrada. Imputação pela mediana e `StandardScaler` são ajustados dentro do pipeline de treino. As métricas descrevem este conjunto temporal e não garantem desempenho futuro nem prontidão para uso operacional.

**Limitações e interpretação:** os dados de qualidade do ar são do CAMS Global, têm resolução nativa de 3h fora da Europa e valores horários interpolados; clima vem de reanálise, não de medição direta local. A série foi analisada descritivamente antes da definição do split, portanto o holdout não é totalmente cego. A triagem de features nos folds também pode introduzir viés de seleção. O modelo é um protótipo acadêmico, não um sistema de alerta oficial ou orientação de saúde.

---

## Estrutura do repositório

Arquitetura de referência do projeto, com indicação do que já está implementado:

```text
Ciencia-de-Dados-e-Aprendizagem-de-Maquina/
├── README.md
├── LICENSE                           # concluído (MIT)
├── requirements.txt                  # concluído
├── config/
│   └── params.yaml                   # configurado para o período validado
├── data/
│   ├── raw/                          # JSONs de janeiro/2025 e arquivos versionados do período ampliado
│   └── interim/                      # merge e dados rotulados do período ampliado
├── notebooks/
│   ├── 01_Coleta_Dados.ipynb         # consulta APIs e salva os JSONs brutos
│   ├── 02_Merge_Dados.ipynb          # audita horários e integra as fontes
│   └── 03_Demonstracao_Modelo_Final.ipynb # demonstra inferência com o modelo empacotado
├── src/
│   ├── coleta/
│   │   └── Coleta_Dados.py           # concluído; não sobrescreve outro período
│   ├── transformacao/
│   │   ├── Merge_Dados.py            # merge versionado por período
│   │   ├── Calcular_Alvo_IQAr.py      # subíndices CETESB e rótulo t+1h
│   │   └── Features_Temporais.py     # atributos retrospectivos
│   ├── analise/                      # EDA de desenvolvimento
│   ├── validacao/
│   │   └── Separacao_Temporal.py     # folds expansivos e teste final por horário-alvo
│   └── modelagem/                    # baselines, comparativos, avaliação e empacotamento
├── models/                           # pipeline final joblib
├── reports/                          # métricas, previsões, erros e figuras
├── tests/                            # testes automatizados
├── docs/
│   ├── RFC.md
│   ├── Dicionario_de_Dados.md
│   ├── Relatorio_EDA_Desenvolvimento.md
│   └── sprints/                      # registros e decisões das Sprints 1–5
```

A pasta `data/` contém os arquivos de entrada e processamento versionados neste projeto. O diretório `data/processed/` não faz parte do fluxo atual; os artefatos usados pela modelagem ficam em `data/interim/`.

---

## Trabalho realizado na Sprint 1 (registro histórico)

- Configuração centralizada (local, latitude, longitude, datas, fuso horário), sem valores fixados diretamente no código de coleta.
- Requisições às duas fontes exigidas pela Trilha B (qualidade do ar e clima), com `timeout=30` e `raise_for_status()`.
- Dados brutos preservados sem transformação em `data/raw/`; a coleta ampliada passou a usar nomes versionados pelo período e preservou os arquivos legados de janeiro/2025.
- RFC formalizado, com evento, horizonte, classe positiva, custo de falso negativo, documentação das APIs e tabela de variáveis.
- Dicionário de dados v0.1 criado.
- `requirements.txt` e `LICENSE` (MIT) adicionados ao repositório.

## Encerramento acadêmico e de equipe

> As pendências técnicas abaixo foram concluídas nas Sprints seguintes. Permanecem como tarefas de organização acadêmica os registros individuais e decisões formais que só a equipe pode confirmar.

| Item a confirmar pela equipe | Situação |
|---|---|
| Definir Scrum Master e atualizar eventuais registros do Scrum | Não definido neste repositório |
| Completar diários, contribuições individuais, feedbacks e rubricas da disciplina | Depende dos integrantes/docente |
| Confirmar usuário decisor operacional do caso de uso | Ainda não definido; escopo permanece acadêmico |

As entregas técnicas inicialmente listadas — coleta ampliada, validação de esquema e merge, alvo e split temporal, notebooks, EDA, engenharia/comparação de features, modelagem e documentação — estão descritas nas seções anteriores e nos diários das Sprints 1–5.

---

## Documentação

- [RFC e decisões de escopo](docs/RFC.md)
- [Dicionário de dados](docs/Dicionario_de_Dados.md)
- [Relatório EDA e guia passo a passo](docs/Relatorio_EDA_Desenvolvimento.md)
- [Sprint 1 — coleta e definição do problema](docs/sprints/Sprint1_TrilhaB.md)
- [Sprint 2 — EDA e preparação](docs/sprints/Sprint2_TrilhaB.md)
- [Sprint 3 — baselines e comparação inicial](docs/sprints/Sprint3_TrilhaB.md)
- [Sprint 4 — atributos temporais e comparação formal](docs/sprints/Sprint4_TrilhaB.md)
- [Sprint 5 — modelo final, avaliação e model card](docs/sprints/Sprint5_TrilhaB.md)
- [Demonstração interativa do pipeline](notebooks/03_Demonstracao_Modelo_Final.ipynb)
