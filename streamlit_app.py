"""Dashboard interativo Streamlit — Trilha B: Qualidade do Ar (UBC / Mogi das Cruzes).

Interface moderna, visual e autoexplicativa (pensada para público leigo e banca avaliadora):
1. Aba 1 — Previsão Atual (Ao Vivo): consulta imediata às 2 APIs da Open-Meteo, cálculo CETESB,
   cartões explicativos e tabela horária dinâmica (+1h oficial, +7h turno e +24h dia completo).
2. Aba 2 — Desempenho Histórico: comparativo dinâmico entre Baselines, Árvore de Decisão,
   Random Forest e XGBoost (Holdout 2025–2026 e Validação 2024-Q4), explicação didática das
   métricas e auditoria linha a linha dos episódios reais de poluição.
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


def _injetar_estilo_moderno() -> None:
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2.5rem;
            max-width: 1280px;
        }
        .hero-box {
            background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 60%, #047857 100%);
            color: #ffffff;
            padding: 1.6rem 1.9rem;
            border-radius: 16px;
            box-shadow: 0 12px 28px -8px rgba(15, 23, 42, 0.28);
            margin-bottom: 1rem;
        }
        .hero-badges {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-bottom: 0.65rem;
        }
        .hero-badge {
            background: rgba(255, 255, 255, 0.14);
            border: 1px solid rgba(255, 255, 255, 0.25);
            color: #f8fafc;
            padding: 0.22rem 0.72rem;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 600;
        }
        .hero-title {
            font-size: 1.75rem;
            font-weight: 800;
            margin: 0 0 0.35rem 0;
            letter-spacing: -0.02em;
            color: #ffffff;
        }
        .hero-sub {
            font-size: 0.98rem;
            color: #e2e8f0;
            margin: 0;
            line-height: 1.5;
        }
        .warn-banner {
            background: #fffbeb;
            border: 1px solid #fde68a;
            border-left: 5px solid #f59e0b;
            color: #78350f;
            padding: 0.85rem 1.15rem;
            border-radius: 10px;
            font-size: 0.9rem;
            margin-bottom: 1.25rem;
            line-height: 1.45;
        }
        .step-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
            gap: 0.85rem;
            margin: 0.75rem 0 1.25rem 0;
        }
        .step-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-top: 4px solid #2563eb;
            border-radius: 12px;
            padding: 1rem 1.1rem;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
        }
        .step-card.green { border-top-color: #059669; }
        .step-card.amber { border-top-color: #d97706; }
        .step-card.purple { border-top-color: #7c3aed; }
        .step-card.red { border-top-color: #dc2626; }
        .step-num {
            display: inline-block;
            background: #eff6ff;
            color: #1d4ed8;
            font-size: 0.74rem;
            font-weight: 800;
            padding: 0.16rem 0.55rem;
            border-radius: 999px;
            margin-bottom: 0.4rem;
            text-transform: uppercase;
        }
        .step-card h4 {
            margin: 0 0 0.35rem 0;
            font-size: 1rem;
            font-weight: 700;
            color: #0f172a;
        }
        .step-card p {
            margin: 0;
            font-size: 0.86rem;
            color: #475569;
            line-height: 1.45;
        }
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 0.9rem;
            margin: 0.85rem 0 1.1rem 0;
        }
        .kpi-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 1.05rem 1.15rem;
            box-shadow: 0 4px 14px rgba(15, 23, 42, 0.05);
        }
        .kpi-card.ok {
            background: linear-gradient(180deg, #ecfdf5 0%, #ffffff 65%);
            border-color: #a7f3d0;
        }
        .kpi-card.alerta {
            background: linear-gradient(180deg, #fef2f2 0%, #ffffff 65%);
            border-color: #fecaca;
        }
        .kpi-label {
            font-size: 0.8rem;
            font-weight: 700;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.03em;
            margin-bottom: 0.25rem;
        }
        .kpi-value {
            font-size: 1.55rem;
            font-weight: 800;
            color: #0f172a;
            margin-bottom: 0.3rem;
        }
        .kpi-desc {
            font-size: 0.82rem;
            color: #475569;
            line-height: 1.38;
        }
        .explain-box {
            background: #f8fafc;
            border: 1px solid #cbd5e1;
            border-left: 5px solid #2563eb;
            border-radius: 12px;
            padding: 1.1rem 1.3rem;
            margin: 0.9rem 0 1.3rem 0;
            font-size: 0.91rem;
            color: #1e293b;
            line-height: 1.55;
        }
        .explain-box.green {
            background: #f0fdf4;
            border-color: #bbf7d0;
            border-left-color: #059669;
        }
        .explain-box h4 {
            margin: 0 0 0.45rem 0;
            font-size: 1.02rem;
            color: #0f172a;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource
def carregar_artefato_modelo():
    caminho = Path("models/modelo_final_sprint5.joblib")
    return joblib.load(caminho)


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
    pipeline = artefato["pipeline"]
    limiar = float(artefato["decision_threshold"])
    probs = pipeline.predict_proba(df_validos[list(FEATURES_SPRINT4)])[:, 1]
    df_validos["probabilidade_risco"] = probs
    df_validos["alerta_previsto"] = (probs >= limiar).astype(int)
    df_validos["iqar_evento"] = df_validos[COLUNA_IQAR].shift(-1)
    return df_validos


def main() -> None:
    _injetar_estilo_moderno()
    artefato = carregar_artefato_modelo()
    limiar_oficial = float(artefato["decision_threshold"])

    # =========================================================================
    # BARRA LATERAL (SIDEBAR): Controles simples e diretos
    # =========================================================================
    with st.sidebar:
        logo_path = Path("docs/assets/logo.png")
        if logo_path.exists():
            st.image(str(logo_path), use_container_width=True)
        st.title("⚙️ Controles do Painel")
        st.caption("Local monitorado: Campus da Universidade Braz Cubas (Mogi das Cruzes – SP)")

        horizonte_projecao = st.radio(
            "1️⃣ Quantas horas à frente você quer ver na Aba 1?",
            options=[1, 7, 24],
            index=2,
            format_func=lambda h: (
                "Oficial: +1 hora (Próxima hora)"
                if h == 1
                else ("Experimental: +7 horas (Próximo turno)" if h == 7 else "Experimental: +24 horas (Dia inteiro)")
            ),
        )

        st.divider()
        particao_hist = st.selectbox(
            "2️⃣ Qual período histórico quer consultar na Aba 2?",
            options=[
                "Teste Recente (Holdout: 2025–2026)",
                "Validação Temporal (2024-Q4)",
            ],
            index=0,
        )

        st.divider()
        st.markdown(
            "**📌 Ficha Rápida do Modelo:**\n"
            "- **Algoritmo:** Random Forest (300 árvores)\n"
            "- **Limiar de Alerta:** `30%` (`0,30`)\n"
            "- **Alvo:** Prever `IQAr > 100` em `t + 1h`\n"
            "- **Recall no Teste:** `98,14%` (158 de 161 alertas)\n\n"
            "**🔗 Links do Projeto:**\n"
            "- [Artigo Técnico (GitHub Pages)](https://diogogomesb.github.io/Ciencia-de-Dados-e-Aprendizagem-de-Maquina/)\n"
            "- [Repositório no GitHub](https://github.com/DiogoGomesB/Ciencia-de-Dados-e-Aprendizagem-de-Maquina)"
        )

    # =========================================================================
    # CABEÇALHO MODERNO (HERO) E AVISO REGULATÓRIO
    # =========================================================================
    st.markdown(
        """
        <div class="hero-box">
            <div class="hero-badges">
                <span class="hero-badge">🎓 Sistemas de Informação · UBC 2026/2</span>
                <span class="hero-badge">🌬️ Trilha B — Qualidade do Ar Inadequada</span>
                <span class="hero-badge">🌲 Modelo: Random Forest (300 árvores)</span>
                <span class="hero-badge">🎯 Regra Oficial: Tabela 2.7 da CETESB</span>
            </div>
            <div class="hero-title">ArPrev — Sistema de Antecipação de Poluição do Ar (+1h)</div>
            <p class="hero-sub">
                Monitoramento preditivo para o campus da <strong>Universidade Braz Cubas (Mogi das Cruzes – SP)</strong>:
                consulta dados abertos de poluentes e clima em tempo real e avisa com <strong>1 hora de antecedência</strong>
                quando o Índice de Qualidade do Ar (<code>IQAr</code>) corre risco de ultrapassar <strong>100 pontos (Ar Inadequado)</strong>.
            </p>
        </div>
        <div class="warn-banner">
            ⚠️ <strong>Aviso de Transparência e Uso Responsável:</strong> As previsões deste painel são
            <strong>estimativas experimentais</strong> geradas por um modelo de Aprendizado de Máquina sobre dados
            atmosféricos de grade aberta (<em>Open-Meteo / CAMS</em>) e <strong>não substituem boletins oficiais</strong>
            da CETESB ou da Defesa Civil.
        </div>
        """,
        unsafe_allow_html=True,
    )

    aba1, aba2 = st.tabs(
        [
            "📡 1. Previsão Ao Vivo (Agora na UBC)",
            "📊 2. Resultado Histórico e Comparativo de Modelos",
        ]
    )

    # =========================================================================
    # ABA 1: PREVISÃO ATUAL (CONSULTA À API + TABELA DINÂMICA EXPLICADA)
    # =========================================================================
    with aba1:
        st.markdown("### 🔄 Como funciona esta previsão ao vivo? (Em 4 passos simples)")
        st.markdown(
            """
            <div class="step-grid">
                <div class="step-card">
                    <span class="step-num">Passo 1 · Coleta ao Vivo</span>
                    <h4>🌐 Consulta às 2 APIs da Open-Meteo</h4>
                    <p>O sistema vai na internet agora e busca os dados da UBC em duas APIs gratuitas: a <strong>API de Qualidade do Ar</strong> (6 poluentes: Ozônio, PM2,5, PM10, CO, NO2 e SO2) e a <strong>API de Clima</strong> (temperatura, umidade, chuva, vento e pressão).</p>
                </div>
                <div class="step-card amber">
                    <span class="step-num">Passo 2 · Regra da CETESB</span>
                    <h4>📏 Cálculo da Nota do Ar (IQAr)</h4>
                    <p>Usando a <strong>Tabela 2.7 da CETESB</strong>, tiramos a média das últimas horas de cada poluente (24h, 8h ou 1h) e damos uma nota para cada um. A nota oficial da hora (<code>IQAr</code>) é a <strong>pior (maior)</strong> das 6 notas. Acima de <strong>100 pontos</strong>, o ar é <em>Inadequado</em>.</p>
                </div>
                <div class="step-card purple">
                    <span class="step-num">Passo 3 · As 15 Pistas (Features)</span>
                    <h4>🧩 União de Poluentes + Clima</h4>
                    <p>Juntamos na mesma linha as 6 notas dos poluentes + as 5 variáveis de clima (pois calor fabrica mais ozônio e vento espalha a poluição) + 4 médias e variações das últimas 3 horas para o modelo saber se a poluição está subindo.</p>
                </div>
                <div class="step-card green">
                    <span class="step-num">Passo 4 · Votação do Modelo</span>
                    <h4>🌲 300 Árvores Decidem (+1h)</h4>
                    <p>O arquivo salvo (<code>modelo_final_sprint5.joblib</code>) passa essas 15 pistas por <strong>300 árvores de decisão</strong>. Se <strong>30% ou mais</strong> das árvores votarem que o ar vai passar de 100 na próxima hora, o painel dispara <strong>🚨 ALERTA</strong>.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_btn, col_info = st.columns([1, 3], vertical_alignment="center")
        with col_btn:
            st.button("🔄 Atualizar Dados da API Agora", type="primary", use_container_width=True)
        with col_info:
            st.caption(
                "Clique no botão ao lado para refazer a consulta ao vivo nas APIs da Open-Meteo e recalcular a previsão imediatamente."
            )

        try:
            t_inicio = time.perf_counter()
            res_1h = prever_proxima_hora().iloc[0]
            latencia_1h_ms = (time.perf_counter() - t_inicio) * 1000.0

            prob_1h = float(res_1h["probabilidade estimada de IQAr > 100"])
            alerta_1h = int(prob_1h >= limiar_oficial)
            horario_dados = pd.Timestamp(res_1h["horário dos dados até t"])
            horario_evento = pd.Timestamp(res_1h["horário do evento previsto"])

            classe_status = "alerta" if alerta_1h == 1 else "ok"
            texto_status = "🚨 ALERTA ATIVO" if alerta_1h == 1 else "✅ SEM ALERTA (AR BOM)"
            desc_status = (
                f"O modelo estima risco de o IQAr passar de 100 às {horario_evento:%H:%M}. Recomenda-se suspender treinos intensos ao ar livre."
                if alerta_1h == 1
                else f"Para as {horario_evento:%H:%M}, a qualidade do ar na UBC deve permanecer adequada (IQAr até 100 pontos)."
            )

            st.markdown(
                f"""
                <div class="kpi-grid">
                    <div class="kpi-card {classe_status}">
                        <div class="kpi-label">1. Decisão para a Próxima Hora ({horario_evento:%d/%m às %H:%M})</div>
                        <div class="kpi-value">{texto_status}</div>
                        <div class="kpi-desc">{desc_status}</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-label">2. Probabilidade de Risco (IQAr &gt; 100)</div>
                        <div class="kpi-value">{prob_1h * 100:.1f}%</div>
                        <div class="kpi-desc">Porcentagem calculada pelas 300 árvores da Random Forest. O alarme toca quando chega a <strong>{limiar_oficial * 100:.0f}% (limiar oficial)</strong>.</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-label">3. Última Leitura Observada (Hora t)</div>
                        <div class="kpi-value">{horario_dados:%d/%m às %H:%M}</div>
                        <div class="kpi-desc">Horário do dado mais recente entregue pelas APIs da Open-Meteo (o modelo usa apenas o passado até esta hora).</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-label">4. Tempo Total da Consulta (Latência)</div>
                        <div class="kpi-value">{latencia_1h_ms:.0f} ms</div>
                        <div class="kpi-desc">Tempo total gasto para buscar as 2 APIs na internet, calcular o IQAr da CETESB e rodar as 300 árvores.</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            df_proj = (
                projetar_proximas_horas(horas_frente=horizonte_projecao)
                if horizonte_projecao > 1
                else res_1h.to_frame().T.assign(**{"horizonte": "+1h", "iqar projetado (CAMS)": np.nan})
            )
            col_prob = "probabilidade estimada de IQAr > 100"
            df_proj["alerta_simulado"] = (df_proj[col_prob].astype(float) >= limiar_oficial).astype(int)

            st.markdown(
                f"### 📋 Tabela Dinâmica de Previsão Horária (`+{horizonte_projecao}h` selecionadas na barra lateral)"
            )
            df_proj_exib = pd.DataFrame(
                {
                    "Horizonte": df_proj["horizonte"] if "horizonte" in df_proj.columns else "+1h",
                    "Leitura Base (Hora t)": pd.to_datetime(df_proj["horário dos dados até t"]).dt.strftime("%d/%m/%Y %H:%M"),
                    "Hora Prevista (t + 1h)": pd.to_datetime(df_proj["horário do evento previsto"]).dt.strftime("%d/%m/%Y %H:%M"),
                    "IQAr Projetado pela API (Pontos)": df_proj["iqar projetado (CAMS)"].apply(
                        lambda v: round(float(v), 1) if pd.notna(v) else np.nan
                    ),
                    "Probabilidade de Ar Ruim (%)": (df_proj[col_prob].astype(float) * 100).round(2),
                    "Limiar de Segurança": f"{limiar_oficial * 100:.0f}%",
                    "Situação Prevista pelo Modelo": df_proj["alerta_simulado"].map(
                        lambda a: "🚨 ALERTA: Risco de Ar Inadequado (IQAr > 100)"
                        if a == 1
                        else "✅ Normal: Ar Adequado (IQAr <= 100)"
                    ),
                }
            )
            st.dataframe(
                df_proj_exib,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Probabilidade de Ar Ruim (%)": st.column_config.ProgressColumn(
                        "Probabilidade de Ar Ruim (%)",
                        help="Chance estimada pela Random Forest de o IQAr ultrapassar 100 pontos. A partir de 30% o alerta é disparado.",
                        format="%.2f%%",
                        min_value=0.0,
                        max_value=100.0,
                    ),
                    "IQAr Projetado pela API (Pontos)": st.column_config.NumberColumn(
                        "IQAr Projetado pela API (Pontos)",
                        help="Nota do IQAr calculada sobre as concentrações previstas pela Open-Meteo (até 40 = Boa; 41–80 = Moderada; 81–100 = Ruim moderada; >100 = Inadequada).",
                        format="%.1f pts",
                    ),
                },
            )

            st.markdown(
                """
                <div class="explain-box">
                    <h4>📖 Guia Rápido para Leigos — O que significa cada coluna da tabela acima?</h4>
                    <ul>
                        <li><strong>Horizonte (<code>+1h</code> até <code>+24h</code>):</strong> quantas horas à frente estamos olhando. Você pode mudar entre <code>+1h</code>, <code>+7h</code> e <code>+24h</code> no menu da esquerda e a tabela se reconstrói na hora.</li>
                        <li><strong>Leitura Base (Hora <em>t</em>) vs. Hora Prevista (<em>t + 1h</em>):</strong> nosso modelo sempre olha para o ar da <em>Leitura Base</em> para avisar como estará o ar <strong>1 hora depois</strong> (na <em>Hora Prevista</em>).</li>
                        <li><strong>IQAr Projetado pela API (Pontos):</strong> é a nota do ar segundo a tabela da CETESB: de <code>0 a 40</code> o ar está <strong>Bom</strong>; de <code>41 a 80</code> está <strong>Moderado</strong>; e quando passa de <strong><code>100 pontos</code></strong> entra na faixa crítica (<strong>Inadequado</strong>).</li>
                        <li><strong>Probabilidade de Ar Ruim (%) e Situação Prevista:</strong> mostra a barra de risco calculada pela nossa Random Forest. Sempre que essa barra chega a <strong>30% ou mais</strong>, a última coluna muda para <strong>🚨 ALERTA</strong>.</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )
        except Exception as erro_api:
            st.warning(
                f"Não foi possível consultar a API Open-Meteo ao vivo neste instante ({erro_api}). "
                "Verifique a conexão de rede ou consulte a Aba 2 para ver os resultados históricos."
            )

    # =========================================================================
    # ABA 2: DESEMPENHO HISTÓRICO E COMPARATIVO DE MODELOS (100% EXPLICADO)
    # =========================================================================
    with aba2:
        st.markdown("### 🧪 Como testamos se o modelo funciona de verdade? (Divisão no Tempo sem Trapaça)")
        st.markdown(
            """
            <div class="step-grid">
                <div class="step-card">
                    <span class="step-num">1 · Base Histórica Real</span>
                    <h4>📅 35.736 Horas (2022 a 2026)</h4>
                    <p>Coletamos 4 anos de dados horários de Mogi das Cruzes nas duas APIs da Open-Meteo e rotulamos cada hora pela <strong>Tabela 2.7 da CETESB</strong>: <code>1 (Alerta)</code> quando o IQAr da hora seguinte passou de 100 (904 horas = 2,53%) e <code>0 (Ar Normal)</code> até 100.</p>
                </div>
                <div class="step-card amber">
                    <span class="step-num">2 · Split Temporal Estrito</span>
                    <h4>⏳ Passado Treina, Futuro Testa</h4>
                    <p>Nunca sorteamos horas aleatórias (para o modelo não "colar" das 14h e 16h ao prever as 15h). Treinamos no passado (<strong>2022 a 2024: 21.121 horas</strong>) e guardamos o futuro (<strong>2025 a 2026: 14.592 horas</strong>) trancado para uma única prova final (<em>Holdout</em>).</p>
                </div>
                <div class="step-card green">
                    <span class="step-num">3 · Modelo Campeão</span>
                    <h4>🏆 Random Forest: 98,14% de Recall</h4>
                    <p>Nas <strong>14.592 horas inéditas</strong> de 2025–2026 aconteceram <strong>161 episódios reais</strong> de ar inadequado. Nossa Random Forest avisou <strong>158 deles com 1h de antecedência</strong>, errando apenas 3 vezes em quase dois anos!</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(f"### 1️⃣ Tabela Comparativa Dinâmica dos Modelos — *{particao_hist}*")
        st.caption(
            "Dica: troque o período na barra lateral esquerda entre o **Teste Recente (Holdout: 2025–2026)** e a **Validação Temporal (2024-Q4)** para ver todos os números abaixo atualizarem automaticamente."
        )

        df_comp = carregar_metricas_comparativas()
        filtro_fold = "holdout_2025_2026" if "Holdout" in particao_hist else "validacao_2024_Q4"
        df_fold = df_comp[df_comp["fold"] == filtro_fold].copy() if "fold" in df_comp.columns else df_comp.copy()
        df_fold = df_fold.sort_values(["recall_classe_1", "f1_classe_1"], ascending=[False, False])

        nomes_modelos_pt = {
            "random_forest_balanced": "🏆 Random Forest (Modelo Escolhido)",
            "xgboost_balanced": "⚡ XGBoost (Gradient Boosting)",
            "arvore_decisao_cart": "🌳 Árvore de Decisão Única (CART)",
            "regressao_logistica_balanced": "📈 Regressão Logística Balanceada",
            "gaussian_naive_bayes": "🎲 Gaussian Naive Bayes (Baseline)",
            "persistencia_iqar_atual": "🔁 Persistência (Repete o IQAr da hora t)",
            "dummy_prior": "🛑 Dummy (Chuta sempre 'Ar Adequado')",
        }

        total_horas_fold = (df_fold["tp"] + df_fold["tn"] + df_fold["fp"] + df_fold["fn"]).astype(int)
        acuracia_fold = ((df_fold["tp"] + df_fold["tn"]) / total_horas_fold * 100).round(2)

        df_fold_exib = pd.DataFrame(
            {
                "Modelo Avaliado": df_fold["modelo"].map(lambda m: nomes_modelos_pt.get(m, m)),
                "Como Funciona": df_fold["descricao"],
                "Recall — Alertas Detectados (%)": (df_fold["recall_classe_1"] * 100).round(2),
                "Precisão (%)": (df_fold["precisao_classe_1"] * 100).round(2),
                "F1-Score — Equilíbrio (%)": (df_fold["f1_classe_1"] * 100).round(2),
                "Acurácia Geral (%)": acuracia_fold,
                "TP (Alertas Certos)": df_fold["tp"].astype(int),
                "FN (Falhas Críticas!)": df_fold["fn"].astype(int),
                "FP (Alarmes Preventivos)": df_fold["fp"].astype(int),
                "TN (Horas Normais Certas)": df_fold["tn"].astype(int),
                "Velocidade no Lote (ms)": df_fold["tempo_predicao_ms"].round(1),
            }
        )
        st.dataframe(
            df_fold_exib,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Recall — Alertas Detectados (%)": st.column_config.ProgressColumn(
                    "Recall — Alertas Detectados (%)",
                    help="Nossa métrica principal: de todos os alertas reais que aconteceram, quantos % o modelo capturou?",
                    format="%.2f%%",
                    min_value=0.0,
                    max_value=100.0,
                ),
                "F1-Score — Equilíbrio (%)": st.column_config.ProgressColumn(
                    "F1-Score — Equilíbrio (%)",
                    help="Nota de equilíbrio entre capturar todos os alertas (Recall) e não dar alarme falso demais (Precisão).",
                    format="%.2f%%",
                    min_value=0.0,
                    max_value=100.0,
                ),
                "Precisão (%)": st.column_config.NumberColumn(
                    "Precisão (%)",
                    format="%.2f%%",
                ),
                "Acurácia Geral (%)": st.column_config.NumberColumn(
                    "Acurácia Geral (%)",
                    help="Cuidado: como ~98,9% das horas são normais, até o Dummy que chuta 'Normal' sempre tira ~98,9% de acurácia errando todos os alertas!",
                    format="%.2f%%",
                ),
                "Velocidade no Lote (ms)": st.column_config.NumberColumn(
                    "Velocidade no Lote (ms)",
                    format="%.1f ms",
                ),
            },
        )

        st.markdown(
            """
            <div class="step-grid">
                <div class="step-card green">
                    <span class="step-num">Métrica Nº 1 · Recall</span>
                    <h4>🎯 Recall (98,14% na Random Forest)</h4>
                    <p><strong>O que é:</strong> De todos os alertas reais que aconteceram, quantos % o modelo avisou?<br>
                    <strong>Por que é a principal:</strong> Porque deixar de avisar quando o ar fica ruim expõe alunos a risco respiratório.</p>
                </div>
                <div class="step-card">
                    <span class="step-num">Métrica Nº 2 · Precisão e F1</span>
                    <h4>⚖️ Precisão (78,2%) e F1-Score (87,1%)</h4>
                    <p><strong>Precisão:</strong> Quando o modelo toca a sirene, quantas vezes o ar realmente passou de 100?<br>
                    <strong>F1-Score:</strong> É a média que equilibra Recall e Precisão (evita que um modelo chute "Alerta" o dia todo).</p>
                </div>
                <div class="step-card amber">
                    <span class="step-num">Armadilha · Acurácia</span>
                    <h4>⚠️ Por que a Acurácia de 98,9% engana?</h4>
                    <p>Olhe a última linha da tabela (<strong>Dummy</strong>): ele chuta <em>"Ar Adequado"</em> o ano inteiro, tira <strong>98,90% de Acurácia Geral</strong>, mas acerta <strong>ZERO alertas (Recall = 0%)</strong>! Por isso nunca usamos a Acurácia sozinha.</p>
                </div>
                <div class="step-card red">
                    <span class="step-num">Os 4 Resultados · TP, FN, FP, TN</span>
                    <h4>🔍 Entenda as 4 siglas da tabela</h4>
                    <p><strong>TP:</strong> Alerta real avisado certo (158).<br>
                    <strong>FN (Pior erro!):</strong> Ar ficou ruim e o modelo não avisou (só 3 na RF!).<br>
                    <strong>FP:</strong> Alarme preventivo (44).<br>
                    <strong>TN:</strong> Hora normal certa (14.387).</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()
        st.markdown(f"### 2️⃣ Auditoria na Prática: O que o Modelo Previu vs. O que Aconteceu de Verdade ({particao_hist})")
        df_hist = carregar_serie_historica_com_previsoes()

        if "Holdout" in particao_hist:
            recorte_part = df_hist[df_hist["event_time_dt"] >= pd.Timestamp("2025-01-01")].copy()
            nome_periodo_txt = "Teste Final (Holdout: Janeiro/2025 a Agosto/2026)"
        else:
            recorte_part = df_hist[
                (df_hist["event_time_dt"] >= pd.Timestamp("2024-10-01"))
                & (df_hist["event_time_dt"] < pd.Timestamp("2025-01-01"))
            ].copy()
            nome_periodo_txt = "Validação Temporal (4º Trimestre de 2024: Outubro a Dezembro/2024)"

        recorte_part["alerta_simulado"] = (recorte_part["probabilidade_risco"] >= limiar_oficial).astype(int)
        tp_p = int(((recorte_part[COLUNA_ALVO] == 1) & (recorte_part["alerta_simulado"] == 1)).sum())
        fp_p = int(((recorte_part[COLUNA_ALVO] == 0) & (recorte_part["alerta_simulado"] == 1)).sum())
        fn_p = int(((recorte_part[COLUNA_ALVO] == 1) & (recorte_part["alerta_simulado"] == 0)).sum())
        total_pos_p = int(recorte_part[COLUNA_ALVO].sum())

        st.markdown(
            f"""
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-label">Total de Horas Analisadas</div>
                    <div class="kpi-value">{len(recorte_part):,} h</div>
                    <div class="kpi-desc">Período selecionado: <strong>{nome_periodo_txt}</strong> (dados de <code>data/processed/</code>).</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Episódios Reais de Poluição (IQAr &gt; 100)</div>
                    <div class="kpi-value">{total_pos_p} horas</div>
                    <div class="kpi-desc">Horas em que o índice oficial da CETESB realmente ultrapassou 100 pontos.</div>
                </div>
                <div class="kpi-card ok">
                    <div class="kpi-label">Alertas Capturados 1h Antes (TP)</div>
                    <div class="kpi-value">{tp_p} de {total_pos_p} ({(tp_p / max(1, total_pos_p)) * 100:.1f}%)</div>
                    <div class="kpi-desc">Episódios críticos em que a Random Forest avisou com 1 hora de antecedência.</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Erros no Período (FN e FP)</div>
                    <div class="kpi-value">{fn_p} FN  ·  {fp_p} FP</div>
                    <div class="kpi-desc">Apenas <strong>{fn_p} falhas críticas (FN)</strong> e <strong>{fp_p} alarmes preventivos (FP)</strong> no período inteiro.</div>
                </div>
            </div>
            """.replace(",", "."),
            unsafe_allow_html=True,
        )

        # Tabela interativa mostrando os episódios reais de poluição (IQAr > 100) e o que o modelo fez 1h antes
        eventos_reais_df = recorte_part[recorte_part[COLUNA_ALVO] == 1].copy()
        eventos_reais_df = eventos_reais_df.sort_values("event_time_dt", ascending=False).head(30)

        tabela_auditoria = pd.DataFrame(
            {
                "Hora da Leitura (t)": eventos_reais_df["time_dt"].dt.strftime("%d/%m/%Y %H:%M"),
                "Hora do Evento Crítico (t + 1h)": eventos_reais_df["event_time_dt"].dt.strftime("%d/%m/%Y %H:%M"),
                "IQAr em t (Antes)": eventos_reais_df[COLUNA_IQAR].round(1),
                "IQAr Real em t + 1h (Depois)": eventos_reais_df["iqar_evento"].round(1),
                "Probabilidade Dada pelo Modelo 1h Antes (%)": (eventos_reais_df["probabilidade_risco"] * 100).round(1),
                "Limiar": f"{limiar_oficial * 100:.0f}%",
                "Resultado da Previsão 1h Antes": eventos_reais_df["alerta_simulado"].map(
                    lambda a: "✅ ACERTOU O ALERTA (Verdadeiro Positivo — TP)"
                    if a == 1
                    else "❌ FALHA CRÍTICA: Não avisou (Falso Negativo — FN)"
                ),
            }
        )

        st.markdown("#### 📋 Tabela de Auditoria Linha a Linha (Últimos 30 Episódios Reais de Poluição com `IQAr > 100`)")
        st.dataframe(
            tabela_auditoria,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Probabilidade Dada pelo Modelo 1h Antes (%)": st.column_config.ProgressColumn(
                    "Probabilidade Dada pelo Modelo 1h Antes (%)",
                    help="Probabilidade emitida pela Random Forest 1 hora antes do evento. Quando é >= 30%, o modelo acerta o alerta!",
                    format="%.1f%%",
                    min_value=0.0,
                    max_value=100.0,
                ),
                "IQAr em t (Antes)": st.column_config.NumberColumn("IQAr em t (Antes)", format="%.1f pts"),
                "IQAr Real em t + 1h (Depois)": st.column_config.NumberColumn(
                    "IQAr Real em t + 1h (Depois)", format="%.1f pts"
                ),
            },
        )

        st.markdown(
            """
            <div class="explain-box green">
                <h4>💡 Como explicar esta Tabela de Auditoria na apresentação?</h4>
                <ul>
                    <li><strong>De onde vêm esses dados:</strong> o painel lê a nossa série histórica salva no repositório (<code>data/processed/dados_com_alvo_2022-08-04_2026-08-31.csv</code>), filtra as horas em que a poluição realmente passou de <strong>100 pontos</strong> e mostra o que o nosso modelo (<code>modelo_final_sprint5.joblib</code>) respondeu <strong>1 hora antes</strong>.</li>
                    <li><strong>Compare as colunas <em>IQAr em t (Antes)</em> e <em>IQAr Real em t + 1h (Depois)</em>:</strong> repare que mesmo quando o IQAr na hora <em>t</em> ainda estava abaixo de 100 (por exemplo, 92 ou 96 pontos), a <strong>Random Forest já enxergava a tendência de subida</strong> pela média das últimas 3h e pelo calor, emitindo probabilidade acima de 30% e <strong>antecipando o alerta antes de o ar ficar ruim!</strong></li>
                    <li><strong>Transparência total nos erros:</strong> na tabela acima também aparecem com total honestidade as únicas <strong>3 horas de Falha Crítica (FN)</strong> de dezembro de 2025, quando o ozônio subiu de forma muito abrupta em 1 hora e a probabilidade ficou abaixo de 30%.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()
