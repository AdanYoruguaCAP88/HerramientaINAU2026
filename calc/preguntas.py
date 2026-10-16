"""Extensión de preguntas para incorporar evidencia documentada."""
from .evaluador import EstadoSituacion
from .alternativas import EvaluacionAlternativa
from .evidencia import EvidenciaParaBrecha, buscar_evidencia, Experiencia


def responder_preguntas_con_evidencia(
    estado: EstadoSituacion,
    alternativas: list[EvaluacionAlternativa] | None = None,
    repositorio: list[Experiencia] | None = None,
    contexto_uruguay: dict | None = None,
) -> list[dict]:
    from .preguntas import responder_preguntas
    respuestas_base = responder_preguntas(estado, alternativas)
    salida = [r.__dict__ for r in respuestas_base]
    if not repositorio:
        return salida
    evidencia = buscar_evidencia(estado, repositorio, contexto_uruguay)
    for r in salida:
        if r["numero"] == 4:
            if evidencia:
                bloques = []
                for e in evidencia:
                    if e.sin_evidencia_suficiente:
                        bloques.append(f"[{e.brecha_elemento}] Sin evidencia documentada: {e.mensaje_ausencia}")
                    else:
                        for p in e.experiencias_relevantes[:3]:
                            bloques.append(f"[{e.brecha_elemento}] Experiencia '{p.experiencia_id}': pertinencia {p.puntaje:.2f} — {', '.join(p.razones[:2])}")
                r["respuesta"] += " | Mecanismos documentados: " + " || ".join(bloques)
            break
    for r in salida:
        if r["numero"] == 6:
            faltantes = []
            for e in evidencia:
                if e.sin_evidencia_suficiente:
                    faltantes.append(f"Sin experiencia documentada para {e.brecha_elemento}")
                for p in e.experiencias_relevantes:
                    faltantes.extend(p.informacion_faltante)
            if faltantes:
                r["respuesta"] += " | Faltantes de evidencia: " + " || ".join(set(faltantes))
            break
    return salida


def bloque_evidencia_markdown(evidencia: list[EvidenciaParaBrecha]) -> str:
    lineas = ["## Evidencia internacional recuperada", ""]
    if not evidencia:
        lineas.append("_No se recuperó evidencia del repositorio para esta situación._")
        return "\n".join(lineas)
    for e in evidencia:
        lineas.append(f"### {e.brecha_elemento} ({e.dimension})")
        lineas.append(f"**Dimensiones a investigar:** {', '.join(e.problemas_a_investigar)}")
        if e.sin_evidencia_suficiente:
            lineas.append(f"⚠ **{e.mensaje_ausencia}**")
        else:
            for p in e.experiencias_relevantes:
                lineas.append(f"- **{p.experiencia_id}** (pertinencia {p.puntaje:.2f})")
                lineas.extend(f"  - {raz}" for raz in p.razones)
                if p.diferencias_contextuales:
                    lineas.append(f"  - Diferencias: {'; '.join(p.diferencias_contextuales)}")
                if p.informacion_faltante:
                    lineas.append(f"  - Faltantes: {'; '.join(p.informacion_faltante)}")
        lineas.append("")
    return "\n".join(lineas)
