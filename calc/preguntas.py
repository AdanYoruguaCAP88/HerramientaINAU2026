"""Las siete preguntas como salida central; las respuestas no exceden la evidencia."""
from dataclasses import dataclass, field
from .modelo import Estado
from .evaluador import EstadoSituacion
from .alternativas import EvaluacionAlternativa
from .evidencia import EvidenciaParaBrecha, buscar_evidencia, Experiencia

@dataclass
class RespuestaPregunta:
    numero: int
    pregunta: str
    respuesta: str
    estado: Estado
    sustentos: list[str] = field(default_factory=list)
    advertencias: list[str] = field(default_factory=list)

def responder_preguntas(estado: EstadoSituacion, alternativas: list[EvaluacionAlternativa] | None = None) -> list[RespuestaPregunta]:
    alternativas=alternativas or []
    out=[]
    negativas=[b for b in estado.brechas if b.diferencia is not None and b.diferencia<0]
    desconocidas=[b for b in estado.brechas if b.diferencia is None]
    incumplidas=[r for r in estado.restricciones if r.estado=="incumple"]
    if negativas or incumplidas:
        parts=[]
        if negativas: parts.append("insuficiencias calculadas: "+", ".join(f"{b.elemento} ({b.diferencia:+.1f} h/sem; requerimiento estimado)" for b in negativas))
        if incumplidas: parts.append("restricciones incumplidas: "+", ".join(r.id for r in incumplidas))
        if desconocidas: parts.append("dimensiones sin determinar: "+", ".join(b.elemento for b in desconocidas))
        out.append(RespuestaPregunta(1,"¿Cuál es exactamente el problema?","; ".join(parts),Estado.HIPOTESIS,[b.elemento for b in negativas]+[r.id for r in incumplidas],["Los requerimientos de personal proceden de extrapolación."]))
    elif desconocidas or estado.incertidumbres:
        out.append(RespuestaPregunta(1,"¿Cuál es exactamente el problema?","No puede determinarse por completo con los datos disponibles; hay dimensiones sin evaluar.",Estado.DESCONOCIDO,[b.elemento for b in desconocidas],["La ausencia de una brecha numérica no demuestra suficiencia."]))
    else:
        out.append(RespuestaPregunta(1,"¿Cuál es exactamente el problema?","No se detectan incumplimientos en las dimensiones evaluadas.",Estado.HIPOTESIS,advertencias=["Esto no demuestra suficiencia en dimensiones no evaluadas."]))
    out.append(RespuestaPregunta(2,"¿Qué recursos necesito para resolverlo?","; ".join(f"{r}: {h:.1f} h/sem estimadas" for r,h in estado.personal_requerido.items() if h>0) or "No hay requerimientos calculables.",Estado.HIPOTESIS,list(estado.personal_requerido),["Extrapolación de la configuración; validar la semántica de horas por unidad."]))
    if not estado.restricciones:
        out.append(RespuestaPregunta(3,"¿Qué restricciones tengo?","No se evaluaron restricciones.",Estado.DESCONOCIDO))
    else:
        out.append(RespuestaPregunta(3,"¿Qué restricciones tengo?","; ".join(f"{r.descripcion} ({r.estado})" for r in estado.restricciones),Estado.DESCONOCIDO if any(r.estado=="indeterminado" for r in estado.restricciones) else Estado.HIPOTESIS,[r.id for r in estado.restricciones]))
    if not alternativas:
        out.append(RespuestaPregunta(4,"¿Qué alternativas son viables?","No se declararon alternativas; no corresponde generar ni recomendar ninguna.",Estado.DESCONOCIDO))
    else:
        out.append(RespuestaPregunta(4,"¿Qué alternativas son viables?","; ".join(f"{a.alternativa.id}: {a.veredicto} — {a.motivo}" for a in alternativas),Estado.HIPOTESIS,[a.alternativa.id for a in alternativas],["Evaluable no equivale a viabilidad institucional demostrada."]))
    if not alternativas:
        out.append(RespuestaPregunta(5,"¿Qué consecuencias puede tener cada alternativa?","Sin alternativas declaradas, no hay consecuencias que comparar.",Estado.DESCONOCIDO))
    else:
        out.append(RespuestaPregunta(5,"¿Qué consecuencias puede tener cada alternativa?"," | ".join(f"{a.alternativa.id}: {a.comparacion.resumen}" for a in alternativas),Estado.HIPOTESIS,[a.alternativa.id for a in alternativas],["Son diferencias calculadas entre escenarios, no efectos observados ni causales."]))
    if estado.incertidumbres:
        out.append(RespuestaPregunta(6,"¿Qué información me falta?","; ".join(f"{i.variable} ({i.razon})" for i in estado.incertidumbres),Estado.DESCONOCIDO,[i.variable for i in estado.incertidumbres]))
    else:
        out.append(RespuestaPregunta(6,"¿Qué información me falta?","No se registraron incertidumbres; verificar que todas las dimensiones pertinentes estén modeladas.",Estado.HIPOTESIS))
    checks=[f"Verificar {i.variable}: {i.consecuencia}" for i in estado.incertidumbres]
    checks += [f"Revisar {r.id}: {r.descripcion}" for r in estado.restricciones if r.estado in {"incumple","indeterminado"}]
    out.append(RespuestaPregunta(7,"¿Qué debería verificar antes de intervenir?","; ".join(dict.fromkeys(checks)) if checks else "No hay verificaciones pendientes identificadas en las dimensiones modeladas.",Estado.DESCONOCIDO if checks else Estado.HIPOTESIS))
    return out

def responder_preguntas_con_evidencia(estado: EstadoSituacion, alternativas: list[EvaluacionAlternativa] | None = None, repositorio: list[Experiencia] | None = None, contexto_uruguay: dict | None = None) -> list[dict]:
    salida=[r.__dict__.copy() for r in responder_preguntas(estado,alternativas)]
    if not repositorio: return salida
    evidencia=buscar_evidencia(estado,repositorio,contexto_uruguay)
    for r in salida:
        if r["numero"]==4 and evidencia:
            bloques=[]
            for e in evidencia:
                if e.sin_evidencia_suficiente: bloques.append(f"[{e.brecha_elemento}] Sin evidencia documentada: {e.mensaje_ausencia}")
                else:
                    for p in e.experiencias_relevantes[:3]:
                        bloques.append(f"[{e.brecha_elemento}] {p.experiencia_id}: pertinencia {p.puntaje:.2f} — {', '.join(p.razones[:2])}")
            r["respuesta"] += " | Evidencia recuperada (no recomendación): " + " || ".join(bloques)
        if r["numero"]==6:
            missing=[]
            for e in evidencia:
                if e.sin_evidencia_suficiente: missing.append(f"Sin experiencia documentada para {e.brecha_elemento}")
                for p in e.experiencias_relevantes: missing.extend(p.informacion_faltante)
            if missing: r["respuesta"] += " | Faltantes de evidencia: " + " || ".join(dict.fromkeys(missing))
    return salida

def bloque_evidencia_markdown(evidencia: list[EvidenciaParaBrecha]) -> str:
    lines=["## Evidencia internacional recuperada",""]
    if not evidencia: return "\n".join(lines+["_No se recuperó evidencia del repositorio para esta situación._"])
    for e in evidencia:
        lines += [f"### {e.brecha_elemento} ({e.dimension})",f"**Dimensiones a investigar:** {', '.join(e.problemas_a_investigar)}"]
        if e.sin_evidencia_suficiente: lines.append(f"⚠ **{e.mensaje_ausencia}**")
        else:
            for p in e.experiencias_relevantes:
                lines.append(f"- **{p.experiencia_id}** (pertinencia {p.puntaje:.2f}; estado {p.estado.value})")
                lines.extend(f"  - {x}" for x in p.razones)
                if p.diferencias_contextuales: lines.append("  - Diferencias: "+"; ".join(p.diferencias_contextuales))
                if p.informacion_faltante: lines.append("  - Faltantes: "+"; ".join(p.informacion_faltante))
        lines.append("")
    return "\n".join(lines)
