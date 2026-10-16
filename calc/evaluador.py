"""Evaluador de situaciones: conserva por separado estado operativo y epistemológico."""
from dataclasses import dataclass, field
from typing import Any, Optional
import math
from .modelo import Estado, Resultado, Variable, Tipo, calcular_estado_resultado
from .situacion import Situacion, GrupoAtendido

@dataclass
class Brecha:
    dimension: str
    elemento: str
    requerido: Optional[float]
    disponible: Optional[float]
    diferencia: Optional[float]
    estado: Estado
    motivo: Optional[str] = None
    estado_operativo: str = "indeterminado"

@dataclass
class Restriccion:
    id: str
    descripcion: str
    estado: str
    valor_observado: Any
    valor_normativo: Any
    motivo: str
    fuente: Optional[str] = None

@dataclass
class Incertidumbre:
    variable: str
    estado: Estado
    razon: str
    consecuencia: str

@dataclass
class EstadoSituacion:
    situacion_id: str
    origen: str
    capacidad: dict
    personal_requerido: dict
    personal_disponible: dict
    brechas: list[Brecha]
    restricciones: list[Restriccion]
    recursos: dict
    costos: dict
    incertidumbres: list[Incertidumbre]
    estado_global: str
    advertencias: list[str] = field(default_factory=list)

def _unidad_para_grupo(grupo: GrupoAtendido, config: dict):
    for u in config.get("unidades_atencion", []):
        uid = u.get("id")
        if grupo.edad == 0 and grupo.modalidad == "EO" and uid == "EO":
            return u
        if 1 <= grupo.edad <= 3 and uid == f"{grupo.edad}A_{grupo.modalidad}":
            return u
    return None

def _horas_requeridas_por_rol(situacion: Situacion, config: dict) -> Resultado:
    roles = set(config.get("roles_por_grupo", []))
    totales = {rol: 0.0 for rol in roles}
    advertencias, sin_match = [], []
    for g in situacion.grupos:
        u = _unidad_para_grupo(g, config)
        if u is None:
            sin_match.append(g.id)
            continue
        max_por_grupo = u.get("ninos_por_grupo_max")
        grupos_modelo = u.get("grupos")
        if not isinstance(max_por_grupo, (int, float)) or max_por_grupo <= 0 or not isinstance(grupos_modelo, (int, float)) or grupos_modelo <= 0:
            sin_match.append(g.id)
            advertencias.append(f"Unidad {u.get('id')} sin parámetros válidos para extrapolar horas.")
            continue
        # Las horas config se interpretan como total de la unidad modelo:
        # escala por fracción de un grupo equivalente, no por unidad completa.
        factor = g.ninos / (max_por_grupo * grupos_modelo)
        for rol in roles:
            totales[rol] += float(u.get("horas_semana_total_unidad", {}).get(rol, 0)) * factor
    for rol, horas in config.get("roles_fijos_horas_semana", {}).items():
        totales[rol] = totales.get(rol, 0.0) + float(horas)
    if sin_match:
        advertencias.append(f"Grupos sin unidad aplicable o parámetros válidos: {sin_match}")
    var = Variable(id="horas_requeridas", definicion="Horas semanales por rol estimadas desde la unidad de referencia", valor=totales, unidad="horas_semana", tipo=Tipo.OPERATIVA, estado=Estado.HIPOTESIS, limitaciones="Extrapolación proporcional; requiere validación metodológica.")
    return Resultado(valor=totales, variables_usadas=[var], advertencias=advertencias, estado_resultado=calcular_estado_resultado([var]))

def _personal_disponible_dict(situacion: Situacion):
    totales = {}
    for p in situacion.personal_disponible:
        if p.rol in totales:
            totales[p.rol] += float(p.horas_semana)
        else:
            totales[p.rol] = float(p.horas_semana)
    return totales

def _calcular_brechas(requerido: dict, disponible: dict) -> list[Brecha]:
    out = []
    for rol in sorted(set(requerido) | set(disponible)):
        req, disp = requerido.get(rol), disponible.get(rol)
        if req is None:
            out.append(Brecha("personal", rol, None, disp, None, Estado.DESCONOCIDO, "Rol disponible no contemplado en la configuración", "indeterminado")); continue
        if disp is None:
            out.append(Brecha("personal", rol, req, None, None, Estado.DESCONOCIDO, "No hay personal declarado para este rol", "indeterminado")); continue
        delta = disp - req
        if delta < 0:
            operativo = "incumple"
        elif req > 0 and delta < req * 0.10:
            operativo = "cerca"
        else:
            operativo = "cumple"
        # El requerimiento procede de una extrapolación: la diferencia no es V.
        out.append(Brecha("personal", rol, req, disp, delta, Estado.HIPOTESIS, "Diferencia calculada contra requerimiento extrapolado", operativo))
    return out

def _evaluar_restricciones(situacion, config, brechas):
    out = []
    total_grupos = sum(g.ninos for g in situacion.grupos)
    if total_grupos != situacion.poblacion_ninos:
        out.append(Restriccion("R0_POBLACION", "Población declarada coincide con la suma de los grupos", "indeterminado", {"poblacion_declarada": situacion.poblacion_ninos, "suma_grupos": total_grupos}, "valores iguales", "Inconsistencia entre dos campos de entrada; debe corregirla el responsable."))
    for g in situacion.grupos:
        u = _unidad_para_grupo(g, config)
        if u is None:
            out.append(Restriccion(f"R1_{g.id}", "Tamaño de grupo dentro de rango", "indeterminado", g.ninos, None, "No hay unidad de configuración aplicable")); continue
        lo, hi = u.get("ninos_por_grupo_min"), u.get("ninos_por_grupo_max")
        if lo is None or hi is None:
            state, motivo = "indeterminado", "La configuración no contiene rango completo"
        elif lo <= g.ninos <= hi:
            state, motivo = "cumple", "Dentro del rango declarado en la configuración"
        else:
            state, motivo = "incumple", "Fuera del rango declarado en la configuración"
        out.append(Restriccion(f"R1_{g.id}", f"Tamaño de grupo (rango {lo}-{hi})", state, g.ninos, {"min":lo,"max":hi}, motivo))
    for b in brechas:
        if b.dimension != "personal": continue
        if b.diferencia is None:
            out.append(Restriccion(f"R3_{b.elemento}", f"Suficiencia de horas para rol {b.elemento}", "indeterminado", b.disponible, b.requerido, b.motivo or "Faltan datos"))
        elif b.diferencia < 0:
            out.append(Restriccion(f"R3_{b.elemento}", f"Horas del rol {b.elemento} no inferiores al requerimiento calculado", "incumple", b.disponible, b.requerido, "El requerimiento es una estimación; verificarlo contra la fuente normativa aplicable"))
        elif b.estado_operativo == "cerca":
            out.append(Restriccion(f"R3_{b.elemento}", f"Margen estrecho en rol {b.elemento}", "cerca", b.disponible, b.requerido, "Margen inferior al 10%; umbral de diseño, no norma"))
    return out

def _registrar_incertidumbres(situacion, config, brechas, restricciones, escenario):
    inc = []
    if situacion.presupuesto_disponible_ur is None:
        inc.append(Incertidumbre("presupuesto_disponible_ur", Estado.DESCONOCIDO, "No declarado por el usuario", "La suficiencia presupuestal queda indeterminada"))
    fin = config.get("financiamiento", {})
    valor_ur = escenario.get("valor_ur_pesos", fin.get("valor_ur_pesos"))
    if fin.get("tarifas_ur_por_hora_rol") is None:
        inc.append(Incertidumbre("tarifas_ur_por_hora_rol", Estado.DESCONOCIDO, "Dato no disponible en la configuración utilizada", "No se puede calcular un costo de personal desagregado por rol"))
    if valor_ur is None:
        inc.append(Incertidumbre("valor_ur_pesos", Estado.DESCONOCIDO, "Dato no disponible en configuración ni escenario", "La conversión a pesos queda indeterminada"))
    if fin.get("regla_descuento_bajo_minimo") is None:
        inc.append(Incertidumbre("regla_descuento_bajo_minimo", Estado.DESCONOCIDO, "Fórmula no disponible en la configuración utilizada", "La cuantía del descuento queda indeterminada"))
    for r in restricciones:
        if r.estado == "indeterminado":
            inc.append(Incertidumbre(r.id, Estado.DESCONOCIDO, r.motivo, f"No se puede evaluar: {r.descripcion}"))
    if any(b.diferencia is None for b in brechas):
        inc.append(Incertidumbre("personal_disponible", Estado.DESCONOCIDO, "Faltan horas declaradas para uno o más roles", "La suficiencia de esos roles queda indeterminada"))
    return inc

def evaluar_situacion(situacion: Situacion, config: dict, escenario: Optional[dict] = None) -> EstadoSituacion:
    escenario = escenario or {}
    advertencias = []
    if situacion.origen not in {"observada","propuesta","implementada","observada_post"}:
        advertencias.append(f"Origen no reconocido: {situacion.origen}")
    for g in situacion.grupos:
        if g.edad not in (0,1,2,3) or g.modalidad not in {"EO","4H","8H"} or g.ninos < 0:
            advertencias.append(f"Datos de grupo inválidos o no reconocidos: {g.id}")
    if any(not math.isfinite(float(p.horas_semana)) or p.horas_semana < 0 for p in situacion.personal_disponible):
        advertencias.append("Hay horas de personal negativas o no finitas.")
    ninos = sum(g.ninos for g in situacion.grupos)
    rh = _horas_requeridas_por_rol(situacion, config)
    disp = _personal_disponible_dict(situacion)
    brechas = _calcular_brechas(rh.valor, disp)
    restricciones = _evaluar_restricciones(situacion, config, brechas)
    fin = config.get("financiamiento", {})
    valor_ur = escenario.get("valor_ur_pesos", fin.get("valor_ur_pesos"))
    transfer = fin.get("transferencia_total_declarada_ur")
    costos = {"transferencia_mensual_ur": transfer,
              "por_cupo_ur": (transfer / fin["cupos_convenidos"] if transfer is not None and fin.get("cupos_convenidos") else None),
              "valor_ur_pesos": valor_ur,
              "conversion_pesos": transfer * valor_ur if transfer is not None and valor_ur is not None else None,
              "alcance": "Transferencia declarada en configuración; no equivale al costo calculado de esta situación."}
    incertidumbres = _registrar_incertidumbres(situacion, config, brechas, restricciones, escenario)
    if any(r.estado == "incumple" for r in restricciones):
        global_state = "CRÍTICO"
    elif any(r.estado == "cerca" for r in restricciones):
        global_state = "PREVENTIVO"
    elif incertidumbres or advertencias or rh.advertencias:
        global_state = "INDETERMINADO"
    else:
        global_state = "OPERATIVO"
    return EstadoSituacion(situacion.id, situacion.origen,
        {"ninos_totales": ninos, "poblacion_declarada": situacion.poblacion_ninos, "grupos":len(situacion.grupos)},
        rh.valor, disp, brechas, restricciones,
        {"materiales":[r.__dict__ for r in situacion.recursos_materiales], "estado_suficiencia":"INDETERMINADO"},
        costos, incertidumbres, global_state, advertencias + rh.advertencias)
