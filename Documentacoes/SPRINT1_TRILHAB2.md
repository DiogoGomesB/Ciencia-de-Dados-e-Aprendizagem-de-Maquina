# Sprint 1 — Trilha B: Qualidade do Ar Inadequada

**Projeto:** Previsão da Qualidade do Ar Inadequada na Região da Faculdade UBC
**Trilha:** B — Qualidade do ar inadequada
**Disciplina:** Ciência de Dados e Aprendizado de Máquina
**Sprint:** 1
**Período:** 17/08/2026 a 17/09/2026
**Data de atualização:** 17/09/2026

---

## 1. Objetivo da Sprint

A Sprint 1 teve como objetivo estruturar a base inicial do projeto de previsão de qualidade do ar inadequada, realizando a definição inicial das fontes de dados, a coleta dos dados brutos e a documentação das variáveis que serão utilizadas nas etapas seguintes.

Nesta etapa, o foco foi manter os dados em seu estado bruto, sem realizar procedimentos de limpeza, imputação, criação de atributos derivados ou definição definitiva da variável-alvo.

---

## 2. Problema abordado

O projeto tem como objetivo estudar a ocorrência de condições de qualidade do ar inadequada na região da Faculdade Universidade Braz Cubas (UBC), em Mogi das Cruzes/SP.

A proposta é utilizar dados de qualidade do ar associados a condições meteorológicas para, nas próximas etapas do projeto, desenvolver um modelo capaz de realizar a previsão da ocorrência de qualidade do ar inadequada.

A Sprint 1 concentra-se na estruturação das fontes e na obtenção dos dados necessários para essa finalidade.

---

## 3. Fontes de dados

Foram definidas duas fontes principais para a coleta dos dados:

### 3.1 Open-Meteo Air Quality API

**Endpoint:**

`https://air-quality-api.open-meteo.com/v1/air-quality`

A API foi utilizada para obtenção de variáveis relacionadas à qualidade do ar.

As variáveis coletadas foram:

* `pm10`
* `pm2_5`
* `carbon_monoxide`
* `nitrogen_dioxide`
* `sulphur_dioxide`
* `ozone`

Os dados possuem resolução temporal horária.

Os dados de qualidade do ar utilizados pela API são provenientes de modelos atmosféricos/reanálises e, portanto, não representam uma medição pontual realizada diretamente em uma estação localizada na Faculdade UBC.

---

### 3.2 Open-Meteo Historical Weather API

**Endpoint:**

`https://archive-api.open-meteo.com/v1/archive`

A API foi utilizada para obtenção das condições meteorológicas históricas relacionadas ao mesmo período da coleta de qualidade do ar.

As variáveis coletadas foram:

* `temperature_2m`
* `relative_humidity_2m`
* `precipitation`
* `wind_speed_10m`
* `pressure_msl`

Os dados possuem resolução temporal horária e são provenientes de modelos/reanálises meteorológicas.

---

## 4. Período inicial de coleta

A coleta inicial realizada na Sprint 1 utilizou o seguinte período:

| Informação                   | Valor              |
| ---------------------------- | ------------------ |
| Data inicial                 | 01/01/2025         |
| Data final                   | 31/01/2025         |
| Resolução                    | Horária            |
| Registros de qualidade do ar | 744                |
| Registros meteorológicos     | 744                |
| Local de referência          | Mogi das Cruzes/SP |
| Latitude solicitada          | -23.514561         |
| Longitude solicitada         | -46.186832         |
| Fuso horário                 | America/Sao_Paulo  |

O período acima representa a primeira coleta realizada para validação do processo de obtenção e armazenamento dos dados.

O período definitivo utilizado no projeto ainda deverá ser validado e definido nas próximas etapas.

---

## 5. Processo de coleta

A coleta foi realizada por meio do arquivo:

`Coleta_Dados.py`

O script utiliza requisições HTTP para acessar as APIs da Open-Meteo e salvar as respostas em formato JSON.

A estrutura utilizada na Sprint 1 mantém os dados brutos separados por fonte.

### Arquivos gerados

```text
data/
└── raw/
    ├── air_quality_raw.json
    └── weather_raw.json
```

Os arquivos da pasta `data/raw/` representam os dados originais obtidos das APIs e devem permanecer sem alterações durante as etapas posteriores.

---

## 6. Variáveis coletadas

### 6.1 Qualidade do ar

| Variável           | Unidade | Tipo              |
| ------------------ | ------- | ----------------- |
| `pm10`             | μg/m³   | Numérica contínua |
| `pm2_5`            | μg/m³   | Numérica contínua |
| `carbon_monoxide`  | μg/m³   | Numérica contínua |
| `nitrogen_dioxide` | μg/m³   | Numérica contínua |
| `sulphur_dioxide`  | μg/m³   | Numérica contínua |
| `ozone`            | μg/m³   | Numérica contínua |

### 6.2 Condições meteorológicas

| Variável               | Unidade | Tipo              |
| ---------------------- | ------- | ----------------- |
| `temperature_2m`       | °C      | Numérica contínua |
| `relative_humidity_2m` | %       | Numérica contínua |
| `precipitation`        | mm      | Numérica contínua |
| `wind_speed_10m`       | km/h    | Numérica contínua |
| `pressure_msl`         | hPa     | Numérica contínua |

### 6.3 Variável temporal

| Variável | Tipo      | Descrição                                   |
| -------- | --------- | ------------------------------------------- |
| `time`   | Data-hora | Data e horário correspondentes à observação |

A variável `time` será utilizada posteriormente para realizar a integração temporal entre os dados de qualidade do ar e os dados meteorológicos.

---

## 7. Validação inicial dos dados

Após a coleta inicial, foi realizada uma verificação dos arquivos brutos.

Foram identificados:

* 744 registros horários na fonte de qualidade do ar;
* 744 registros horários na fonte meteorológica;
* período entre 01/01/2025 00:00 e 31/01/2025 23:00;
* ausência de valores nulos na coleta inicial;
* presença das variáveis previstas na configuração do script;
* unidades de medida compatíveis com as especificações das APIs.

A validação realizada nesta etapa teve caráter inicial e não substitui o processo de limpeza e análise exploratória previsto para a Sprint 2.

---

## 8. Coordenadas e resolução espacial

Foram utilizadas inicialmente as seguintes coordenadas como referência para a coleta:

* **Latitude:** -23.514561
* **Longitude:** -46.186832

As APIs podem retornar coordenadas diferentes das coordenadas solicitadas devido ao funcionamento das grades espaciais dos modelos utilizados.

Na coleta realizada, foram observadas pequenas diferenças entre as coordenadas solicitadas e as coordenadas retornadas pelas APIs.

Essa diferença não foi tratada como erro de coleta, pois os dados utilizados são provenientes de modelos/reanálises espaciais e representam uma célula de grade, e não necessariamente um ponto exato de medição.

Essa limitação deverá ser considerada durante a interpretação dos resultados.

---

## 9. Integração dos dados

Na Sprint 1, os dados foram coletados e armazenados separadamente.

O merge entre os dados de qualidade do ar e os dados meteorológicos **ainda não foi realizado**.

A integração deverá utilizar a variável temporal `time` como referência para associação das observações horárias.

A estrutura esperada após a integração será uma tabela contendo, para cada horário, as variáveis de qualidade do ar e as variáveis meteorológicas correspondentes.

---

## 10. Limpeza dos dados

A limpeza definitiva dos dados não foi realizada na Sprint 1.

A pasta:

```text
data/raw/
```

deve permanecer preservada com os dados originais coletados.

As etapas de tratamento, limpeza, análise de valores ausentes, identificação de inconsistências e preparação da tabela para EDA serão realizadas na Sprint 2, utilizando a pasta:

```text
data/interim/
```

---

## 11. Variável-alvo

A variável-alvo ainda não foi formalizada na Sprint 1.

A definição da classe de **qualidade do ar inadequada**, incluindo:

* variável utilizada para construção do alvo;
* limiar adotado;
* justificativa do limiar;
* horizonte de previsão;
* deslocamento temporal;
* distribuição das classes;

será realizada na Sprint 2.

O limiar deverá ser definido com base no conjunto de treino, evitando utilizar informações do conjunto de teste durante essa decisão.

---

## 12. Features e atributos derivados

Não foram definidos atributos derivados definitivos na Sprint 1.

Possíveis transformações, como:

* valores defasados (`lag`);
* médias móveis;
* variáveis de calendário;
* agregações;
* outras transformações temporais;

serão avaliadas nas sprints seguintes.

A inclusão de cada atributo deverá ser justificada e deverá respeitar o instante em que a informação estaria disponível para a previsão, evitando vazamento de dados.

---

## 13. Risco de vazamento de dados

Na Sprint 1 ainda não foram definidas formalmente as variáveis excluídas por risco de vazamento.

Essa análise será realizada na Sprint 2, após a definição da variável-alvo e do horizonte de previsão.

As informações utilizadas para construir o próprio alvo ou que somente estariam disponíveis após o instante da previsão não deverão ser utilizadas como features do modelo.

---

## 14. Estrutura atual do projeto

A estrutura relacionada aos dados na Sprint 1 é:

```text
Ciencia-de-Dados-e-Aprendizagem-de-Maquina/
│
├── data/
│   └── raw/
│       ├── air_quality_raw.json
│       └── weather_raw.json
│
├── docs/
│   └── Dicionario_de_Dados.md
│
├── src/
│
├── notebooks/
│
├── Coleta_Dados.py
│
└── README.md
```

Os diretórios e arquivos que ainda não foram utilizados poderão ser preenchidos nas sprints seguintes conforme o avanço do projeto.

---

## 15. Entregas realizadas na Sprint 1

| Entrega                        | Status              |
| ------------------------------ | ------------------- |
| Definição inicial do problema  | Concluído           |
| Definição das fontes de dados  | Concluído           |
| Configuração das APIs          | Concluído           |
| Script de coleta               | Concluído           |
| Coleta inicial dos dados       | Concluído           |
| Armazenamento dos dados brutos | Concluído           |
| Validação inicial da coleta    | Concluído           |
| Dicionário de Dados            | Concluído           |
| Merge entre as fontes          | Pendente            |
| Limpeza dos dados              | Sprint 2            |
| Definição formal do alvo       | Sprint 2            |
| Criação de features            | Sprint 2 / Sprint 4 |
| Modelagem                      | Sprints posteriores |

---

## 16. Limitações identificadas

Durante a Sprint 1 foram identificadas as seguintes limitações:

1. Os dados de qualidade do ar são provenientes de modelos/reanálises e não de uma estação de medição localizada exatamente na Faculdade UBC.

2. Os dados representam uma grade espacial dos modelos utilizados pelas APIs.

3. As coordenadas retornadas pelas APIs podem apresentar diferenças em relação às coordenadas originalmente solicitadas.

4. A coleta inicial contempla somente janeiro de 2025 e ainda não representa necessariamente o período definitivo do projeto.

5. O conjunto de dados ainda não passou pela etapa de limpeza e tratamento.

6. O merge entre as duas fontes ainda não foi realizado.

7. A variável-alvo e seu respectivo limiar ainda não foram definidos.

8. Ainda não foram realizadas análises exploratórias ou treinamento de modelos nesta Sprint.

---

## 17. Próximas etapas — Sprint 2

Para a Sprint 2 estão previstas as seguintes atividades:

* Realizar o merge entre os dados de qualidade do ar e meteorológicos;
* Definir e aplicar as regras de limpeza;
* Criar a tabela em `data/interim/`;
* Realizar análise exploratória dos dados;
* Identificar valores ausentes e inconsistências;
* Formalizar a variável-alvo;
* Definir o horizonte de previsão;
* Definir o limiar da classe positiva utilizando o conjunto de treino;
* Realizar o split temporal entre treino e teste;
* Criar os primeiros atributos derivados;
* Avaliar possíveis riscos de vazamento;
* Atualizar o Dicionário de Dados para a versão `v0.2`.

---

## 18. Conclusão da Sprint 1

A Sprint 1 estabeleceu a estrutura inicial necessária para o desenvolvimento do projeto de previsão da qualidade do ar inadequada.

Foram definidas as fontes de dados, implementado o processo inicial de coleta, armazenados os dados brutos e documentadas as variáveis utilizadas.

A coleta inicial apresentou 744 observações horárias em cada uma das duas fontes para o período de 01/01/2025 a 31/01/2025.

As etapas de integração, limpeza, definição formal do alvo, criação de atributos e modelagem permanecem para as sprints seguintes, mantendo nesta primeira etapa a separação entre dados brutos e dados processados.
