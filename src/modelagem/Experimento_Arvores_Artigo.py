"""Experimento comparativo completo (Baseline, Árvore de Decisão, Random Forest e XGBoost).

Preserva integralmente os artefatos da Sprint 5 e gera:
- Métricas de risco (Recall, Precisão, F1, Matriz de Confusão) e tempos de treino/inferência;
- Curva de profundidade da Árvore de Decisão (ilustrando overfitting);
- Figuras didáticas para o Artigo Técnico (GitHub Pages em docs/assets/) e relatórios;
- Cópia idempotente do dataset processado em data/processed/.
"""

from __future__ import annotations

import shutil
import time
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier, plot_tree
from xgboost import XGBClassifier

from src.modelagem.Avaliar_Baselines import (
    FEATURES_SPRINT4,
    _calcular_metricas,
    _validar_persistencia,
    criar_pipeline_naive_bayes,
    criar_pipeline_sprint4,
)
from src.transformacao.Calcular_Alvo_IQAr import COLUNA_ALVO
from src.transformacao.Features_Temporais import adicionar_resumos_curto_prazo
from src.validacao.Separacao_Temporal import (
    criar_folds_temporais,
    separar_teste_final,
)

FOLD_VALIDACAO = "2024-Q4"
COLUNAS_CONTEXTO = ("ozone", "pm2_5")
LIMIAR_ALERTA = 0.30


def _carregar_dados_e_config() -> tuple[pd.DataFrame, dict[str, Any], int]:
    with Path("config/params.yaml").open("r", encoding="utf-8") as arquivo:
        config = yaml.safe_load(arquivo)
    evaluation = config["evaluation"]
    horizonte_horas = int(evaluation["target_horizon_hours"])
    periodo = {
        "start_date": config["collection"]["start_date"],
        "end_date": config["collection"]["end_date"],
    }
    caminho_dados = (
        Path(config["paths"]["interim_data"])
        / config["paths"]["labeled_filename"].format(**periodo)
    )
    dados = pd.read_csv(caminho_dados, parse_dates=["time"])
    return dados, evaluation, horizonte_horas


def garantir_dados_processados() -> Path:
    """Garante que o arquivo tratado com alvo exista também em data/processed/."""
    origem = Path("data/interim/dados_com_alvo_2022-08-04_2026-08-31.csv")
    destino_dir = Path("data/processed")
    destino_dir.mkdir(parents=True, exist_ok=True)
    destino = destino_dir / origem.name
    if origem.exists() and not destino.exists():
        shutil.copy2(origem, destino)
    return destino


def _medir_treino_e_predicao(
    modelo: Any,
    x_treino: pd.DataFrame,
    y_treino: pd.Series,
    x_aval: pd.DataFrame,
    limiar: float = 0.5,
) -> tuple[np.ndarray, np.ndarray | None, float, float, float]:
    """Treina o modelo e mede tempos de fit (s) e inferência (ms total e por linha)."""
    t0 = time.perf_counter()
    modelo.fit(x_treino, y_treino)
    tempo_treino_s = time.perf_counter() - t0

    t1 = time.perf_counter()
    if hasattr(modelo, "predict_proba"):
        probabilidades = modelo.predict_proba(x_aval)[:, 1]
        y_pred = (probabilidades >= limiar).astype(int)
    else:
        probabilidades = None
        y_pred = modelo.predict(x_aval)
    tempo_pred_ms = (time.perf_counter() - t1) * 1000.0
    latencia_unitaria_ms = tempo_pred_ms / max(len(x_aval), 1)
    return y_pred, probabilidades, tempo_treino_s, tempo_pred_ms, latencia_unitaria_ms


def executar_comparativo_completo() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """Compara Baseline, Árvore de Decisão, Random Forest e XGBoost na validação e no teste."""
    dados_completos, evaluation, horizonte_horas = _carregar_dados_e_config()
    dados_temp = adicionar_resumos_curto_prazo(dados_completos, COLUNAS_CONTEXTO)
    dados_temp["event_time"] = pd.to_datetime(
        dados_temp["time"], errors="raise"
    ) + pd.Timedelta(hours=horizonte_horas)

    # 1. Partição de validação temporal (2024-Q4) para ajuste honesto sem tocar o teste
    desenvolvimento, teste_final = separar_teste_final(
        dados_temp,
        evaluation["final_test"]["start"],
        evaluation["final_test"]["end"],
        horizonte_horas,
    )
    folds = [f for f in evaluation["validation_folds"] if f["name"] == FOLD_VALIDACAO]
    treino_val, val_q4 = criar_folds_temporais(
        desenvolvimento, folds, horizonte_horas
    )[FOLD_VALIDACAO]

    # Razão de desbalanceamento no treino para o XGBoost (negativos / positivos)
    y_tr_val = treino_val[COLUNA_ALVO].astype(int)
    y_val = val_q4[COLUNA_ALVO].astype(int)
    scale_pos_val = float((y_tr_val == 0).sum() / max((y_tr_val == 1).sum(), 1))

    y_tr_full = desenvolvimento[COLUNA_ALVO].astype(int)
    y_test = teste_final[COLUNA_ALVO].astype(int)
    scale_pos_full = float((y_tr_full == 0).sum() / max((y_tr_full == 1).sum(), 1))

    def _construir_candidatos(scale_pos: float) -> dict[str, tuple[Any, float, str]]:
        return {
            "dummy_prior": (
                DummyClassifier(strategy="prior"),
                0.50,
                "Baseline (sempre classe majoritária)",
            ),
            "gaussian_naive_bayes": (
                criar_pipeline_naive_bayes(FEATURES_SPRINT4),
                0.50,
                "Baseline probabilístico (Gaussian NB)",
            ),
            "regressao_logistica_balanced": (
                criar_pipeline_sprint4(
                    LogisticRegression(
                        class_weight="balanced", max_iter=1000, random_state=42
                    )
                ),
                0.30,
                "Linear balanceado (limiar 0,30)",
            ),
            "arvore_decisao_cart": (
                criar_pipeline_sprint4(
                    DecisionTreeClassifier(
                        max_depth=6,
                        min_samples_leaf=5,
                        class_weight="balanced",
                        criterion="gini",
                        random_state=42,
                    )
                ),
                0.30,
                "Árvore de Decisão CART (max_depth=6, balanced, limiar 0,30)",
            ),
            "random_forest_balanced": (
                criar_pipeline_sprint4(
                    RandomForestClassifier(
                        n_estimators=300,
                        class_weight="balanced",
                        min_samples_leaf=2,
                        n_jobs=-1,
                        random_state=42,
                    )
                ),
                0.30,
                "Random Forest Bagging (300 árvores, balanced, limiar 0,30)",
            ),
            "xgboost_balanced": (
                criar_pipeline_sprint4(
                    XGBClassifier(
                        n_estimators=300,
                        max_depth=5,
                        learning_rate=0.05,
                        subsample=0.8,
                        colsample_bytree=0.8,
                        scale_pos_weight=scale_pos,
                        reg_lambda=1.0,
                        eval_metric="logloss",
                        random_state=42,
                        n_jobs=-1,
                    )
                ),
                0.30,
                "XGBoost Boosting (300 árvores, lr=0,05, max_depth=5, limiar 0,30)",
            ),
        }

    linhas_comparativo: list[dict[str, Any]] = []
    artefatos_treinados_teste: dict[str, Any] = {}

    for nome_particao, df_tr, y_tr, df_av, y_av, scale_pos in [
        ("validacao_2024_Q4", treino_val, y_tr_val, val_q4, y_val, scale_pos_val),
        ("holdout_2025_2026", desenvolvimento, y_tr_full, teste_final, y_test, scale_pos_full),
    ]:
        # Regra de persistência
        t0 = time.perf_counter()
        y_pers = _validar_persistencia(df_av, nome_particao)
        tempo_pred_pers = (time.perf_counter() - t0) * 1000.0
        m_pers = _calcular_metricas(
            y_av,
            y_pers,
            fold=nome_particao,
            modelo="persistencia_iqar_atual",
            grupo_features="regra_dominio_iqar_t",
            n_treino=len(df_tr),
        )
        linhas_comparativo.append(
            m_pers
            | {
                "descricao": "Persistência (IQAr em t > 100)",
                "limiar": 0.50,
                "tempo_treino_s": 0.0,
                "tempo_predicao_ms": round(tempo_pred_pers, 4),
                "latencia_por_amostra_ms": round(tempo_pred_pers / len(df_av), 6),
            }
        )

        candidatos = _construir_candidatos(scale_pos)
        x_tr = df_tr[list(FEATURES_SPRINT4)]
        x_av = df_av[list(FEATURES_SPRINT4)]

        for nome_mod, (pipeline, limiar, descricao) in candidatos.items():
            y_pred, probs, t_fit, t_pred_ms, lat_ms = _medir_treino_e_predicao(
                pipeline, x_tr, y_tr, x_av, limiar=limiar
            )
            m = _calcular_metricas(
                y_av,
                y_pred,
                fold=nome_particao,
                modelo=nome_mod,
                grupo_features="features_sprint4",
                n_treino=len(df_tr),
            )
            linhas_comparativo.append(
                m
                | {
                    "descricao": descricao,
                    "limiar": limiar,
                    "tempo_treino_s": round(t_fit, 4),
                    "tempo_predicao_ms": round(t_pred_ms, 4),
                    "latencia_por_amostra_ms": round(lat_ms, 6),
                }
            )
            if nome_particao == "holdout_2025_2026":
                artefatos_treinados_teste[nome_mod] = {
                    "pipeline": pipeline,
                    "y_pred": y_pred,
                    "probs": probs,
                    "metricas": m,
                }

    # 2. Estudo de profundidade da Árvore de Decisão (overfitting) na validação 2024-Q4
    linhas_profundidade: list[dict[str, Any]] = []
    x_tr_v = treino_val[list(FEATURES_SPRINT4)]
    x_val_v = val_q4[list(FEATURES_SPRINT4)]
    for depth in [1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, None]:
        arvore = criar_pipeline_sprint4(
            DecisionTreeClassifier(
                max_depth=depth,
                class_weight="balanced",
                criterion="gini",
                random_state=42,
            )
        )
        arvore.fit(x_tr_v, y_tr_val)
        pred_tr = (arvore.predict_proba(x_tr_v)[:, 1] >= 0.30).astype(int)
        pred_vl = (arvore.predict_proba(x_val_v)[:, 1] >= 0.30).astype(int)
        m_tr = _calcular_metricas(
            y_tr_val,
            pred_tr,
            fold="treino",
            modelo="dt",
            grupo_features="features_sprint4",
            n_treino=len(x_tr_v),
        )
        m_vl = _calcular_metricas(
            y_val,
            pred_vl,
            fold="validacao_2024_Q4",
            modelo="dt",
            grupo_features="features_sprint4",
            n_treino=len(x_tr_v),
        )
        clf_dt = arvore.named_steps["classificador"]
        linhas_profundidade.append(
            {
                "max_depth_config": str(depth) if depth is not None else "Sem limite",
                "profundidade_real": int(clf_dt.get_depth()),
                "n_folhas": int(clf_dt.get_n_leaves()),
                "recall_treino": round(float(m_tr["recall_classe_1"]), 4),
                "f1_treino": round(float(m_tr["f1_classe_1"]), 4),
                "recall_validacao": round(float(m_vl["recall_classe_1"]), 4),
                "precisao_validacao": round(float(m_vl["precisao_classe_1"]), 4),
                "f1_validacao": round(float(m_vl["f1_classe_1"]), 4),
                "fp_validacao": int(m_vl["fp"]),
                "fn_validacao": int(m_vl["fn"]),
            }
        )

    return (
        pd.DataFrame(linhas_comparativo),
        pd.DataFrame(linhas_profundidade),
        {
            "treino_val": treino_val,
            "val_q4": val_q4,
            "desenvolvimento": desenvolvimento,
            "teste_final": teste_final,
            "artefatos_teste": artefatos_treinados_teste,
        },
    )


def gerar_figuras_artigo(
    df_comp: pd.DataFrame,
    df_prof: pd.DataFrame,
    contexto: dict[str, Any],
) -> None:
    """Gera figuras didáticas em reports/figures/ e docs/assets/."""
    pastas = [Path("reports/figures"), Path("docs/assets")]
    for p in pastas:
        p.mkdir(parents=True, exist_ok=True)

    def _salvar_em_ambas(fig: plt.Figure, nome_arquivo: str) -> None:
        for p in pastas:
            fig.savefig(p / nome_arquivo, dpi=160, bbox_inches="tight")
        plt.close(fig)

    # Figura 1: Árvore de Decisão Rasa (max_depth=3) treinada nos dados reais (sem escalonamento para exibir unidades reais do domínio!)
    desenvolvimento = contexto["desenvolvimento"]
    x_dev = desenvolvimento[list(FEATURES_SPRINT4)].copy()
    x_dev = x_dev.fillna(x_dev.median(numeric_only=True))
    y_dev = desenvolvimento[COLUNA_ALVO].astype(int)

    arvore_rasa = DecisionTreeClassifier(
        max_depth=3,
        min_samples_leaf=20,
        class_weight="balanced",
        criterion="gini",
        random_state=42,
    )
    arvore_rasa.fit(x_dev, y_dev)

    fig1, ax1 = plt.subplots(figsize=(21, 9.8))
    plot_tree(
        arvore_rasa,
        feature_names=list(FEATURES_SPRINT4),
        class_names=["Ar Normal (<=100)", "ALERTA (>100)"],
        filled=True,
        rounded=True,
        impurity=True,
        proportion=True,
        precision=1,
        fontsize=9,
        ax=ax1,
    )
    ax1.set_title(
        "Árvore de Decisão Rasa (Profundidade = 3) nas Variáveis Originais do Domínio (UBC 2022–2024)\n"
        "Laranja = Folhas de Ar Normal (IQAr <= 100)   |   Azul = Folhas de Alerta de Risco (IQAr > 100)",
        fontsize=13.5,
        fontweight="bold",
        pad=18,
    )
    ax1.text(
        0.18,
        0.93,
        "RAMO ESQUERDO (SIM: iqar_ozone <= 83,6)\n94,1% das horas caem aqui → Quase sempre Ar Normal",
        transform=ax1.transAxes,
        ha="center",
        va="center",
        fontsize=10.5,
        fontweight="bold",
        color="#7c2d12",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#ffedd5", edgecolor="#ea580c", lw=1.4),
    )
    ax1.text(
        0.82,
        0.93,
        "RAMO DIREITO (NÃO: iqar_ozone > 83,6)\nSe media_3h_ozone > 117,8 → Dispara ALERTA!",
        transform=ax1.transAxes,
        ha="center",
        va="center",
        fontsize=10.5,
        fontweight="bold",
        color="#1e3a8a",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#dbeafe", edgecolor="#2563eb", lw=1.4),
    )
    _salvar_em_ambas(fig1, "fig_arvore_decisao_rasa.png")

    # Figura 2: Efeito da profundidade da Árvore de Decisão (Overfitting)
    fig2, (ax2a, ax2b) = plt.subplots(1, 2, figsize=(14.5, 5.6))
    x_labels = df_prof["max_depth_config"].tolist()
    x_idx = np.arange(len(x_labels))

    ax2a.axvspan(7.5, len(x_labels) - 0.5, color="#fee2e2", alpha=0.45, label="Zona de Overfitting (depth >= 12)")
    ax2a.plot(x_idx, df_prof["f1_treino"], marker="o", linewidth=2.2, color="#1d4ed8", label="F1 no Treino (passado)")
    ax2a.plot(x_idx, df_prof["f1_validacao"], marker="s", linewidth=2.2, color="#dc2626", label="F1 na Validação (2024-Q4)")
    ax2a.plot(x_idx, df_prof["recall_validacao"], marker="^", linestyle="--", linewidth=2.0, color="#059669", label="Recall na Validação")
    ax2a.set_xticks(x_idx)
    ax2a.set_xticklabels(x_labels, rotation=30)
    ax2a.set_ylim(0.56, 1.06)
    ax2a.set_xlabel("Profundidade Máxima da Árvore (max_depth)")
    ax2a.set_ylabel("Métrica (0 a 1)")
    ax2a.set_title("1. Quando a Árvore Cresce Demais: Overfitting", fontweight="bold")
    ax2a.grid(True, alpha=0.3)
    ax2a.legend(loc="lower right", fontsize=8.8)

    # Anotações didáticas no gráfico da esquerda
    ax2a.annotate(
        "Ponto ideal (depth=8)\nF1=0,96 | Recall=97,8%",
        xy=(6, float(df_prof.loc[6, "f1_validacao"])),
        xytext=(3.2, 0.67),
        ha="center",
        fontsize=8.8,
        fontweight="bold",
        color="#065f46",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#d1fae5", edgecolor="#059669", lw=1.2),
        arrowprops=dict(arrowstyle="->", color="#059669", lw=1.4),
    )
    ax2a.annotate(
        "OVERFITTING (decora o treino):\nTreino = 1,00, mas Recall cai p/ 84,8%",
        xy=(9, float(df_prof.loc[9, "recall_validacao"])),
        xytext=(8.6, 0.73),
        ha="center",
        fontsize=8.6,
        fontweight="bold",
        color="#991b1b",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#fef2f2", edgecolor="#dc2626", lw=1.2),
        arrowprops=dict(arrowstyle="->", color="#dc2626", lw=1.4),
    )

    ax2b.axvspan(7.5, len(x_labels) - 0.5, color="#fee2e2", alpha=0.45)
    b_fp = ax2b.bar(x_idx - 0.19, df_prof["fp_validacao"], width=0.38, color="#f59e0b", label="Falsos Positivos (FP: alarme preventivo)")
    b_fn = ax2b.bar(x_idx + 0.19, df_prof["fn_validacao"], width=0.38, color="#ef4444", label="Falsos Negativos (FN: falha crítica!)")
    for bar_group, cor_txt in ((b_fp, "#92400e"), (b_fn, "#991b1b")):
        for b in bar_group:
            v = int(round(b.get_height()))
            ax2b.text(
                b.get_x() + b.get_width() / 2,
                b.get_height() + 0.8,
                str(v),
                ha="center",
                va="bottom",
                fontsize=8.0,
                fontweight="bold",
                color=cor_txt,
            )
    ax2b.set_xticks(x_idx)
    ax2b.set_xticklabels(x_labels, rotation=30)
    ax2b.set_ylim(0, 70)
    ax2b.set_xlabel("Profundidade Máxima da Árvore (max_depth)")
    ax2b.set_ylabel("Quantidade de Erros em 2024-Q4 (46 alertas reais)")
    ax2b.set_title("2. Troca entre Alarmes Falsos (FP) e Alertas Perdidos (FN)", fontweight="bold")
    ax2b.grid(True, alpha=0.3)
    ax2b.legend(loc="upper right", fontsize=8.8)
    ax2b.annotate(
        "No overfitting (depth >= 12),\nos Falsos Negativos saltam\nde 1 para 7 alertas perdidos!",
        xy=(8.19, 7.5),
        xytext=(7.6, 33),
        ha="center",
        fontsize=8.8,
        fontweight="bold",
        color="#991b1b",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#fef2f2", edgecolor="#dc2626", lw=1.2),
        arrowprops=dict(arrowstyle="->", color="#dc2626", lw=1.4),
    )
    fig2.tight_layout()
    _salvar_em_ambas(fig2, "fig_overfitting_profundidade.png")

    # Figura 3: Comparativo de métricas no Holdout (2025-2026) entre Baseline e os 3 modelos de árvore
    df_holdout = df_comp[df_comp["fold"] == "holdout_2025_2026"].copy()
    ordem = [
        "dummy_prior",
        "persistencia_iqar_atual",
        "gaussian_naive_bayes",
        "arvore_decisao_cart",
        "xgboost_balanced",
        "random_forest_balanced",
    ]
    nomes_curtos = {
        "dummy_prior": "Dummy\n(Baseline)",
        "persistencia_iqar_atual": "Persistência\n(IQAr em t)",
        "gaussian_naive_bayes": "Gaussian\nNaive Bayes",
        "arvore_decisao_cart": "Árvore de\nDecisão (CART)",
        "xgboost_balanced": "XGBoost\n(Boosting)",
        "random_forest_balanced": "Random Forest\n(Escolhido)",
    }
    df_h = df_holdout.set_index("modelo").loc[ordem].reset_index()

    fig3, ax3 = plt.subplots(figsize=(12, 5.5))
    idx = np.arange(len(df_h))
    largura = 0.26
    vals_rec = df_h["recall_classe_1"].to_numpy(dtype=float)
    vals_prec = df_h["precisao_classe_1"].to_numpy(dtype=float)
    vals_f1 = df_h["f1_classe_1"].to_numpy(dtype=float)

    # Quando o valor real é 0.00 (Dummy), desenha uma base mínima (0.018) para mostrar as 3 barras no eixo
    b1 = ax3.bar(idx - largura, np.where(vals_rec == 0, 0.018, vals_rec), width=largura, color="#059669", label="Recall (Sensibilidade)")
    b2 = ax3.bar(idx, np.where(vals_prec == 0, 0.018, vals_prec), width=largura, color="#2563eb", label="Precisão")
    b3 = ax3.bar(idx + largura, np.where(vals_f1 == 0, 0.018, vals_f1), width=largura, color="#7c3aed", label="F1-Score")

    ax3.set_xticks(idx)
    ax3.set_xticklabels([nomes_curtos[m] for m in df_h["modelo"]], fontsize=10)
    ax3.set_ylim(0, 1.12)
    ax3.set_ylabel("Valor da Métrica (0 a 1)")
    ax3.set_title("Desempenho Comparativo no Período Recente de Teste (Holdout 2025–2026: 14.592 horas)", fontweight="bold")
    ax3.grid(axis="y", alpha=0.3)
    ax3.legend(loc="upper left")

    for barras, valores_reais in ((b1, vals_rec), (b2, vals_prec), (b3, vals_f1)):
        for b, val_real in zip(barras, valores_reais):
            if val_real == 0:
                b.set_alpha(0.45)
                b.set_edgecolor("#dc2626")
                b.set_linewidth(1.0)
            h_pos = b.get_height()
            ax3.text(
                b.get_x() + b.get_width() / 2,
                h_pos + 0.015,
                f"{val_real:.2f}",
                ha="center",
                va="bottom",
                fontsize=8.5,
                fontweight="bold" if val_real == 0 else "normal",
                color="#b91c1c" if val_real == 0 else "#0f172a",
            )

    ax3.annotate(
        "Chuta só 'Ar Adequado'\n(98,9% acurácia, 0% alertas)",
        xy=(0, 0.09),
        xytext=(-0.04, 0.25),
        ha="center",
        va="bottom",
        fontsize=8.0,
        color="#991b1b",
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.28", facecolor="#fef2f2", edgecolor="#f87171", lw=1),
        arrowprops=dict(arrowstyle="->", color="#dc2626", lw=1.2),
    )
    fig3.tight_layout()
    _salvar_em_ambas(fig3, "fig_comparacao_modelos_metricas.png")

    # Figura 4: Matrizes de confusão lado a lado das 3 famílias de árvores no Holdout
    from matplotlib.patches import Rectangle

    fig4, axes4 = plt.subplots(1, 3, figsize=(15, 5.0))
    modelos_arvore = [
        ("arvore_decisao_cart", "1. Árvore de Decisão (CART)", "Perdeu 22 alertas reais (alta variância)", "#b45309"),
        ("random_forest_balanced", "2. Random Forest (ESCOLHIDO ★)", "★ Só 3 falhas críticas em 14.592h!", "#047857"),
        ("xgboost_balanced", "3. XGBoost (Boosting)", "Menor alarme falso (20 FP), mas 6 falhas", "#1d4ed8"),
    ]
    cores_quadrantes = [
        [("#e2e8f0", "#0f172a", "#94a3b8"), ("#fef3c7", "#92400e", "#f59e0b")],
        [("#fee2e2", "#991b1b", "#dc2626"), ("#dcfce7", "#065f46", "#059669")],
    ]
    rotulos = [
        ["TN (Ar Normal Certo)", "FP (Alarme Preventivo)"],
        ["FN (FALHA CRÍTICA!)", "TP (Alerta Detectado)"],
    ]
    for ax, (cod, titulo, resumo_baixo, cor_destaque) in zip(axes4, modelos_arvore):
        linha = df_holdout[df_holdout["modelo"] == cod].iloc[0]
        matriz = np.array([[int(linha["tn"]), int(linha["fp"])], [int(linha["fn"]), int(linha["tp"])]])
        ax.set_xlim(-0.5, 1.5)
        ax.set_ylim(1.5, -0.5)
        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        ax.set_xticklabels(["Previsto:\nAr Normal (0)", "Previsto:\nALERTA (1)"], fontsize=9.5, fontweight="bold")
        ax.set_yticklabels(["Real:\nAr Normal (0)", "Real:\nALERTA (1)"], fontsize=9.5, fontweight="bold")
        ax.set_title(
            f"{titulo}\nRecall = {linha['recall_classe_1']*100:.1f}%  |  F1 = {linha['f1_classe_1']*100:.1f}%",
            fontsize=11,
            fontweight="bold",
            color=cor_destaque if "ESCOLHIDO" in titulo else "#0f172a",
            pad=10,
        )
        for i in range(2):
            for j in range(2):
                bg_c, txt_c, borda_c = cores_quadrantes[i][j]
                lw_q = 2.4 if (i == 1 and j == 0) else 1.3
                ax.add_patch(
                    Rectangle((j - 0.48, i - 0.48), 0.96, 0.96, facecolor=bg_c, edgecolor=borda_c, linewidth=lw_q)
                )
                ax.text(
                    j,
                    i - 0.12,
                    rotulos[i][j],
                    ha="center",
                    va="center",
                    color=txt_c,
                    fontweight="bold",
                    fontsize=9.0,
                )
                ax.text(
                    j,
                    i + 0.16,
                    f"{matriz[i, j]:,}".replace(",", "."),
                    ha="center",
                    va="center",
                    color=txt_c,
                    fontweight="bold",
                    fontsize=14.0 if (i == 1 and j == 0) else 12.5,
                )
        ax.set_xlabel(resumo_baixo, fontsize=9.5, fontweight="bold", color=cor_destaque, labelpad=8)
        for spine in ax.spines.values():
            spine.set_visible(False)

    fig4.suptitle(
        "Matrizes de Confusão no Teste Final (Holdout 2025–2026: 14.592 horas, sendo 161 alertas reais)\n"
        "Quadrante Vermelho (FN) = Erro mais grave (ar ficou ruim e o modelo não avisou)",
        fontsize=12.5,
        fontweight="bold",
        y=1.04,
    )
    fig4.tight_layout()
    _salvar_em_ambas(fig4, "fig_matriz_confusao_3_arvores.png")

    # Figura 5: Importância das Features (Random Forest vs XGBoost) e Latência
    artefatos = contexto["artefatos_teste"]
    rf_clf = artefatos["random_forest_balanced"]["pipeline"].named_steps["classificador"]
    xgb_clf = artefatos["xgboost_balanced"]["pipeline"].named_steps["classificador"]

    nomes_amigaveis = {
        "iqar_ozone": "iqar_ozone (Subíndice O3 atual)",
        "media_3h_ozone": "media_3h_ozone (Média 3h de O3)",
        "iqar_pm2_5": "iqar_pm2_5 (Subíndice PM2,5)",
        "iqar_pm10": "iqar_pm10 (Subíndice PM10)",
        "temperature_2m": "temperature_2m (Temperatura)",
        "media_3h_pm2_5": "media_3h_pm2_5 (Média 3h PM2,5)",
        "delta_2h_ozone": "delta_2h_ozone (Variação 2h O3)",
        "iqar_carbon_monoxide": "iqar_carbon_monoxide (Subíndice CO)",
        "iqar_sulphur_dioxide": "iqar_sulphur_dioxide (Subíndice SO2)",
        "relative_humidity_2m": "relative_humidity_2m (Umidade)",
        "wind_speed_10m": "wind_speed_10m (Vento)",
        "pressure_msl": "pressure_msl (Pressão)",
        "delta_2h_pm2_5": "delta_2h_pm2_5 (Variação 2h PM2,5)",
        "iqar_nitrogen_dioxide": "iqar_nitrogen_dioxide (Subíndice NO2)",
        "precipitation": "precipitation (Chuva)",
    }

    imp_df = pd.DataFrame(
        {
            "feature": [nomes_amigaveis.get(f, f) for f in FEATURES_SPRINT4],
            "Random Forest (Gini)": rf_clf.feature_importances_,
            "XGBoost (Gain)": xgb_clf.feature_importances_,
        }
    ).sort_values("Random Forest (Gini)", ascending=True).tail(10)

    fig5, (ax5a, ax5b) = plt.subplots(1, 2, figsize=(15, 5.6))
    y_pos = np.arange(len(imp_df))
    b_rf = ax5a.barh(y_pos - 0.19, imp_df["Random Forest (Gini)"] * 100, height=0.38, color="#1d4ed8", label="Random Forest (Gini)")
    b_xgb = ax5a.barh(y_pos + 0.19, imp_df["XGBoost (Gain)"] * 100, height=0.38, color="#f97316", label="XGBoost (Gain)")
    for b_grp, cor_t in ((b_rf, "#1e3a8a"), (b_xgb, "#9a3412")):
        for b in b_grp:
            w_val = b.get_width()
            if w_val >= 1.2:
                ax5a.text(
                    w_val + 0.8,
                    b.get_y() + b.get_height() / 2,
                    f"{w_val:.1f}%",
                    va="center",
                    ha="left",
                    fontsize=8.0,
                    fontweight="bold",
                    color=cor_t,
                )
    ax5a.set_yticks(y_pos)
    ax5a.set_yticklabels(imp_df["feature"], fontsize=9.2)
    ax5a.set_xlim(0, 76)
    ax5a.set_xlabel("Importância Relativa na Decisão (%)")
    ax5a.set_title("1. Top 10 Variáveis Mais Importantes (O que o Modelo Olha?)", fontweight="bold")
    ax5a.grid(axis="x", alpha=0.3)
    ax5a.legend(loc="lower right")
    ax5a.text(
        0.36,
        0.26,
        "Ozônio atual + Média 3h de O3\nconcentram 67,6% da decisão\nna Random Forest (e 87,1% no XGBoost)",
        transform=ax5a.transAxes,
        fontsize=8.6,
        fontweight="bold",
        color="#1e3a8a",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="#eff6ff", edgecolor="#3b82f6", lw=1.2),
    )

    df_tempos = df_holdout.set_index("modelo").loc[
        ["arvore_decisao_cart", "random_forest_balanced", "xgboost_balanced"]
    ].reset_index()
    nomes_t = ["Árvore Única\n(CART)", "Random Forest\n(300 árvores)", "XGBoost\n(300 árvores)"]
    x_t = np.arange(3)
    bt1 = ax5b.bar(x_t - 0.19, df_tempos["tempo_treino_s"] * 1000, width=0.36, color="#0ea5e9", label="Treino (21.121h em ms)")
    bt2 = ax5b.bar(x_t + 0.19, df_tempos["tempo_predicao_ms"], width=0.36, color="#10b981", label="Previsão de todas as 14.592h (ms)")
    for b_grp, cor_t in ((bt1, "#0369a1"), (bt2, "#047857")):
        for b in b_grp:
            h_v = b.get_height()
            ax5b.text(
                b.get_x() + b.get_width() / 2,
                h_v + 16,
                f"{h_v:.0f} ms",
                ha="center",
                va="bottom",
                fontsize=9.0,
                fontweight="bold",
                color=cor_t,
            )
    ax5b.set_xticks(x_t)
    ax5b.set_xticklabels(nomes_t, fontsize=9.8)
    ax5b.set_ylim(0, max(df_tempos["tempo_treino_s"] * 1000) * 1.18)
    ax5b.set_ylabel("Tempo Total (milissegundos)")
    ax5b.set_title("2. Tempo de Treino e de Previsão em Lote (ms)", fontweight="bold")
    ax5b.grid(axis="y", alpha=0.3)
    ax5b.legend(loc="upper right")
    ax5b.text(
        0.04,
        0.58,
        "Prever 14.592h leva < 0,1 s!\nRandom Forest: ~0,007 ms/hora\n(instantâneo p/ o usuário)",
        transform=ax5b.transAxes,
        ha="left",
        fontsize=8.4,
        fontweight="bold",
        color="#065f46",
        bbox=dict(boxstyle="round,pad=0.32", facecolor="#ecfdf5", edgecolor="#10b981", lw=1.2),
    )
    fig5.tight_layout()
    _salvar_em_ambas(fig5, "fig_importancia_e_latencia.png")


def main() -> None:
    destino_proc = garantir_dados_processados()
    print(f"Dataset processado garantido em: {destino_proc}")

    df_comp, df_prof, contexto = executar_comparativo_completo()
    pasta_rel = Path("reports/modeling")
    pasta_rel.mkdir(parents=True, exist_ok=True)
    df_comp.to_csv(pasta_rel / "artigo_comparativo_modelos.csv", index=False, encoding="utf-8")
    df_prof.to_csv(pasta_rel / "artigo_profundidade_arvore.csv", index=False, encoding="utf-8")

    gerar_figuras_artigo(df_comp, df_prof, contexto)
    print("\n=== Comparativo Completo (Validação 2024-Q4 e Holdout 2025-2026) ===")
    colunas_exibir = [
        "fold",
        "modelo",
        "limiar",
        "recall_classe_1",
        "precisao_classe_1",
        "f1_classe_1",
        "tp",
        "fp",
        "fn",
        "tempo_treino_s",
        "tempo_predicao_ms",
    ]
    print(df_comp[colunas_exibir].to_string(index=False))
    print("\n=== Curva de Profundidade da Árvore de Decisão (Validação 2024-Q4) ===")
    print(df_prof.to_string(index=False))


if __name__ == "__main__":
    main()
