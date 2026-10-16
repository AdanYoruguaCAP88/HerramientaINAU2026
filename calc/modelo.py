"""Tipos epistemológicos y resultado genérico del motor NeoX."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
class Estado(str, Enum):
    DESCONOCIDO="?"
    NO_VERIFICADO="L"
    HIPOTESIS="H"
    SINTETICO="SINT"
    SECUNDARIO="V2"
    VERIFICADO="V"
class Tipo(str, Enum):
    OBSERVADA="observada"
    OPERATIVA="operativa"
    ESTIMADA="estimada"
_ORDEN=[Estado.DESCONOCIDO,Estado.NO_VERIFICADO,Estado.HIPOTESIS,Estado.SECUNDARIO,Estado.VERIFICADO]
@dataclass
class Variable:
    id:str
    definicion:str
    valor:Any
    unidad:str
    tipo:Tipo
    estado:Estado
    fecha_corte:Optional[str]=None
    fuente:Optional[str]=None
    metodo_calculo:Optional[str]=None
    responsable_actualizacion:Optional[str]=None
    frecuencia_actualizacion:Optional[str]=None
    limitaciones:Optional[str]=None
@dataclass
class Resultado:
    valor:Any
    variables_usadas:list=field(default_factory=list)
    advertencias:list=field(default_factory=list)
    estado_resultado:Estado=Estado.VERIFICADO
    @property
    def es_indeterminado(self):
        return self.estado_resultado==Estado.DESCONOCIDO or self.valor is None
    @property
    def contiene_sintetico(self):
        return any(v.estado==Estado.SINTETICO for v in self.variables_usadas)
def calcular_estado_resultado(variables:list)->Estado:
    relevant=[v for v in variables if v.estado!=Estado.SINTETICO]
    if not relevant or any(v.estado==Estado.DESCONOCIDO for v in relevant): return Estado.DESCONOCIDO
    return min((v.estado for v in relevant),key=_ORDEN.index)
