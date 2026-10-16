"""CLI v0.3: situación + alternativas + repositorio → informe estructurado."""
import argparse
import json
from pathlib import Path
from .config import cargar_config, cargar_escenario
from .situacion import Situacion, GrupoAtendido, PersonalDisponible, RecursosMateriales, Alternativa
from .evaluador import evaluar_situacion
from .alternativas import evaluar_alternativa
from .evidencia import cargar_repositorio
from .preguntas import responder_preguntas_con_evidencia
from .informe import escribir_informe


def _situacion_desde_json(d: dict) -> Situacion:
    return Situacion(
        id=d["id"], ubicacion=d.get("ubicacion", ""), origen=d.get("origen", "observada"),
        poblacion_ninos=d.get("poblacion_ninos", 0),
        grupos=[GrupoAtendido(**g) for g in d.get("grupos", [])],
        personal_disponible=[PersonalDisponible(**p) for p in d.get("personal_disponible", [])],
        recursos_materiales=[RecursosMateriales(**r) for r in d.get("recursos_materiales", [])],
        presupuesto_disponible_ur=d.get("presupuesto_disponible_ur"),
        problema_declarado=d.get("problema_declarado"), notas=d.get("notas", []), fecha=d.get("fecha"),
    )


def _alternativa_desde_json(d: dict) -> Alternativa:
    return Alternativa(id=d["id"], descripcion=d["descripcion"],
        situacion_propuesta=_situacion_desde_json(d["situacion_propuesta"]),
        autor=d.get("autor", "usuario"), notas=d.get("notas", []))


def main() -> int:
    ap = argparse.ArgumentParser(prog="calc")
    ap.add_argument("--config", required=True)
    ap.add_argument("--situacion", required=True)
    ap.add_argument("--alternativas", default=None)
    ap.add_argument("--repositorio", default="repositorio/experiencias.json")
    ap.add_argument("--escenario", default=None)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    cfg = cargar_config(args.config)
    esc = cargar_escenario(args.escenario) if args.escenario else {}
    sit_json = json.loads(Path(args.situacion).read_text(encoding="utf-8"))
    situacion = _situacion_desde_json(sit_json)
    estado_base = evaluar_situacion(situacion, cfg, esc)
    alternativas_eval = []
    if args.alternativas:
        alts_json = json.loads(Path(args.alternativas).read_text(encoding="utf-8"))
        # Acepta tanto una lista como un objeto con clave "alternativas".
        if isinstance(alts_json, dict):
            alts_json = alts_json.get("alternativas", [])
        for a in alts_json:
            alt = _alternativa_desde_json(a)
            alternativas_eval.append(evaluar_alternativa(alt, cfg, estado_base, esc))
    repositorio = cargar_repositorio(args.repositorio) if Path(args.repositorio).exists() else []
    respuestas = responder_preguntas_con_evidencia(estado_base, alternativas_eval, repositorio)
    escribir_informe(args.out, estado_base, alternativas_eval, respuestas)
    print(f"Estado global: {estado_base.estado_global}")
    print(f"Brechas negativas: {len([b for b in estado_base.brechas if b.diferencia is not None and b.diferencia < 0])}")
    print(f"Alternativas evaluadas: {len(alternativas_eval)}")
    print(f"Experiencias en repositorio: {len(repositorio)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
