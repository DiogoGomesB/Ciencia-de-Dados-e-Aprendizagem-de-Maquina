"""Gera os diagramas do projeto em PDF e JPG em docs/diagramas/."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

RAIZ = Path(__file__).resolve().parents[2]
SAIDA = RAIZ / "docs" / "diagramas"


def _caixa(ax, x, y, w, h, texto, cor):
    ax.add_patch(
        FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.15",
            facecolor=cor, edgecolor="#333333", linewidth=1.2,
        )
    )
    ax.text(x + w / 2, y + h / 2, texto, ha="center", va="center", fontsize=9)


def _seta(ax, x1, y1, x2, y2):
    ax.add_patch(
        FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=14, color="#333333")
    )


def _salvar(fig, nome):
    SAIDA.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "jpg"):
        destino = SAIDA / f"{nome}.{ext}"
        fig.savefig(destino, dpi=200, bbox_inches="tight", facecolor="white")
        print(destino)
    plt.close(fig)


def diagrama_pipeline():
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 7)
    ax.axis("off")
    ax.set_title("Pipeline do projeto — Qualidade do Ar Inadequada (Mogi das Cruzes/SP)", fontsize=13, weight="bold")

    w, h = 3.0, 1.1
    etapas = [
        (0.5, 5.2, "Open-Meteo\nAir Quality + Weather\n(APIs)", "#cfe8ff"),
        (5.5, 5.2, "Coleta\nsrc/coleta/Coleta_Dados.py\n→ data/raw (JSON)", "#e6e6e6"),
        (10.5, 5.2, "Merge por horário\nsrc/transformacao/Merge_Dados.py\n→ data/interim (CSV)", "#e6e6e6"),
        (10.5, 3.4, "Alvo IQAr > 100 em t+1h\nCalcular_Alvo_IQAr.py\n(subíndices CETESB)", "#fff2cc"),
        (5.5, 3.4, "Split temporal\nvalidação expansiva 2024\nholdout 2025–2026", "#fff2cc"),
        (0.5, 3.4, "EDA e features\nFeatures_Temporais.py\n(médias 3h, deltas 2h)", "#fff2cc"),
        (0.5, 1.6, "Comparação de modelos\nvalidação 2024-Q4\nRandom Forest, limiar 0,3", "#d9f2d9"),
        (5.5, 1.6, "Avaliação final única\nholdout 2025–2026\n(não repetir)", "#f8d7da"),
        (10.5, 1.6, "Pipeline empacotado\nmodels/modelo_final_sprint5.joblib", "#d9f2d9"),
        (5.5, 0.1, "Previsão +1h (dados recentes)\nnotebooks/03_Previsao_\nProxima_Hora.ipynb", "#e8d9f2"),
    ]
    for x, y, t, c in etapas:
        _caixa(ax, x, y, w, h, t, c)

    _seta(ax, 3.5, 5.75, 5.5, 5.75)
    _seta(ax, 8.5, 5.75, 10.5, 5.75)
    _seta(ax, 12.0, 5.2, 12.0, 4.5)
    _seta(ax, 10.5, 3.95, 8.5, 3.95)
    _seta(ax, 5.5, 3.95, 3.5, 3.95)
    _seta(ax, 2.0, 3.4, 2.0, 2.7)
    _seta(ax, 3.5, 2.15, 5.5, 2.15)
    _seta(ax, 8.5, 2.15, 10.5, 2.15)
    _seta(ax, 12.0, 1.6, 8.5, 0.65)
    _salvar(fig, "diagrama_pipeline")


def diagrama_split():
    fig, ax = plt.subplots(figsize=(14, 4.5))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 5)
    ax.axis("off")
    ax.set_title("Split temporal por horário do evento (t+1h) — 04/08/2022 a 31/08/2026", fontsize=13, weight="bold")

    def faixa(x, w, y, texto, cor):
        ax.add_patch(plt.Rectangle((x, y), w, 0.55, facecolor=cor, edgecolor="#333333"))
        ax.text(x + w / 2, y + 0.27, texto, ha="center", va="center", fontsize=8)

    ax.text(0.1, 4.6, "Validação expansiva: cada fold treina com tudo que vem antes do trimestre validado", fontsize=9, weight="bold")
    x_val = [6.5, 8.1, 9.7, 11.3]
    for i, (xv, nome) in enumerate(zip(x_val, ["Q1", "Q2", "Q3", "Q4"])):
        yy = 3.9 - i * 0.65
        faixa(0.1, xv - 0.1, yy, f"treino do fold {i + 1} (2022-08 em diante)", "#cfe8ff")
        faixa(xv, 1.6, yy, f"valida 2024-{nome}", "#fff2cc")
    faixa(12.9, 1.0, 3.9 - 3 * 0.65, "holdout", "#f8d7da")

    ax.text(0.1, 0.5, "Holdout 2025-01-01 a 2026-08-31 (14.592 linhas, 161 positivos): consultado uma única vez, após congelar modelo e limiar.",
            fontsize=9, color="#a00000", weight="bold")
    _salvar(fig, "diagrama_split_temporal")


if __name__ == "__main__":
    diagrama_pipeline()
    diagrama_split()
