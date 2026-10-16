# Registro de pruebas e integración — CAIF v0.3

Fecha: 2026-10-16

## Estado del repositorio

Se subieron los seis archivos de la capa de evidencia v0.3. La integración aún no está completa porque faltan los módulos base v0.2, las configuraciones y los escenarios necesarios para importar y ejecutar el paquete.

## Pruebas

**No se ha ejecutado pytest contra el contenido actual del repositorio.** Los resultados anteriores de 7 pruebas aprobadas y 3 fallidas correspondían a una extracción temporal previa del documento fuente, no a una ejecución reproducible del repositorio GitHub. No deben interpretarse como estado de las pruebas de esta carga.

## Auditoría estática inicial de la capa v0.3

1. La extensión de `calc/preguntas.py` importa `responder_preguntas` desde el propio módulo. Al fusionarla, debe preservarse la función base de v0.2 para evitar una importación circular o un símbolo inexistente.
2. Aunque `_MAPA_DIMENSIONES` declara dimensiones para capacidad, recursos y presupuesto, `_dimension_de_brecha` actualmente solo mapea brechas de personal. La recuperación de evidencia para las otras dimensiones todavía no está implementada.
3. La CLI acepta una lista o un objeto con clave `alternativas`, pero ese cambio debe probarse con el formato real de los escenarios.
4. Las entradas del repositorio están marcadas por el autor como reportadas y pendientes de verificación contra fuentes originales. El código no verifica por sí mismo la exactitud de las referencias ni valida la transferencia de resultados a Uruguay.

## Criterio de aceptación pendiente

- Restaurar e integrar todos los módulos base v0.2.
- Fusionar la extensión de preguntas con la función base existente.
- Incorporar configuraciones y escenarios de prueba.
- Ejecutar `python -m compileall calc` y `python -m pytest -q`.
- Revisar cada fallo contra la especificación y documentar el resultado real.
- Mantener explícito que el prototipo no recomienda ni sustituye el juicio del responsable.
