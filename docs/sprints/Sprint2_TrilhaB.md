# Diário de Sprint 2 — Limpeza, tratamento, EDA e engenharia de atributos
**Período:** 18/09/2026 a 27/09/2026
**Trilha definitiva do grupo:** B — Qualidade do ar inadequada

**Equipe:** Davi Gama dos Santos - 33121079, Diogo Gomes Barbosa - 35866276, Eudenis de Souza Vieira - 32751621, Gabriel Januário Alves - 35609991, João Pedro Barreto da Silva - 33297185
**Scrum Master do Sprint:** A preencher conforme definição da equipe.
**Repositório GitHub:** A preencher com o link do repositório.

> A aula pode usar a **Trilha A (chuva intensa)** só como exemplo de método. **A entrega é nos dados brutos da Trilha B coletados na Sprint 1** (`data/raw/`).
>
> Ordem obrigatória: **inspeção → limpeza e tratamento → split → imputação estatística só no treino (se houver NA) → EDA no treino → alvo → features**. Não se faz EDA no bruto. Não há modelagem (baseline na Sprint 3).

### Contrato desta sprint

| Artefato | Origem / destino |
|---|---|
| `data/raw/` + `config/` + N do merge | Sprint 1 — **não substituir por outra coleta sem versionar** |
| RFC v0.1 e dicionário v0.1 | Sprint 1 |
| `data/interim/` + log de limpeza (N antes/depois) | Sprint 3 em diante (tabela de trabalho) |
| Split (corte, N treino/teste) | Sprints 3, 4 e 5 — **mesmo corte** |
| Alvo formal (limiar, horizonte, desbalanceamento no treino) | Sprints 3–5 |
| Features iniciais justificadas + dicionário v0.2 | Sprint 3 (transformer) e 4 (base para iterar) |

**Não sai daqui:** Dummy, persistência, Naive Bayes, F1, modelo escolhido.

- [x] Confirmei que o notebook desta sprint lê o `data/raw` da Sprint 1

---

## 1. Limpeza e tratamento (antes da EDA)

`data/raw/` permanece intocado. A tabela tratada vai para `data/interim/`.

### 1.1 Inspeção (contar o sujo, ainda sem corrigir)

- [x] Estatística descritiva das colunas numéricas
- [x] Ausentes quantificados por coluna
- [x] Duplicatas (linhas e por chave de unidade de análise)
- [ ] Valores inválidos de domínio (ex.: poluente negativo) e sentinelas da API

**Diagnóstico (números):**
Foram identificados:
- 744 registros de qualidade do ar
- 744 registros meteorológicos
- Nenhum valor nulo encontrado na coleta inicial
- Nenhuma duplicata encontrada na coluna 'time'

### 1.2 Regras aplicadas

Não imputar com média/mediana/moda do dataset **inteiro**. Isso vaza o teste. Imputação estatística, se precisar, é a seção 3 (depois do split).

- [x] Tipos e unidades padronizados
- [x] Duplicatas tratadas com contagem
- [ ] Sentinelas → `NaN` explícito
- [ ] Inválidos de domínio tratados com regra escrita (remover / `NaN` / correção só se a fonte tiver erro conhecido)
- [x] Log: o que foi feito, em quantas linhas/células, N depois
- [x] Tabela salva em `data/interim/`
- [ ] Dicionário (log de limpeza) atualizado

| Problema encontrado | Regra aplicada | Linhas/células afetadas | N depois |
|---|---|---|---|
| Nenhum valor nulo identificado | Não necessária | 0 | 744 |
| Nenhuma duplicata na coluna 'time' | Não necessária | 0 | 744 |

**N após a limpeza:** 744 registros
**Evidências (link do notebook/commit):** Script `src/transformacao/Merge_Dados.py` executado. Arquivo `data/interim/dados_merged.csv` gerado.

## 2. Split temporal

Sobre a tabela **já limpa** (`data/interim/`).

- [ ] Treino = período mais antigo; teste = mais recente (sem embaralhar)
- [ ] Data de corte explícita; N treino e N teste
- [ ] Teste isolado: não usa para limiar, janelas, lags nem parâmetros de imputação

**Corte:** Pendente - o split temporal ainda não foi definido.
**N treino / N teste:** Pendente.
**Justificativa:** O split temporal deverá ser definido após análise exploratória e definição do alvo.

## 3. Tratamento estatístico residual (depois do split, antes da EDA)

Só NA que a limpeza de domínio não resolveu. Parâmetros saem **somente do treino**.

- [ ] Estratégia justificada (imputar agora / deixar NA para o `ColumnTransformer` da Sprint 3)
- [ ] Se imputar: regra ajustada no treino e aplicada ao teste

**Regra residual (ou "não há NA restantes"):** Pendente - como não há valores nulos, não necessária imputação.

## 4. Análise exploratória (EDA) — treino já tratado

- [ ] Estatística descritiva da variável de origem do alvo **no treino**
- [ ] Série temporal, histogramas, boxplots
- [ ] Correlação no treino (pode ser espúria em série temporal)
- [ ] Outliers discutidos (não só plotados)

> Desbalanceamento de **classes** só depois da seção 5 (quando o alvo existir). Nesta seção explora-se a variável de origem (contínua ou categórica bruta).

**Principais achados da EDA (treino):** Pendente - EDA ainda não realizada.

**Evidências (gráficos, link do notebook):** Pendente.

## 5. Definição da variável-alvo

**Classe positiva:** Pendente - a ser definida após EDA.
**Limiar e justificativa (treino, alinhada ao RFC):** Pendente.
**Horizonte / deslocamento:** 1h à frente (definido no RFC).
**Desbalanceamento no treino:** Pendente.

- [ ] Classe positiva sem ambiguidade, ligada ao custo de FN
- [ ] Desbalanceamento das classes quantificado **no treino** (ex.: "12% positivos vs. 88% negativos")
- [ ] Seção do alvo no dicionário preenchida
- [ ] Colunas de construção do alvo na lista de exclusão (vazamento)

## 6. Engenharia de atributos (Feature Engineering)

- [ ] Médias móveis, lags e agregações só com informação anterior ao ponto de previsão
- [ ] Cada feature seria calculável **no momento real da previsão** (mesmo horizonte do RFC)
- [ ] Timestamp e IDs **não** entram como número; calendário (hora, dia da semana, estação) vale
- [ ] Variáveis de calendário quando pertinente (hora, dia da semana, estação)
- [ ] Parâmetros de janela definidos **no treino**, depois aplicados ao teste
- [ ] Vazamento ausente (texto + código: `.shift()` / `.rolling()` sem o instante-alvo nem o futuro)
- [ ] Cada atributo justificado um a um; dicionário atualizado

**Descrição e justificativa dos atributos:** Pendente - features ainda não foram criadas.

**Evidências (trecho de código, link do notebook):** Pendente.

## 7. Scrum

- [ ] Atualizações semanais no board
- [ ] Board refletindo o estado real

**Link do board:** Pendente.

## 8. Diário de bordo (retrospectiva individual)

| Integrante | O que fiz nesta Sprint | Dificuldades | O que pretendo manter/ajustar |
|---|---|---|---|
| Davi Gama dos Santos | A preencher pelo integrante. | A preencher. | A preencher. |
| Diogo Gomes Barbosa | A preencher pelo integrante. | A preencher. | A preencher. |
| Eudenis de Souza Vieira | A preencher pelo integrante. | A preencher. | A preencher. |
| Gabriel Januário Alves | A preencher pelo integrante. | A preencher. | A preencher. |
| João Pedro Barreto da Silva | A preencher pelo integrante. | A preencher. | A preencher. |

---

## Rubrica de avaliação — Sprint 2 (nota de 0 a 4,0)

| Critério | Peso | O que caracteriza nota máxima | Nota atribuída | Observações |
|---|---|---|---|---|
| Limpeza e tratamento | 1,0 | Inspeção numérica, regras explícitas, log com N, `interim` gerado, raw intocado, sem estatística global para imputar | Pendente | Merge realizado, mas limpeza completa pendente |
| Split temporal | 0,5 | Corte explícito na tabela limpa; teste isolado | Pendente | Split ainda não definido |
| EDA e variável-alvo | 1,0 | EDA no treino tratado; alvo formalizado no treino; dicionário atualizado | Pendente | EDA e alvo ainda não realizados |
| Engenharia de atributos | 1,0 | Janelas/lags coerentes, sem vazamento, parâmetros no treino, atributos justificados um a um | Pendente | Features ainda não criadas |
| Scrum + diário de bordo | 0,5 | Board com histórico; diário reflexivo de todos | Pendente | Diário ainda não preenchido |
| **Nota final da Sprint 2** | **4,0** | | **___ / 4,0** | |

---

## Observações

A Sprint 2 foi **parcialmente executada**:
- ✅ Merge entre as fontes realizado via script `Merge_Dados.py`
- ✅ Arquivo `data/interim/dados_merged.csv` gerado com 744 registros
- ✅ Inspeção inicial realizada (sem nulos, sem duplicatas)
- ❌ Split temporal não definido
- ❌ Análise exploratória (EDA) não realizada
- ❌ Variável-alvo não formalizada
- ❌ Features derivadas não criadas
- ❌ Dicionário de dados não atualizado para v0.2

**Conclusão:** A Sprint 2 necessita ser completada antes de prosseguir para a Sprint 3. Os artefatos essenciais (split, alvo, features) ainda não foram criados.
