# Registro de pruebas e integración — CAIF v0.2/v0.3

Fecha: 2026-10-16

## Cambios incorporados tras auditoría

- Restaurados los módulos base de situación, modelo epistemológico, configuración, evaluación, alternativas, comparación, preguntas e informe.
- Corregida la escala de horas: las horas de unidad se interpretan como total de la unidad de referencia y se escalan por niños/(máximo por grupo × grupos de referencia). Esta interpretación debe confirmarse documentalmente antes de uso real.
- Separados estado operativo de brecha y estado epistemológico.
- Registrada la discrepancia entre población declarada y suma de grupos sin corregir silenciosamente el dato de origen.
- Añadida incertidumbre cuando faltan horas de un rol o no se puede evaluar una restricción.
- Evitado equiparar “evaluable” con viabilidad institucional demostrada.
- Integrada la función base de las siete preguntas con la capa de evidencia v0.3.
- Comparación describe diferencias; no atribuye causalidad.
- Recursos materiales quedan explícitamente sin evaluación de suficiencia.

## Automatización

Se añadió `.github/workflows/caif-tests.yml` para ejecutar compilación y pruebas en GitHub Actions ante push, pull request o ejecución manual. En la comprobación realizada desde esta sesión no se devolvieron checks de estado; por ello no se afirma que el workflow haya terminado ni que esté aprobado.

## Pruebas

**No se ha podido ejecutar `pytest` contra el repositorio remoto en este entorno**: el intento de clonar GitHub desde el entorno de ejecución falló por falta de resolución DNS (`Could not resolve host: github.com`). Por tanto, no se declara una ejecución de pruebas aprobada. Se añadieron pruebas de regresión para que se ejecuten en un entorno con acceso al repositorio.

Comandos reproducibles:

```bash
python -m pip install -r requirements.txt
python -m compileall calc
python -m pytest -q
```

## Limitaciones pendientes

1. Confirmar documentalmente la semántica de `horas_semana_total_unidad`; la fórmula implementada es una hipótesis explícita, no una validación de norma.
2. Resolver con el responsable la diferencia entre población declarada (40) y suma de grupos (53).
3. Incorporar una matriz verificable de requerimientos de recursos materiales.
4. Validar reglas normativas y fuentes oficiales de cada restricción.
5. Corregir y auditar la pertinencia de las experiencias del repositorio contra fuentes originales.
6. Revisar el mapeo de evidencia por dimensión; la recuperación actual se concentra principalmente en brechas de personal.
7. Ejecutar pruebas y revisar resultados reales antes de considerar aceptado el prototipo.

Estado: **código incorporado; pruebas no ejecutadas; aprobación técnica pendiente**.
