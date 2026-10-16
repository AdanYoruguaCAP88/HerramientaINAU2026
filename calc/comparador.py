"""Comparación descriptiva entre estados; no infiere causalidad ni aprendizaje."""
from dataclasses import dataclass
from .evaluador import EstadoSituacion

@dataclass
class DeltaDimension:
    elemento: str
    base: float | None
    alterno: float | None
    diferencia: float | None
    estado: str = "calculado"

@dataclass
class Comparacion:
    base_id: str
    alterno_id: str
    deltas_personal: list[DeltaDimension]
    deltas_brechas: list[DeltaDimension]
    deltas_costo_ur: float | None
    restricciones_nuevas: list[str]
    restricciones_resueltas: list[str]
    incertidumbres_nuevas: list[str]
    incertidumbres_resueltas: list[str]
    resumen: str = ""

def _delta(base, alt):
    out=[]
    for k in sorted(set(base)|set(alt)):
        b,a=base.get(k),alt.get(k)
        diff=(a-b) if isinstance(a,(int,float)) and isinstance(b,(int,float)) else None
        estado="calculado" if diff is not None else ("falta_base" if b is None else "falta_alternativa" if a is None else "no_numerico")
        out.append(DeltaDimension(k,b,a,diff,estado))
    return out

def comparar(base: EstadoSituacion, alterno: EstadoSituacion) -> Comparacion:
    dp=_delta(base.personal_disponible,alterno.personal_disponible)
    db=_delta({b.elemento:b.diferencia for b in base.brechas},{b.elemento:b.diferencia for b in alterno.brechas})
    rb={r.id for r in base.restricciones if r.estado=="incumple"}
    ra={r.id for r in alterno.restricciones if r.estado=="incumple"}
    ib={i.variable for i in base.incertidumbres}; ia={i.variable for i in alterno.incertidumbres}
    cb=base.costos.get("transferencia_mensual_ur"); ca=alterno.costos.get("transferencia_mensual_ur")
    dc=(ca-cb) if isinstance(ca,(int,float)) and isinstance(cb,(int,float)) else None
    cambios=sum(1 for d in dp if d.diferencia not in (None,0))
    return Comparacion(base.situacion_id,alterno.situacion_id,dp,db,dc,sorted(ra-rb),sorted(rb-ra),sorted(ia-ib),sorted(ib-ia),
      f"Comparación descriptiva {base.situacion_id} → {alterno.situacion_id}: {cambios} cambios numéricos en personal. La transferencia comparada es un parámetro de configuración, no un costo específico de la alternativa.")
