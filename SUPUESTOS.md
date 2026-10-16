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
