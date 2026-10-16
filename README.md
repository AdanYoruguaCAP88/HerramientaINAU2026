# Herramienta Adaptativa INAU — prototipo CAIF v0.3

Repositorio de trabajo para el prototipo CAIF v0.3.

## Objetivo

Estructurar una situación operativa, explicitar brechas e incertidumbres y recuperar evidencia documentada sin generar recomendaciones ni sustituir el criterio del responsable.

## Estado de esta carga

Se han incorporado los archivos de la capa de evidencia v0.3:

- `calc/evidencia.py`
- `repositorio/experiencias.json`
- `calc/preguntas.py` (extensión de preguntas con evidencia)
- `calc/__main__.py` (CLI con opción de repositorio)
- `tests/test_evidencia.py`
- `SUPUESTOS.md`

**Integración incompleta:** el repositorio no contiene todavía el paquete base v0.2 requerido por estos archivos (entre otros, `calc/modelo.py`, `calc/evaluador.py`, `calc/situacion.py`, `calc/config.py`, `calc/alternativas.py` y `calc/informe.py`), ni las configuraciones y escenarios de prueba. Por eso no sería correcto afirmar que el paquete completo compila o que la batería de pruebas se ejecutó desde este repositorio.

Además, la extensión de preguntas debe fusionarse con la implementación base de `responder_preguntas`; no debe reemplazarla ni importarse a sí misma como si fuera un módulo separado.

## Ejecución prevista cuando esté completo

```bash
python -m pip install pytest
python -m pytest -q
```

Estado: prototipo en integración; no validado para uso institucional real.
