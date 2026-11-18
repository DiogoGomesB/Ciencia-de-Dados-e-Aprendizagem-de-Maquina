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
    fig, ax = plt.subplots(figsize=(15, 8.2))
    ax.set_xlim(-2.3, 14.2)
    ax.set_ylim(-0.2, 8.2)
    ax.axis("off")

    ax.text(
        -2.1, 7.85,
        "Arquitetura do Pipeline — Do Dado Bruto ao Alerta ao Vivo (Passo 1 ao 10)",
        fontsize=15, weight="bold", color="#0f172a", va="center",
    )
    ax.text(
        -2.1, 7.38,
        "Siga os números de 1 a 10: coletamos 35.736 horas na Open-Meteo, calculamos o IQAr oficial da CETESB, "
        "separamos passado e futuro sem vazamento e empacotamos o modelo.",
        fontsize=10, color="#334155", va="center",
    )

    fases = [
        (5.95, "FASE 1\nColeta e Junção", "#1e40af", "#dbeafe"),
        (4.05, "FASE 2\nAlvo CETESB e\nSplit Temporal", "#92400e", "#fef3c7"),
        (2.15, "FASE 3\nModelagem e\nTeste Cego", "#065f46", "#d1fae5"),
        (0.55, "FASE 4\nOperação", "#5b21b6", "#ede9fe"),
    ]
    for y_c, rotulo, cor_txt, cor_bg in fases:
        ax.add_patch(
            FancyBboxPatch(
                (-2.1, y_c - 0.52), 2.1, 1.04,
                boxstyle="round,pad=0.02,rounding_size=0.12",
                facecolor=cor_bg, edgecolor=cor_txt, linewidth=1.2,
            )
        )
        ax.text(-1.05, y_c, rotulo, ha="center", va="center", fontsize=9.2, weight="bold", color=cor_txt)

    w, h = 3.6, 1.22
    etapas = [
        (0.4, 5.34, "1. APIs Abertas Open-Meteo", "6 poluentes (CAMS) + 5 variáveis\nde clima (ERA5) em Mogi das Cruzes", "Sem chave paga (2022–2026)", "#cfe8ff", "#1e3a8a"),
        (5.2, 5.34, "2. Coleta Bruta Imutável", "Baixa as séries horárias e salva\nos arquivos originais sem editar", "Coleta_Dados.py → data/raw (JSON)", "#e2e8f0", "#1e293b"),
        (10.0, 5.34, "3. União por Horário (Merge)", "Junta poluentes e clima na mesma\nlinha de tempo (35.736 horas)", "Merge_Dados.py → data/interim (CSV)", "#e2e8f0", "#1e293b"),
        (10.0, 3.44, "4. Cálculo do IQAr (CETESB)", "Calcula os 6 subíndices oficiais e\ncria o alvo: IQAr > 100 em t+1h", "Calcular_Alvo_IQAr.py (2,53% alertas)", "#fff2cc", "#78350f"),
        (5.2, 3.44, "5. Split Temporal Estrito", "Passado treina (2022–2024: 21.121h)\nFuturo testa (2025–2026: 14.592h)", "Separacao_Temporal.py (sem sorteio)", "#fff2cc", "#78350f"),
        (0.4, 3.44, "6. Memória Curta (15 Features)", "Cria médias de 3h e variações de 2h\nde Ozônio e PM2,5 só até a hora t", "Features_Temporais.py (sem olhar t+1h)", "#fff2cc", "#78350f"),
        (0.4, 1.54, "7. Seleção na Validação (2024)", "Compara Baselines, Árvore, RF e\nXGBoost; congela RF + limiar 0,30", "Avaliar_Baselines.py (0 FN em 2024-Q4)", "#d9f2d9", "#064e3b"),
        (5.2, 1.54, "8. Prova Final Única (Holdout)", "Testa uma única vez em 2025–2026:\n98,14% Recall (158/161 alertas)", "Apenas 3 Falsos Negativos em 14.592h", "#f8d7da", "#7f1d1d"),
        (10.0, 1.54, "9. Modelo Empacotado", "Salva o Pipeline completo (mediana,\nescala, 300 árvores e limiar 0,30)", "models/modelo_final_sprint5.joblib", "#d9f2d9", "#064e3b"),
        (5.2, -0.06, "10. Previsão ao Vivo (Dashboard)", "Consulta a Open-Meteo agora e exibe\no alerta (+1h, +7h e +24h) na tela", "streamlit_app.py & Notebook", "#e8d9f2", "#4c1d95"),
    ]
    for x, y, titulo, meio, rodape, cor_fundo, cor_titulo in etapas:
        ax.add_patch(
            FancyBboxPatch(
                (x, y), w, h,
                boxstyle="round,pad=0.02,rounding_size=0.14",
                facecolor=cor_fundo, edgecolor="#334155", linewidth=1.3,
            )
        )
        ax.text(x + w / 2, y + h - 0.22, titulo, ha="center", va="center", fontsize=9.8, weight="bold", color=cor_titulo)
        ax.text(x + w / 2, y + h / 2 - 0.02, meio, ha="center", va="center", fontsize=8.5, color="#0f172a", linespacing=1.18)
        ax.text(x + w / 2, y + 0.17, rodape, ha="center", va="center", fontsize=7.8, color="#475569", style="italic")

    # Setas seguindo a ordem 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> 8 -> 9 -> 10
    _seta(ax, 4.0, 5.95, 5.2, 5.95)     # 1 -> 2
    _seta(ax, 8.8, 5.95, 10.0, 5.95)    # 2 -> 3
    _seta(ax, 11.8, 5.34, 11.8, 4.66)   # 3 -> 4
    _seta(ax, 10.0, 4.05, 8.8, 4.05)    # 4 -> 5
    _seta(ax, 5.2, 4.05, 4.0, 4.05)     # 5 -> 6
    _seta(ax, 2.2, 3.44, 2.2, 2.76)     # 6 -> 7
    _seta(ax, 4.0, 2.15, 5.2, 2.15)     # 7 -> 8
    _seta(ax, 8.8, 2.15, 10.0, 2.15)    # 8 -> 9
    _seta(ax, 11.8, 1.54, 8.8, 0.55)    # 9 -> 10
    _salvar(fig, "diagrama_pipeline")


def diagrama_split_explicado():
    """Versão completa e didática (infográfico alto) do split temporal, para apresentação e impressão."""
    import pandas as pd
    from matplotlib.patches import Rectangle

    inicio = pd.Timestamp("2022-08-04")
    fim = pd.Timestamp("2026-09-01")
    total_dias = (fim - inicio).days

    def px(data):
        """Converte uma data em posição horizontal (0 a 100) da linha do tempo."""
        return (pd.Timestamp(data) - inicio).days / total_dias * 100.0

    azul, amarelo, rosa, cinza = "#cfe8ff", "#fff2cc", "#f8d7da", "#ececec"
    borda = "#333333"

    fig, ax = plt.subplots(figsize=(16, 16.8))
    ax.set_xlim(-14, 103)
    ax.set_ylim(-5, 136)
    ax.axis("off")

    def bloco(x0, x1, y, h, cor, texto="", fs=10, hatch=None, cor_texto="#111111", peso="normal"):
        ax.add_patch(
            Rectangle((x0, y), x1 - x0, h, facecolor=cor, edgecolor=borda, linewidth=1.1, hatch=hatch)
        )
        if texto:
            ax.text((x0 + x1) / 2, y + h / 2, texto, ha="center", va="center",
                    fontsize=fs, color=cor_texto, weight=peso, linespacing=1.25)

    # ------------------------------------------------------------------ título
    ax.text(-14, 134.5, "Como dividimos os dados no tempo (split temporal)", fontsize=19, weight="bold", va="center")
    ax.text(-14, 130.6,
            "Objetivo do modelo: olhando para o ar de agora (hora t), prever se na hora seguinte (t+1h) "
            "o ar será inadequado, isto é, IQAr > 100.\n"
            "Cada hora com ar inadequado é chamada de \"alerta\". Dados: 04/08/2022 a 31/08/2026, uma linha por hora.",
            fontsize=11, va="center", color="#333333", linespacing=1.4)

    # ------------------------------------- O que é split temporal e para que serve
    ax.text(-14, 126.3, "O que é split temporal?", fontsize=14, weight="bold", va="center")
    ax.text(-14, 123.4,
            "É dividir os dados pela ordem do tempo: o passado treina o modelo e o futuro testa. "
            "Compare os dois jeitos de dividir (cada quadradinho é um bloco de horas):",
            fontsize=11, va="center", color="#333333")

    def quadrados(y, padrao):
        for i, tipo in enumerate(padrao):
            bloco(i * 2.4, (i + 1) * 2.4, y, 4.2, azul if tipo == "T" else rosa)

    # Jeito errado: sorteio aleatório mistura treino e teste
    padrao_errado = "TTPTTTPTTPTTTTPTTTPTTPTT"
    ax.text(-14, 118.9, "ERRADO:\nsorteio aleatório", fontsize=10, weight="bold", va="center", color="#a00000",
            linespacing=1.2)
    quadrados(116.8, padrao_errado)
    for i, hora in [(1, "14h"), (2, "15h"), (3, "16h")]:
        ax.text(i * 2.4 + 1.2, 115.3, hora, ha="center", va="center", fontsize=8.5, color="#555555")
    ax.text(62, 118.9,
            "O teste (rosa) fica misturado com o treino (azul). O modelo vê as 14h\n"
            "e as 16h e acerta a das 15h só copiando as horas vizinhas: é o\n"
            "vazamento de dados (data leakage). Parece ótimo, mas falha no uso real.",
            fontsize=9.6, va="center", color="#7a0000", linespacing=1.3)

    # Jeito certo: split temporal
    padrao_certo = "T" * 16 + "P" * 8
    ax.text(-14, 111.1, "CERTO:\nsplit temporal", fontsize=11, weight="bold", va="center", color="#0a6b2d",
            linespacing=1.2)
    quadrados(109.0, padrao_certo)
    ax.text(0, 107.4, "passado  →  futuro", ha="left", va="center", fontsize=8.5, color="#555555")
    ax.text(62, 111.1,
            "O teste (rosa) vem sempre depois do treino (azul), como no uso real:\n"
            "o modelo só conhece o passado e nunca vê o futuro. Foi isso que\n"
            "fizemos neste projeto.",
            fontsize=9.6, va="center", color="#0a4a20", linespacing=1.3)

    ax.text(-14, 105.0, "Para que serve?", fontsize=14, weight="bold", va="center")
    servicos = [
        ("Resultado honesto", "O teste imita o uso real:\no modelo só conhece o passado."),
        ("Evita vazamento de dados", "Impede que o modelo use informação\ndo futuro (ou de horas vizinhas)."),
        ("Prova de verdade", "Mostra se funciona com dados que ele\nnunca viu, como estudar com a prova\nantiga e fazer a prova nova."),
    ]
    for i, (tit, desc) in enumerate(servicos):
        x0 = -14 + i * 37.5
        bloco(x0, x0 + 36, 92.6, 9.4, "#e8f5e9")
        ax.text(x0 + 1.2, 99.6, tit, fontsize=11, weight="bold", va="center")
        ax.text(x0 + 1.2, 95.9, desc, fontsize=9.6, va="center", color="#333333", linespacing=1.25)

    # ---------------------------------------------- legenda em linguagem simples
    ax.text(-14, 89.3, "Como ler as cores (pense em estudar para uma prova):", fontsize=12, weight="bold", va="center")
    legenda = [
        (-14, azul, "TREINO = exercícios para estudar", "o modelo aprende o padrão\ncom horas do passado"),
        (23, amarelo, "VALIDAÇÃO = simulado", "testa e ajusta o modelo\n(escolha do modelo e do limiar)"),
        (60, rosa, "HOLDOUT = prova final", "dados guardados, abertos uma\núnica vez, só no fim"),
    ]
    for x0, cor, titulo, desc in legenda:
        bloco(x0, x0 + 35, 79.5, 7.2, cor)
        ax.text(x0 + 1.2, 84.6, titulo, fontsize=11, weight="bold", va="center")
        ax.text(x0 + 1.2, 81.7, desc, fontsize=10, va="center", color="#333333", linespacing=1.2)

    # ------------------------------------------------- 1) visão geral proporcional
    ax.text(-14, 74.6, "1) Visão geral: a linha do tempo completa (largura proporcional ao tempo)",
            fontsize=13, weight="bold", va="center")
    y0, h0 = 61.0, 7.5
    bloco(px("2022-08-04"), px("2024-01-01"), y0, h0, azul,
          "Só treino\nago/2022 a dez/2023", fs=10.5)
    bloco(px("2024-01-01"), px("2025-01-01"), y0, h0, amarelo,
          "2024\nvalidação em\n4 trimestres", fs=10.5)
    bloco(px("2025-01-01"), px("2026-09-01"), y0, h0, rosa,
          "HOLDOUT (prova final)\njan/2025 a ago/2026", fs=10.5, peso="bold")

    # chaves de contagem acima da barra
    ax.plot([px("2022-08-04"), px("2025-01-01") - 0.3], [70.2, 70.2], color=borda, linewidth=1.4)
    ax.text((px("2022-08-04") + px("2025-01-01")) / 2, 71.7,
            "Desenvolvimento (treino + validação): 21.121 horas, 743 alertas (3,52%)",
            ha="center", va="center", fontsize=10.5, weight="bold")
    ax.plot([px("2025-01-01") + 0.3, px("2026-09-01")], [70.2, 70.2], color="#a00000", linewidth=1.4)
    ax.text((px("2025-01-01") + px("2026-09-01")) / 2, 71.7,
            "Teste final: 14.592 horas, 161 alertas (1,10%)",
            ha="center", va="center", fontsize=10.5, weight="bold", color="#a00000")

    # eixo de datas
    for data, rotulo in [("2022-08-04", "04/08/2022"), ("2023-01-01", "2023"), ("2024-01-01", "2024"),
                         ("2025-01-01", "2025"), ("2026-01-01", "2026"), ("2026-09-01", "31/08/2026")]:
        ax.plot([px(data)] * 2, [y0 - 1.2, y0], color=borda, linewidth=1.1)
        ax.text(px(data), y0 - 2.6, rotulo, ha="center", va="center", fontsize=10)
    ax.annotate("", xy=(100, y0 - 4.6), xytext=(0, y0 - 4.6),
                arrowprops=dict(arrowstyle="-|>", color="#555555", linewidth=1.3))
    ax.text(50, y0 - 6.2, "tempo  (passado  →  futuro)", ha="center", va="center", fontsize=10, color="#555555")

    # --------------------------------------- 2) quatro rodadas de validação (2024)
    ax.text(-14, 50.8,
            "2) Como escolhemos o modelo: 4 rodadas de validação em 2024 (a cada rodada o treino cresce e o simulado avança)",
            fontsize=13, weight="bold", va="center")
    trimestres = [
        ("2024-Q1", "2024-01-01", "2024-04-01", "12.337 h (356 alertas)", "2.184 h (114 alertas)"),
        ("2024-Q2", "2024-04-01", "2024-07-01", "14.521 h (470 alertas)", "2.184 h (55 alertas)"),
        ("2024-Q3", "2024-07-01", "2024-10-01", "16.705 h (525 alertas)", "2.208 h (172 alertas)"),
        ("2024-Q4", "2024-10-01", "2025-01-01", "18.913 h (697 alertas)", "2.208 h (46 alertas)"),
    ]
    altura, passo, topo = 4.6, 8.4, 41.6
    for i, (nome, ini, fi, txt_treino, txt_val) in enumerate(trimestres):
        yy = topo - i * passo
        ax.text(-14, yy + altura / 2, f"Rodada {i + 1}", fontsize=11.5, weight="bold", va="center")
        bloco(px("2022-08-04"), px(ini), yy, altura, azul, "treino: tudo que veio antes", fs=10)
        bloco(px(ini), px(fi), yy, altura, amarelo, f"valida\n{nome}", fs=8.6)
        if nome != "2024-Q4":
            largura_gap = px("2025-01-01") - px(fi)
            texto_gap = "não usado\nnesta rodada" if largura_gap > 12 else ""
            bloco(px(fi), px("2025-01-01"), yy, altura, cinza, texto_gap, fs=8.6, cor_texto="#666666")
        bloco(px("2025-01-01"), px("2026-09-01"), yy, altura, rosa)
        ax.text((px("2025-01-01") + px("2026-09-01")) / 2, yy + altura / 2,
                "holdout: fechado, ninguém olha", ha="center", va="center", fontsize=9.8,
                color="#7a0000", weight="bold",
                bbox=dict(boxstyle="round,pad=0.25", facecolor="#fdf0f1", edgecolor="none"))
        ax.text(0, yy - 1.5,
                f"Treino: {txt_treino}   →   Validação: {txt_val}",
                fontsize=9.6, va="center", color="#333333")

    # --------------------------------------------- 3) regras que evitam "trapaça"
    ax.text(-14, 10.6, "3) As 4 regras que impedem o modelo de \"trapacear\"", fontsize=13, weight="bold", va="center")
    regras = [
        ("1. O passado treina,\no futuro testa",
         "Nunca usamos dados de depois\npara prever o que veio antes."),
        ("2. Nada de embaralhar",
         "As 15h parecem com as 14h e 16h.\nSorteando as horas o modelo\n\"decoraria\" a resposta."),
        ("3. Vale a hora do rótulo",
         "A linha das 23h de 31/12/2024\nprevê a 00h de 01/01/2025,\nentão vai para o teste,\nnão para o treino."),
        ("4. Holdout só uma vez",
         "Só abrimos depois de congelar\no modelo (Random Forest)\ne o limiar de alerta (0,30)."),
    ]
    larg = 28.0
    for i, (tit, txt) in enumerate(regras):
        x0 = -14 + i * (larg + 1.6)
        bloco(x0, x0 + larg, -4.4, 12.2, "#f6f6f6")
        ax.text(x0 + 1.0, 5.0, tit, fontsize=10.4, weight="bold", va="center", linespacing=1.1)
        ax.text(x0 + 1.0, -0.6, txt, fontsize=9.2, va="center", color="#333333", linespacing=1.2)

    _salvar(fig, "diagrama_split_temporal_explicado")


def diagrama_split():
    """Versão simples para o artigo: poucas palavras, fontes grandes, legível em tela de 800 px."""
    import pandas as pd
    from matplotlib.patches import Rectangle

    inicio = pd.Timestamp("2022-08-04")
    fim = pd.Timestamp("2026-09-01")
    total_dias = (fim - inicio).days

    def px(data):
        return (pd.Timestamp(data) - inicio).days / total_dias * 100.0

    azul, amarelo, rosa, cinza = "#cfe8ff", "#fff2cc", "#f8d7da", "#ececec"
    borda = "#333333"

    fig, ax = plt.subplots(figsize=(10, 5.4))
    ax.set_xlim(-15, 101)
    ax.set_ylim(-18, 66)
    ax.axis("off")

    def bloco(x0, x1, y, h, cor, texto="", fs=12, cor_texto="#111111", peso="normal"):
        ax.add_patch(Rectangle((x0, y), x1 - x0, h, facecolor=cor, edgecolor=borda, linewidth=1.2))
        if texto:
            ax.text((x0 + x1) / 2, y + h / 2, texto, ha="center", va="center",
                    fontsize=fs, color=cor_texto, weight=peso, linespacing=1.2)

    ax.text(-15, 63, "Split temporal: o passado treina, o futuro testa", fontsize=16, weight="bold", va="center")

    trimestres = [("Q1", "2024-01-01", "2024-04-01"), ("Q2", "2024-04-01", "2024-07-01"),
                  ("Q3", "2024-07-01", "2024-10-01"), ("Q4", "2024-10-01", "2025-01-01")]
    altura, passo, topo = 8.5, 12.5, 44.0
    for i, (nome, ini, fi) in enumerate(trimestres):
        yy = topo - i * passo
        ax.text(-15, yy + altura / 2, f"Rodada {i + 1}", fontsize=12, weight="bold", va="center")
        bloco(px("2022-08-04"), px(ini), yy, altura, azul, "treino", fs=12)
        bloco(px(ini), px(fi), yy, altura, amarelo, nome, fs=11.5)
        if px("2025-01-01") - px(fi) > 0.5:
            bloco(px(fi), px("2025-01-01"), yy, altura, cinza)
        bloco(px("2025-01-01"), px("2026-09-01"), yy, altura, rosa, "holdout (fechado)",
              fs=12, cor_texto="#7a0000", peso="bold")

    # eixo de datas
    y_eixo = topo - 3 * passo - 2.2
    for data, rotulo in [("2022-08-04", "ago/2022"), ("2024-01-01", "2024"),
                         ("2025-01-01", "2025"), ("2026-09-01", "ago/2026")]:
        ax.plot([px(data)] * 2, [y_eixo, y_eixo + 1.6], color=borda, linewidth=1.2)
        ax.text(px(data), y_eixo - 2.8, rotulo, ha="center", va="center", fontsize=11.5)
    ax.annotate("", xy=(100, y_eixo), xytext=(0, y_eixo),
                arrowprops=dict(arrowstyle="-|>", color="#555555", linewidth=1.3))
    ax.text(50, y_eixo - 7.4, "tempo (passado → futuro)", ha="center", va="center", fontsize=11.5, color="#555555")

    # legenda
    y_leg = -14.2
    itens = [(-15, azul, "Treino: o modelo aprende"), (22, amarelo, "Validação: ajusta (Q1 a Q4 de 2024)"),
             (72, rosa, "Holdout: prova final")]
    for x0, cor, texto in itens:
        ax.add_patch(Rectangle((x0, y_leg), 3.2, 4.2, facecolor=cor, edgecolor=borda, linewidth=1.1))
        ax.text(x0 + 4.4, y_leg + 2.1, texto, fontsize=10.8, va="center")

    _salvar(fig, "diagrama_split_temporal")


if __name__ == "__main__":
    diagrama_pipeline()
    diagrama_split()
    diagrama_split_explicado()
