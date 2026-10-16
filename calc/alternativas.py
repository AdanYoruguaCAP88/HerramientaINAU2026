"""Evaluación de alternativas declaradas por el responsable; no genera ni recomienda."""
from dataclasses import dataclass, field
from .situacion import Alternativa
from .evaluador import EstadoSituacion, evaluar_situacion
from .comparador import comparar, Comparacion

@dataclass
class EvaluacionAlternativa:
    alternativa: Alternativa
    estado: EstadoSituacion
    comparacion: Comparacion
    veredicto: str
    motivo: str
    condiciones_requeridas: list[str] = field(default_factory=list)

def evaluar_alternativa(alt: Alternativa, config: dict, estado_base: EstadoSituacion, escenario: dict | None = None) -> EvaluacionAlternativa:
    estado=evaluar_situacion(alt.situacion_propuesta,config,escenario)
    comp=comparar(estado_base,estado)
    if any(r.estado=="incumple" and r.id.startswith("R3") for r in estado.restricciones):
        veredicto,motivo="viola_invariante","Se detecta una insuficiencia frente al requerimiento calculado; el requerimiento requiere validación."
    elif any(r.estado=="incumple" for r in estado.restricciones):
        veredicto,motivo="viola_restriccion","Se detecta una restricción incumplida según la configuración."
    elif any(r.estado=="indeterminado" for r in estado.restricciones) or estado.estado_global=="INDETERMINADO":
        veredicto,motivo="no_evaluable","Hay restricciones o dimensiones relevantes que no pueden evaluarse con los datos disponibles."
    else:
        veredicto,motivo="evaluable","La alternativa se pudo evaluar frente a las reglas y datos disponibles; esto no demuestra viabilidad institucional."
    condiciones=[]
    for b in estado.brechas:
        if b.diferencia is not None and b.diferencia<0:
            condiciones.append(f"Déficit calculado de {abs(b.diferencia):.1f} h/sem para '{b.elemento}' (requerimiento estimado).")
        elif b.diferencia is None:
            condiciones.append(f"Declarar/verificar datos para '{b.elemento}'.")
    if estado.costos.get("conversion_pesos") is None:
        condiciones.append("No se puede convertir la transferencia declarada a pesos sin valor de UR.")
    return EvaluacionAlternativa(alt,estado,comp,veredicto,motivo,condiciones)
