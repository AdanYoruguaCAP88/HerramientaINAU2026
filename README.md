# Herramienta Adaptativa INAU — prototipo CAIF v0.3

Herramienta experimental para estructurar situaciones operativas, brechas, restricciones e incertidumbres, comparar alternativas declaradas por personas y recuperar experiencias documentadas sin generar recomendaciones.

## Principios

- La herramienta no decide ni recomienda.
- Las alternativas las declara el responsable.
- Los datos desconocidos no se convierten en cero ni en suficiencia presumida.
- Los requerimientos extrapolados se identifican como hipótesis.
- Las diferencias entre escenarios no demuestran efectos causales.
- Las fuentes del repositorio de evidencia requieren verificación independiente.

## Estructura incorporada

- `calc/modelo.py`: estados epistemológicos genéricos.
- `calc/situacion.py`: modelo de situación y alternativas.
- `calc/config.py`: carga de JSON.
- `calc/evaluador.py`: brechas, restricciones e incertidumbres.
- `calc/alternativas.py`: evaluación de alternativas declaradas.
- `calc/comparador.py`: comparación descriptiva.
- `calc/preguntas.py`: siete preguntas y extensión de evidencia v0.3.
- `calc/informe.py`: informes Markdown y JSON.
- `calc/__main__.py`: interfaz CLI.
- `config/caif_san_carlos.json`: configuración de referencia recuperada del documento de trabajo.
- `escenarios/tacuarembo_40ninos.json` y `escenarios/tacuarembo_alternativas.json`: datos del escenario presentado.
- `repositorio/experiencias.json`: experiencias documentadas pendientes de auditoría de fuentes.
- `tests/test_v0_2.py` y `tests/test_evidencia.py`: pruebas de regresión.

## Hallazgo de integridad conservado intencionalmente

El escenario recibido declara 40 niños, pero los cuatro grupos suman 53. No se modificó ninguno de los dos datos sin confirmación de origen. El evaluador registra la discrepancia como restricción indeterminada y el informe expone ambas cifras.

## Ejecutar

Desde la raíz del repositorio:

```bash
python -m pip install -r requirements.txt
python -m compileall calc
python -m pytest -q
python -m calc --config config/caif_san_carlos.json --situacion escenarios/tacuarembo_40ninos.json --alternativas escenarios/tacuarembo_alternativas.json --repositorio repositorio/experiencias.json --out salida
```

## Estado

**Prototipo en integración y auditoría. No validado para uso institucional ni para decisiones reales sobre centros CAIF.** La extrapolación de horas debe contrastarse con la semántica documentada de las unidades y las fuentes normativas aplicables. La configuración conserva parámetros financieros desconocidos. La suficiencia de recursos materiales se informa como indeterminada porque no hay una matriz de requerimientos implementada.
