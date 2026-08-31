# Ciência de Dados e Aprendizagem de Máquina

**Projeto Acadêmico** — Universidade Braz Cubas  
**Turma:** Segunda Noite N1  

## 📚 Sobre o Projeto

Projeto desenvolvido para a disciplina de Ciência de Dados e Aprendizagem de Máquina da Universidade Braz Cubas. O tema central é a **Qualidade do Ar Inadequada**, aplicando técnicas de Ciência de Dados para analisar dados ambientais e, posteriormente, desenvolver um modelo preditivo.

Atualmente, o projeto encontra-se na etapa de **Coleta de Dados**, utilizando informações históricas obtidas por meio de APIs públicas.

---

## 🎯 Objetivo

Utilizar dados históricos de qualidade do ar e condições meteorológicas para identificar e analisar fatores relacionados à ocorrência de condições inadequadas de qualidade do ar.

### Fontes de Dados
* **Open-Meteo Air Quality API** — Dados relacionados à qualidade do ar.
* **Open-Meteo Historical Weather API** — Dados meteorológicos históricos.

---

## 👥 Integrantes

| Nome | R.A. |
| :--- | :--- |
| Davi Gama dos Santos | 33121079 |
| Diogo Gomes Barbosa | 35866276 |
| Eudenis de Souza Vieira | 32751621 |
| Gabriel Januário Alves | 35609991 |
| João Pedro Barreto da Silva | 33297185 |

---

## 🛠️ Tecnologias Utilizadas

* **Python** (Linguagem principal)
* **Bibliotecas para requisições e manipulação de dados** *(ex: Requests, Pandas - a definir conforme o avanço)*
* **APIs REST** (Open-Meteo)

---

## 📁 Estrutura do Projeto

```text
PROJETOAPI/
│
├── dados/
│   ├── processed/
│   │   └── # Dados após limpeza e processamento
│   │
│   └── raw/
│       ├── air_quality_raw.json
│       └── weather_raw.json
│
├── src/
│   ├── coleta/
│   │   └── Coleta_Dados.py
│   │
│   ├── exploracao/
│   │   └── # Análise exploratória dos dados
│   │
│   ├── features/
│   │   └── # Criação e seleção de variáveis
│   │
│   ├── limpeza/
│   │   └── # Tratamento e preparação dos dados
│   │
│   └── modelo/
│       └── # Treinamento e aplicação do modelo
│
└── README.md
