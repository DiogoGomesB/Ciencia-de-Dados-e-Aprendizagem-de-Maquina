"""Treina e empacota o modelo/limiar congelado usando somente dados de treino."""

from pathlib import Path

import joblib
import pandas as pd
import yaml

from src.modelagem.Avaliar_Baselines import (
    FEATURES_SPRINT4,
    criar_pipeline_sprint4,
)
from src.modelagem.Avaliar_Modelo_Final_Sprint5 import (
    LIMIAR_FINAL_CONGELADO,
    MODELO_FINAL_CONGELADO,
)
from src.modelagem.Comparar_Modelos_Sprint5 import _classificadores_novos
from src.transformacao.Calcular_Alvo_IQAr import COLUNA_ALVO
from src.transformacao.Features_Temporais import adicionar_resumos_curto_prazo
from src.validacao.Separacao_Temporal import separar_teste_final


def treinar_modelo_final(
    dados: pd.DataFrame,
    inicio_teste: str,
    fim_teste: str,
    horizonte_horas: int = 1,
) -> dict:
    """Ajusta o pipeline final no treino temporal e retorna seus metadados."""
    dados_temporais = adicionar_resumos_curto_prazo(
        dados,
        ("ozone", "pm2_5"),
    )
    dados_temporais["event_time"] = pd.to_datetime(
        dados_temporais["time"],
        errors="raise",
    ) + pd.Timedelta(hours=horizonte_horas)
    treino, _ = separar_teste_final(
        dados_temporais,
        inicio_teste,
        fim_teste,
        horizonte_horas,
    )
    try:
        classificador = _classificadores_novos()[MODELO_FINAL_CONGELADO]
    except KeyError as exc:
        raise RuntimeError(
            f"Classificador congelado '{MODELO_FINAL_CONGELADO}' não está configurado."
        ) from exc
    pipeline = criar_pipeline_sprint4(classificador)
    pipeline.fit(treino[list(FEATURES_SPRINT4)], treino[COLUNA_ALVO].astype(int))
    return {
        "artifact_version": 1,
        "model_name": MODELO_FINAL_CONGELADO,
        "pipeline": pipeline,
        "features": list(FEATURES_SPRINT4),
        "decision_threshold": LIMIAR_FINAL_CONGELADO,
        "training_rows": len(treino),
        "training_event_time_before": inicio_teste,
        "target_horizon_hours": horizonte_horas,
    }


def main() -> None:
    with Path("config/params.yaml").open("r", encoding="utf-8") as arquivo:
        config = yaml.safe_load(arquivo)
    periodo = {
        "start_date": config["collection"]["start_date"],
        "end_date": config["collection"]["end_date"],
    }
    caminho_dados = (
        Path(config["paths"]["interim_data"])
        / config["paths"]["labeled_filename"].format(**periodo)
    )
    dados = pd.read_csv(caminho_dados, parse_dates=["time"])
    evaluation = config["evaluation"]
    artefato = treinar_modelo_final(
        dados,
        evaluation["final_test"]["start"],
        evaluation["final_test"]["end"],
        evaluation["target_horizon_hours"],
    )
    pasta_modelos = Path("models")
    pasta_modelos.mkdir(parents=True, exist_ok=True)
    caminho_modelo = pasta_modelos / "modelo_final_sprint5.joblib"
    joblib.dump(artefato, caminho_modelo)
    print(
        f"Modelo empacotado em {caminho_modelo}; "
        f"{artefato['training_rows']} linhas de treino; "
        f"limiar congelado {artefato['decision_threshold']:.1f}."
    )


if __name__ == "__main__":
    main()
