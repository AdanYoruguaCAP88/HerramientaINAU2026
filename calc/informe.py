"""Serialización del estado, alternativas y siete preguntas a Markdown y JSON."""
import json
from pathlib import Path
from dataclasses import asdict, is_dataclass
from enum import Enum
from .evaluador import EstadoSituacion
from .alternativas import EvaluacionAlternativa

def _jsonable(value):
    if isinstance(value, Enum): return value.value
    if is_dataclass(value): return {k:_jsonable(v) for k,v in asdict(value).items()}
    if isinstance(value, dict): return {k:_jsonable(v) for k,v in value.items()}
    if isinstance(value, (list,tuple)): return [_jsonable(v) for v in value]
    return value

def _estado_a_dict(e: EstadoSituacion):
    return _jsonable(e)

def _alt_a_dict(a: EvaluacionAlternativa):
    return {"id":a.alternativa.id,"descripcion":a.alternativa.descripcion,"veredicto":a.veredicto,"motivo":a.motivo,"condiciones_requeridas":a.condiciones_requeridas,"estado":_estado_a_dict(a.estado),"comparacion":_jsonable(a.comparacion)}

def escribir_informe(carpeta, estado_base, alternativas, respuestas):
    folder=Path(carpeta); folder.mkdir(parents=True,exist_ok=True)
    payload={"estado_base":_estado_a_dict(estado_base),"alternativas":[_alt_a_dict(a) for a in alternativas],"preguntas":[_jsonable(r) for r in respuestas]}
    (folder/"informe.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    lines=["# Informe estructurado de situación","",f"**Situación:** `{estado_base.situacion_id}` ({estado_base.origen})",f"**Estado global:** `{estado_base.estado_global}`","",
      "## Las 7 preguntas",""]
    for r in respuestas:
        d=_jsonable(r)
        lines += [f"### {d['numero']}. {d['pregunta']}",d["respuesta"],f"**Estado epistemológico:** `{d['estado']}`"]
        if d.get("sustentos"): lines.append("**Sustentos:** "+", ".join(d["sustentos"]))
        lines += ["- ⚠ "+x for x in d.get("advertencias",[])]
        lines.append("")
    if alternativas:
        lines += ["## Alternativas evaluadas",""]
        for a in alternativas:
            lines += [f"### {a.alternativa.id}",a.alternativa.descripcion,f"**Clasificación:** `{a.veredicto}` — {a.motivo}"]
            lines += ["- "+x for x in a.condiciones_requeridas]; lines.append("")
    lines += ["## Integridad y limitaciones","",f"- Niños declarados: {estado_base.capacidad.get('poblacion_declarada')}",f"- Suma de grupos: {estado_base.capacidad.get('ninos_totales')}",f"- Grupos: {estado_base.capacidad.get('grupos')}","",
              "### Advertencias"]
    lines += ["- "+x for x in estado_base.advertencias] or ["- Sin advertencias de cálculo registradas."]
    lines += ["","### Incertidumbres"]
    lines += [f"- **{i.variable}** ({i.razon}): {i.consecuencia}" for i in estado_base.incertidumbres] or ["- No registradas."]
    (folder/"informe.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
