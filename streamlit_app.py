"""Dashboard interativo Streamlit — Trilha B: Qualidade do Ar (UBC / Mogi das Cruzes).

Possui duas abas principais conforme especificação do Plano de Ensino:
1. Previsão Atual: consulta imediata às APIs Open-Meteo, inferência ao vivo (+1h oficial e projeções +7h/+24h), probabilidade de risco e latência.
2. Desempenho Histórico: comparativo entre Baseline, Árvore de Decisão, Random Forest e XGBoost, matrizes de confusão e série histórica (Previsto vs. Real).
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
    page_title="ArPrev | Foco na Antecipação de Condições Inadequadas",
    page_icon="🌬️",
    layout="wide",
    initial_sidebar_state="expanded",
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
def carregar_curva_profundidade() -> pd.DataFrame:
    caminho = Path("reports/modeling/artigo_profundidade_arvore.csv")
    if caminho.exists():
        return pd.read_csv(caminho)
    return pd.DataFrame()


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
    return df_validos


def main() -> None:
    artefato = carregar_artefato_modelo()
    limiar_oficial = float(artefato["decision_threshold"])

    # =========================================================================
    # BARRA LATERAL (SIDEBAR): Filtros de tempo, Seletor de Data e Modo Avançado
    # =========================================================================
    with st.sidebar:
        logo_path = Path("docs/assets/logo.png")
        if logo_path.exists():
            st.image(str(logo_path), use_container_width=True)
        st.title("⚙️ Controles do Painel")
        st.caption("Ponto de referência: Universidade Braz Cubas (Mogi das Cruzes – SP)")

        horizonte_projecao = st.radio(
            "Horizonte de projeção ao vivo (Aba 1):",
            options=[1, 7, 24],
            index=2,
            format_func=lambda h: (
                "Oficial: +1 hora"
                if h == 1
                else ("Experimental: +7h (Turno)" if h == 7 else "Experimental: +24h (Dia completo)")
            ),
        )

        st.divider()
        st.subheader("📅 Filtros de Tempo (Aba 2)")
        particao_hist = st.selectbox(
            "Período de análise histórica:",
            options=[
                "Teste Recente (Holdout: 2025–2026)",
                "Validação Temporal (2024-Q4)",
                "Série Completa (2022–2026)",
            ],
            index=0,
        )

        data_seletor = st.date_input(
            "Seletor de data para inspeção detalhada:",
            value=pd.to_datetime("2025-12-27").date(),
            min_value=pd.to_datetime("2022-08-05").date(),
            max_value=pd.to_datetime("2026-08-31").date(),
        )
        janela_dias_grafico = st.slider(
            "Janela de visualização ao redor da data (dias):",
            min_value=2,
            max_value=30,
            value=7,
        )

        st.divider()
        modo_avancado = st.toggle("🔬 Modo Avançado (Auditoria & Limiar)", value=False)
        if modo_avancado:
            limiar_simulacao = st.slider(
                "Simular limiar de probabilidade:",
                min_value=0.05,
                max_value=0.95,
                value=limiar_oficial,
                step=0.05,
                help="O limiar oficial congelado na validação é 0,30.",
            )
        else:
            limiar_simulacao = limiar_oficial

        st.divider()
        st.markdown(
            "**Links Rápidos:**\n"
            "- [Artigo Técnico (GitHub Pages)](https://diogogomesb.github.io/Ciencia-de-Dados-e-Aprendizagem-de-Maquina/)\n"
            "- [Repositório GitHub](https://github.com/DiogoGomesB/Ciencia-de-Dados-e-Aprendizagem-de-Maquina)\n"
            "- [Documentação e RFC](https://github.com/DiogoGomesB/Ciencia-de-Dados-e-Aprendizagem-de-Maquina/blob/main/docs/RFC.md)"
        )

    # =========================================================================
    # CABEÇALHO E AVISO REGULATÓRIO OBRIGATÓRIO
    # =========================================================================
    col_logo, col_title = st.columns([1, 6], vertical_alignment="center")
    with col_logo:
        logo_path = Path("docs/assets/logo.png")
        if logo_path.exists():
            st.image(str(logo_path), use_container_width=True)
    with col_title:
        st.title("🌬️ ArPrev — Foco na Antecipação de Condições Inadequadas")
        st.caption("Classificação Preditiva de Risco Respiratório (IQAr > 100) · Universidade Braz Cubas (Mogi das Cruzes / SP)")
    st.warning(
        "⚠️ **Aviso Importante:** As previsões exibidas neste painel são **estimativas experimentais** "
        "produzidas por modelo de aprendizado de máquina sobre dados atmosféricos abertos (Open-Meteo / CAMS) "
        "e **não substituem alertas oficiais** da CETESB ou da Defesa Civil."
    )

    aba1, aba2 = st.tabs(
        [
            "📡 1. Previsão Atual (Inferência ao Vivo)",
            "📊 2. Desempenho Histórico e Comparativo de Modelos",
        ]
    )

    # =========================================================================
    # ABA 1: PREVISÃO ATUAL (CONSULTA À API + INFERÊNCIA AO VIVO)
    # =========================================================================
    with aba1:
        st.subheader("Consulta Imediata às APIs Open-Meteo e Inferência em Tempo Real")
        col_btn, col_info = st.columns([1, 3])
        with col_btn:
            atualizar_agora = st.button("🔄 Atualizar Coleta ao Vivo", type="primary", use_container_width=True)
        with col_info:
            st.caption(
                "Conecta aos endpoints `air-quality-api.open-meteo.com` e `api.open-meteo.com/v1/forecast`, "
                "calcula os subíndices CETESB e executa o pipeline `RandomForestClassifier` (300 árvores)."
            )

        try:
            t_inicio = time.perf_counter()
            res_1h = prever_proxima_hora().iloc[0]
            latencia_1h_ms = (time.perf_counter() - t_inicio) * 1000.0

            prob_1h = float(res_1h["probabilidade estimada de IQAr > 100"])
            alerta_1h = int(prob_1h >= limiar_simulacao)
            horario_dados = pd.Timestamp(res_1h["horário dos dados até t"])
            horario_evento = pd.Timestamp(res_1h["horário do evento previsto"])

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                status_txt = "🚨 ALERTA" if alerta_1h == 1 else "✅ Sem alerta"
                st.metric(
                    label=f"Previsão oficial (+1h: {horario_evento:%d/%m %H:%M})",
                    value=status_txt,
                    delta=f"Limiar ativo: {limiar_simulacao:.0%}",
                    delta_color="off",
                )
            with c2:
                st.metric(
                    label="Probabilidade de IQAr > 100",
                    value=f"{prob_1h:.1%}",
                    delta=f"{(prob_1h - limiar_simulacao) * 100:+.1f} p.p. vs limiar",
                    delta_color="inverse",
                )
            with c3:
                st.metric(
                    label="Dados disponíveis até (t)",
                    value=f"{horario_dados:%d/%m %H:%M}",
                )
            with c4:
                st.metric(
                    label="Latência total (API + modelo)",
                    value=f"{latencia_1h_ms:.0f} ms",
                )

            if alerta_1h == 1:
                st.error(
                    f"**Recomendação preventiva (UBC):** risco estimado de ar inadequado para "
                    f"**{horario_evento:%d/%m/%Y %H:%M}** (probabilidade de **{prob_1h:.1%}**). Sugere-se transferir "
                    "práticas esportivas intensas para ambientes cobertos e orientar grupos sensíveis."
                )
            else:
                st.success(
                    f"**Sem alerta pela regra:** para **{horario_evento:%d/%m/%Y %H:%M}**, a probabilidade estimada de "
                    f"IQAr > 100 é **{prob_1h:.1%}**, abaixo do limiar ativo."
                )

            if horizonte_projecao > 1:
                st.markdown(f"#### 🔭 Projeção experimental para as próximas **{horizonte_projecao} horas**")
                df_proj = projetar_proximas_horas(horas_frente=horizonte_projecao)
                col_prob = "probabilidade estimada de IQAr > 100"
                df_proj["alerta_simulado"] = (df_proj[col_prob] >= limiar_simulacao).astype(int)

                fig_p, (ax_p1, ax_p2) = plt.subplots(1, 2, figsize=(13, 4.2))
                horas_lbl = pd.to_datetime(df_proj["horário do evento previsto"]).dt.strftime("%d/%m %Hh")
                x_i = np.arange(len(df_proj))
                passo = max(1, len(x_i) // 8)

                cores_bar = ["#dc2626" if a == 1 else "#2563eb" for a in df_proj["alerta_simulado"]]
                ax_p1.bar(x_i, df_proj[col_prob] * 100, color=cores_bar, alpha=0.85)
                ax_p1.axhline(limiar_simulacao * 100, color="#dc2626", linestyle="--", label=f"Limiar ({limiar_simulacao:.0%})")
                ax_p1.set_xticks(x_i[::passo])
                ax_p1.set_xticklabels(horas_lbl.iloc[::passo], rotation=35)
                ax_p1.set_ylim(0, 105)
                ax_p1.set_ylabel("Probabilidade (%)")
                ax_p1.set_title(f"Probabilidade de IQAr > 100 (+1h a +{horizonte_projecao}h)")
                ax_p1.grid(axis="y", alpha=0.3)
                ax_p1.legend()

                ax_p2.plot(x_i, df_proj["iqar projetado (CAMS)"], marker="o", color="#059669", linewidth=2, label="IQAr projetado (CAMS/Open-Meteo)")
                ax_p2.axhline(100, color="#d97706", linestyle="--", label="Limite CETESB (IQAr = 100)")
                ax_p2.set_xticks(x_i[::passo])
                ax_p2.set_xticklabels(horas_lbl.iloc[::passo], rotation=35)
                ax_p2.set_ylabel("IQAr (pontos)")
                ax_p2.set_title("IQAr calculado sobre as concentrações previstas pela API")
                ax_p2.grid(True, alpha=0.3)
                ax_p2.legend()
                fig_p.tight_layout()
                st.pyplot(fig_p)
                plt.close(fig_p)

                with st.expander("📋 Ver tabela horária detalhada da projeção", expanded=False):
                    st.dataframe(df_proj, use_container_width=True)

            if modo_avancado:
                st.markdown("#### 🔬 Modo avançado: metadados do artefato serializado (`joblib`)")
                st.json(
                    {
                        "model_name": artefato["model_name"],
                        "decision_threshold_oficial": artefato["decision_threshold"],
                        "training_rows": artefato["training_rows"],
                        "target_horizon_hours": artefato["target_horizon_hours"],
                        "features": list(artefato["features"]),
                    }
                )
        except Exception as erro_api:
            st.warning(
                f"Não foi possível consultar a API Open-Meteo ao vivo neste instante ({erro_api}). "
                "Verifique a conexão de rede ou utilize a Aba 2 para inspecionar os dados históricos."
            )

    # =========================================================================
    # ABA 2: DESEMPENHO HISTÓRICO E COMPARATIVO DE MODELOS
    # =========================================================================
    with aba2:
        st.subheader("1. Experimento Comparativo: Baseline vs. Árvore de Decisão, Random Forest e XGBoost")
        df_comp = carregar_metricas_comparativas()

        filtro_fold = (
            "holdout_2025_2026"
            if "Holdout" in particao_hist or "Série" in particao_hist
            else "validacao_2024_Q4"
        )
        df_fold = df_comp[df_comp["fold"] == filtro_fold].copy() if "fold" in df_comp.columns else df_comp.copy()

        colunas_tabela = [
            c
            for c in [
                "modelo",
                "descricao",
                "limiar",
                "recall_classe_1",
                "precisao_classe_1",
                "f1_classe_1",
                "tp",
                "fp",
                "fn",
                "tn",
                "tempo_treino_s",
                "tempo_predicao_ms",
            ]
            if c in df_fold.columns
        ]
        st.dataframe(
            df_fold[colunas_tabela].sort_values("f1_classe_1", ascending=False),
            use_container_width=True,
            hide_index=True,
        )

        c_fig1, c_fig2 = st.columns(2)
        with c_fig1:
            caminho_f3 = Path("reports/figures/fig_comparacao_modelos_metricas.png")
            if caminho_f3.exists():
                st.image(str(caminho_f3), caption="Comparação de Recall, Precisão e F1 no Holdout (2025–2026).")
        with c_fig2:
            caminho_f4 = Path("reports/figures/fig_matriz_confusao_3_arvores.png")
            if caminho_f4.exists():
                st.image(str(caminho_f4), caption="Matrizes de Confusão: Árvore de Decisão, Random Forest e XGBoost.")

        st.divider()
        st.subheader("2. Série Histórica: Previsão Gerada vs. Ocorrência Real")
        df_hist = carregar_serie_historica_com_previsoes()

        data_ini = pd.Timestamp(data_seletor) - pd.Timedelta(days=janela_dias_grafico // 2)
        data_fim = pd.Timestamp(data_seletor) + pd.Timedelta(days=janela_dias_grafico)
        recorte = df_hist[(df_hist["event_time_dt"] >= data_ini) & (df_hist["event_time_dt"] <= data_fim)].copy()

        if len(recorte) > 0:
            recorte["alerta_simulado"] = (recorte["probabilidade_risco"] >= limiar_simulacao).astype(int)
            tp_rec = int(((recorte[COLUNA_ALVO] == 1) & (recorte["alerta_simulado"] == 1)).sum())
            fp_rec = int(((recorte[COLUNA_ALVO] == 0) & (recorte["alerta_simulado"] == 1)).sum())
            fn_rec = int(((recorte[COLUNA_ALVO] == 1) & (recorte["alerta_simulado"] == 0)).sum())

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Horas na Janela Selecionada", len(recorte))
            m2.metric("Alertas Reais (IQAr > 100)", int(recorte[COLUNA_ALVO].sum()))
            m3.metric("Alertas Detectados (TP)", tp_rec)
            m4.metric("Falsos Negativos (FN) / Falsos Positivos (FP)", f"{fn_rec} FN / {fp_rec} FP")

            fig_h, (ax_h1, ax_h2) = plt.subplots(2, 1, figsize=(13, 6.2), sharex=True)
            ax_h1.plot(recorte["event_time_dt"], recorte[COLUNA_IQAR].shift(-1), color="#0f172a", linewidth=1.6, label="IQAr Real no Horário do Evento")
            ax_h1.axhline(100, color="#dc2626", linestyle="--", label="Limite CETESB (IQAr = 100)")
            eventos_reais = recorte[recorte[COLUNA_ALVO] == 1]
            if len(eventos_reais) > 0:
                ax_h1.scatter(
                    eventos_reais["event_time_dt"],
                    eventos_reais[COLUNA_IQAR].shift(-1).fillna(105),
                    color="#dc2626",
                    zorder=5,
                    label="Episódio Real (Classe 1)",
                )
            ax_h1.set_ylabel("IQAr")
            ax_h1.set_title(f"Comparativo Real vs. Previsto ({data_ini.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')})")
            ax_h1.grid(True, alpha=0.3)
            ax_h1.legend(loc="upper right")

            ax_h2.plot(recorte["event_time_dt"], recorte["probabilidade_risco"] * 100, color="#2563eb", linewidth=1.8, label="Probabilidade Prevista (Random Forest)")
            ax_h2.axhline(limiar_simulacao * 100, color="#dc2626", linestyle="--", label=f"Limiar de Alerta ({limiar_simulacao:.0%})")
            ax_h2.fill_between(
                recorte["event_time_dt"],
                0,
                recorte["probabilidade_risco"] * 100,
                where=(recorte["probabilidade_risco"] >= limiar_simulacao),
                color="#ef4444",
                alpha=0.25,
                label="Período em Alerta Previsto",
            )
            ax_h2.set_ylim(0, 105)
            ax_h2.set_ylabel("Probabilidade (%)")
            ax_h2.set_xlabel("Data e Hora do Evento")
            ax_h2.grid(True, alpha=0.3)
            ax_h2.legend(loc="upper right")
            fig_h.tight_layout()
            st.pyplot(fig_h)
            plt.close(fig_h)
        else:
            st.info("Nenhum registro encontrado para o intervalo selecionado.")

        if modo_avancado:
            st.divider()
            st.subheader("🔬 Diagnóstico Avançado: Interpretabilidade da Árvore e Importância das Variáveis")
            c_adv1, c_adv2 = st.columns(2)
            with c_adv1:
                caminho_f1 = Path("reports/figures/fig_arvore_decisao_rasa.png")
                if caminho_f1.exists():
                    st.image(str(caminho_f1), caption="Árvore de Decisão rasa (profundidade 3) com regras no domínio.")
            with c_adv2:
                caminho_f5 = Path("reports/figures/fig_importancia_e_latencia.png")
                if caminho_f5.exists():
                    st.image(str(caminho_f5), caption="Importância das variáveis (Random Forest vs. XGBoost) e latência.")

            df_prof = carregar_curva_profundidade()
            if not df_prof.empty:
                st.write("**Tabela de Overfitting da Árvore de Decisão por Profundidade (`max_depth`):**")
                st.dataframe(df_prof, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
