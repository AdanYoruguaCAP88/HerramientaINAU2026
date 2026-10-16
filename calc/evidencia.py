"""Módulo de evidencia y mecanismos de intervención (v0.3).

El módulo NO propone soluciones. Recupera experiencias documentadas de un
repositorio externo, evalúa su pertinencia para la situación analizada, y
presenta la evidencia al responsable con su estado epistemológico.
"""
from dataclasses import dataclass, field
from typing import Optional
import json
from pathlib import Path

from .modelo import Estado
from .evaluador import EstadoSituacion, Brecha, Restriccion


@dataclass
class ContextoAplicacion:
    pais: str
    organismo: str
    poblacion: str
    territorio: str
    nivel_descentralizacion: str
    anio_inicio: Optional[int] = None
    duracion_meses: Optional[int] = None
    requiere_especializacion: Optional[bool] = None
    requiere_presupuesto_adicional: Optional[bool] = None


@dataclass
class ResultadoDocumentado:
    tipo: str
    indicador: str
    resultado: str
    magnitud: Optional[str] = None
    periodo_seguimiento_meses: Optional[int] = None
    atribucion: str = "no_establecida"
    limitaciones: list[str] = field(default_factory=list)


@dataclass
class Experiencia:
    id: str
    titulo: str
    problema_abordado: list[str]
    intervencion: str
    contexto: ContextoAplicacion
    resultados: list[ResultadoDocumentado]
    fuente_primaria: str
    fuentes_secundarias: list[str] = field(default_factory=list)
    condiciones_requeridas: list[str] = field(default_factory=list)
    riesgos_conocidos: list[str] = field(default_factory=list)
    grado_pertinencia_uruguay: str = "por_evaluar"
    notas: list[str] = field(default_factory=list)


@dataclass
class Pertinencia:
    experiencia_id: str
    dimension: str
    puntaje: float
    razones: list[str]
    diferencias_contextuales: list[str]
    informacion_faltante: list[str]
    estado: Estado


@dataclass
class EvidenciaParaBrecha:
    brecha_elemento: str
    dimension: str
    problemas_a_investigar: list[str]
    experiencias_relevantes: list[Pertinencia]
    sin_evidencia_suficiente: bool
    mensaje_ausencia: Optional[str] = None


def cargar_repositorio(ruta: str | Path) -> list[Experiencia]:
    """Carga el repositorio de experiencias desde JSON."""
    data = json.loads(Path(ruta).read_text(encoding="utf-8"))
    experiencias = []
    for e in data.get("experiencias", []):
        ctx = ContextoAplicacion(**e["contexto"])
        resultados = [ResultadoDocumentado(**r) for r in e.get("resultados", [])]
        experiencias.append(Experiencia(
            id=e["id"], titulo=e["titulo"],
            problema_abordado=e["problema_abordado"],
            intervencion=e["intervencion"], contexto=ctx,
            resultados=resultados, fuente_primaria=e["fuente_primaria"],
            fuentes_secundarias=e.get("fuentes_secundarias", []),
            condiciones_requeridas=e.get("condiciones_requeridas", []),
            riesgos_conocidos=e.get("riesgos_conocidos", []),
            grado_pertinencia_uruguay=e.get("grado_pertinencia_uruguay", "por_evaluar"),
            notas=e.get("notas", []),
        ))
    return experiencias


_MAPA_DIMENSIONES = {
    "personal": {
        "insuficiencia_horas": ["dimensionamiento_personal", "organizacion_turnos"],
        "rol_no_contemplado": ["dimensionamiento_personal", "perfiles_rol"],
    },
    "capacidad": {"grupo_fuera_rango": ["organizacion_grupos", "ratios_atencion"]},
    "recursos": {"materiales_insuficientes": ["recursos_materiales", "financiamiento"]},
    "presupuesto": {"presupuesto_no_declarado": ["financiamiento", "modelos_costeo"]},
}


def _dimension_de_brecha(b: Brecha) -> list[str]:
    dims = []
    if b.dimension == "personal" and b.diferencia is not None and b.diferencia < 0:
        dims.extend(_MAPA_DIMENSIONES["personal"]["insuficiencia_horas"])
    if b.dimension == "personal" and b.motivo and "no contemplado" in b.motivo.lower():
        dims.extend(_MAPA_DIMENSIONES["personal"]["rol_no_contemplado"])
    return dims


def _dimension_de_restriccion(r: Restriccion) -> list[str]:
    dims = []
    if r.id.startswith("R1") and r.estado == "incumple":
        dims.extend(_MAPA_DIMENSIONES["capacidad"]["grupo_fuera_rango"])
    if r.id.startswith("R3"):
        dims.extend(["supervision", "calidad_atencion"])
    return dims


def _evaluar_pertinencia(exp: Experiencia, dimension: str,
                         contexto_uruguay: dict) -> Pertinencia:
    razones, diferencias, faltantes = [], [], []
    if dimension not in exp.problema_abordado:
        return Pertinencia(exp.id, dimension, 0.0,
            ["La experiencia no aborda esta dimensión"], [], [], Estado.VERIFICADO)

    puntaje = 0.4
    razones.append(f"Aborda la dimensión '{dimension}'")
    tipos = {r.tipo for r in exp.resultados}
    if "evaluacion_independiente" in tipos:
        puntaje += 0.25
        razones.append("Tiene evaluación independiente")
    elif "evaluacion_externa" in tipos:
        puntaje += 0.15
        razones.append("Tiene evaluación externa")
    elif "informe_institucional" in tipos:
        puntaje += 0.05
        razones.append("Informe institucional (no evaluación independiente)")
    else:
        faltantes.append("No hay evaluación documentada")

    if any(r.atribucion == "causal" for r in exp.resultados):
        puntaje += 0.15
        razones.append("Al menos un resultado tiene atribución causal")
    elif any(r.atribucion == "correlacional" for r in exp.resultados):
        puntaje += 0.05
        razones.append("Resultados correlacionales (no causales)")

    if exp.contexto.poblacion.lower() in ("infancia", "primera infancia", "ninez"):
        puntaje += 0.10
        razones.append("Población comparable (infancia)")
    else:
        diferencias.append(f"Población '{exp.contexto.poblacion}' distinta de la uruguaya")

    if exp.contexto.nivel_descentralizacion == contexto_uruguay.get("nivel_descentralizacion", "mixto"):
        puntaje += 0.05
        razones.append("Nivel de descentralización comparable")
    else:
        diferencias.append(f"Descentralización '{exp.contexto.nivel_descentralizacion}' distinta de la uruguaya")

    if exp.contexto.territorio in ("rural", "mixto") and contexto_uruguay.get("territorio") == "rural":
        puntaje += 0.05
        razones.append("Contexto territorial comparable")

    if exp.condiciones_requeridas:
        faltantes.append(f"Requiere verificar: {', '.join(exp.condiciones_requeridas)}")

    puntaje = min(1.0, puntaje)
    if "evaluacion_independiente" not in tipos:
        estado = Estado.NO_VERIFICADO if tipos else Estado.DESCONOCIDO
    else:
        estado = Estado.VERIFICADO
    return Pertinencia(exp.id, dimension, puntaje, razones, diferencias, faltantes, estado)


def buscar_evidencia(estado: EstadoSituacion, repositorio: list[Experiencia],
                     contexto_uruguay: dict | None = None) -> list[EvidenciaParaBrecha]:
    """Recupera y evalúa evidencia; no propone ni recomienda alternativas."""
    contexto_uruguay = contexto_uruguay or {
        "pais": "Uruguay", "nivel_descentralizacion": "centralizado", "territorio": "mixto"
    }
    salidas = []
    for b in estado.brechas:
        if b.diferencia is None or b.diferencia >= 0:
            continue
        dims = _dimension_de_brecha(b)
        if not dims:
            continue
        pertinencias = [ _evaluar_pertinencia(exp, d, contexto_uruguay)
                         for exp in repositorio for d in dims ]
        pertinencias = [p for p in pertinencias if p.puntaje > 0]
        pertinencias.sort(key=lambda x: -x.puntaje)
        salidas.append(EvidenciaParaBrecha(
            brecha_elemento=b.elemento, dimension=b.dimension,
            problemas_a_investigar=dims, experiencias_relevantes=pertinencias,
            sin_evidencia_suficiente=not pertinencias,
            mensaje_ausencia=(f"No hay experiencias documentadas en el repositorio para la dimensión '{', '.join(dims)}'. Antes de intervenir, se necesita investigación adicional."
                              if not pertinencias else None),
        ))

    for r in estado.restricciones:
        if r.estado != "incumple":
            continue
        dims = _dimension_de_restriccion(r)
        if not dims:
            continue
        pertinencias = [_evaluar_pertinencia(exp, d, contexto_uruguay)
                        for exp in repositorio for d in dims]
        pertinencias = [p for p in pertinencias if p.puntaje > 0]
        pertinencias.sort(key=lambda x: -x.puntaje)
        salidas.append(EvidenciaParaBrecha(
            brecha_elemento=r.id, dimension="restriccion",
            problemas_a_investigar=dims, experiencias_relevantes=pertinencias,
            sin_evidencia_suficiente=not pertinencias,
            mensaje_ausencia="No hay experiencias documentadas para esta restricción." if not pertinencias else None,
        ))
    return salidas
