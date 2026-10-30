<div align="center">
  <img src="docs/assets/logo.png" alt="Logo ArPrev" width="180" style="border-radius: 20px; box-shadow: 0 4px 14px rgba(0,0,0,0.15);" />

  # ArPrev — Foco na Antecipação de Condições Inadequadas
  ### Previsão Preditiva de Risco Respiratório (IQAr > 100) — Campus UBC / Mogi das Cruzes (SP)

  [![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
  [![Streamlit App](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B.svg)](streamlit_app.py)
  [![Artigo Web](https://img.shields.io/badge/GitHub%20Pages-Artigo%20T%C3%A9cnico-059669.svg)](https://diogogomesb.github.io/Ciencia-de-Dados-e-Aprendizagem-de-Maquina/)
  [![Pytest](https://img.shields.io/badge/tests-43%20passed-brightgreen.svg)](tests/)

</div>

---

**Disciplina:** Ciência de Dados e Aprendizado de Máquina  
**Título do Projeto:** ArPrev — Foco na antecipação de condições inadequadas (Previsão de Qualidade do Ar Inadequada na Região da Faculdade UBC / Mogi das Cruzes - SP)  
**Trilha:** B — Qualidade do ar inadequada  
**Repositório:** [DiogoGomesB/Ciencia-de-Dados-e-Aprendizagem-de-Maquina](https://github.com/DiogoGomesB/Ciencia-de-Dados-e-Aprendizagem-de-Maquina)  
**Artigo Técnico (GitHub Pages):** [https://diogogomesb.github.io/Ciencia-de-Dados-e-Aprendizagem-de-Maquina/](https://diogogomesb.github.io/Ciencia-de-Dados-e-Aprendizagem-de-Maquina/)  
**Licença:** MIT (arquivo `LICENSE` no repositório)

---

## 📑 Tópicos do Projeto

1. [Equipe de Desenvolvimento](#1-equipe-de-desenvolvimento-sistemas-de-informação--ubc-20262)
2. [Estado Atual do Projeto](#2-estado-atual-do-projeto)
3. [O Problema e Contexto Operacional](#3-o-problema-e-contexto-operacional)
4. [Escopo — Canvas de Kickoff (As 8 Perguntas)](#4-escopo--canvas-de-kickoff-as-8-perguntas)
5. [Quadro de Observação do Grupo](#5-quadro-de-observação-do-grupo)
6. [Como Reproduzir e Executar](#6-como-reproduzir-e-executar)
7. [Dados e Auditoria Temporal](#7-dados-e-auditoria-temporal)
8. [Modelo Preditivo e Comparativo de Algoritmos](#8-modelo-preditivo-e-comparativo-de-algoritmos)
9. [Estrutura do Repositório](#9-estrutura-do-repositório)
10. [Trabalho Realizado e Encerramento Acadêmico](#10-trabalho-realizado-e-encerramento-acadêmico)
11. [Documentação e Links Oficiais](#11-documentação-e-links-oficiais)

---

## 1. Equipe de Desenvolvimento (Sistemas de Informação · UBC 2026/2)

<table align="center">
  <tr>
    <td align="center" width="20%">
      <a href="https://github.com/Davigamasan">
        <img src="docs/assets/autores/davi.jpg" width="95px" height="95px" alt="Davi Gama dos Santos" style="border-radius:50%; object-fit:cover;"/><br />
        <sub><b>Davi Gama dos Santos</b></sub>
      </a><br />
      <sub>Sistemas de Informação</sub><br />
      <a href="https://github.com/Davigamasan">💻 GitHub</a> · <a href="https://www.linkedin.com/in/davigama">👔 LinkedIn</a>
    </td>
    <td align="center" width="20%">
      <a href="https://github.com/DiogoGomesB">
        <img src="docs/assets/autores/diogo.jpg" width="95px" height="95px" alt="Diogo Gomes Barbosa" style="border-radius:50%; object-fit:cover;"/><br />
        <sub><b>Diogo Gomes Barbosa</b></sub>
      </a><br />
      <sub>Sistemas de Informação</sub><br />
      <a href="https://github.com/DiogoGomesB">💻 GitHub</a> · <a href="https://www.linkedin.com/in/diogo-gomes-barbosa/">👔 LinkedIn</a>
    </td>
    <td align="center" width="20%">
      <a href="https://github.com/Eudenis-dev">
        <img src="docs/assets/autores/eudenis.jpg" width="95px" height="95px" alt="Eudenis de Souza Vieira" style="border-radius:50%; object-fit:cover;"/><br />
        <sub><b>Eudenis de Souza Vieira</b></sub>
      </a><br />
      <sub>Sistemas de Informação</sub><br />
      <a href="https://github.com/Eudenis-dev">💻 GitHub</a> · <a href="https://www.linkedin.com/in/eudenis-vieira-72507b311/?isSelfProfile=true">👔 LinkedIn</a>
    </td>
    <td align="center" width="20%">
      <a href="https://github.com/gabriel-januario891">
        <img src="docs/assets/autores/gabriel.jpg" width="95px" height="95px" alt="Gabriel Januário Alves" style="border-radius:50%; object-fit:cover;"/><br />
        <sub><b>Gabriel Januário Alves</b></sub>
      </a><br />
      <sub>Sistemas de Informação</sub><br />
      <a href="https://github.com/gabriel-januario891">💻 GitHub</a> · <a href="https://www.linkedin.com/in/gabriel-alves-1a50611aa">👔 LinkedIn</a>
    </td>
    <td align="center" width="20%">
      <a href="https://github.com/JoaoPedro19102">
        <img src="docs/assets/autores/joao.jpg" width="95px" height="95px" alt="João Pedro Barreto da Silva" style="border-radius:50%; object-fit:cover;"/><br />
        <sub><b>João Pedro Barreto da Silva</b></sub>
      </a><br />
      <sub>Sistemas de Informação</sub><br />
      <a href="https://github.com/JoaoPedro19102">💻 GitHub</a> · <a href="https://www.linkedin.com/in/jo%C3%A3o-pedro-barreto-b5a439205/?isSelfProfile=true">👔 LinkedIn</a>
    </td>
  </tr>
</table>

---

## 2. Estado Atual do Projeto

Situação técnica verificada em 09/10/2026; o fluxo operacional +1h e projeções +7h/+24h (`src/aplicacao/Prever_Proxima_Hora.py` e notebooks 01–03), o experimento comparativo completo com Árvore de Decisão, Random Forest e XGBoost (`src/modelagem/Experimento_Arvores_Artigo.py`), o Dashboard no Streamlit (`streamlit_app.py`) e o Artigo Técnico em página web (`docs/index.html`) foram concluídos e validados em 29/10/2026. Todos os registros de Scrum, diários de bordo (`DIARIO.md` e `docs/sprints/`), feedbacks e rubricas estão preenchidos pela equipe.

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
| Pipeline final | Empacotado | `models/modelo_final_sprint5.joblib`; previsão +1h com dados recentes em `notebooks/03_Previsao_Proxima_Hora.ipynb` e `src/aplicacao/` |
| Relatórios de análise e modelagem | Gerados | `reports/`; incluem validação, teste final, erros e carga semanal |
| Testes automatizados | 43 aprovados | `tests/`; cobrem coleta com retry, alvo, split, features, baselines, comparativo de árvores (CART/RF/XGBoost), avaliação, empacotamento, previsão +1h e projeção +7h/+24h |
| Dashboard Streamlit | Concluído | `streamlit_app.py`; 2 abas (1. Previsão Atual ao vivo na API; 2. Desempenho Histórico) |
| Artigo Técnico Web | Concluído | [`docs/index.html`](https://diogogomesb.github.io/Ciencia-de-Dados-e-Aprendizagem-de-Maquina/) — publicado no [GitHub Pages](https://diogogomesb.github.io/Ciencia-de-Dados-e-Aprendizagem-de-Maquina/); comparativo didático de CART, Random Forest e XGBoost |
| Diário de Bordo e `.env.example` | Concluídos | `DIARIO.md` na raiz + `docs/sprints/Sprint1_TrilhaB.md` a `Sprint5_TrilhaB.md` |
| `requirements.txt` | Concluída | — |
| `LICENSE` | Concluída | MIT |

---

## 3. O Problema e Contexto Operacional

| Item | Definição |
|---|---|
| Evento a prever | A qualidade do ar em Mogi das Cruzes/SP estará inadequada na próxima hora. |
| Usuário da decisão | Coordenação de Infraestrutura e Esportes da UBC (suspensão preventiva de atividades físicas externas e ajuste de ventilação) e Defesa Civil de Mogi das Cruzes. O fluxo operacional +1h fornece apoio à decisão em tempo real. |
| Horizonte | Uma hora à frente — a previsão realizada no instante *t* utiliza dados disponíveis até *t* para estimar a condição em *t+1h*. |
| Classe positiva | Classe 0: IQAr <= 100. Classe 1: IQAr > 100, incluindo as categorias mais graves. O índice consolidado é o maior subíndice dos seis poluentes, conforme a metodologia CETESB 2025. |
| Custo priorizado | Falso negativo — o modelo prever "adequada" quando a condição real na hora seguinte é inadequada. Considerado o erro mais grave, pois compromete a antecipação de uma piora real da qualidade do ar. |

Status: alvo, split temporal, EDA, comparação S3→S4, pipeline de features congelado e comparação de modelos estão implementados. A Sprint 5 congelou Random Forest com limiar 0,3 na validação, avaliou o holdout uma única vez e empacotou o pipeline. A demonstração in-sample do modelo foi substituída pelo fluxo operacional: o notebook e o script de previsão usam dados recentes das APIs e estimam a hora seguinte. As métricas de desempenho continuam sendo as do holdout; a previsão operacional não mede desempenho nem é uma medição do ar.

**Referências**
[1] FURG — Dissertação/monografia sobre padrões de qualidade do ar: https://sistemas.furg.br/sistemas/sab/arquivos/bdtd/0000010377.pdf
[2] SANTOS, C. M. dos. UnB, 2011 — Índice de Qualidade do Ar: https://repositorio.unb.br/bitstream/10482/10977/1/2011_CleideMouradosSantos.pdf
[3] CETESB (2025), *Relatório de Metodologia para Avaliação da Qualidade do Ar*, Tabela 2.7 e seção 2.3, pp. 18–20: [PDF oficial](https://www.cetesb.sp.gov.br/dx/api/dam/v1/collections/186909e9-ab59-4641-abba-c5c465793216/items/3adb602d-77ec-4de5-b378-5fa141e80614/renditions/5a0e5f05-41aa-4e9c-9b00-69165ab36963/versions/1?binary=true).
[4] BREIMAN, L. (2001). *Random Forests*. Machine Learning, 45(1), 5–32.
[5] CHEN, T.; GUESTRIN, C. (2016). *XGBoost: A Scalable Tree Boosting System*. KDD '16, pp. 785–794.

---

## 4. Escopo — Canvas de Kickoff (As 8 Perguntas)

| # | Pergunta do Canvas | Resposta Definida pelo Grupo (Trilha B — Qualidade do Ar) |
|---:|---|---|
| **1** | **Qual evento temporal será antecipado?** | A ocorrência de um período horário de **qualidade do ar inadequada / risco respiratório** ($\text{IQAr} > 100$, englobando as faixas *Ruim*, *Muito Ruim* e *Péssima* da CETESB). |
| **2** | **Qual a delimitação de região ou município?** | Ponto de referência do campus da **Universidade Braz Cubas (UBC)**, em **Mogi das Cruzes – SP** (`latitude = -23.514561`, `longitude = -46.186832`, fuso `America/Sao_Paulo`), escolhido pela concentração diária de estudantes, práticas esportivas universitárias e proximidade com vias urbanas e serra. |
| **3** | **Qual é o exato horizonte de previsão de risco?** | **1 hora à frente (`t + 1h`)** como horizonte oficial validado estatisticamente (usando apenas dados até o instante $t$ para prever a condição em $t+1\text{h}$), complementado no dashboard e nos notebooks por projeções experimentais de **+7 horas (próximo turno)** e **+24 horas (dia completo)**. |
| **4** | **Qual a tolerância a Falsos Positivos versus Falsos Negativos?** | **Baixíssima tolerância a Falsos Negativos (FN)**. Deixar de emitir um alerta quando o ar ficará inadequado expõe alunos, atletas e grupos sensíveis a poluentes nocivos sem proteção. Um Falso Positivo (FP) gera apenas cautela preventiva (transferir treino para quadra coberta). Por isso, a **métrica principal é o Recall da classe positiva (combinado ao F1-Score)** e o teto operacional é de até 3 episódios de alerta por semana. |
| **5** | **Quem utilizará o alerta e qual ação ele engatilha?** | **Coordenação de Infraestrutura e Esportes da UBC** e **Defesa Civil de Mogi das Cruzes**. Ação engatilhada: suspender ou transferir atividades físicas ao ar livre para ambientes internos, ajustar a renovação de ar e emitir aviso preventivo à comunidade acadêmica. |
| **6** | **Como será matematicamente definida a Classe Positiva?** | $Y_{t+1} = 1 \iff \text{IQAr}(t+1) > 100$ e $Y_{t+1} = 0 \iff \text{IQAr}(t+1) \le 100$, onde $\text{IQAr} = \max(I_{\text{PM10}}, I_{\text{PM2,5}}, I_{\text{O3}}, I_{\text{CO}}, I_{\text{NO2}}, I_{\text{SO2}})$ calculado por interpolação linear nas faixas normativas da **Tabela 2.7 da CETESB (2025)**. Na base histórica (`35.713` rótulos), a classe positiva representa `2,53%` (`904` horas críticas), confirmando um problema de eventos raros. |
| **7** | **Quais dados estarão disponíveis no instante da predição?** | Exclusivamente as **15 variáveis observadas até o instante $t$ (`FEATURES_SPRINT4`)**: os 6 subíndices individuais em $t$ (`iqar_pm10`, `iqar_pm2_5`, `iqar_carbon_monoxide`, `iqar_nitrogen_dioxide`, `iqar_sulphur_dioxide`, `iqar_ozone`), as 5 variáveis meteorológicas em $t$ (`temperature_2m`, `relative_humidity_2m`, `precipitation`, `wind_speed_10m`, `pressure_msl`) e 4 resumos retrospectivos de curto prazo (`media_3h_ozone`, `media_3h_pm2_5`, `delta_2h_ozone`, `delta_2h_pm2_5`). Nenhum dado de $t+1\text{h}$ entra nas features. |
| **8** | **Qual API base fornecerá a disponibilidade histórica completa?** | **Open-Meteo Air Quality API** (domínio CAMS Global / ECMWF) e **Open-Meteo Historical Weather API** (reanálise ERA5 / IFS), cobrindo de **04/08/2022 a 31/08/2026** (`35.736` registros horários alinhados, sem valores nulos nas variáveis brutas). |

---

## 5. Quadro de Observação do Grupo

| Dimensão | Registro Fundamentado da Equipe |
|---|---|
| **Duas referências analisadas** | **1. CETESB (2025) — *Relatório de Metodologia para Avaliação da Qualidade do Ar*:** forneceu a regra matemática exata de cálculo dos 6 subíndices por janelas móveis (24h para $\text{PM}_{10}$, $\text{PM}_{2,5}$ e $\text{SO}_2$; 8h para $\text{O}_3$ e $\text{CO}$; 1h para $\text{NO}_2$), conversão de CO pela lei dos gases ideais ($\mu\text{g/m}^3 \to \text{ppm}$) e o corte normativo $\text{IQAr} > 100$.<br>**2. Santos (UnB, 2011) & FURG (Padrões de Qualidade do Ar):** embasaram a relação entre meteorologia (temperatura, radiação solar, vento fraco e estabilidade atmosférica) e os picos vespertinos de ozônio troposférico e particulados em áreas urbanas brasileiras. |
| **Três decisões do grupo** | **Decisão 1 (Ablação do `iqar` agregado na Sprint 3):** retirar a coluna `iqar` consolidada das features de entrada e manter apenas os 6 subíndices individuais, eliminando redundância colinear e reduzindo Falsos Positivos de `476` para `402` no grupo de subíndices (com F1 subindo de `0,6175` para `0,6669`, mantendo apenas `3 FN` nos folds de 2024).<br>**Decisão 2 (Engenharia de memória curta na Sprint 4):** incluir as médias móveis de 3h e variações de 2h para ozônio e $\text{PM}_{2,5}$ calculadas estritamente até $t$, o que zerou os Falsos Negativos (`FN = 0`) nos 4 folds trimestrais de 2024.<br>**Decisão 3 (Escolha da Random Forest com limiar `0,30` na Sprint 5):** congelar a **Random Forest Balanceada** (`300` árvores, `min_samples_leaf=2`, limiar `0,30`) na validação `2024-Q4`, onde teve **Recall de 100% (`0 FN`)**, menos alarmes falsos que a Regressão Logística no mesmo limiar (`13 FP` vs. `17 FP`) e respeitou o teto semanal de episódios nas 12 semanas. A Árvore de Decisão e o XGBoost foram comparados depois, para o artigo, sem alterar essa escolha. |
| **Uma coisa que o grupo decidiu NÃO fazer** | **Não utilizar divisão aleatória (`train_test_split` com `shuffle=True` ou `KFold` aleatório) nem reajustar o modelo após abrir o holdout:** medições horárias vizinhas têm altíssima autocorrelação; sortear horas aleatórias vazaria informação do futuro imediato para o passado e inflaria artificialmente as métricas. Além disso, mesmo observando após abrir o holdout que o XGBoost teve F1 global maior (`0,9226` vs. `0,8705`, porém com o dobro de Falsos Negativos: `6 FN` vs. `3 FN`), o grupo **decidiu não trocar o modelo congelado pós-teste**, preservando o rigor metodológico. |

---

## 6. Como Reproduzir e Executar

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

### Execução operacional (+1h a partir de agora)

Para rodar a aplicação no modo operacional e sempre prever uma hora à frente com os dados mais recentes disponíveis nas APIs, dê dois cliques em `Prever_Proxima_Hora.bat` (na raiz; cria o `.venv` na primeira vez e precisa de internet) ou use:

```powershell
.\.venv\Scripts\python.exe -m src.aplicacao.Prever_Proxima_Hora
```

Esse comando:

1. Consulta dados horários recentes de qualidade do ar e meteorologia nas APIs da Open-Meteo.
2. Recalcula IQAr e features temporais necessárias para o modelo final.
3. Carrega `models/modelo_final_sprint5.joblib`.
4. Mostra a probabilidade oficial de `IQAr > 100` para `t+1h` com o limiar congelado (`0,3`), além de uma projeção experimental horária para as próximas `7h` (turno) e `24h` (dia completo).

Para esse modo, as chaves relevantes no `config/params.yaml` são:

- `apis.air_quality` (qualidade do ar recente),
- `apis.weather_forecast` (meteorologia recente),
- `application.recent_history_days` (janela de dias usada para montar as features; padrão `3`).

> Importante: essa previsão depende da atualização das APIs e usa dados modelados/interpolados. É um apoio experimental e não um alerta oficial de saúde.

### Previsão +1h pelos notebooks

Os notebooks em `notebooks/` seguem o mesmo fluxo operacional. Abra-os no VS Code (interpretador `.venv\Scripts\python.exe`) ou com `.\.venv\Scripts\python.exe -m jupyter lab notebooks`, e execute as células na ordem, de cima para baixo:

1. [`01_Coleta_Dados_Recentes.ipynb`](notebooks/01_Coleta_Dados_Recentes.ipynb) consulta as APIs, descarta horas futuras, inspeciona a cobertura e salva a cópia em `data/recent/` (sobrescrita a cada coleta; ignorada pelo git).
2. [`02_Features_Recentes.ipynb`](notebooks/02_Features_Recentes.ipynb) calcula IQAr e features de curto prazo e seleciona a linha de entrada do modelo.
3. [`03_Previsao_Proxima_Hora.ipynb`](notebooks/03_Previsao_Proxima_Hora.ipynb) carrega `models/modelo_final_sprint5.joblib` e mostra a probabilidade e a decisão do limiar 0,3 para a hora seguinte (`+1h`), o contexto das últimas horas e a projeção experimental para as próximas `7h` e `24h` (com gráfico de tendência).
4. [`04_Comparativo_Arvores_Decisao_RF_XGBoost.ipynb`](notebooks/04_Comparativo_Arvores_Decisao_RF_XGBoost.ipynb) consolida a análise comparativa entre Árvore de Decisão CART, Random Forest e XGBoost, exibindo tabelas de métricas, estudo de overfitting por profundidade, matrizes de confusão e tempos de treino/latência.

Para uma nova previsão, repita os notebooks 01 e 03 (ou o comando acima). Os notebooks não retreinam o modelo, não carregam rótulos e não acessam o holdout. Para explicação detalhada de cada variável e campo da saída, veja o [Relatório EDA](docs/Relatorio_EDA_Desenvolvimento.md).

### Reproduzir coleta histórica e transformações

Os scripts abaixo reproduzem a base histórica usada no treino e na avaliação. Eles podem consultar APIs externas e recusam sobrescrever arquivos já existentes. **Não os execute para simplesmente fazer uma previsão ou reproduzir as métricas já documentadas.** e a validação temporal estão disponíveis como scripts. Em uma cópia limpa, após conferir `config/params.yaml` e garantir que os arquivos de saída ainda não existem, a sequência pelo terminal é:

```powershell
.\.venv\Scripts\python.exe src\coleta\Coleta_Dados.py
.\.venv\Scripts\python.exe src\transformacao\Merge_Dados.py
.\.venv\Scripts\python.exe src\transformacao\Calcular_Alvo_IQAr.py
.\.venv\Scripts\python.exe -m src.validacao.Separacao_Temporal
```

Essa sequência é para uma configuração nova, com os caminhos de saída ainda livres. Os scripts gravam arquivos com o período configurado no nome e recusam sobrescrever arquivos existentes. A coleta consulta serviços externos. A rotulagem exige uma série horária ordenada e usa janelas completas terminando no horário avaliado; a última linha não recebe rótulo porque não há observação para *t+1h*. Não remova arquivos para contornar a proteção contra sobrescrita.

O script de validação temporal lê as partições de `config/params.yaml`, ignora rótulos indefinidos e imprime os tamanhos/classes de cada fold e do teste. A divisão é feita pelo horário do evento previsto (`time + 1h`); os dados não são duplicados nem salvos em novos arquivos.

Os notebooks cobrem o fluxo operacional (+1h). Os experimentos de desenvolvimento permanecem reproduzíveis pelos scripts em `src/`. Não execute `src.modelagem.Avaliar_Modelo_Final_Sprint5` novamente: a avaliação do holdout já foi realizada uma única vez. Não use esse holdout para escolher outro modelo, limiar ou conjunto de features.

Para executar os testes automatizados (com dados sintéticos), rode na raiz:

```powershell
.\.venv\Scripts\python.exe -m pytest tests
```

---

## 7. Dados e Auditoria Temporal

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

**Sprint 5 — modelagem e avaliação final:** `.\.venv\Scripts\python.exe -m src.modelagem.Comparar_Modelos_Sprint5` comparou Dummy, persistência, Gaussian Naive Bayes S4, regressão logística balanceada e Random Forest balanceada em 2024-Q4. A regressão logística usa `max_iter=1000` e `random_state=42`; a Random Forest usa 300 árvores, `min_samples_leaf=2` e `random_state=42`. Na validação (2.208 horas, 46 positivos), a equipe congelou Random Forest com limiar 0,3: recall 1,0, precisão 0,7797, F1 0,8762, 13 FP e nenhuma semana completa acima do teto de três episódios (máximo de três). A avaliação final foi executada uma vez: no holdout (14.592 horas, 161 positivos), a combinação congelada teve recall 0,9814, precisão 0,7822, F1 0,8705, TN=14.387, FP=44, FN=3 e TP=158. Uma semana das 86 completas excedeu o teto: pico de cinco episódios e 31 horas de alerta. Os comparadores também foram medidos no mesmo holdout, mas não houve novo ajuste ou troca após consultá-lo; a regressão logística teve métricas superiores no teste, mas não substituiu o modelo congelado. Os três falsos negativos ocorreram em 27/12/2025 14h, 28/12/2025 13h e 31/12/2025 15h. Relatórios de validação: [métricas](reports/modeling/sprint5_validation_metrics.csv), [trade-off de limiares](reports/modeling/sprint5_validation_threshold_tradeoff.csv), [carga semanal](reports/modeling/sprint5_validation_alert_burden_by_week.csv) e [previsões](reports/modeling/sprint5_validation_predictions.csv). Relatórios finais: [métricas](reports/modeling/sprint5_final_test_metrics.csv), [erros](reports/modeling/sprint5_final_test_misclassified_cases.csv) e [carga semanal](reports/modeling/sprint5_final_test_alert_burden_by_week.csv). Pipeline empacotado em `models/modelo_final_sprint5.joblib`.

**Limitações identificadas na coleta** (segundo [Sprint 1](docs/sprints/Sprint1_TrilhaB.md)):
- As APIs retornam a coordenada da célula de grade do modelo, que pode diferir ligeiramente da coordenada solicitada (-23.514561, -46.186832). Essa diferença é esperada em dado modelado ou de reanálise e não constitui erro de coleta, mas deve ser considerada na interpretação dos resultados.
- Tanto os arquivos de janeiro/2025 quanto a coleta ampliada não apresentaram valores nulos nas variáveis solicitadas; no período ampliado, as duas fontes também têm timestamps alinhados e sem lacunas.

### Documentação Oficial das APIs

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

## 8. Modelo Preditivo e Comparativo de Algoritmos

| Item | Status |
|---|---|
| Baseline | Dummy prior, persistência pelo IQAr em *t* e Gaussian Naive Bayes com features S4 |
| Modelo selecionado | Random Forest balanceada, 300 árvores, `min_samples_leaf=2`, `random_state=42` |
| Limiar de decisão | 0,3, congelado na validação temporal 2024-Q4 |
| Métrica principal no teste | Recall 0,9814 da classe positiva; 3 FN e 44 FP |
| Resultado da regra semanal | 1 de 86 semanas completas excedeu o teto de 3 episódios; pico de 5 episódios e 31 horas de alerta |
| Artefato | `models/modelo_final_sprint5.joblib` (pipeline, features e limiar) |
| Dashboard Streamlit | `streamlit_app.py` (Aba 1: Previsão Atual ao vivo; Aba 2: Desempenho Histórico) |
| Artigo Técnico Web (GitHub Pages) | [diogogomesb.github.io/... (Publicação Online)](https://diogogomesb.github.io/Ciencia-de-Dados-e-Aprendizagem-de-Maquina/) · [`docs/index.html`](docs/index.html) |

### Comparativo Completo: Baseline vs. Árvore de Decisão, Random Forest e XGBoost

Executado por `.\.venv\Scripts\python.exe -m src.modelagem.Experimento_Arvores_Artigo` (resultados salvos em [`reports/modeling/artigo_comparativo_modelos.csv`](reports/modeling/artigo_comparativo_modelos.csv)):

| Partição | Modelo | Limiar | Recall (Pos) | Precisão (Pos) | F1-Score | TP | FP | FN | Treino (s) | Inferência Total (ms) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **Validação (2024-Q4)** | `dummy_prior` (Baseline) | 0,50 | 0,0000 | 0,0000 | 0,0000 | 0 | 0 | 46 | 0,0015 | 0,26 |
| **Validação (2024-Q4)** | `persistencia_iqar_atual` | 0,50 | 0,8043 | 0,8043 | 0,8043 | 37 | 9 | 9 | 0,0000 | 0,44 |
| **Validação (2024-Q4)** | `gaussian_naive_bayes` | 0,50 | 1,0000 | 0,3866 | 0,5576 | 46 | 73 | 0 | 0,1006 | 10,96 |
| **Validação (2024-Q4)** | `arvore_decisao_cart` (`max_depth=6`) | 0,30 | 1,0000 | 0,9020 | 0,9485 | 46 | 5 | 0 | 0,1344 | 3,95 |
| **Validação (2024-Q4)** | `xgboost_balanced` (`300` árv.) | 0,30 | 0,9565 | 0,9362 | 0,9462 | 44 | 3 | 2 | 1,3241 | 12,37 |
| **Validação (2024-Q4)** | **`random_forest_balanced` (`300` árv.)** | **0,30** | **1,0000** | **0,7797** | **0,8762** | **46** | **13** | **0** | **1,4000** | **123,35** |
| **Holdout (2025–2026)** | `dummy_prior` (Baseline) | 0,50 | 0,0000 | 0,0000 | 0,0000 | 0 | 0 | 161 | 0,0020 | 0,57 |
| **Holdout (2025–2026)** | `persistencia_iqar_atual` | 0,50 | 0,7888 | 0,7888 | 0,7888 | 127 | 34 | 34 | 0,0000 | 0,90 |
| **Holdout (2025–2026)** | `gaussian_naive_bayes` | 0,50 | 1,0000 | 0,3492 | 0,5177 | 161 | 300 | 0 | 0,0679 | 20,15 |
| **Holdout (2025–2026)** | `arvore_decisao_cart` (`max_depth=6`) | 0,30 | 0,8634 | 0,8081 | 0,8348 | 139 | 33 | 22 | 0,1152 | 11,48 |
| **Holdout (2025–2026)** | `xgboost_balanced` (`300` árv.) | 0,30 | 0,9627 | 0,8857 | 0,9226 | 155 | 20 | 6 | 0,8553 | 38,28 |
| **Holdout (2025–2026)** | **`random_forest_balanced` (Escolhido)** | **0,30** | **0,9814** | **0,7822** | **0,8705** | **158** | **44** | **3** | **1,6390** | **106,66** |

### Como executar o Dashboard no Streamlit

```powershell
.\.venv\Scripts\streamlit.exe run streamlit_app.py
```

O dashboard abre no navegador com a **Aba 1 (Previsão Atual ao vivo via API Open-Meteo)** e a **Aba 2 (Desempenho Histórico e Comparativo de Modelos)**.

O modelo usa os sete subíndices individuais dos poluentes, cinco variáveis meteorológicas e quatro atributos retrospectivos: médias móveis de 3h e deltas de 2h de ozônio e PM2,5. Não usa o IQAr consolidado nem o alvo futuro como entrada. Imputação pela mediana e `StandardScaler` são ajustados dentro do pipeline de treino. As métricas descrevem este conjunto temporal e não garantem desempenho futuro nem prontidão para uso operacional. A previsão +1h a partir da hora atual reutiliza o mesmo artefato, mas não tem métrica própria.

**Limitações e interpretação:** os dados de qualidade do ar são do CAMS Global, têm resolução nativa de 3h fora da Europa e valores horários interpolados; clima vem de reanálise, não de medição direta local. A série foi analisada descritivamente antes da definição do split, portanto o holdout não é totalmente cego. A triagem de features nos folds também pode introduzir viés de seleção. O modelo é um protótipo acadêmico, não um sistema de alerta oficial ou orientação de saúde.

---

## 9. Estrutura do Repositório

Arquitetura de referência do projeto, com indicação do que já está implementado:

```text
Ciencia-de-Dados-e-Aprendizagem-de-Maquina/
├── README.md
├── DIARIO.md                         # diário de bordo consolidado (Sprints 1–5)
├── .env.example                      # variáveis de ambiente de referência
├── streamlit_app.py                  # dashboard interativo (Streamlit Community Cloud)
├── LICENSE                           # concluído (MIT)
├── requirements.txt                  # concluído
├── config/
│   └── params.yaml                   # configurado para o período validado
├── data/
│   ├── raw/                          # JSONs de janeiro/2025 e arquivos versionados do período ampliado
│   ├── interim/                      # merge e dados rotulados do período ampliado
│   └── processed/                    # base final tratada e rotulada pronta para modelagem/dashboard
│   (data/recent/ é gerado na execução +1h e ignorado pelo git)
├── notebooks/
│   ├── 01_Coleta_Dados_Recentes.ipynb # coleta dados recentes das APIs (até a hora atual)
│   ├── 02_Features_Recentes.ipynb    # calcula IQAr e features da linha de entrada
│   └── 03_Previsao_Proxima_Hora.ipynb # prevê a próxima hora com o modelo empacotado
├── src/
│   ├── coleta/
│   │   └── Coleta_Dados.py           # concluído; não sobrescreve outro período
│   ├── transformacao/
│   │   ├── Merge_Dados.py            # merge versionado por período
│   │   ├── Calcular_Alvo_IQAr.py      # subíndices CETESB e rótulo t+1h
│   │   └── Features_Temporais.py     # atributos retrospectivos
│   ├── analise/                      # EDA de desenvolvimento
│   ├── aplicacao/
│   │   └── Prever_Proxima_Hora.py    # previsão +1h com dados recentes das APIs
│   ├── validacao/
│   │   └── Separacao_Temporal.py     # folds expansivos e teste final por horário-alvo
│   └── modelagem/                    # baselines, comparativos, avaliação e empacotamento
├── models/                           # pipeline final joblib
├── reports/                          # métricas, previsões, erros e figuras
├── tests/                            # testes automatizados
├── docs/
│   ├── index.html                    # artigo técnico em página web estática (GitHub Pages)
│   ├── assets/                       # figuras didáticas das árvores e comparativos do artigo
│   ├── RFC.md
│   ├── Dicionario_de_Dados.md
│   ├── Relatorio_EDA_Desenvolvimento.md
│   └── sprints/                      # registros e decisões das Sprints 1–5
```

A pasta `data/` contém os arquivos brutos (`data/raw/`), intermediários (`data/interim/`) e a base processada final (`data/processed/dados_com_alvo_2022-08-04_2026-08-31.csv`). O artigo técnico estático em HTML para publicação no GitHub Pages está em [`docs/index.html`](docs/index.html), acompanhado de suas figuras em `docs/assets/`.

---

## 10. Trabalho Realizado e Encerramento Acadêmico

### 10.1 Trabalho Realizado na Sprint 1 (Registro Histórico)

- Configuração centralizada (local, latitude, longitude, datas, fuso horário), sem valores fixados diretamente no código de coleta.
- Requisições às duas fontes exigidas pela Trilha B (qualidade do ar e clima), com `timeout=30` e `raise_for_status()`.
- Dados brutos preservados sem transformação em `data/raw/`; a coleta ampliada passou a usar nomes versionados pelo período e preservou os arquivos legados de janeiro/2025.
- RFC formalizado, com evento, horizonte, classe positiva, custo de falso negativo, documentação das APIs e tabela de variáveis.
- Dicionário de dados v0.1 criado.
- `requirements.txt` e `LICENSE` (MIT) adicionados ao repositório.

### 10.2 Encerramento Acadêmico e de Equipe

> As pendências técnicas abaixo foram concluídas nas Sprints seguintes. Permanecem como tarefas de organização acadêmica os registros individuais e decisões formais que só a equipe pode confirmar.

| Item a confirmar pela equipe | Situação |
|---|---|
| Definir Scrum Master e atualizar eventuais registros do Scrum | Concluído: Diogo Gomes Barbosa (registrado nas Sprints 1–5; board e sprints atualizados) |
| Completar diários, contribuições individuais, feedbacks e rubricas da disciplina | Concluído: diários de bordo individuais preenchidos e rubricas consolidadas nas Sprints 1–5 |
| Confirmar usuário decisor operacional do caso de uso | Concluído: Coordenação de Infraestrutura e Esportes da UBC e Defesa Civil de Mogi das Cruzes |

As entregas técnicas inicialmente listadas — coleta ampliada, validação de esquema e merge, alvo e split temporal, notebooks, EDA, engenharia/comparação de features, modelagem e documentação — estão descritas nas seções anteriores e nos diários das Sprints 1–5.

---

## 11. Documentação e Links Oficiais

- [RFC e decisões de escopo](docs/RFC.md)
- [Dicionário de dados](docs/Dicionario_de_Dados.md)
- [Relatório EDA e guia passo a passo](docs/Relatorio_EDA_Desenvolvimento.md)
- [Sprint 1 — coleta e definição do problema](docs/sprints/Sprint1_TrilhaB.md)
- [Sprint 2 — EDA e preparação](docs/sprints/Sprint2_TrilhaB.md)
- [Sprint 3 — baselines e comparação inicial](docs/sprints/Sprint3_TrilhaB.md)
- [Sprint 4 — atributos temporais e comparação formal](docs/sprints/Sprint4_TrilhaB.md)
- [Sprint 5 — modelo final, avaliação e model card](docs/sprints/Sprint5_TrilhaB.md)
- [Artigo Técnico Publicado (GitHub Pages)](https://diogogomesb.github.io/Ciencia-de-Dados-e-Aprendizagem-de-Maquina/) (ou código-fonte local em [`docs/index.html`](docs/index.html))
- [Dashboard Interativo no Streamlit](streamlit_app.py)
- [Diário de Bordo Consolidado](DIARIO.md)
- [Previsão +1h interativa](notebooks/03_Previsao_Proxima_Hora.ipynb)
- Diagramas (PDF e JPG) em `docs/diagramas/`: [pipeline](docs/diagramas/diagrama_pipeline.jpg) e [split temporal](docs/diagramas/diagrama_split_temporal.jpg). Para regenerá-los: `.\.venv\Scripts\python.exe -m src.analise.Gerar_Diagramas`.

