from collections.abc import Mapping, Sequence
from pathlib import Path

import pandas as pd
import yaml

from src.transformacao.Calcular_Alvo_IQAr import COLUNA_ALVO


def _preparar_dados(
    dados: pd.DataFrame,
    horizonte_horas: int,
) -> tuple[pd.Series, pd.Series]:
    colunas_necessarias = {"time", COLUNA_ALVO}
    ausentes = colunas_necessarias.difference(dados.columns)
    if ausentes:
        raise ValueError(
            f"Colunas necessárias ausentes para a separação temporal: {sorted(ausentes)}"
        )
    if horizonte_horas <= 0:
        raise ValueError("O horizonte deve ser um número positivo de horas.")

    tempos = pd.to_datetime(dados["time"], errors="raise")
    if tempos.isna().any():
        raise ValueError("A coluna 'time' contém timestamps ausentes.")
    if tempos.duplicated().any():
        raise ValueError("A coluna 'time' contém timestamps duplicados.")
    if not tempos.is_monotonic_increasing:
        raise ValueError("Os timestamps devem estar em ordem cronológica crescente.")
    if not tempos.diff().iloc[1:].eq(pd.Timedelta(hours=1)).all():
        raise ValueError(
            "A série deve conter timestamps consecutivos, com intervalo de 1 hora."
        )
    if tempos.dt.tz is not None:
        raise ValueError(
            "Os timestamps devem usar o horário local sem informação de fuso."
        )

    alvo = pd.to_numeric(dados[COLUNA_ALVO], errors="raise")
    rotulos_definidos = alvo.dropna()
    if not rotulos_definidos.isin((0, 1)).all():
        raise ValueError(f"A coluna '{COLUNA_ALVO}' deve conter apenas 0, 1 ou nulos.")

    horario_alvo = tempos + pd.Timedelta(hours=horizonte_horas)
    return horario_alvo, alvo


def _ler_limites(inicio: str, fim: str) -> tuple[pd.Timestamp, pd.Timestamp]:
    horario_inicio = pd.Timestamp(inicio)
    horario_fim = pd.Timestamp(fim)
    if pd.isna(horario_inicio) or pd.isna(horario_fim):
        raise ValueError("Os limites temporais não podem ser ausentes.")
    if horario_inicio.tz is not None or horario_fim.tz is not None:
        raise ValueError("Os limites temporais devem ser informados sem fuso horário.")
    if horario_inicio != horario_inicio.floor("h") or horario_fim != horario_fim.floor("h"):
        raise ValueError("Os limites temporais devem coincidir com o início de uma hora.")
    if horario_inicio >= horario_fim:
        raise ValueError("O início do período deve ser anterior ao fim.")
    return horario_inicio, horario_fim


def criar_folds_temporais(
    dados: pd.DataFrame,
    folds: Sequence[Mapping[str, str]],
    horizonte_horas: int = 1,
) -> dict[str, tuple[pd.DataFrame, pd.DataFrame]]:
    """Cria folds expansivos usando o instante do rótulo, não o da feature."""
    if not folds:
        raise ValueError("É necessário configurar ao menos um fold de validação.")

    horario_alvo, alvo = _preparar_dados(dados, horizonte_horas)
    folds_lidos: list[tuple[str, pd.Timestamp, pd.Timestamp]] = []
    nomes: set[str] = set()

    for fold in folds:
        nome = fold["name"]
        if not nome or nome in nomes:
            raise ValueError("Os nomes dos folds devem ser únicos e não vazios.")
        inicio, fim = _ler_limites(fold["start"], fold["end"])
        if folds_lidos and inicio < folds_lidos[-1][2]:
            raise ValueError("Os períodos de validação devem estar ordenados e não sobrepostos.")
        nomes.add(nome)
        folds_lidos.append((nome, inicio, fim))

    rotulos_definidos = alvo.notna()
    resultado: dict[str, tuple[pd.DataFrame, pd.DataFrame]] = {}
    for nome, inicio, fim in folds_lidos:
        mascara_treino = rotulos_definidos & horario_alvo.lt(inicio)
        mascara_validacao = (
            rotulos_definidos & horario_alvo.ge(inicio) & horario_alvo.lt(fim)
        )
        treino = dados.loc[mascara_treino].copy()
        validacao = dados.loc[mascara_validacao].copy()
        if treino.empty or validacao.empty:
            raise ValueError(f"O fold '{nome}' não possui treino ou validação.")
        resultado[nome] = (treino, validacao)

    return resultado


def separar_teste_final(
    dados: pd.DataFrame,
    inicio_teste: str,
    fim_teste: str,
    horizonte_horas: int = 1,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Separa o treino final e o teste pela data do evento rotulado."""
    inicio, fim = _ler_limites(inicio_teste, fim_teste)
    horario_alvo, alvo = _preparar_dados(dados, horizonte_horas)
    rotulos_definidos = alvo.notna()

    if (rotulos_definidos & horario_alvo.ge(fim)).any():
        raise ValueError(
            "Há rótulos definidos fora do período de teste configurado; revise os limites."
        )

    mascara_treino = rotulos_definidos & horario_alvo.lt(inicio)
    mascara_teste = rotulos_definidos & horario_alvo.ge(inicio) & horario_alvo.lt(fim)
    treino = dados.loc[mascara_treino].copy()
    teste = dados.loc[mascara_teste].copy()
    if treino.empty or teste.empty:
        raise ValueError("O período configurado não possui treino ou teste.")
    return treino, teste


def _imprimir_resumo(nome: str, dados: pd.DataFrame) -> None:
    positivos = int(pd.to_numeric(dados[COLUNA_ALVO]).eq(1).sum())
    negativos = len(dados) - positivos
    taxa_positiva = positivos / len(dados)
    print(
        f"{nome}: {len(dados)} linhas; {positivos} positivos; "
        f"{negativos} negativos; taxa positiva {taxa_positiva:.2%}"
    )


def main() -> None:
    with Path("config/params.yaml").open("r", encoding="utf-8") as arquivo:
        config = yaml.safe_load(arquivo)

    periodo = {
        "start_date": config["collection"]["start_date"],
        "end_date": config["collection"]["end_date"],
    }
    paths = config["paths"]
    caminho_dados = (
        Path(paths["interim_data"])
        / paths["labeled_filename"].format(**periodo)
    )
    dados = pd.read_csv(caminho_dados)
    evaluation = config["evaluation"]
    horizonte_horas = evaluation["target_horizon_hours"]

    folds = criar_folds_temporais(
        dados,
        evaluation["validation_folds"],
        horizonte_horas,
    )
    for nome, (treino, validacao) in folds.items():
        _imprimir_resumo(f"{nome} — treino expansivo", treino)
        _imprimir_resumo(f"{nome} — validação", validacao)

    treino_final, teste_final = separar_teste_final(
        dados,
        evaluation["final_test"]["start"],
        evaluation["final_test"]["end"],
        horizonte_horas,
    )
    _imprimir_resumo("Treino final", treino_final)
    _imprimir_resumo("Teste final", teste_final)


if __name__ == "__main__":
    main()
