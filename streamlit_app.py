"""Dashboard interativo Streamlit — Trilha B: Qualidade do Ar (UBC / Mogi das Cruzes).

Interface única e coerente (mesma paleta do artigo em docs/index.html), pensada para público leigo:
1. Aba "Previsão ao vivo": resultado primeiro (cartões), depois como ele foi calculado e a tabela
   das próximas horas (+1h oficial, +7h e +24h experimentais).
2. Aba "Resultados do teste": seletor de período (Holdout 2025–2026 ou Validação 2024-Q4), tabela
   comparativa dos modelos, explicação das métricas e auditoria linha a linha dos episódios reais.
"""

from __future__ import annotations

import time
from pathlib import Path

import joblib
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
# ESTILO VISUAL ÚNICO (mesma paleta do artigo: azul #2563eb, verde #059669, âmbar #d97706)
# =============================================================================
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
  --primary: #2563eb;
  --primary-dark: #1d4ed8;
  --primary-subtle: #eff6ff;
  --green: #059669;
  --green-subtle: #ecfdf5;
  --amber: #d97706;
  --amber-subtle: #fffbeb;
  --red: #dc2626;
  --red-subtle: #fef2f2;
  --purple: #7c3aed;
  --purple-subtle: #f5f3ff;
  --text: #0f172a;
  --muted: #475569;
  --light: #64748b;
  --border: #e2e8f0;
  --surface: #ffffff;
  --page: #f8fafc;
  --radius: 14px;
  --shadow: 0 1px 2px rgba(15, 23, 42, 0.04), 0 8px 24px -12px rgba(15, 23, 42, 0.12);
}

html, body, [class*="css"], .stMarkdown, .stDataFrame, button, input, label {
  font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif !important;
}

.block-container { padding-top: 1.4rem; padding-bottom: 3rem; max-width: 1240px; }
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }

/* ---------- Barra lateral ---------- */
section[data-testid="stSidebar"] {
  background: var(--surface);
  border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] .block-container { padding-top: 1rem; }
.side-brand { font-size: 1.15rem; font-weight: 800; color: var(--text); margin: 0.2rem 0 0.1rem 0; }
.side-sub { font-size: 0.8rem; color: var(--light); margin-bottom: 0.9rem; }
.side-card {
  background: var(--page); border: 1px solid var(--border); border-radius: 12px;
  padding: 0.8rem 0.9rem; margin-bottom: 0.8rem; font-size: 0.84rem; color: var(--muted); line-height: 1.5;
}
.side-card b { color: var(--text); }
.side-title { font-size: 0.72rem; font-weight: 800; letter-spacing: 0.06em; text-transform: uppercase; color: var(--light); margin-bottom: 0.45rem; }
.scale-row { display: flex; align-items: center; gap: 0.5rem; margin: 0.22rem 0; }
.scale-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }

/* ---------- Abas (estilo pílula) ---------- */
.stTabs [data-baseweb="tab-list"] {
  gap: 0.4rem; background: var(--surface); border: 1px solid var(--border);
  border-radius: 999px; padding: 0.3rem; width: fit-content; margin-bottom: 1.1rem;
}
.stTabs [data-baseweb="tab"] {
  height: auto; padding: 0.5rem 1.1rem; border-radius: 999px;
  font-weight: 600; font-size: 0.92rem; color: var(--muted); background: transparent;
}
.stTabs [aria-selected="true"] { background: var(--primary) !important; color: #ffffff !important; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }

/* ---------- Botões e seletores ---------- */
.stButton > button {
  border-radius: 10px; font-weight: 600; padding: 0.55rem 1rem;
  box-shadow: 0 4px 12px -6px rgba(37, 99, 235, 0.55);
}
div[role="radiogroup"] { gap: 0.5rem; flex-wrap: wrap; }
div[role="radiogroup"] > label {
  background: var(--surface); border: 1px solid var(--border); border-radius: 999px;
  padding: 0.35rem 0.9rem 0.35rem 0.6rem; margin-right: 0 !important;
}
div[role="radiogroup"] > label:has(input:checked) { border-color: var(--primary); background: var(--primary-subtle); }
.stRadio > label p { font-weight: 600; color: var(--text); }

/* ---------- Tabelas ---------- */
[data-testid="stDataFrame"] {
  border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden;
  box-shadow: var(--shadow); background: var(--surface);
}

/* ---------- Cabeçalho (hero) ---------- */
.hero {
  background: linear-gradient(120deg, #0f172a 0%, #1e3a8a 55%, #0f766e 100%);
  color: #ffffff; border-radius: 20px; padding: 1.7rem 2rem; margin-bottom: 0.9rem;
  box-shadow: 0 18px 40px -20px rgba(15, 23, 42, 0.55);
}
.hero-tags { display: flex; flex-wrap: wrap; gap: 0.45rem; margin-bottom: 0.8rem; }
.hero-tag {
  background: rgba(255, 255, 255, 0.12); border: 1px solid rgba(255, 255, 255, 0.22);
  padding: 0.2rem 0.7rem; border-radius: 999px; font-size: 0.76rem; font-weight: 600; color: #e2e8f0;
}
.hero h1 { font-size: 1.85rem; font-weight: 800; letter-spacing: -0.02em; margin: 0 0 0.4rem 0; color: #ffffff; padding: 0; }
.hero p { margin: 0; color: #cbd5e1; font-size: 0.98rem; line-height: 1.55; max-width: 860px; }
.hero code { background: rgba(255, 255, 255, 0.14); color: #ffffff; padding: 0.05rem 0.35rem; border-radius: 5px; }

/* ---------- Faixas de aviso / explicação ---------- */
.note {
  border-radius: 12px; padding: 0.95rem 1.15rem; margin: 0.8rem 0 1.1rem 0;
  font-size: 0.9rem; line-height: 1.6; color: var(--text);
  background: var(--primary-subtle); border: 1px solid #bfdbfe; border-left: 5px solid var(--primary);
}
.note.amber { background: var(--amber-subtle); border-color: #fde68a; border-left-color: var(--amber); color: #78350f; }
.note.green { background: var(--green-subtle); border-color: #a7f3d0; border-left-color: var(--green); }
.note h4 { margin: 0 0 0.4rem 0; font-size: 0.98rem; font-weight: 700; color: var(--text); }
.note ul { margin: 0.2rem 0 0 1.1rem; padding: 0; }
.note li { margin-bottom: 0.3rem; }

/* ---------- Títulos de seção ---------- */
.sec { margin: 1.6rem 0 0.7rem 0; }
.sec .eyebrow { font-size: 0.72rem; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; color: var(--primary); }
.sec h3 { font-size: 1.3rem; font-weight: 800; color: var(--text); margin: 0.15rem 0 0.2rem 0; padding: 0; letter-spacing: -0.01em; }
.sec p { margin: 0; color: var(--muted); font-size: 0.92rem; line-height: 1.5; }

/* ---------- Cartões explicativos ---------- */
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 0.85rem; margin: 0.4rem 0 0.9rem 0; }
.card {
  background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
  padding: 1rem 1.1rem; box-shadow: var(--shadow); position: relative; overflow: hidden;
}
.card::before { content: ""; position: absolute; top: 0; left: 0; right: 0; height: 4px; background: var(--primary); }
.card.green::before { background: var(--green); }
.card.amber::before { background: var(--amber); }
.card.purple::before { background: var(--purple); }
.card.red::before { background: var(--red); }
.tag {
  display: inline-block; font-size: 0.7rem; font-weight: 800; letter-spacing: 0.04em; text-transform: uppercase;
  padding: 0.15rem 0.55rem; border-radius: 999px; margin-bottom: 0.45rem;
  background: var(--primary-subtle); color: var(--primary-dark);
}
.card.green .tag { background: var(--green-subtle); color: #047857; }
.card.amber .tag { background: var(--amber-subtle); color: #b45309; }
.card.purple .tag { background: var(--purple-subtle); color: #6d28d9; }
.card.red .tag { background: var(--red-subtle); color: #b91c1c; }
.card h4 { margin: 0 0 0.35rem 0; font-size: 1rem; font-weight: 700; color: var(--text); }
.card p { margin: 0; font-size: 0.86rem; color: var(--muted); line-height: 1.5; }
.card code, .note code { background: #f1f5f9; color: #0f172a; padding: 0.05rem 0.3rem; border-radius: 5px; font-size: 0.85em; }

/* ---------- Cartões de números (KPI) ---------- */
.kpi .label { font-size: 0.74rem; font-weight: 700; color: var(--light); text-transform: uppercase; letter-spacing: 0.04em; }
.kpi .value { font-size: 1.6rem; font-weight: 800; color: var(--text); margin: 0.2rem 0 0.3rem 0; letter-spacing: -0.01em; }
.kpi .desc { font-size: 0.82rem; color: var(--muted); line-height: 1.45; }
.kpi.ok { background: linear-gradient(180deg, var(--green-subtle) 0%, #ffffff 70%); }
.kpi.ok::before { background: var(--green); }
.kpi.ok .value { color: #047857; }
.kpi.alerta { background: linear-gradient(180deg, var(--red-subtle) 0%, #ffffff 70%); }
.kpi.alerta::before { background: var(--red); }
.kpi.alerta .value { color: #b91c1c; }
</style>
"""


def _html(conteudo: str) -> None:
    """Renderiza HTML removendo indentação (evita o Markdown tratar o HTML como bloco de código)."""
    linhas = [linha.strip() for linha in conteudo.splitlines() if linha.strip()]
    st.markdown("\n".join(linhas), unsafe_allow_html=True)


def _secao(etiqueta: str, titulo: str, subtitulo: str = "") -> None:
    sub = f"<p>{subtitulo}</p>" if subtitulo else ""
    _html(f'<div class="sec"><div class="eyebrow">{etiqueta}</div><h3>{titulo}</h3>{sub}</div>')


def _cartoes(itens: list[tuple[str, str, str, str]]) -> None:
    """Grade de cartões explicativos: (cor, etiqueta, título, texto)."""
    blocos = "".join(
        f'<div class="card {cor}"><span class="tag">{etq}</span><h4>{tit}</h4><p>{txt}</p></div>'
        for cor, etq, tit, txt in itens
    )
    _html(f'<div class="grid">{blocos}</div>')


def _kpis(itens: list[tuple[str, str, str, str]]) -> None:
    """Grade de cartões numéricos: (classe, rótulo, valor, descrição)."""
    blocos = "".join(
        f'<div class="card kpi {cls}"><div class="label">{rot}</div>'
        f'<div class="value">{val}</div><div class="desc">{desc}</div></div>'
        for cls, rot, val, desc in itens
    )
    _html(f'<div class="grid">{blocos}</div>')


def _nota(conteudo: str, cor: str = "") -> None:
    _html(f'<div class="note {cor}">{conteudo}</div>')


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
    df_validos = df[df[COLUNA_ALVO].notna()].copy()
    df_validos[COLUNA_ALVO] = df_validos[COLUNA_ALVO].astype(int)

    artefato = carregar_artefato_modelo()
    probs = artefato["pipeline"].predict_proba(df_validos[list(FEATURES_SPRINT4)])[:, 1]
    df_validos["probabilidade_risco"] = probs
    df_validos["iqar_evento"] = df_validos[COLUNA_IQAR].shift(-1)
    return df_validos


@st.cache_data(ttl=300, show_spinner="Consultando as APIs da Open-Meteo...")
def consultar_previsao_ao_vivo() -> tuple[pd.Series, float, pd.Timestamp]:
    """Consulta as 2 APIs e roda o modelo. Guarda o resultado por 5 minutos."""
    inicio = time.perf_counter()
    resultado = prever_proxima_hora().iloc[0]
    latencia_ms = (time.perf_counter() - inicio) * 1000.0
    return resultado, latencia_ms, pd.Timestamp.now()


@st.cache_data(ttl=300, show_spinner="Calculando as próximas horas...")
def consultar_projecao(horas: int) -> pd.DataFrame:
    return projetar_proximas_horas(horas_frente=horas)


# =============================================================================
# APLICAÇÃO
# =============================================================================
def main() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
    artefato = carregar_artefato_modelo()
    limiar = float(artefato["decision_threshold"])

    # ---------------------------------------------------------------- Barra lateral
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
            <div class="side-title">Ficha do modelo</div>
            <b>Algoritmo:</b> Random Forest (300 árvores)<br>
            <b>O que prevê:</b> se o IQAr passará de 100 na próxima hora<br>
            <b>Limiar de alerta:</b> {limiar * 100:.0f}% de probabilidade<br>
            <b>Teste 2025–2026:</b> avisou 158 de 161 episódios (98,14%)
            </div>
            """
        )
        _html(
            """
            <div class="side-card">
            <div class="side-title">Escala do IQAr (CETESB)</div>
            <div class="scale-row"><span class="scale-dot" style="background:#16a34a"></span><b>0–40</b>&nbsp;Boa</div>
            <div class="scale-row"><span class="scale-dot" style="background:#eab308"></span><b>41–80</b>&nbsp;Moderada</div>
            <div class="scale-row"><span class="scale-dot" style="background:#f97316"></span><b>81–120</b>&nbsp;Ruim</div>
            <div class="scale-row"><span class="scale-dot" style="background:#dc2626"></span><b>121–200</b>&nbsp;Muito ruim</div>
            <div class="scale-row"><span class="scale-dot" style="background:#7e22ce"></span><b>&gt; 200</b>&nbsp;Péssima</div>
            <div style="margin-top:0.45rem">O projeto considera <b>ar inadequado</b> quando o IQAr passa de <b>100</b>.</div>
            </div>
            """
        )
        st.markdown(
            "[📄 Artigo técnico](https://diogogomesb.github.io/Ciencia-de-Dados-e-Aprendizagem-de-Maquina/)  \n"
            "[💻 Repositório no GitHub](https://github.com/DiogoGomesB/Ciencia-de-Dados-e-Aprendizagem-de-Maquina)"
        )

    # ---------------------------------------------------------------- Cabeçalho
    _html(
        """
        <div class="hero">
        <div class="hero-tags">
        <span class="hero-tag">🎓 Sistemas de Informação · UBC 2026/2</span>
        <span class="hero-tag">🌬️ Trilha B — Qualidade do Ar</span>
        <span class="hero-tag">🌲 Random Forest · 300 árvores</span>
        <span class="hero-tag">📏 Regra oficial: Tabela 2.7 da CETESB</span>
        </div>
        <h1>ArPrev — Aviso de ar inadequado com 1 hora de antecedência</h1>
        <p>Consultamos dados abertos de poluentes e clima para o campus da <strong>Universidade Braz Cubas</strong>
        e estimamos se o Índice de Qualidade do Ar (<code>IQAr</code>) vai passar de <strong>100 pontos</strong>
        na próxima hora — o limite a partir do qual a CETESB considera o ar inadequado.</p>
        </div>
        """
    )
    _nota(
        "⚠️ <strong>Uso responsável:</strong> as previsões são <strong>estimativas experimentais</strong> de um modelo "
        "de aprendizado de máquina sobre dados de grade aberta (Open-Meteo / CAMS) e <strong>não substituem</strong> "
        "os boletins oficiais da CETESB ou da Defesa Civil.",
        "amber",
    )

    aba1, aba2 = st.tabs(["📡  Previsão ao vivo", "📊  Resultados do teste"])

    # =========================================================================
    # ABA 1 — PREVISÃO AO VIVO
    # =========================================================================
    with aba1:
        col_tit, col_btn = st.columns([4, 1], vertical_alignment="bottom")
        with col_tit:
            _secao(
                "Agora no campus",
                "Como estará o ar na próxima hora?",
                "Resultado calculado com os dados mais recentes das APIs da Open-Meteo.",
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

            _kpis(
                [
                    (
                        "alerta" if alerta_1h else "ok",
                        f"Previsão para {horario_evento:%d/%m às %H:%M}",
                        "🚨 Alerta" if alerta_1h else "✅ Ar adequado",
                        (
                            "Risco de o IQAr passar de 100. Recomenda-se levar treinos intensos para local coberto."
                            if alerta_1h
                            else "O modelo não espera que o IQAr passe de 100 na próxima hora."
                        ),
                    ),
                    (
                        "",
                        "Probabilidade de ar inadequado",
                        _pct_br(prob_1h, 1),
                        f"Chance calculada pelas 300 árvores. O alerta só dispara a partir de <strong>{limiar * 100:.0f}%</strong>.",
                    ),
                    (
                        "",
                        "Último dado usado (hora t)",
                        f"{horario_dados:%d/%m · %H:%M}",
                        "Hora mais recente já fechada nas APIs. O modelo usa só o que já aconteceu até aqui.",
                    ),
                    (
                        "",
                        "Tempo da consulta",
                        f"{latencia_ms:.0f} ms",
                        f"Buscar as 2 APIs, calcular o IQAr e rodar o modelo. Consultado às {consultado_em:%H:%M}; "
                        "refaz sozinho a cada 5 min ou no botão.",
                    ),
                ]
            )

            _secao("Por trás do resultado", "Como chegamos nesse número (4 passos)")
            _cartoes(
                [
                    (
                        "",
                        "Passo 1 · Coleta",
                        "🌐 Duas APIs abertas",
                        "A <strong>API de Qualidade do Ar</strong> traz 6 poluentes (ozônio, PM2,5, PM10, CO, NO2, SO2) "
                        "e a <strong>API de Clima</strong> traz temperatura, umidade, chuva, vento e pressão, para a "
                        "localização da UBC.",
                    ),
                    (
                        "amber",
                        "Passo 2 · Regra CETESB",
                        "📏 Nota do ar (IQAr)",
                        "Cada poluente vira uma nota pela <strong>Tabela 2.7 da CETESB</strong> (média de 24h, 8h ou 1h). "
                        "O IQAr da hora é a <strong>pior</strong> das 6 notas.",
                    ),
                    (
                        "purple",
                        "Passo 3 · 15 pistas",
                        "🧩 Poluentes + clima + tendência",
                        "As 6 notas, as 5 variáveis de clima e 4 resumos das últimas horas (médias de 3h e variações de 2h "
                        "de ozônio e PM2,5) formam a linha que o modelo lê.",
                    ),
                    (
                        "green",
                        "Passo 4 · Decisão",
                        "🌲 300 árvores votam",
                        f"O modelo salvo calcula a probabilidade de o IQAr passar de 100 na hora seguinte. "
                        f"Com <strong>{limiar * 100:.0f}% ou mais</strong>, o painel mostra <strong>🚨 Alerta</strong>.",
                    ),
                ]
            )

            _secao(
                "Planejamento",
                "Próximas horas",
                "Escolha quantas horas à frente quer ver. A tabela abaixo se atualiza na hora.",
            )
            horizonte = st.radio(
                "Horizonte da previsão",
                options=[1, 7, 24],
                index=2,
                horizontal=True,
                label_visibility="collapsed",
                format_func=lambda h: {
                    1: "⏱️ +1 hora · oficial",
                    7: "🌤️ +7 horas · experimental",
                    24: "📅 +24 horas · experimental",
                }[h],
            )
            _cartoes(
                [
                    (
                        "green",
                        "+1 hora · oficial",
                        "⏱️ Só dados que já aconteceram",
                        "Usa medições até a hora atual para prever a hora seguinte. É o horizonte que foi testado "
                        "(98,14% dos alertas capturados em 2025–2026).",
                    ),
                    (
                        "amber",
                        "+7 horas · experimental",
                        "🌤️ O próximo turno",
                        "As APIs também entregam a <strong>previsão</strong> de poluentes e clima. Aplicamos a mesma "
                        "regra da CETESB e o mesmo modelo hora a hora, até 7 horas à frente.",
                    ),
                    (
                        "purple",
                        "+24 horas · experimental",
                        "📅 O dia inteiro",
                        "Mesmo cálculo para as próximas 24 horas. É experimental porque também depende de a previsão "
                        "do tempo da API acertar — quanto mais longe, maior a incerteza.",
                    ),
                ]
            )

            if horizonte == 1:
                df_proj = res_1h.to_frame().T.assign(**{"horizonte": "+1h", "iqar projetado (CAMS)": np.nan})
            else:
                df_proj = consultar_projecao(horizonte).copy()
            probs_proj = df_proj[COL_PROB].astype(float)
            alertas_proj = probs_proj >= limiar
            # A projeção (+7h/+24h) chama a hora t de "horário base da janela"; a previsão +1h, de "horário dos dados até t".
            col_hora_t = "horário dos dados até t" if "horário dos dados até t" in df_proj.columns else "horário base da janela"

            tabela = pd.DataFrame(
                {
                    "Horizonte": df_proj["horizonte"].astype(str),
                    "Dado usado (hora t)": pd.to_datetime(df_proj[col_hora_t]).dt.strftime("%d/%m %H:%M"),
                    "Hora prevista (t + 1h)": pd.to_datetime(df_proj["horário do evento previsto"]).dt.strftime("%d/%m %H:%M"),
                    "IQAr previsto pela API": pd.to_numeric(df_proj["iqar projetado (CAMS)"], errors="coerce").round(1),
                    "Probabilidade de ar inadequado": (probs_proj * 100).round(2),
                    "Situação": np.where(alertas_proj, "🚨 Alerta (IQAr > 100)", "✅ Ar adequado"),
                }
            )
            st.dataframe(
                tabela,
                width="stretch",
                hide_index=True,
                height=min(420, 38 + 35 * len(tabela)),
                column_config={
                    "Probabilidade de ar inadequado": st.column_config.ProgressColumn(
                        "Probabilidade de ar inadequado",
                        help=f"Chance estimada pelo modelo. O alerta dispara a partir de {limiar * 100:.0f}%.",
                        format="%.2f%%",
                        min_value=0.0,
                        max_value=100.0,
                    ),
                    "IQAr previsto pela API": st.column_config.NumberColumn(
                        "IQAr previsto pela API",
                        help="Nota do IQAr calculada sobre as concentrações previstas pela Open-Meteo. "
                        "Na linha +1h fica vazia porque ela usa só dados já medidos.",
                        format="%.1f",
                    ),
                },
            )
            _nota(
                """
                <h4>📖 Como ler a tabela</h4>
                <ul>
                <li><strong>Dado usado (hora t) → Hora prevista (t + 1h):</strong> cada linha usa os dados de uma hora
                para dizer como estará o ar na hora seguinte.</li>
                <li><strong>IQAr previsto pela API:</strong> a nota do ar calculada sobre a previsão da Open-Meteo
                (até 40 = boa; 41–80 = moderada; acima de 100 = inadequada).</li>
                <li><strong>Probabilidade de ar inadequado:</strong> a barra mostra a chance calculada pelo modelo.
                Quando ela chega ao limiar, a coluna <em>Situação</em> vira <strong>🚨 Alerta</strong>.</li>
                </ul>
                """
            )
        except Exception as erro_api:  # noqa: BLE001 — mostrar o erro ao usuário em vez de quebrar a página
            _nota(
                f"⚠️ Não foi possível consultar a Open-Meteo agora (<code>{erro_api}</code>). "
                "Tente o botão <strong>Atualizar agora</strong> em instantes ou veja a aba <strong>Resultados do teste</strong>.",
                "amber",
            )

    # =========================================================================
    # ABA 2 — RESULTADOS DO TESTE
    # =========================================================================
    with aba2:
        _secao(
            "Avaliação",
            "O modelo funciona de verdade?",
            "Treinamos com o passado e testamos com um período que o modelo nunca viu.",
        )
        _cartoes(
            [
                (
                    "",
                    "1 · Base histórica",
                    "📅 35.736 horas (2022–2026)",
                    "Cada hora recebeu o gabarito pela regra da CETESB: <code>1</code> quando o IQAr da hora seguinte "
                    "passou de 100 (2,53% das horas) e <code>0</code> nas demais.",
                ),
                (
                    "amber",
                    "2 · Divisão no tempo",
                    "⏳ Passado treina, futuro testa",
                    "Nada de sortear horas: o treino vai até 2024 (21.121 h) e 2025–2026 (14.592 h) ficou guardado "
                    "para uma prova final, aberta uma única vez.",
                ),
                (
                    "green",
                    "3 · Resultado",
                    "🏆 158 de 161 alertas",
                    "No teste final houve 161 horas de ar inadequado. A Random Forest avisou 158 delas com 1 hora de "
                    "antecedência e deixou passar 3.",
                ),
            ]
        )

        periodo = st.radio(
            "Período avaliado",
            options=["holdout_2025_2026", "validacao_2024_Q4"],
            horizontal=True,
            format_func=lambda p: {
                "holdout_2025_2026": "🎯 Teste final · 2025–2026",
                "validacao_2024_Q4": "🧪 Validação · out–dez/2024",
            }[p],
        )
        nome_periodo = (
            "teste final (jan/2025 a ago/2026)" if periodo == "holdout_2025_2026" else "validação (out a dez/2024)"
        )

        # ------------------------------------------------ Tabela comparativa
        _secao("Comparação", "Qual modelo errou menos?", f"Números do período de {nome_periodo}.")
        df_comp = carregar_metricas_comparativas()
        df_fold = df_comp[df_comp["fold"] == periodo].copy() if "fold" in df_comp.columns else df_comp.copy()
        df_fold = df_fold.sort_values(["recall_classe_1", "f1_classe_1"], ascending=[False, False])

        nomes = {
            "random_forest_balanced": "🏆 Random Forest (escolhido)",
            "xgboost_balanced": "XGBoost",
            "arvore_decisao_cart": "Árvore de Decisão",
            "regressao_logistica_balanced": "Regressão Logística",
            "gaussian_naive_bayes": "Naive Bayes",
            "persistencia_iqar_atual": "Persistência (repete a hora atual)",
            "dummy_prior": "Dummy (sempre diz 'ar adequado')",
        }
        total = df_fold["tp"] + df_fold["tn"] + df_fold["fp"] + df_fold["fn"]
        tabela_comp = pd.DataFrame(
            {
                "Modelo": df_fold["modelo"].map(lambda m: nomes.get(m, m)),
                "Recall · alertas avisados": (df_fold["recall_classe_1"] * 100).round(2),
                "Precisão": (df_fold["precisao_classe_1"] * 100).round(2),
                "F1-Score": (df_fold["f1_classe_1"] * 100).round(2),
                "Acurácia geral": ((df_fold["tp"] + df_fold["tn"]) / total * 100).round(2),
                "✅ Alertas certos (TP)": df_fold["tp"].astype(int),
                "❌ Alertas perdidos (FN)": df_fold["fn"].astype(int),
                "⚠️ Alarmes a mais (FP)": df_fold["fp"].astype(int),
            }
        )
        st.dataframe(
            tabela_comp,
            width="stretch",
            hide_index=True,
            column_config={
                "Recall · alertas avisados": st.column_config.ProgressColumn(
                    "Recall · alertas avisados",
                    help="De todos os episódios reais de ar inadequado, quantos % o modelo avisou.",
                    format="%.2f%%",
                    min_value=0.0,
                    max_value=100.0,
                ),
                "F1-Score": st.column_config.ProgressColumn(
                    "F1-Score",
                    help="Equilíbrio entre avisar todos os alertas e não dar alarme falso demais.",
                    format="%.2f%%",
                    min_value=0.0,
                    max_value=100.0,
                ),
                "Precisão": st.column_config.NumberColumn("Precisão", format="%.2f%%"),
                "Acurácia geral": st.column_config.NumberColumn(
                    "Acurácia geral",
                    help="Engana quando quase todas as horas são normais: veja a linha do Dummy.",
                    format="%.2f%%",
                ),
            },
        )

        # Cartões de métricas com os números do período escolhido
        rf = df_fold[df_fold["modelo"] == "random_forest_balanced"]
        dummy = df_fold[df_fold["modelo"] == "dummy_prior"]
        if not rf.empty:
            rf = rf.iloc[0]
            positivos = int(rf["tp"] + rf["fn"])
            avisos = int(rf["tp"] + rf["fp"])
            texto_dummy = "O Dummy diz 'ar adequado' em todas as horas."
            if not dummy.empty:
                d = dummy.iloc[0]
                acc_dummy = (d["tp"] + d["tn"]) / (d["tp"] + d["tn"] + d["fp"] + d["fn"])
                texto_dummy = (
                    f"O Dummy diz 'ar adequado' em todas as horas e mesmo assim tem "
                    f"<strong>{_pct_br(acc_dummy)}</strong> de acurácia — com <strong>0 alertas avisados</strong>. "
                    "Por isso não usamos a acurácia para escolher o modelo."
                )
            _cartoes(
                [
                    (
                        "green",
                        "Métrica principal",
                        f"🎯 Recall: {_pct_br(rf['recall_classe_1'])}",
                        f"De {positivos} horas de ar inadequado, a Random Forest avisou {int(rf['tp'])}. "
                        "Perder um alerta é o pior erro: expõe alunos sem aviso.",
                    ),
                    (
                        "",
                        "Confiança no alarme",
                        f"⚖️ Precisão: {_pct_br(rf['precisao_classe_1'])}",
                        f"Dos {avisos} alarmes dados, {int(rf['tp'])} eram ar inadequado de verdade. "
                        f"O <strong>F1-Score ({_pct_br(rf['f1_classe_1'])})</strong> equilibra Recall e Precisão.",
                    ),
                    ("amber", "Armadilha", "⚠️ Por que não a acurácia?", texto_dummy),
                    (
                        "red",
                        "Os 4 resultados",
                        "🔍 TP, FN, FP e TN",
                        f"<strong>TP</strong> alerta certo ({int(rf['tp'])}) · <strong>FN</strong> alerta perdido "
                        f"({int(rf['fn'])}) · <strong>FP</strong> alarme a mais ({int(rf['fp'])}) · "
                        f"<strong>TN</strong> hora normal certa ({_int_br(rf['tn'])}).",
                    ),
                ]
            )

        # ------------------------------------------------ Auditoria linha a linha
        _secao(
            "Auditoria",
            "O que o modelo disse 1 hora antes de cada episódio real",
            "Todas as horas em que o IQAr realmente passou de 100 no período escolhido.",
        )
        df_hist = carregar_serie_historica_com_previsoes()
        if periodo == "holdout_2025_2026":
            filtro = df_hist["event_time_dt"] >= pd.Timestamp("2025-01-01")
        else:
            filtro = (df_hist["event_time_dt"] >= pd.Timestamp("2024-10-01")) & (
                df_hist["event_time_dt"] < pd.Timestamp("2025-01-01")
            )
        recorte = df_hist[filtro].copy()
        recorte["alerta"] = recorte["probabilidade_risco"] >= limiar

        reais = recorte[COLUNA_ALVO] == 1
        tp_p = int((reais & recorte["alerta"]).sum())
        fn_p = int((reais & ~recorte["alerta"]).sum())
        fp_p = int((~reais & recorte["alerta"]).sum())
        total_reais = int(reais.sum())

        eventos = recorte[reais].copy()
        antecipados = int(((eventos[COLUNA_IQAR] <= 100) & eventos["alerta"]).sum())

        _kpis(
            [
                ("", "Horas analisadas", f"{_int_br(len(recorte))} h", f"Período de {nome_periodo}."),
                ("", "Episódios reais (IQAr > 100)", f"{total_reais} h", "Horas em que o ar ficou inadequado de verdade."),
                (
                    "ok",
                    "Avisados 1 hora antes",
                    f"{tp_p} de {total_reais}",
                    f"{_pct_br(tp_p / max(1, total_reais), 1)} dos episódios. Em {antecipados} deles o IQAr ainda "
                    "estava em até 100 na hora do aviso.",
                ),
                (
                    "alerta" if fn_p else "ok",
                    "Erros no período",
                    f"{fn_p} FN · {fp_p} FP",
                    f"{fn_p} alerta(s) perdido(s) e {fp_p} alarme(s) a mais.",
                ),
            ]
        )

        eventos = eventos.sort_values(["alerta", "event_time_dt"], ascending=[True, False])
        tabela_aud = pd.DataFrame(
            {
                "Resultado": np.where(eventos["alerta"], "✅ Avisou (TP)", "❌ Não avisou (FN)"),
                "Hora do aviso (t)": eventos["time_dt"].dt.strftime("%d/%m/%Y %H:%M"),
                "Hora do episódio (t + 1h)": eventos["event_time_dt"].dt.strftime("%d/%m/%Y %H:%M"),
                "IQAr na hora do aviso": eventos[COLUNA_IQAR].round(1),
                "IQAr no episódio": eventos["iqar_evento"].round(1),
                "Probabilidade dada 1h antes": (eventos["probabilidade_risco"] * 100).round(1),
            }
        )
        st.dataframe(
            tabela_aud,
            width="stretch",
            hide_index=True,
            height=min(440, 38 + 35 * max(1, len(tabela_aud))),
            column_config={
                "Probabilidade dada 1h antes": st.column_config.ProgressColumn(
                    "Probabilidade dada 1h antes",
                    help=f"O alerta dispara a partir de {limiar * 100:.0f}%.",
                    format="%.1f%%",
                    min_value=0.0,
                    max_value=100.0,
                ),
                "IQAr na hora do aviso": st.column_config.NumberColumn(format="%.1f"),
                "IQAr no episódio": st.column_config.NumberColumn(format="%.1f"),
            },
        )
        _nota(
            f"""
            <h4>💡 Como ler a auditoria</h4>
            <ul>
            <li><strong>De onde vêm os dados:</strong> a série histórica do repositório
            (<code>data/processed/</code>) passa pelo mesmo modelo salvo (<code>modelo_final_sprint5.joblib</code>),
            hora a hora.</li>
            <li><strong>Erros primeiro:</strong> as linhas <strong>❌ Não avisou</strong> aparecem no topo, para
            mostrar com transparência onde o modelo falhou ({fn_p} no período).</li>
            <li><strong>Antecipação:</strong> compare as duas colunas de IQAr. Quando o IQAr ainda estava em até 100
            na hora do aviso e o modelo já alertou, ele percebeu a subida antes de o ar ficar ruim.</li>
            </ul>
            """,
            "green",
        )


if __name__ == "__main__":
    main()
