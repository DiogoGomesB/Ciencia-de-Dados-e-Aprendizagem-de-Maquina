# Dicionário de Dados

**Projeto:** Previsão da Qualidade do Ar Inadequada em Na Região da Faculdade UBC
**Trilha:** B — Qualidade do ar inadequada
**Equipe:** Davi Gama dos Santos - 33121079, Diogo Gomes Barbosa - 35866276, Eudenis de Souza Vieira - 32751621, Gabriel Januário Alves - 35609991, João Pedro Barreto da Silva - 33297185
**Última atualização:** (14/09/2026) — atualizar a cada sprint em que variáveis nasçam ou saiam
**Versão:** v0.1 (Sprint 1)

> Contrato das colunas entre sprints. Sprint 1: fontes e variáveis **brutas**. Sprint 2: log de limpeza, alvo formal, derivados iniciais e exclusões por vazamento. Sprint 4: features iteradas. Sprint 5: conferência com o model card — as colunas do modelo escolhido são estas.

**Unidade de análise (o que é uma linha):**
**N após o merge (Sprint 1, bruto):**
**N após a limpeza (Sprint 2, `data/interim`):**
**Split (Sprint 2):** treino = ________ / teste = ________ (N treino = ____, N teste = ____)

---

## 1. Fontes de dados

| Fonte | API / Endpoint | Cobertura temporal disponível | Resolução temporal | Medido ou modelado? | Limitações conhecidas |
|---|---|---|---|---|---|
|Open-Meteo Air Quality API |https://air-quality-api.open-meteo.com/v1/air-quality |O conjunto de reanálise de qualidade do ar CAMS European possui dados desde 2013. O período efetivamente utilizado no projeto ainda será definido. |Horária |Modelado — os dados de qualidade do ar são provenientes de modelos atmosféricos, não de uma estação de medição localizada exatamente no ponto do projeto. |Resolução espacial de aproximadamente 11 km para o CAMS European; portanto, os valores representam uma grade/modelo atmosférico e não uma medição pontual da Universidade Braz Cubas. |
|Open-Meteo Historical Weather API |https://archive-api.open-meteo.com/v1/archive |Disponibilidade histórica depende do conjunto selecionado. O ERA5 possui dados desde 1940; o período utilizado no projeto ainda será definido. |Horária |Modelado/reanálise — os dados históricos são obtidos a partir de modelos e conjuntos de reanálise meteorológica. |A resolução espacial depende do conjunto utilizado; para ERA5, a documentação informa aproximadamente 25 km. A escolha do período e do conjunto deverá considerar a compatibilidade com os dados de qualidade do ar. |

> **Trilha B:** poluentes Open-Meteo em geral são produto **modelado**, não medição de estação local — declarar na coluna acima.
> **Trilha C:** registrar códigos do IBGE (agregado, variável, classificação) e o que cada um representa. Anotar municípios e safras: N = municípios × safras.

---

## 2. Variáveis brutas (coletadas na Sprint 1)

| Nome da coluna | Fonte | Tipo | Unidade | Descrição | Observações |
|---|---|---|---|---|---|
|time |Open-Meteo Air Quality / Weather |data-hora |ISO 8601 |Data e horário correspondentes à observação. |Será utilizada posteriormente para integração temporal entre as fontes. |
| | | | | | |
| | | | | | |

Observação: nesta Sprint 1, as variáveis acima são registradas como dados brutos. A definição da variável-alvo, suas transformações, defasagens (shift) e eventuais exclusões por vazamento serão documentadas nas sprints seguintes.

*Tipo: numérica contínua / numérica discreta / categórica / data-hora / identificador.*

---

## 2.1 Log de limpeza e tratamento (Sprint 2, antes da EDA)

`data/raw/` permanece intocado. A tabela da EDA é `data/interim/`.

Não imputar com média/mediana/moda do dataset inteiro nesta etapa.

| Problema | Regra aplicada | Linhas/células afetadas | N depois | Observação |
|---|---|---|---|---|
| | | | | |
| | | | | |

**Ausentes restantes após a limpeza de domínio (se houver, tratar no treino na Sprint 2):**

---

## 3. Variável-alvo *(formalizar na Sprint 2; limiar escolhido no treino)*

| Campo | Descrição |
|---|---|
| Nome da coluna | |
| Definição da classe positiva | |
| Limiar adotado e justificativa (evidência do **treino**) | |
| Fonte da variável de origem | |
| Horizonte de previsão (deslocamento aplicado) | |
| Nível de desbalanceamento no treino (% positivos / negativos) | |

---

## 4. Atributos derivados (Sprints 2 e 4)

| Nome do atributo | Variável(is) de origem | Tipo de transformação | Janela/parâmetro (definido no treino) | Calculável no instante da previsão? | Justificativa | Sprint (2 ou 4) | Feature ou alvo? |
|---|---|---|---|---|---|---|---|
| | | | | | | | |
| | | | | | | | |

*Tipo de transformação: média móvel / valor defasado (lag) / agregação (soma, contagem) / variável de calendário / outro (especificar).*

> Cada linha precisa de justificativa — não copiar só o nome da coluna. Parâmetros de janela **não** se reajustam no teste. A Sprint 4 acrescenta linhas novas; não apaga as da Sprint 2 se ainda estiverem no modelo (pode marcar “descartada na seleção”). Timestamp, código IBGE e nome de município **não** entram como número; calendário (mês, safra) vale. “Calculável no instante da previsão” = sim só se os dados de origem já existiriam na hora da decisão (mesmo horizonte do RFC).

---

## 5. Variáveis excluídas das features (risco de vazamento)

| Nome da coluna | Motivo da exclusão |
|---|---|
| | |

> Incluir colunas usadas para construir o alvo e qualquer informação que só existiria depois do evento ou depois do instante de previsão. Elas **não** entram no `ColumnTransformer`.

---

## 6. Observações gerais e limitações do dataset

- (ex.: período com falha de coleta, mudança de metodologia da fonte, viés geográfico, dado modelado, N pequeno)

---

## 7. Histórico de alterações

| Versão | Sprint | Data | O que mudou |
|---|---|---|---|
| v0.1 | 1 | | Fontes, variáveis brutas, N após o merge (bruto) |
| v0.2 | 2 | | Log de limpeza; N em `interim`; split; alvo; derivados iniciais; exclusões |
| v0.3 | 4 | | Features iteradas; seleção |
| v0.4 | 5 | | Conferência com o modelo final / model card |
