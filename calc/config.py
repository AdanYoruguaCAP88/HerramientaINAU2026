"""Carga de configuraciones y escenarios JSON."""
import json
from pathlib import Path

def _cargar(ruta):
    if ruta is None:
        return {}
    p = Path(ruta)
    return json.loads(p.read_text(encoding="utf-8"))

def cargar_config(ruta):
    data = _cargar(ruta)
    if not isinstance(data, dict):
        raise ValueError("La configuración debe ser un objeto JSON.")
    if not isinstance(data.get("unidades_atencion"), list):
        raise ValueError("La configuración debe incluir unidades_atencion como lista.")
    return data

def cargar_escenario(ruta):
    data = _cargar(ruta)
    if not isinstance(data, dict):
        raise ValueError("El escenario debe ser un objeto JSON.")
    return data
