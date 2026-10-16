# Supuestos v0.3 — Módulo de evidencia

## Sobre el repositorio
1. **JSON separado:** actualizarlo no requiere cambiar código; el motor no tiene experiencias hardcodeadas.
2. **Estado epistemológico:** una evaluación independiente no se trata igual que un informe institucional.
3. **Pertinencia calculada:** el campo `grado_pertinencia_uruguay` es una estimación de curación inicial; el motor recalcula proximidad contextual.
4. **Sin importación de prestigio:** la puntuación se basa en dimensión, fuerza de evaluación y comparabilidad contextual.

## Sobre la vinculación brecha → evidencia
1. **Mapeo explícito y auditable:** `_MAPA_DIMENSIONES` declara qué dimensiones busca el motor.
2. **Ausencia explícita:** cuando no hay evidencia, se devuelve `sin_evidencia_suficiente=True`.
3. **Diferencias contextuales:** se presentan junto a las experiencias recuperadas.

## Limitaciones
1. **Repositorio incompleto:** búsqueda exploratoria, no exhaustiva.
2. **Sin validación local:** no se afirma que las experiencias funcionen en Uruguay.
3. **Curación continua:** cada nueva experiencia requiere marcado epistemológico.


## Auditoría de integración v0.2 — 16/10/2026

1. **Extrapolación de horas (HIPÓTESIS):** el cálculo trata `horas_semana_total_unidad` como el total de la unidad modelo y escala por `niños / (máximo_por_grupo × grupos_modelo)`. Esta interpretación debe contrastarse con la documentación de origen antes de usar resultados en decisiones reales.
2. **Discrepancia de población:** el escenario recibido declara 40 niños, mientras que los grupos suman 53. El dato no se corrige automáticamente; la discrepancia queda registrada como restricción indeterminada.
3. **Separación de estados:** el estado operativo (cumple/incumple/cerca/indeterminado) no sustituye al estado epistemológico. Las brechas calculadas desde requerimientos extrapolados conservan estado HIPÓTESIS.
4. **Datos ausentes:** la falta de horas para un rol no equivale a cero horas ni a suficiencia. La brecha y la restricción quedan indeterminadas.
5. **Costos:** la transferencia declarada en la configuración no equivale al costo de la situación concreta. La conversión a pesos depende del valor de UR informado en configuración o escenario.
6. **Recursos materiales:** se registran los recursos declarados, pero, al no existir una matriz documentada de requerimientos por modalidad, su suficiencia queda INDETERMINADA.
7. **Alternativas:** evaluable significa que se pudo ejecutar una evaluación con los datos disponibles; no demuestra viabilidad institucional ni constituye una recomendación.
8. **Comparación:** los deltas describen diferencias entre los estados ingresados. No demuestran causalidad, implementación efectiva ni aprendizaje del sistema.
9. **Evidencia:** la recuperación y el puntaje de pertinencia son instrumentos exploratorios. No verifican por sí mismos la exactitud de las fuentes ni la transferibilidad al contexto uruguayo.
10. **Validación:** el código se incorporó y se añadió CI, pero las pruebas no se consideran aprobadas hasta disponer de un resultado de ejecución verificable.
