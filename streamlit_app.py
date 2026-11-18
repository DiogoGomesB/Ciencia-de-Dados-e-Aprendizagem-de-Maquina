"""Dashboard interativo Streamlit — Trilha B: Qualidade do Ar (UBC / Mogi das Cruzes).

Interface moderna em tema escuro (Dark Slate), visualmente limpa e orientada a gráficos:
1. Aba "Previsão ao Vivo": status imediato do ar na próxima hora (+1h), gráficos visuais de
   projeção horária (+1h, +7h e +24h), tabela com barras de probabilidade e explicações compactas.
2. Aba "Resultados do Teste": comparativo visual entre modelos, matrizes de confusão, gráfico
   dinâmico de série temporal (IQAr Real vs. Probabilidade Prevista) e auditoria de episódios reais.
3. Aba "Dados, Rótulos e Treinamento": guia didático completo explicando de onde vêm os dados das
   2 APIs, como os rótulos (0 e 1) foram gerados pela regra da CETESB, como o modelo foi treinado
   e o resumo das métricas de avaliação para qualquer pessoa entender.
"""

from __future__ import annotations

import time
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from src.aplicacao.Prever_Proxima_Hora import (
    prever_proxima_hora,
    projetar_proximas_horas,
)
from src.modelagem.Avaliar_Baselines import FEATURES_SPRINT4
from src.transformacao.Calcular_Alvo_IQAr import COLUNA_ALVO, COLUNA_IQAR
from src.transformacao.Features_Temporais import adicionar_resumos_curto_prazo

st.set_page_config(
    page_title="ArPrev | Previsão de Qualidade do Ar (UBC)",
    page_icon="🌬️",
    layout="wide",
    initial_sidebar_state="expanded",
)

COL_PROB = "probabilidade estimada de IQAr > 100"

# =============================================================================
# ESTILO VISUAL — TEMA ESCURO MODERNO (Dark Slate & Clean Dashboard)
# =============================================================================
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
  --bg-page: #0b0f19;
  --bg-surface: #111827;
  --bg-card: #131d2e;
  --border: #1e293b;
  --border-subtle: #273549;
  --primary: #3b82f6;
  --primary-glow: rgba(59, 130, 246, 0.25);
  --green: #10b981;
  --green-glow: rgba(16, 185, 129, 0.2);
  --amber: #f59e0b;
  --amber-glow: rgba(245, 158, 11, 0.2);
  --red: #ef4444;
  --red-glow: rgba(239, 68, 68, 0.2);
  --purple: #8b5cf6;
  --text-main: #f8fafc;
  --text-muted: #cbd5e1;
  --text-light: #94a3b8;
  --radius: 12px;
}

html, body, [class*="css"], .stMarkdown, .stDataFrame, button, input, label {
  font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif !important;
}

.stApp {
  background-color: var(--bg-page);
  color: var(--text-main);
}

.block-container {
  padding-top: 1.2rem;
  padding-bottom: 2.8rem;
  max-width: 1240px;
}

#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }

/* ---------- Barra Lateral ---------- */
section[data-testid="stSidebar"] {
  background-color: var(--bg-surface) !important;
  border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] .block-container { padding-top: 1rem; }
.side-brand { font-size: 1.25rem; font-weight: 800; color: #ffffff; margin: 0.2rem 0 0.1rem 0; letter-spacing: -0.01em; }
.side-sub { font-size: 0.8rem; color: var(--text-light); margin-bottom: 0.9rem; line-height: 1.4; }
.side-card {
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px;
  padding: 0.8rem 0.9rem; margin-bottom: 0.8rem; font-size: 0.82rem; color: var(--text-muted); line-height: 1.5;
}
.side-card b { color: var(--text-main); }
.side-title { font-size: 0.72rem; font-weight: 800; letter-spacing: 0.06em; text-transform: uppercase; color: var(--primary); margin-bottom: 0.45rem; }
.scale-row { display: flex; align-items: center; gap: 0.5rem; margin: 0.25rem 0; }
.scale-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }

/* ---------- Abas (estilo pílula moderna) ---------- */
.stTabs [data-baseweb="tab-list"] {
  gap: 0.4rem; background: var(--bg-surface); border: 1px solid var(--border);
  border-radius: 999px; padding: 0.3rem; width: fit-content; margin-bottom: 1.1rem;
}
.stTabs [data-baseweb="tab"] {
  height: auto; padding: 0.5rem 1.2rem; border-radius: 999px;
  font-weight: 600; font-size: 0.92rem; color: var(--text-light); background: transparent; border: none;
}
.stTabs [data-baseweb="tab"]:hover { color: var(--text-main); }
.stTabs [aria-selected="true"] { background: var(--primary) !important; color: #ffffff !important; box-shadow: 0 4px 12px var(--primary-glow); }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }

/* ---------- Botões e Seletores ---------- */
.stButton > button {
  background: var(--primary) !important; color: #ffffff !important;
  border: none !important; border-radius: 9px; font-weight: 600; padding: 0.55rem 1.1rem;
  box-shadow: 0 4px 14px var(--primary-glow); transition: all 0.2s ease;
}
.stButton > button:hover { opacity: 0.92; transform: translateY(-1px); }

div[role="radiogroup"] { gap: 0.5rem; flex-wrap: wrap; }
div[role="radiogroup"] > label {
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 999px;
  padding: 0.35rem 0.95rem 0.35rem 0.7rem; margin-right: 0 !important; color: var(--text-muted);
}
div[role="radiogroup"] > label:has(input:checked) {
  border-color: var(--primary); background: rgba(59, 130, 246, 0.15); color: #ffffff;
}
.stRadio > label p { font-weight: 600; color: var(--text-main); }

/* ---------- Hero Header ---------- */
.hero {
  background: linear-gradient(135deg, #0b1120 0%, #172554 50%, #0f766e 100%);
  color: #ffffff; border-radius: 16px; padding: 1.4rem 1.8rem; margin-bottom: 0.8rem;
  border: 1px solid rgba(255, 255, 255, 0.08); box-shadow: 0 10px 30px rgba(0, 0, 0, 0.45);
}
.hero-tags { display: flex; flex-wrap: wrap; gap: 0.45rem; margin-bottom: 0.65rem; }
.hero-tag {
  background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.18);
  padding: 0.18rem 0.65rem; border-radius: 999px; font-size: 0.74rem; font-weight: 600; color: #e2e8f0;
}
.hero h1 { font-size: 1.65rem; font-weight: 800; letter-spacing: -0.02em; margin: 0 0 0.35rem 0; color: #ffffff; padding: 0; }
.hero p { margin: 0; color: #cbd5e1; font-size: 0.92rem; line-height: 1.5; max-width: 920px; }

/* ---------- Faixa de Alerta Discreta ---------- */
.disclaimer-banner {
  background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.25);
  border-left: 4px solid var(--amber); border-radius: 10px; padding: 0.65rem 0.95rem;
  margin: 0.5rem 0 1rem 0; font-size: 0.84rem; color: #fde68a; line-height: 1.45;
}

/* ---------- Títulos de Seção ---------- */
.sec { margin: 1.2rem 0 0.6rem 0; }
.sec .eyebrow { font-size: 0.7rem; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; color: var(--primary); }
.sec h3 { font-size: 1.2rem; font-weight: 800; color: var(--text-main); margin: 0.1rem 0 0.15rem 0; padding: 0; letter-spacing: -0.01em; }
.sec p { margin: 0; color: var(--text-light); font-size: 0.88rem; line-height: 1.45; }

/* ---------- Cartões de KPI ---------- */
.grid-kpi { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 0.75rem; margin: 0.4rem 0 0.8rem 0; }
.kpi-card {
  background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius);
  padding: 0.9rem 1rem; position: relative; overflow: hidden;
}
.kpi-card::before { content: ""; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: var(--primary); }
.kpi-card.ok::before { background: var(--green); }
.kpi-card.ok { background: linear-gradient(180deg, rgba(16, 185, 129, 0.08) 0%, var(--bg-card) 60%); }
.kpi-card.ok .value { color: #34d399; }
.kpi-card.alerta::before { background: var(--red); }
.kpi-card.alerta { background: linear-gradient(180deg, rgba(239, 68, 68, 0.12) 0%, var(--bg-card) 60%); }
.kpi-card.alerta .value { color: #f87171; }
.kpi-card .label { font-size: 0.72rem; font-weight: 700; color: var(--text-light); text-transform: uppercase; letter-spacing: 0.04em; }
.kpi-card .value { font-size: 1.5rem; font-weight: 800; color: var(--text-main); margin: 0.15rem 0 0.25rem 0; letter-spacing: -0.01em; }
.kpi-card .desc { font-size: 0.8rem; color: var(--text-muted); line-height: 1.4; }

/* ---------- Cartões Explicativos ---------- */
.grid-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 0.75rem; margin: 0.5rem 0; }
.exp-card {
  background: var(--bg-surface); border: 1px solid var(--border); border-radius: 10px;
  padding: 0.85rem 0.95rem; font-size: 0.84rem; color: var(--text-muted); line-height: 1.5;
}
.exp-card h4 { margin: 0 0 0.3rem 0; font-size: 0.92rem; font-weight: 700; color: var(--text-main); }
.exp-card p { margin: 0; font-size: 0.82rem; color: var(--text-light); line-height: 1.45; }
.exp-card .badge {
  display: inline-block; font-size: 0.68rem; font-weight: 700; text-transform: uppercase;
  padding: 0.1rem 0.45rem; border-radius: 999px; margin-bottom: 0.35rem;
  background: rgba(59, 130, 246, 0.18); color: #60a5fa;
}

/* ---------- Dataframe ---------- */
[data-testid="stDataFrame"] {
  border: 1px solid var(--border) !important; border-radius: var(--radius) !important;
  background: var(--bg-surface) !important; overflow: hidden;
}

/* ---------- Badge Dinâmico de Horizonte ---------- */
.dynamic-badge {
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 9px;
  padding: 0.65rem 0.95rem; margin: 0.4rem 0 0.9rem 0; font-size: 0.84rem;
  color: var(--text-muted); line-height: 1.5;
}
.dynamic-badge b, .dynamic-badge strong { color: var(--text-main); }
.dynamic-badge em { color: var(--primary); font-style: normal; font-weight: 600; }

/* ---------- Seção Profunda de Explicação ---------- */
.exp-grid-2 {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 0.9rem; margin: 0.7rem 0 1rem 0;
}
.exp-card-deep {
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px;
  padding: 1.1rem 1.25rem; font-size: 0.85rem; line-height: 1.55; color: var(--text-muted);
}
.exp-card-deep.oficial { border-top: 3px solid var(--green); }
.exp-card-deep.experimental { border-top: 3px solid var(--amber); }
.exp-card-deep h4 {
  margin: 0 0 0.5rem 0; font-size: 1.02rem; font-weight: 700; color: var(--text-main);
  display: flex; align-items: center; justify-content: space-between;
}
.exp-card-deep ul { margin: 0.3rem 0 0.5rem 1.1rem; padding: 0; }
.exp-card-deep li { margin-bottom: 0.35rem; }
.exp-card-deep b, .exp-card-deep strong { color: var(--text-main); }
.exp-card-deep code {
  background: rgba(255, 255, 255, 0.08); color: #e2e8f0; padding: 0.08rem 0.35rem;
  border-radius: 5px; font-size: 0.85em;
}

/* ---------- Expander ---------- */
.streamlit-expanderHeader {
  background-color: var(--bg-card) !important; border-radius: 10px !important;
  border: 1px solid var(--border) !important; color: var(--text-main) !important; font-weight: 600 !important;
}
</style>
"""


def _html(conteudo: str) -> None:
    linhas = [linha.strip() for linha in conteudo.splitlines() if linha.strip()]
    st.markdown("\n".join(linhas), unsafe_allow_html=True)


def _secao(etiqueta: str, titulo: str, subtitulo: str = "") -> None:
    sub = f"<p>{subtitulo}</p>" if subtitulo else ""
    _html(f'<div class="sec"><div class="eyebrow">{etiqueta}</div><h3>{titulo}</h3>{sub}</div>')


def _kpis(itens: list[tuple[str, str, str, str]]) -> None:
    blocos = "".join(
        f'<div class="kpi-card {cls}"><div class="label">{rot}</div>'
        f'<div class="value">{val}</div><div class="desc">{desc}</div></div>'
        for cls, rot, val, desc in itens
    )
    _html(f'<div class="grid-kpi">{blocos}</div>')


def _int_br(valor: float) -> str:
    return f"{int(valor):,}".replace(",", ".")


def _pct_br(fracao: float, casas: int = 2) -> str:
    return f"{fracao * 100:.{casas}f}".replace(".", ",") + "%"


# =============================================================================
# CARREGAMENTO DE DADOS (com cache)
# =============================================================================
@st.cache_resource
def carregar_artefato_modelo():
    return joblib.load(Path("models/modelo_final_sprint5.joblib"))


@st.cache_data
def carregar_metricas_comparativas() -> pd.DataFrame:
    caminho = Path("reports/modeling/artigo_comparativo_modelos.csv")
    if caminho.exists():
        return pd.read_csv(caminho)
    return pd.read_csv("reports/modeling/sprint5_validation_metrics.csv")


@st.cache_data
def carregar_serie_historica_com_previsoes() -> pd.DataFrame:
    caminho_proc = Path("data/processed/dados_com_alvo_2022-08-04_2026-08-31.csv")
    caminho_int = Path("data/interim/dados_com_alvo_2022-08-04_2026-08-31.csv")
    caminho = caminho_proc if caminho_proc.exists() else caminho_int
    df = pd.read_csv(caminho)
    df = adicionar_resumos_curto_prazo(df, ("ozone", "pm2_5"))
    df["time_dt"] = pd.to_datetime(df["time"])
    df["event_time_dt"] = df["time_dt"] + pd.Timedelta(hours=1)
    df["iqar_evento"] = df[COLUNA_IQAR].shift(-1)
    df_validos = df[df[COLUNA_ALVO].notna()].copy()
    df_validos[COLUNA_ALVO] = df_validos[COLUNA_ALVO].astype(int)

    artefato = carregar_artefato_modelo()
    probs = artefato["pipeline"].predict_proba(df_validos[list(FEATURES_SPRINT4)])[:, 1]
    df_validos["probabilidade_risco"] = probs
    return df_validos


@st.cache_data(ttl=300, show_spinner="Consultando as APIs da Open-Meteo...")
def consultar_previsao_ao_vivo() -> tuple[pd.Series, float, pd.Timestamp]:
    inicio = time.perf_counter()
    resultado = prever_proxima_hora().iloc[0]
    latencia_ms = (time.perf_counter() - inicio) * 1000.0
    return resultado, latencia_ms, pd.Timestamp.now()


@st.cache_data(ttl=300, show_spinner="Calculando as próximas horas...")
def consultar_projecao(horas: int) -> pd.DataFrame:
    return projetar_proximas_horas(horas_frente=horas)


# =============================================================================
# APLICAÇÃO PRINCIPAL
# =============================================================================
def main() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
    artefato = carregar_artefato_modelo()
    limiar = float(artefato["decision_threshold"])

    # ---------------------------------------------------------------- Barra Lateral
    with st.sidebar:
        logo_path = Path("docs/assets/logo.png")
        if logo_path.exists():
            st.image(str(logo_path), width=72)
        _html(
            """
            <div class="side-brand">ArPrev</div>
            <div class="side-sub">Previsão de qualidade do ar · Campus UBC, Mogi das Cruzes – SP</div>
            """
        )
        _html(
            f"""
            <div class="side-card">
            <div class="side-title">Ficha Técnica do Modelo</div>
            <b>Algoritmo:</b> Random Forest (300 árvores)<br>
            <b>Alvo:</b> se IQAr passará de 100 na próxima hora (t+1h)<br>
            <b>Limiar de decisão:</b> {limiar * 100:.0f}% de probabilidade<br>
            <b>Recall no teste final:</b> 98,14% (158 de 161 alertas)
            </div>
            """
        )
        _html(
            """
            <div class="side-card">
            <div class="side-title">Escala de Qualidade do Ar (CETESB)</div>
            <div class="scale-row"><span class="scale-dot" style="background:#10b981"></span><b>0–40</b>&nbsp;Boa</div>
            <div class="scale-row"><span class="scale-dot" style="background:#eab308"></span><b>41–80</b>&nbsp;Moderada</div>
            <div class="scale-row"><span class="scale-dot" style="background:#f97316"></span><b>81–120</b>&nbsp;Ruim</div>
            <div class="scale-row"><span class="scale-dot" style="background:#ef4444"></span><b>121–200</b>&nbsp;Muito ruim</div>
            <div class="scale-row"><span class="scale-dot" style="background:#8b5cf6"></span><b>&gt; 200</b>&nbsp;Péssima</div>
            <div style="margin-top:0.4rem; font-size:0.78rem; color:#94a3b8">
            Condição <b>Inadequada</b>: <code>IQAr &gt; 100</code>
            </div>
            </div>
            """
        )
        st.markdown(
            "[📄 Artigo Técnico](https://diogogomesb.github.io/Ciencia-de-Dados-e-Aprendizagem-de-Maquina/)  \n"
            "[💻 Código no GitHub](https://github.com/DiogoGomesB/Ciencia-de-Dados-e-Aprendizagem-de-Maquina)  \n"
            "[📋 RFC do Projeto](https://github.com/DiogoGomesB/Ciencia-de-Dados-e-Aprendizagem-de-Maquina/blob/main/docs/RFC.md)"
        )

    # ---------------------------------------------------------------- Hero Header
    _html(
        """
        <div class="hero">
        <div class="hero-tags">
        <span class="hero-tag">🎓 Sistemas de Informação · UBC 2026/2</span>
        <span class="hero-tag">🌬️ Trilha B — Qualidade do Ar</span>
        <span class="hero-tag">🌲 Random Forest · 300 árvores</span>
        <span class="hero-tag">📏 Tabela 2.7 da CETESB</span>
        </div>
        <h1>ArPrev — Antecipação de Condições Inadequadas de Ar</h1>
        <p>Monitoramento contínuo sobre o campus da <strong>Universidade Braz Cubas</strong> em Mogi das Cruzes.
        Consultamos as APIs abertas da Open-Meteo em tempo real e calculamos a probabilidade de o Índice de Qualidade
        do Ar (<code>IQAr</code>) ultrapassar <strong>100 pontos</strong> com 1 hora de antecedência.</p>
        </div>
        """
    )
    _html(
        """
        <div class="disclaimer-banner">
        ⚠️ <strong>Aviso de uso responsável:</strong> as previsões são estimativas experimentais obtidas por modelos
        de aprendizado de máquina sobre dados de grade aberta (CAMS / Open-Meteo) e não substituem os relatórios
        oficiais da CETESB ou alertas da Defesa Civil.
        </div>
        """
    )

    aba1, aba2, aba3 = st.tabs(
        [
            "📡 Previsão ao Vivo",
            "📊 Resultados do Teste",
            "📖 Dados, Rótulos e Treinamento",
        ]
    )

    # =========================================================================
    # ABA 1 — PREVISÃO AO VIVO
    # =========================================================================
    with aba1:
        col_tit, col_btn = st.columns([4, 1], vertical_alignment="bottom")
        with col_tit:
            _secao(
                "Monitoramento ao Vivo",
                "Como estará o ar na próxima hora?",
                "Inferência gerada pelo modelo Random Forest sobre a leitura mais recente das APIs.",
            )
        with col_btn:
            if st.button("🔄 Atualizar agora", type="primary", width="stretch"):
                consultar_previsao_ao_vivo.clear()
                consultar_projecao.clear()

        try:
            res_1h, latencia_ms, consultado_em = consultar_previsao_ao_vivo()
            prob_1h = float(res_1h[COL_PROB])
            alerta_1h = prob_1h >= limiar
            horario_dados = pd.Timestamp(res_1h["horário dos dados até t"])
            horario_evento = pd.Timestamp(res_1h["horário do evento previsto"])

            # 4 KPIs principais
            _kpis(
                [
                    (
                        "alerta" if alerta_1h else "ok",
                        f"Previsão ({horario_evento:%d/%m às %H:%M})",
                        "🚨 Alerta" if alerta_1h else "✅ Ar Adequado",
                        (
                            "Risco iminente de IQAr > 100. Recomenda-se remanejar atividades físicas ao ar livre."
                            if alerta_1h
                            else "Condição dentro dos padrões adequados de saúde."
                        ),
                    ),
                    (
                        "",
                        "Probabilidade de Risco",
                        _pct_br(prob_1h, 1),
                        f"Votação das 300 árvores. O alerta dispara a partir de <strong>{limiar * 100:.0f}%</strong>.",
                    ),
                    (
                        "",
                        "Último Dado Usado (t)",
                        f"{horario_dados:%d/%m · %H:%M}",
                        "Hora fechada mais recente recebida da API. O modelo não usa dados futuros.",
                    ),
                    (
                        "",
                        "Tempo de Resposta",
                        f"{latencia_ms:.0f} ms",
                        f"Consulta às 2 APIs, cálculo CETESB e inferência. Atualizado às {consultado_em:%H:%M}.",
                    ),
                ]
            )

            # Seletor de Horizonte
            _secao(
                "Planejamento Temporal",
                "Projeção Dinâmica das Próximas Horas",
                "Selecione o horizonte desejado para atualizar os gráficos visuais e a tabela abaixo.",
            )
            horizonte = st.radio(
                "Horizonte da previsão",
                options=[1, 7, 24],
                index=2,
                horizontal=True,
                label_visibility="collapsed",
                format_func=lambda h: {
                    1: "⏱️ +1 hora · Oficial (só dados medidos)",
                    7: "🌤️ +7 horas · Experimental (turno)",
                    24: "📅 +24 horas · Experimental (dia completo)",
                }[h],
            )

            descricoes_horizonte = {
                1: (
                    "⏱️ <strong>Modo Oficial (+1h):</strong> O modelo lê estritamente medições horárias que já aconteceram e "
                    "estão consolidadas até a hora atual (<em>t</em>) para prever se o ar ficará inadequado na próxima hora "
                    "(<em>t + 1h</em>). É o único horizonte <strong>auditado na prova final com 98,14% de recall</strong>."
                ),
                7: (
                    "🌤️ <strong>Modo Experimental (+7h · Turno):</strong> Aplica a Random Forest hora a hora sobre as "
                    "<strong>previsões meteorológicas e de poluentes</strong> da Open-Meteo para cobrir um turno completo. "
                    "Excelente para planejar aulas e treinos, com incerteza moderada."
                ),
                24: (
                    "📅 <strong>Modo Experimental (+24h · Dia Completo):</strong> Projeta a qualidade do ar ao longo de todas as "
                    "próximas 24 horas. Por depender de previsões meteorológicas futuras de modelos globais, a incerteza é cumulativa "
                    "e cresce com a distância do horizonte."
                ),
            }
            _html(f'<div class="dynamic-badge">{descricoes_horizonte[horizonte]}</div>')

            if horizonte == 1:
                df_proj = res_1h.to_frame().T.assign(**{"horizonte": "+1h", "iqar projetado (CAMS)": np.nan})
            else:
                df_proj = consultar_projecao(horizonte).copy()

            probs_proj = df_proj[COL_PROB].astype(float)
            alertas_proj = probs_proj >= limiar
            col_hora_t = "horário dos dados até t" if "horário dos dados até t" in df_proj.columns else "horário base da janela"

            # ------------------------------------------------ Gráficos Visuais da Projeção
            if horizonte > 1:
                fig_p, (ax_p1, ax_p2) = plt.subplots(1, 2, figsize=(12, 3.6), facecolor="#111827")
                for ax in (ax_p1, ax_p2):
                    ax.set_facecolor("#0b0f19")
                    ax.tick_params(colors="#94a3b8", labelsize=8.5)
                    for s in ax.spines.values():
                        s.set_color("#1e293b")
                    ax.grid(True, color="#1e293b", linestyle="--", alpha=0.6)

                horas_lbl = pd.to_datetime(df_proj["horário do evento previsto"]).dt.strftime("%d/%m %Hh")
                x_i = np.arange(len(df_proj))
                passo = max(1, len(x_i) // 8)

                # Gráfico 1: Probabilidade
                cores_bar = ["#ef4444" if a else "#3b82f6" for a in alertas_proj]
                ax_p1.bar(x_i, probs_proj * 100, color=cores_bar, alpha=0.85, width=0.65)
                ax_p1.axhline(limiar * 100, color="#ef4444", linestyle="--", linewidth=1.5, label=f"Limiar de Alerta ({limiar * 100:.0f}%)")
                ax_p1.set_xticks(x_i[::passo])
                ax_p1.set_xticklabels(horas_lbl.iloc[::passo], rotation=30, ha="right")
                ax_p1.set_ylim(0, 105)
                ax_p1.set_ylabel("Probabilidade (%)", color="#cbd5e1", fontsize=9)
                ax_p1.set_title(f"Probabilidade Prevista de Risco (+1h a +{horizonte}h)", color="#f8fafc", fontsize=10.5, fontweight="bold")
                ax_p1.legend(facecolor="#1e293b", edgecolor="#334155", labelcolor="#f8fafc", fontsize=8.5)

                # Gráfico 2: IQAr projetado (CAMS)
                iqar_proj = pd.to_numeric(df_proj["iqar projetado (CAMS)"], errors="coerce")
                ax_p2.plot(x_i, iqar_proj, marker="o", markersize=3.5, color="#10b981", linewidth=1.8, label="IQAr projetado (API)")
                ax_p2.axhline(100, color="#f59e0b", linestyle="--", linewidth=1.5, label="Limite CETESB (IQAr = 100)")
                ax_p2.fill_between(x_i, 100, np.maximum(100, iqar_proj.fillna(0)), color="#ef4444", alpha=0.25, label="Faixa Inadequada")
                ax_p2.set_xticks(x_i[::passo])
                ax_p2.set_xticklabels(horas_lbl.iloc[::passo], rotation=30, ha="right")
                ax_p2.set_ylabel("IQAr (pontos)", color="#cbd5e1", fontsize=9)
                ax_p2.set_title(f"Projeção do IQAr pela API (+1h a +{horizonte}h)", color="#f8fafc", fontsize=10.5, fontweight="bold")
                ax_p2.legend(facecolor="#1e293b", edgecolor="#334155", labelcolor="#f8fafc", fontsize=8.5)

                fig_p.tight_layout()
                st.pyplot(fig_p)
                plt.close(fig_p)
            else:
                # Termômetro visual de probabilidade para +1h
                fig_1h, ax_g = plt.subplots(figsize=(11, 1.8), facecolor="#111827")
                ax_g.set_facecolor("#0b0f19")
                ax_g.tick_params(colors="#94a3b8", labelsize=8.5)
                for s in ax_g.spines.values():
                    s.set_color("#1e293b")
                ax_g.grid(True, axis="x", color="#1e293b", linestyle="--", alpha=0.6)

                cor_bar = "#ef4444" if alerta_1h else "#10b981"
                ax_g.barh([0], [prob_1h * 100], color=cor_bar, height=0.45, alpha=0.9, label=f"Probabilidade Atual ({prob_1h * 100:.1f}%)")
                ax_g.axvline(limiar * 100, color="#ef4444", linestyle="--", linewidth=1.8, label=f"Limiar de Alerta ({limiar * 100:.0f}%)")
                ax_g.set_xlim(0, 100)
                ax_g.set_yticks([])
                ax_g.set_xlabel("Probabilidade Estimada de IQAr > 100 (%)", color="#cbd5e1", fontsize=9)
                ax_g.set_title(f"Termômetro de Risco para a Próxima Hora ({horario_evento:%d/%m às %H:%M})", color="#f8fafc", fontsize=10.5, fontweight="bold")
                ax_g.legend(loc="upper right", facecolor="#1e293b", edgecolor="#334155", labelcolor="#f8fafc", fontsize=8.5)
                fig_1h.tight_layout()
                st.pyplot(fig_1h)
                plt.close(fig_1h)

            # ------------------------------------------------ Tabela Horária
            tabela = pd.DataFrame(
                {
                    "Horizonte": df_proj["horizonte"].astype(str),
                    "Dado usado (hora t)": pd.to_datetime(df_proj[col_hora_t]).dt.strftime("%d/%m %H:%M"),
                    "Hora prevista (t + 1h)": pd.to_datetime(df_proj["horário do evento previsto"]).dt.strftime("%d/%m %H:%M"),
                    "IQAr previsto pela API": pd.to_numeric(df_proj["iqar projetado (CAMS)"], errors="coerce").round(1),
                    "Probabilidade de ar inadequado": (probs_proj * 100).round(2),
                    "Situação": np.where(alertas_proj, "🚨 Alerta (IQAr > 100)", "✅ Ar Adequado"),
                }
            )
            st.dataframe(
                tabela,
                width="stretch",
                hide_index=True,
                height=min(380, 38 + 35 * len(tabela)),
                column_config={
                    "Probabilidade de ar inadequado": st.column_config.ProgressColumn(
                        "Probabilidade de ar inadequado",
                        help=f"Probabilidade estimada pelo modelo Random Forest. Dispara alerta a partir de {limiar * 100:.0f}%.",
                        format="%.2f%%",
                        min_value=0.0,
                        max_value=100.0,
                    ),
                    "IQAr previsto pela API": st.column_config.NumberColumn(
                        "IQAr previsto pela API",
                        help="Índice IQAr calculado sobre as concentrações previstas pela Open-Meteo. Na linha +1h fica vazio porque usa medições reais já fechadas.",
                        format="%.1f",
                    ),
                },
            )

            # ------------------------------------------------ Detalhes Técnicos (Expander)
            with st.expander("ℹ️ Como funciona a previsão e de onde vêm os dados (clique para abrir)", expanded=False):
                _html(
                    f"""
                    <div class="exp-grid-2">
                    <div class="exp-card-deep oficial">
                    <h4><span>⏱️ Previsão Oficial (+1 hora)</span><span class="badge" style="background:rgba(16,185,129,0.18); color:#34d399">Homologado</span></h4>
                    <p><strong>De onde vêm os dados:</strong> Consultamos duas APIs abertas da Open-Meteo em tempo real com as coordenadas exatas da UBC em Mogi das Cruzes (Lat: -23.5228, Lon: -46.1882):</p>
                    <ul>
                    <li><strong>API de Qualidade do Ar:</strong> Fornece as concentrações dos 6 poluentes regulamentados pela CETESB (Ozônio O₃, PM2,5, PM10, CO, NO₂ e SO₂), simulados pelo modelo atmosférico europeu CAMS (Copernicus).</li>
                    <li><strong>API Meteorológica:</strong> Fornece 5 variáveis de tempo (temperatura, umidade relativa, velocidade do vento, precipitação e pressão atmosférica).</li>
                    </ul>
                    <p><strong>Como é medido:</strong> Utiliza exclusivamente dados que <strong>já aconteceram e estão consolidados até a hora atual (<em>t</em>)</strong>. O modelo não utiliza nenhuma estimativa ou dado futuro na sua entrada: ele analisa a realidade física fechada do ambiente.</p>
                    <p><strong>Como é feito o cálculo:</strong></p>
                    <ul>
                    <li><strong>1. Médias Oficiais da CETESB (Tabela 2.7):</strong> O código calcula as médias móveis exigidas pela norma ambiental (24h para PM2,5 e PM10; 8h para O₃ e CO; 1h para NO₂ e SO₂). A pior nota entre os 6 poluentes define o <code>IQAr</code> da hora <em>t</em>.</li>
                    <li><strong>2. Memória e Tendência Recente:</strong> Calcula as médias das últimas 3 horas e as variações das últimas 2 horas de ozônio e PM2,5 para capturar acúmulo de fumaça ou dispersão.</li>
                    <li><strong>3. Votação das 300 Árvores:</strong> As 15 variáveis entram na Random Forest treinada, que estima a probabilidade de o <code>IQAr</code> ultrapassar 100 pontos exatamente em <em>t + 1h</em>.</li>
                    <li><strong>4. Limiar de Alerta (30%):</strong> Se a probabilidade for igual ou superior a <strong>{limiar * 100:.0f}%</strong>, o painel dispara o <strong>🚨 Alerta</strong> com 1 hora de antecedência.</li>
                    </ul>
                    <p><strong>Por que é o oficial?</strong> Foi rigorosamente homologado e auditado no período de teste fechado (Holdout 2025–2026), alcançando <strong>98,14% de Recall</strong> (avisou 158 de 161 episódios reais). Possui validação estatística completa.</p>
                    </div>

                    <div class="exp-card-deep experimental">
                    <h4><span>🌤️ Projeções Estendidas (+7h e +24h)</span><span class="badge" style="background:rgba(245,158,11,0.18); color:#fbbf24">Experimental</span></h4>
                    <p><strong>De onde vêm os dados:</strong> As mesmas APIs da Open-Meteo disponibilizam <strong>previsões atmosféricas futuras</strong> geradas por modelos numéricos globais de supercomputadores (CAMS Forecast, ECMWF e GFS).</p>
                    <p><strong>Como é feito o cálculo:</strong></p>
                    <ul>
                    <li><strong>1. Leitura do Cenário Futuro:</strong> O sistema lê as concentrações de poluentes e o clima que a API <em>prevê</em> para cada uma das próximas horas (<em>t+1, t+2, ..., t+24</em>).</li>
                    <li><strong>2. Simulação CETESB:</strong> Aplica a mesma Tabela 2.7 da CETESB sobre essas previsões horárias para projetar a curva estimada do <code>IQAr</code> da API.</li>
                    <li><strong>3. Inferência Sequencial:</strong> Alimenta a Random Forest com esse cenário para calcular a probabilidade de risco em cada hora do turno ou do dia.</li>
                    </ul>
                    <p><strong>Por que é classificado como EXPERIMENTAL?</strong></p>
                    <ul>
                    <li><strong>1. Erro em Cascata (Incerteza Composta):</strong> Enquanto a previsão de +1h usa medições reais já fechadas, as projeções de +7h e +24h usam <em>previsões de outros modelos</em> como entrada. Se a previsão do tempo errar a força do vento ou a temperatura da tarde, nosso modelo absorve esse erro.</li>
                    <li><strong>2. Dispersão Cumulativa no Tempo:</strong> A atmosfera é um sistema dinâmico. Uma previsão para 3 a 7 horas à frente possui consistência razoável; para 24 horas à frente, a incerteza meteorológica é naturalmente muito maior.</li>
                    <li><strong>3. Uso Recomendado:</strong> Funciona muito bem como ferramenta de <strong>planejamento preventivo</strong> (ex.: coordenadores checarem pela manhã se a tarde/noite demandará atenção). Porém, a decisão operacional final (remanejar alunos) deve sempre ser confirmada pelo monitoramento oficial de <strong>+1 hora</strong>.</li>
                    </ul>
                    </div>
                    </div>

                    <div class="sec" style="margin-top:1.2rem"><div class="eyebrow">Pipeline Técnico</div><h3>As 4 Etapas do Processamento</h3></div>
                    <div class="grid-cards">
                    <div class="exp-card">
                    <span class="badge">Passo 1 · Coleta</span>
                    <h4>🌐 Duas APIs Abertas</h4>
                    <p>Open-Meteo Air Quality (CAMS) + Weather Forecast para as coordenadas do Campus UBC em Mogi das Cruzes.</p>
                    </div>
                    <div class="exp-card">
                    <span class="badge">Passo 2 · CETESB</span>
                    <h4>📏 Regra da Tabela 2.7</h4>
                    <p>Médias móveis de 24h (partículas), 8h (ozônio/CO) e 1h (NO2/SO2). A pior nota define o IQAr da hora t.</p>
                    </div>
                    <div class="exp-card">
                    <span class="badge">Passo 3 · Features</span>
                    <h4>🧩 15 Pistas Temporais</h4>
                    <p>6 notas de poluentes + 5 variáveis climáticas + 4 resumos de tendência (médias de 3h e variações de 2h de O3 e PM2,5).</p>
                    </div>
                    <div class="exp-card">
                    <span class="badge">Passo 4 · Decisão</span>
                    <h4>🌲 300 Árvores Votam</h4>
                    <p>A Random Forest calcula a probabilidade calibrada de o IQAr passar de 100 em t+1h (alerta com {limiar * 100:.0f}% ou mais).</p>
                    </div>
                    </div>

                    <div style="font-size:0.82rem; color:#94a3b8; margin-top:0.8rem; line-height:1.5;">
                    📖 <strong>Como ler a tabela horária:</strong><br>
                    • <strong>Dado usado (hora t) → Hora prevista (t + 1h):</strong> cada linha usa os dados de uma hora para prever a seguinte.<br>
                    • <strong>IQAr previsto pela API:</strong> nota do ar projetada pela Open-Meteo (na linha +1h fica vazia porque usamos apenas medições reais consolidadas).<br>
                    • <strong>Probabilidade de ar inadequado:</strong> a barra mostra o voto ponderado das árvores. Acima de {limiar * 100:.0f}%, a situação torna-se <strong>🚨 Alerta</strong>.
                    </div>
                    """
                )

        except Exception as erro_api:  # noqa: BLE001
            _html(
                f"""
                <div class="disclaimer-banner">
                ⚠️ Não foi possível consultar a API Open-Meteo no momento (<code>{erro_api}</code>).
                Clique no botão <strong>Atualizar agora</strong> em alguns instantes ou consulte a aba <strong>Resultados do Teste</strong>.
                </div>
                """
            )

    # =========================================================================
    # ABA 2 — RESULTADOS DO TESTE
    # =========================================================================
    with aba2:
        col_t2, col_r2 = st.columns([3, 2], vertical_alignment="bottom")
        with col_t2:
            _secao(
                "Avaliação e Desempenho",
                "Validação dos Modelos no Passado",
                "Comparativo entre os algoritmos testados com divisão estritamente temporal (sem vazamento).",
            )
        with col_r2:
            periodo = st.radio(
                "Período de avaliação",
                options=["holdout_2025_2026", "validacao_2024_Q4"],
                horizontal=True,
                label_visibility="collapsed",
                format_func=lambda p: {
                    "holdout_2025_2026": "🎯 Teste Final · 2025–2026",
                    "validacao_2024_Q4": "🧪 Validação · out–dez/2024",
                }[p],
            )

        descricoes_periodo = {
            "holdout_2025_2026": (
                "🎯 <strong>Prova Final Cega (Holdout 2025–2026):</strong> Avaliação sobre <strong>14.592 horas "
                "consecutivas</strong> (1 ano e 8 meses) que ficaram trancadas durante todo o desenvolvimento. "
                "O modelo nunca tinha visto nenhum desses dados e capturou <strong>158 de 161 alertas reais (98,14% de Recall)</strong>, "
                "deixando passar apenas 3 falhas críticas."
            ),
            "validacao_2024_Q4": (
                "🧪 <strong>Simulado Intermediário (Validação 2024-Q4):</strong> Avaliação sobre <strong>2.208 horas</strong> "
                "(outubro a dezembro de 2024). Serviu como teste prévio para calibrar o limiar de decisão em 30% e selecionar "
                "o melhor algoritmo antes de abrir a prova final."
            ),
        }
        _html(f'<div class="dynamic-badge">{descricoes_periodo[periodo]}</div>')

        nome_periodo = (
            "teste final (jan/2025 a ago/2026)" if periodo == "holdout_2025_2026" else "validação temporal (out a dez/2024)"
        )

        df_comp = carregar_metricas_comparativas()
        df_fold = df_comp[df_comp["fold"] == periodo].copy() if "fold" in df_comp.columns else df_comp.copy()
        df_fold = df_fold.sort_values(["recall_classe_1", "f1_classe_1"], ascending=[False, False])

        rf = df_fold[df_fold["modelo"] == "random_forest_balanced"]
        if not rf.empty:
            rf_row = rf.iloc[0]
            positivos = int(rf_row["tp"] + rf_row["fn"])
            total_h = int(rf_row["tp"] + rf_row["tn"] + rf_row["fp"] + rf_row["fn"])
            tp_rf = int(rf_row["tp"])
            fn_rf = int(rf_row["fn"])
            fp_rf = int(rf_row["fp"])

            _kpis(
                [
                    ("", "Horas Avaliadas", f"{_int_br(total_h)} h", f"Período de {nome_periodo}."),
                    ("", "Episódios Reais (IQAr > 100)", f"{positivos} h", "Momentos em que o ar ficou inadequado de verdade."),
                    (
                        "ok",
                        "Alertas Avisados 1h Antes",
                        f"{tp_rf} de {positivos}",
                        f"<strong>{_pct_br(rf_row['recall_classe_1'], 1)}</strong> de Recall. Capturou quase a totalidade dos riscos.",
                    ),
                    (
                        "alerta" if fn_rf > 0 else "ok",
                        "Erros no Período",
                        f"{fn_rf} FN · {fp_rf} FP",
                        f"{fn_rf} alertas não emitidos (falhas críticas) e {fp_rf} alarmes por cautela.",
                    ),
                ]
            )

        # ------------------------------------------------ Figuras Visuais do Pipeline
        _secao(
            "Evidências Visuais",
            "Métricas Comparativas e Matrizes de Confusão",
            "Gráficos gerados durante a execução do pipeline de modelagem.",
        )
        c_fig1, c_fig2 = st.columns(2)
        with c_fig1:
            caminho_f3 = Path("reports/figures/fig_comparacao_modelos_metricas.png")
            if caminho_f3.exists():
                st.image(str(caminho_f3), caption="Recall, Precisão e F1-Score: Random Forest vs. Baselines no Holdout.")
        with c_fig2:
            caminho_f4 = Path("reports/figures/fig_matriz_confusao_3_arvores.png")
            if caminho_f4.exists():
                st.image(str(caminho_f4), caption="Matrizes de Confusão: Árvore de Decisão CART, Random Forest e XGBoost.")

        _html(
            """
            <div style="font-size:0.83rem; color:#94a3b8; background:var(--bg-card); border:1px solid var(--border); border-radius:9px; padding:0.65rem 0.95rem; margin-top:0.4rem; line-height:1.5;">
            💡 <strong>Como ler os gráficos acima:</strong><br>
            • <strong>Gráfico da Esquerda (Barras de Métricas):</strong> O que mais importa para a saúde pública é a barra azul de <strong>Recall</strong> (quantos % dos episódios perigosos o modelo capturou). Repare que o modelo Dummy tem barra zero de Recall (não avisa nada), enquanto a Random Forest lidera com 98,14%.<br>
            • <strong>Gráfico da Direita (Matrizes de Confusão):</strong> Os quadrantes <strong>verdes (TP)</strong> mostram os acertos de ar perigoso; os <strong>amarelos (FP)</strong> são alarmes por cautela; e os <strong>vermelhos (FN)</strong> são as falhas críticas (ar perigoso sem aviso). A Random Forest teve apenas <strong>3 falhas vermelhas</strong>, contra 6 do XGBoost e 22 da Árvore de Decisão individual.
            </div>
            """
        )

        # ------------------------------------------------ Tabela Comparativa de Modelos
        _secao("Tabela Comparativa", "Qual modelo errou menos?", f"Desempenho detalhado para o período de {nome_periodo}.")
        nomes = {
            "random_forest_balanced": "🏆 Random Forest (escolhido)",
            "xgboost_balanced": "XGBoost",
            "arvore_decisao_cart": "Árvore de Decisão CART",
            "regressao_logistica_balanced": "Regressão Logística",
            "gaussian_naive_bayes": "Naive Bayes",
            "persistencia_iqar_atual": "Persistência (repete hora atual)",
            "dummy_prior": "Dummy (sempre chuta ar adequado)",
        }
        total = df_fold["tp"] + df_fold["tn"] + df_fold["fp"] + df_fold["fn"]
        tabela_comp = pd.DataFrame(
            {
                "Modelo": df_fold["modelo"].map(lambda m: nomes.get(m, m)),
                "Recall (Alertas Detectados)": (df_fold["recall_classe_1"] * 100).round(2),
                "Precisão": (df_fold["precisao_classe_1"] * 100).round(2),
                "F1-Score": (df_fold["f1_classe_1"] * 100).round(2),
                "Acurácia Geral": ((df_fold["tp"] + df_fold["tn"]) / total * 100).round(2),
                "✅ Alertas Certos (TP)": df_fold["tp"].astype(int),
                "❌ Falhas Críticas (FN)": df_fold["fn"].astype(int),
                "⚠️ Alarmes por Cautela (FP)": df_fold["fp"].astype(int),
            }
        )
        st.dataframe(
            tabela_comp,
            width="stretch",
            hide_index=True,
            column_config={
                "Recall (Alertas Detectados)": st.column_config.ProgressColumn(
                    "Recall (Alertas Detectados)",
                    help="De todos os episódios reais de IQAr > 100, quantos % o modelo avisou com 1h de antecedência.",
                    format="%.2f%%",
                    min_value=0.0,
                    max_value=100.0,
                ),
                "F1-Score": st.column_config.ProgressColumn(
                    "F1-Score",
                    help="Média harmônica entre Recall e Precisão.",
                    format="%.2f%%",
                    min_value=0.0,
                    max_value=100.0,
                ),
                "Precisão": st.column_config.NumberColumn("Precisão", format="%.2f%%"),
                "Acurácia Geral": st.column_config.NumberColumn(
                    "Acurácia Geral",
                    help="Atenção: em classes raras a acurácia é ilusória (veja como o Dummy atinge quase 99% sem avisar nenhum alerta).",
                    format="%.2f%%",
                ),
            },
        )

        # ------------------------------------------------ Gráfico Dinâmico: Real vs. Previsto
        _secao(
            "Série Temporal Dinâmica",
            "Previsão Gerada 1h Antes vs. Ocorrência Real",
            "Comportamento hora a hora durante o episódio mais crítico do período selecionado.",
        )
        df_hist = carregar_serie_historica_com_previsoes()
        if periodo == "holdout_2025_2026":
            data_ini = pd.Timestamp("2025-12-24")
            data_fim = pd.Timestamp("2026-01-03")
            titulo_recorte = "Episódio Crítico de Verão no Holdout (24/12/2025 a 03/01/2026)"
        else:
            data_ini = pd.Timestamp("2024-09-25")
            data_fim = pd.Timestamp("2024-10-05")
            titulo_recorte = "Episódio Crítico na Validação (25/09/2024 a 05/10/2024)"

        recorte = df_hist[(df_hist["event_time_dt"] >= data_ini) & (df_hist["event_time_dt"] <= data_fim)].copy()

        if len(recorte) > 0:
            recorte["alerta_emitido"] = (recorte["probabilidade_risco"] >= limiar).astype(int)
            fig_h, (ax_h1, ax_h2) = plt.subplots(2, 1, figsize=(12, 5.4), sharex=True, facecolor="#111827")
            for ax in (ax_h1, ax_h2):
                ax.set_facecolor("#0b0f19")
                ax.tick_params(colors="#94a3b8", labelsize=8.5)
                for s in ax.spines.values():
                    s.set_color("#1e293b")
                ax.grid(True, color="#1e293b", linestyle="--", alpha=0.6)

            # Subplot 1: IQAr Real
            ax_h1.plot(recorte["event_time_dt"], recorte["iqar_evento"], color="#38bdf8", linewidth=1.6, label="IQAr Real no Evento (t+1h)")
            ax_h1.axhline(100, color="#f59e0b", linestyle="--", linewidth=1.5, label="Limite CETESB (IQAr = 100)")
            ev_reais = recorte[recorte[COLUNA_ALVO] == 1]
            if len(ev_reais) > 0:
                ax_h1.scatter(
                    ev_reais["event_time_dt"],
                    ev_reais["iqar_evento"].fillna(105),
                    color="#ef4444",
                    s=28,
                    zorder=5,
                    label="Episódio Real (IQAr > 100)",
                )
            ax_h1.set_ylabel("IQAr (pontos)", color="#cbd5e1", fontsize=9)
            ax_h1.set_title(f"{titulo_recorte} — Ocorrência Real", color="#f8fafc", fontsize=10.5, fontweight="bold")
            ax_h1.legend(loc="upper right", facecolor="#1e293b", edgecolor="#334155", labelcolor="#f8fafc", fontsize=8)

            # Subplot 2: Probabilidade Prevista
            ax_h2.plot(recorte["event_time_dt"], recorte["probabilidade_risco"] * 100, color="#818cf8", linewidth=1.8, label="Probabilidade (Random Forest)")
            ax_h2.axhline(limiar * 100, color="#ef4444", linestyle="--", linewidth=1.5, label=f"Limiar de Alerta ({limiar * 100:.0f}%)")
            ax_h2.fill_between(
                recorte["event_time_dt"],
                0,
                recorte["probabilidade_risco"] * 100,
                where=(recorte["probabilidade_risco"] >= limiar),
                color="#ef4444",
                alpha=0.3,
                label="Período em Alerta Preventivo (1h Antes)",
            )
            ax_h2.set_ylim(0, 105)
            ax_h2.set_ylabel("Probabilidade (%)", color="#cbd5e1", fontsize=9)
            ax_h2.set_xlabel("Data e Hora do Evento", color="#cbd5e1", fontsize=9)
            ax_h2.legend(loc="upper right", facecolor="#1e293b", edgecolor="#334155", labelcolor="#f8fafc", fontsize=8)

            fig_h.tight_layout()
            st.pyplot(fig_h)
            plt.close(fig_h)

            _html(
                """
                <div style="font-size:0.83rem; color:#94a3b8; background:var(--bg-card); border:1px solid var(--border); border-radius:9px; padding:0.65rem 0.95rem; margin-top:0.4rem; line-height:1.5;">
                💡 <strong>Como ler a série temporal acima:</strong><br>
                • <strong>Gráfico Superior (O que aconteceu de verdade):</strong> A linha azul claro mostra o valor real do <code>IQAr</code> medido no campus. A linha amarela tracejada marca o limite regulamentar da CETESB (100 pontos). As <strong>bolinhas vermelhas</strong> destacam os momentos em que o ar de fato ficou inadequado.<br>
                • <strong>Gráfico Inferior (O que a Random Forest previu 1 hora antes):</strong> A linha roxa mostra a probabilidade de risco calculada pelas 300 árvores. Note que <strong>sempre antes de as bolinhas vermelhas estourarem no gráfico de cima, a linha roxa já cruzou a linha de alerta de 30%</strong> (área sombreada vermelha), dando 1 hora cheia de antecedência para agir!
                </div>
                """
            )

        # ------------------------------------------------ Auditoria dos Episódios Reais
        _secao(
            "Auditoria de Episódios",
            "O que o modelo previu 1 hora antes de cada episódio real",
            "Horas em que o IQAr realmente ultrapassou 100 pontos, com as falhas (FN) destacadas no topo.",
        )
        if periodo == "holdout_2025_2026":
            filtro_aud = df_hist["event_time_dt"] >= pd.Timestamp("2025-01-01")
        else:
            filtro_aud = (df_hist["event_time_dt"] >= pd.Timestamp("2024-10-01")) & (
                df_hist["event_time_dt"] < pd.Timestamp("2025-01-01")
            )
        recorte_aud = df_hist[filtro_aud].copy()
        recorte_aud["alerta"] = recorte_aud["probabilidade_risco"] >= limiar
        eventos_aud = recorte_aud[recorte_aud[COLUNA_ALVO] == 1].copy()
        eventos_aud = eventos_aud.sort_values(["alerta", "event_time_dt"], ascending=[True, False])

        tabela_aud = pd.DataFrame(
            {
                "Resultado": np.where(eventos_aud["alerta"], "✅ Avisou 1h antes (TP)", "❌ Não avisou (FN)"),
                "Hora do Aviso (t)": eventos_aud["time_dt"].dt.strftime("%d/%m/%Y %H:%M"),
                "Hora do Episódio (t+1h)": eventos_aud["event_time_dt"].dt.strftime("%d/%m/%Y %H:%M"),
                "IQAr na Hora do Aviso": eventos_aud[COLUNA_IQAR].round(1),
                "IQAr no Episódio Real": eventos_aud["iqar_evento"].round(1),
                "Probabilidade dada 1h antes": (eventos_aud["probabilidade_risco"] * 100).round(1),
            }
        )
        st.dataframe(
            tabela_aud,
            width="stretch",
            hide_index=True,
            height=min(380, 38 + 35 * max(1, len(tabela_aud))),
            column_config={
                "Probabilidade dada 1h antes": st.column_config.ProgressColumn(
                    "Probabilidade dada 1h antes",
                    help=f"Probabilidade estimada na hora t. O alerta dispara a partir de {limiar * 100:.0f}%.",
                    format="%.1f%%",
                    min_value=0.0,
                    max_value=100.0,
                ),
                "IQAr na Hora do Aviso": st.column_config.NumberColumn(format="%.1f"),
                "IQAr no Episódio Real": st.column_config.NumberColumn(format="%.1f"),
            },
        )
        _html(
            """
            <div style="font-size:0.83rem; color:#94a3b8; background:var(--bg-card); border:1px solid var(--border); border-radius:9px; padding:0.65rem 0.95rem; margin-top:0.5rem; line-height:1.5;">
            🔍 <strong>Como ler a auditoria linha a linha:</strong><br>
            • <strong>Transparência com as falhas:</strong> As linhas <strong>❌ Não avisou 1h antes (FN)</strong> aparecem obrigatoriamente no topo para auditoria direta (foram apenas 3 falhas em todo o Holdout de 14.592 horas).<br>
            • <strong>Antecipação comprovada:</strong> Compare a coluna <em>IQAr na Hora do Aviso</em> com <em>IQAr no Episódio Real</em>. Em dezenas de episódios, o IQAr ainda estava abaixo de 100 (ar normal) no momento do aviso, provando que o modelo antecipa o pico antes de o ar piorar.
            </div>
            """
        )

        # ------------------------------------------------ Metodologia Explicada (Expander)
        with st.expander("ℹ️ Metodologia e Conceitos: Split Temporal, Acurácia vs. Recall e Tipos de Erro (clique para abrir)", expanded=False):
            _html(
                f"""
                <div class="exp-grid-2">
                <div class="exp-card-deep oficial">
                <h4><span>⏳ Split Temporal (Sem Shuffle)</span><span class="badge" style="background:rgba(59,130,246,0.18); color:#60a5fa">Metodologia</span></h4>
                <p><strong>De onde vêm os dados históricos:</strong> Analisamos <strong>35.736 horas consecutivas</strong> (de 04/08/2022 a 31/08/2026) sobre Mogi das Cruzes.</p>
                <p><strong>Como o tempo foi dividido:</strong></p>
                <ul>
                <li><strong>Treino (21.121 h · 2022 a set/2024):</strong> O passado utilizado pelos algoritmos para aprender padrões atmosféricos e correlações físico-químicas.</li>
                <li><strong>Validação (2.208 h · out a dez/2024):</strong> Simulado intermediário para calibrar hiperparâmetros e fixar o limiar de decisão em 30%.</li>
                <li><strong>Teste Final Cego / Holdout (14.592 h · jan/2025 a ago/2026):</strong> Prova final guardada a sete chaves, aberta uma única vez para medir a eficácia real.</li>
                </ul>
                <p><strong>Por que o sorteio aleatório é proibido?</strong> Em problemas como fotos de cães e gatos, pode-se sortear dados à vontade. Porém, em séries temporais de clima, sortear horas causaria <strong>vazamento de dados (data leakage)</strong>: o modelo treinaria com as 14h de uma terça e tentaria prever as 15h da mesma terça. Isso seria "colar na prova", criando uma ilusão de perfeição. O Split Temporal garante que o modelo só aprende com o passado e prevê o futuro inédito.</p>
                </div>

                <div class="exp-card-deep experimental">
                <h4><span>⚠️ A Armadilha da Acurácia Geral</span><span class="badge" style="background:rgba(239,68,68,0.18); color:#f87171">Métrica Crítica</span></h4>
                <p><strong>O paradoxo do ar limpo:</strong> Em Mogi das Cruzes, felizmente, em mais de <strong>97,5% do tempo o ar é adequado</strong> (IQAr ≤ 100). Apenas em 2,53% das horas o ar fica inadequado (evento raro e perigoso).</p>
                <p><strong>O modelo "Dummy" (Preguiçoso):</strong></p>
                <ul>
                <li>Se criarmos um modelo bobo que simplesmente chuta <em>"Ar Adequado"</em> em todas as 14.592 horas do teste, ele acertará 14.431 horas normais e terá impressionantes <strong>98,90% de Acurácia Geral</strong>!</li>
                <li>Porém, ele deixará passar <strong>161 de 161 episódios de poluição (0% de Recall)</strong>. Alunos asmáticos fariam treinos ao ar livre sob ar tóxico sem receber nenhum aviso.</li>
                </ul>
                <p><strong>Por que escolhemos o Recall da Classe 1?</strong> O Recall mede: <em>"De todos os episódios em que o ar realmente ficou perigoso, quantos % o modelo conseguiu avisar com antecedência?"</em>. A Random Forest atingiu <strong>98,14% de Recall</strong>, avisando 158 de 161 episódios reais, com <strong>F1-Score de 87,05%</strong> (equilíbrio contra alarmes em excesso).</p>
                </div>

                <div class="exp-card-deep">
                <h4><span>🏥 Impacto Prático na Saúde Pública</span><span class="badge" style="background:rgba(16,185,129,0.18); color:#34d399">Interpretação</span></h4>
                <p>O que significa cada tipo de resultado no mundo real:</p>
                <ul>
                <li><strong>✅ Verdadeiro Positivo (TP = 158): "Proteção Efetiva"</strong><br>
                O modelo avisou 1 hora antes e o ar realmente passou de 100. Alunos foram encaminhados para a quadra coberta e janelas foram fechadas a tempo.</li>
                <li><strong>❌ Falso Negativo (FN = 3): "Falha Crítica (Pior Erro)"</strong><br>
                O ar ficou perigoso e o modelo não avisou. Expõe pessoas vulneráveis sem aviso. Minimizamos esse erro ao máximo (apenas 3 falhas em 14.592 horas).</li>
                <li><strong>⚠️ Falso Positivo (FP = 44): "Alarme por Cautela"</strong><br>
                O modelo emitiu alerta, mas o IQAr parou em 85 ou 95 (quase 100). O treino foi transferido por precaução. Em saúde humana, o excesso de zelo é infinitamente preferível à negligência.</li>
                <li><strong>🛡️ Verdadeiro Negativo (TN = 14.387): "Rotina Normal"</strong><br>
                Dia com ar limpo em que o sistema permaneceu em silêncio, sem alarmes falsos desnecessários.</li>
                </ul>
                </div>

                <div class="exp-card-deep">
                <h4><span>🌲 Por que a Random Forest Venceu?</span><span class="badge" style="background:rgba(139,92,246,0.18); color:#a78bfa">Algoritmo Escolhido</span></h4>
                <p>Comparativo didático entre as 7 abordagens avaliadas:</p>
                <ul>
                <li><strong>Dummy:</strong> 0% de Recall (inútil para saúde).</li>
                <li><strong>Persistência:</strong> repete a hora atual; chega sempre 1 hora atrasada (não antecipa picos rápidos).</li>
                <li><strong>Regressão Logística & Naive Bayes:</strong> modelos lineares simples que não capturam inversões térmicas complexas.</li>
                <li><strong>Árvore de Decisão Individual (CART):</strong> sofre com alta variância e perdeu 22 alertas (86,34% de Recall).</li>
                <li><strong>XGBoost:</strong> excelente modelo, mas ainda perdeu 6 alertas críticos (96,27% de Recall).</li>
                <li><strong>Random Forest (300 árvores):</strong> venceu ao combinar 300 árvores de decisão independentes (bagging). O comitê cancela os ruídos individuais, atingindo <strong>98,14% de Recall</strong> e <strong>F1 de 87,05%</strong>, com estabilidade máxima.</li>
                </ul>
                </div>
                </div>
                """
            )

    # =========================================================================
    # ABA 3 — DADOS, RÓTULOS E TREINAMENTO (GUIA DIDÁTICO COMPLETO)
    # =========================================================================
    with aba3:
        _secao(
            "Guia Didático Completo",
            "Como construímos o sistema: dos dados brutos ao alerta preventivo",
            "Explicação clara e sem jargões pesados sobre de onde vêm os dados, como criamos o gabarito (rótulos 0 e 1), como treinamos a Random Forest e como avaliamos as métricas.",
        )

        _kpis(
            [
                (
                    "",
                    "Base Histórica Total",
                    "35.736 horas",
                    "4 anos contínuos (ago/2022 a ago/2026) medidos hora a hora para o Campus da UBC em Mogi das Cruzes.",
                ),
                (
                    "",
                    "Fontes Integradas",
                    "2 APIs Abertas",
                    "Qualidade do Ar (6 poluentes CAMS) + Meteorologia (5 variáveis de clima), unidas pela mesma hora.",
                ),
                (
                    "alerta",
                    "Rótulos (Gabarito 0 vs. 1)",
                    "905 alertas (2,53%)",
                    "905 horas de ar inadequado (<strong>Rótulo = 1</strong>) contra 34.807 horas de ar adequado (<strong>Rótulo = 0</strong>).",
                ),
                (
                    "ok",
                    "Modelo Treinado",
                    "15 Pistas → +1h",
                    f"300 árvores da Random Forest leem a hora <em>t</em> e disparam alerta a partir de <strong>{limiar * 100:.0f}%</strong> de risco.",
                ),
            ]
        )

        # ------------------------------------------------ 1. De onde pegamos os dados
        _secao(
            "1 · Origem dos Dados",
            "De onde pegamos os dados e por que usamos duas APIs?",
            "Poluição e clima caminham juntos: uma API mede os poluentes no ar e a outra informa se o vento e a chuva vão espalhá-los ou concentrá-los.",
        )
        _html(
            """
            <div class="exp-grid-2">
            <div class="exp-card-deep oficial">
            <h4><span>🏭 API 1 — Poluentes do Ar (Open-Meteo Air Quality / CAMS)</span><span class="badge" style="background:rgba(16,185,129,0.18); color:#34d399">Gera o IQAr e Rótulos</span></h4>
            <p><strong>De onde vem:</strong> Reanálise química global do programa europeu <em>Copernicus Atmosphere Monitoring Service (CAMS)</em>, consultada exatamente nas coordenadas do campus da <strong>Universidade Braz Cubas</strong> (<code>Latitude -23.5228, Longitude -46.1882</code>).</p>
            <p><strong>O que coletamos (os 6 poluentes oficiais da CETESB):</strong></p>
            <ul>
            <li><strong>Ozônio (O₃):</strong> poluente que se forma à tarde quando a luz do sol reage com gases de escapamento.</li>
            <li><strong>Partículas Finas (PM2,5) e Inaláveis (PM10):</strong> poeira fina e fumaça de queimadas ou veículos que penetram nos pulmões.</li>
            <li><strong>Gases urbanos (CO, NO₂ e SO₂):</strong> Monóxido de Carbono, Dióxido de Nitrogênio e Dióxido de Enxofre ligados ao trânsito e à indústria.</li>
            </ul>
            <p><strong>Papel duplo no projeto:</strong> Essa API serve tanto para <strong>calcular a nota oficial do ar (<code>IQAr</code>) e criar o gabarito (rótulo 0 ou 1)</strong> quanto para fornecer as 6 notas de poluição da hora atual que o modelo lê.</p>
            </div>

            <div class="exp-card-deep">
            <h4><span>🌦️ API 2 — Condições do Tempo (Open-Meteo Weather Archive)</span><span class="badge" style="background:rgba(59,130,246,0.18); color:#60a5fa">Pistas de Clima</span></h4>
            <p><strong>De onde vem:</strong> Reanálise meteorológica horária de superfície (ERA5 / Open-Meteo) consultada para a mesma coordenada da UBC e no mesmo fuso horário (<code>America/Sao_Paulo</code>).</p>
            <p><strong>O que coletamos (5 variáveis de clima):</strong></p>
            <ul>
            <li><strong>Temperatura do ar a 2m (°C) e Umidade Relativa (%):</strong> calor forte e ar seco aceleram a formação de ozônio e mantêm a poeira suspensa.</li>
            <li><strong>Velocidade do Vento (km/h) e Chuva (mm):</strong> vento forte sopra a fumaça para longe e a chuva "lava" as partículas do ar.</li>
            <li><strong>Pressão Atmosférica (hPa):</strong> ajuda a identificar bloqueios atmosféricos e inversões térmicas que "tampam" a poluição perto do chão.</li>
            </ul>
            <p><strong>Por que não rotulamos essa segunda API separadamente?</strong> Porque pela norma da CETESB quem define se o ar está poluído são os <strong>poluentes</strong>, e não o calor ou o vento isolados. Ao juntarmos as duas APIs pela data e hora exata (<code>time</code>), o clima entra na mesma linha como <strong>pistas explicativas (features)</strong> para o modelo prever se o ar vai piorar ou limpar na hora seguinte!</p>
            </div>
            </div>
            """
        )

        # ------------------------------------------------ 2. Como criamos os rótulos
        _secao(
            "2 · Rotulagem dos Dados (Gabarito)",
            "Como transformamos números brutos no rótulo 0 (Ar Adequado) ou 1 (Alerta)?",
            "Não inventamos nenhuma regra subjetiva: aplicamos a matemática oficial da Tabela 2.7 da CETESB e olhamos 1 hora para frente.",
        )
        _html(
            """
            <div class="grid-cards">
            <div class="exp-card">
            <span class="badge">Passo A · Médias da Lei</span>
            <h4>📏 Médias Móveis da CETESB</h4>
            <p>A CETESB não avalia um minuto isolado. Calculamos a média exigida por lei para cada poluente: <strong>24 horas</strong> para PM2,5 e PM10; <strong>8 horas</strong> para Ozônio e CO (convertendo CO para ppm); e <strong>1 hora</strong> direta para NO₂ e SO₂.</p>
            </div>
            <div class="exp-card">
            <span class="badge">Passo B · Nota de 0 a 300+</span>
            <h4>🏆 A Pior Nota Vira o IQAr</h4>
            <p>Cada poluente recebe uma nota pela Tabela 2.7 da CETESB (0–40 Boa, 41–80 Moderada, 81–120 Ruim, &gt;100 Inadequada). O <strong>IQAr da hora <em>t</em></strong> é sempre a <strong>maior (pior) nota</strong> entre os 6 poluentes naquela hora.</p>
            </div>
            <div class="exp-card">
            <span class="badge">Passo C · Olhar para t + 1h</span>
            <h4>⏭️ Deslocamento de +1 Hora</h4>
            <p>Como o objetivo é <strong>avisar 1 hora antes</strong>, a linha da hora <em>t</em> recebe como gabarito o que aconteceu na hora seguinte (<em>t + 1h</em>): se o IQAr de <em>t + 1h</em> passou de <strong>100</strong>, a linha recebe <strong>Rótulo = 1 (Alerta)</strong>; caso contrário, <strong>Rótulo = 0 (Adequado)</strong>.</p>
            </div>
            </div>
            """
        )

        tabela_exemplo_rotulo = pd.DataFrame(
            {
                "Hora da Linha (t)": ["12:00", "13:00", "14:00", "15:00"],
                "IQAr Medido Agora (hora t)": [
                    "78,0 (Moderada)",
                    "96,0 (Ainda ≤ 100)",
                    "106,5 (Inadequada)",
                    "109,2 (Inadequada)",
                ],
                "IQAr na Próxima Hora (t + 1h)": [
                    "96,0 às 13:00 (≤ 100)",
                    "106,5 às 14:00 (> 100!)",
                    "109,2 às 15:00 (> 100!)",
                    "84,0 às 16:00 (≤ 100)",
                ],
                "Rótulo Gravado na Linha (Alvo)": [
                    "0 — ✅ Ar Adequado",
                    "1 — 🚨 Emitir Alerta 1h Antes!",
                    "1 — 🚨 Manter Alerta!",
                    "0 — ✅ Ar Adequado",
                ],
                "Explicação Simples do Gabarito": [
                    "Às 13:00 o índice subiu para 96, mas ainda não ultrapassou 100.",
                    "Às 13:00 o ar ainda estava ≤ 100, mas às 14:00 passou de 100. O Rótulo 1 ensina o modelo a avisar já às 13:00!",
                    "Às 15:00 o ar continuará acima de 100, então às 14:00 o alerta permanece ativo.",
                    "Às 16:00 o vento limpou o ar (caiu para 84), então às 15:00 já não há alerta para a próxima hora.",
                ],
            }
        )
        st.dataframe(tabela_exemplo_rotulo, width="stretch", hide_index=True)

        # ------------------------------------------------ 3. Como treinamos o modelo
        _secao(
            "3 · Treinamento do Modelo",
            "Como ensinamos a Random Forest a prever sem trapacear?",
            "Entregamos 15 pistas da hora atual, separamos passado e futuro sem sorteio e compensamos a raridade dos dias poluídos.",
        )
        _html(
            f"""
            <div class="exp-grid-2">
            <div class="exp-card-deep">
            <h4><span>🧩 As 15 Pistas (Features) que o Modelo Lê na Hora <em>t</em></span><span class="badge" style="background:rgba(139,92,246,0.18); color:#a78bfa">Entradas do Modelo</span></h4>
            <p>Para decidir se o ar vai passar de 100 na próxima hora, o modelo analisa exatamente <strong>15 informações</strong> da hora atual:</p>
            <ul>
            <li><strong>1. As 6 Notas Atuais dos Poluentes (Subíndices CETESB):</strong> notas individuais de Ozônio, PM2,5, PM10, CO, NO₂ e SO₂ na hora <em>t</em>. Mostram qual poluente já está perto do limite de 100.</li>
            <li><strong>2. Os 4 Resumos de Memória Curta (Velocidade de Subida):</strong> a média das últimas 3 horas (<code>media_3h</code>) e a variação das últimas 2 horas (<code>delta_2h</code>) do Ozônio e do PM2,5. É assim que o modelo diferencia um <code>IQAr = 92</code> que está <strong>subindo rápido</strong> (vai estourar 100!) de um <code>IQAr = 92</code> que já está <strong>caindo</strong>.</li>
            <li><strong>3. As 5 Variáveis de Clima:</strong> Temperatura, Umidade, Vento, Chuva e Pressão na hora <em>t</em>, que indicam se o tempo vai concentrar ou espalhar a poluição nos próximos 60 minutos.</li>
            </ul>
            <p><em>Nota de engenharia:</em> removemos os valores brutos originais em µg/m³ quando já usamos suas notas CETESB para evitar informação duplicada (colinearidade).</p>
            </div>

            <div class="exp-card-deep oficial">
            <h4><span>🌲 Como Treinamos as 300 Árvores (Sem Vazamento)</span><span class="badge" style="background:rgba(16,185,129,0.18); color:#34d399">Treinamento</span></h4>
            <p>O treinamento seguiu <strong>3 regras rigorosas</strong> de Ciência de Dados:</p>
            <ul>
            <li><strong>1. Divisão Cronológica Estrita (Split Temporal):</strong> nunca embaralhamos as horas! O modelo estudou apenas o passado (<strong>Treino: 2022 a set/2024 — 21.121 h</strong>), foi ajustado num simulado (<strong>Validação: out a dez/2024 — 2.208 h</strong>) e fez a prova final cega no futuro (<strong>Holdout: 2025 a 2026 — 14.592 h</strong>).</li>
            <li><strong>2. Peso Equilibrado para Eventos Raros (<code>class_weight = "balanced"</code>):</strong> como só <strong>2,53%</strong> das horas têm <code>Rótulo = 1</code>, demos peso ~39 vezes maior para cada hora poluída durante o treino. Assim, o modelo é fortemente penalizado se ignorar um episódio de ar ruim.</li>
            <li><strong>3. Comitê de 300 Árvores + Régua de {limiar * 100:.0f}%:</strong> limitamos a profundidade de cada árvore (<code>max_depth = 8</code>) para ela aprender regras gerais em vez de decorar o passado. Quando <strong>{limiar * 100:.0f}% ou mais</strong> das árvores votam risco, o alerta preventivo é acionado!</li>
            </ul>
            </div>
            </div>
            """
        )

        # ------------------------------------------------ 4. Resumo das Métricas
        _secao(
            "4 · Resumo das Métricas",
            "Como medimos se o modelo é bom e por que a Acurácia engana?",
            "Como os rótulos são muito desbalanceados (97,5% ar bom vs. 2,5% ar ruim), precisamos olhar para as métricas da Classe 1 (Alerta).",
        )
        _html(
            """
            <div class="exp-grid-2">
            <div class="exp-card-deep oficial">
            <h4><span>🎯 As 3 Métricas que Realmente Importam (Foco no Alerta)</span><span class="badge" style="background:rgba(16,185,129,0.18); color:#34d399">Critério Oficial</span></h4>
            <ul>
            <li><strong>1. Recall / Sensibilidade (98,14% no Teste Final — Métrica Principal):</strong><br>
            <em>Pergunta em português claro:</em> "De todas as 161 horas em que o ar realmente ficou inadequado em 2025–2026, quantas o modelo conseguiu avisar 1 hora antes?"<br>
            <em>Resultado:</em> Avisou <strong>158 de 161</strong> (perdeu apenas 3). É nossa métrica número 1 porque deixar de avisar um episódio real (<strong>Falso Negativo</strong>) expõe alunos à poluição sem proteção.</li>
            <li><strong>2. Precisão (78,22% no Teste Final):</strong><br>
            <em>Pergunta em português claro:</em> "Quando o painel toca o alarme, qual a chance de o ar realmente passar de 100?"<br>
            <em>Resultado:</em> De 202 alarmes emitidos no teste, <strong>158 eram ar inadequado real</strong> e <strong>44 foram alarmes por cautela (Falsos Positivos)</strong> em horas em que o índice subiu perto de 100 mas recuou.</li>
            <li><strong>3. F1-Score (87,05% no Teste Final):</strong><br>
            <em>Pergunta em português claro:</em> "O modelo tem bom equilíbrio entre capturar todos os perigos e não tocar alarme falso o dia inteiro?"<br>
            <em>Resultado:</em> Combina Recall e Precisão numa nota única. Mostra que a Random Forest protege a saúde com alta confiabilidade operacional.</li>
            </ul>
            </div>

            <div class="exp-card-deep experimental">
            <h4><span>⚠️ Por que NÃO escolhemos o modelo pela Acurácia Geral?</span><span class="badge" style="background:rgba(245,158,11,0.18); color:#fbbf24">Cuidado com a Ilusão</span></h4>
            <p><strong>O número que parece perfeito, mas esconde o perigo:</strong></p>
            <ul>
            <li>No teste final de 2025–2026 (14.592 horas), o ar esteve adequado em <strong>14.431 horas (98,90% do tempo)</strong> e inadequado em apenas <strong>161 horas (1,10% do tempo)</strong>.</li>
            <li>Se criarmos um modelo preguiçoso (<em>Dummy</em>) que <strong>nunca faz cálculo nenhum e chuta "Ar Adequado" o ano inteiro</strong>, ele vai acertar todas as 14.431 horas normais e ganhar <strong>98,90% de Acurácia Geral</strong>!</li>
            <li>Porém, esse modelo preguiçoso terá <strong>0% de Recall</strong> (errará todas as 161 horas poluídas) e será 100% inútil para proteger a universidade.</li>
            </ul>
            <p><strong>Resumo para guardar:</strong> A <em>Acurácia Geral</em> (que na nossa Random Forest chegou a <strong>99,68%</strong>) só é alta porque quase todos os dias são normais (14.387 Verdadeiros Negativos). Para provar que a inteligência artificial funciona em eventos raros, o que vale é o <strong>Recall (98,14%)</strong> e o <strong>F1-Score (87,05%)</strong> sobre os episódios de risco!</p>
            </div>
            </div>
            """
        )

        # ------------------------------------------------ Expander Visual Opcional
        with st.expander("🖼️ Ver Diagramas do Pipeline, Importância das 15 Variáveis e Árvore de Decisão (clique para abrir)", expanded=False):
            c_d1, c_d2 = st.columns(2)
            with c_d1:
                caminho_pipe = Path("docs/diagramas/diagrama_pipeline.jpg")
                if caminho_pipe.exists():
                    st.image(str(caminho_pipe), caption="Arquitetura completa do pipeline (da coleta nas 2 APIs até a decisão em produção).")
            with c_d2:
                caminho_split = Path("docs/diagramas/diagrama_split_temporal_explicado.jpg")
                if caminho_split.exists():
                    st.image(str(caminho_split), caption="Infográfico da Divisão Temporal (Treino, Validação e Holdout sem vazamento).")

            c_d3, c_d4 = st.columns(2)
            with c_d3:
                caminho_imp = Path("reports/figures/fig_importancia_e_latencia.png")
                if caminho_imp.exists():
                    st.image(str(caminho_imp), caption="Ranking das variáveis que mais pesam na decisão da Random Forest e tempo de resposta.")
            with c_d4:
                caminho_over = Path("reports/figures/fig_overfitting_profundidade.png")
                if caminho_over.exists():
                    st.image(str(caminho_over), caption="Controle de profundidade das árvores (por que evitamos árvores profundas que decoram o treino).")


if __name__ == "__main__":
    main()
