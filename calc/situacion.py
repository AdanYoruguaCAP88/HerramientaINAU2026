"""Modelos de entrada declarados por el usuario; no contienen lógica normativa."""
from dataclasses import dataclass, field
from typing import Optional

ORIGENES_VALIDOS = {"observada", "propuesta", "implementada", "observada_post"}

@dataclass
class GrupoAtendido:
    id: str
    edad: int
    modalidad: str
    ninos: int

@dataclass
class PersonalDisponible:
    rol: str
    horas_semana: float
    perfil: Optional[str] = None
    notas: Optional[str] = None

@dataclass
class RecursosMateriales:
    item: str
    cantidad: float
    unidad: str

@dataclass
class Situacion:
    id: str
    ubicacion: str
    origen: str
    poblacion_ninos: int
    grupos: list[GrupoAtendido]
    personal_disponible: list[PersonalDisponible]
    recursos_materiales: list[RecursosMateriales] = field(default_factory=list)
    presupuesto_disponible_ur: Optional[float] = None
    problema_declarado: Optional[str] = None
    notas: list[str] = field(default_factory=list)
    fecha: Optional[str] = None

@dataclass
class Alternativa:
    id: str
    descripcion: str
    situacion_propuesta: Situacion
    autor: str = "usuario"
    notas: list[str] = field(default_factory=list)
