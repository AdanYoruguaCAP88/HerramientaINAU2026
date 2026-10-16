# Registro de pruebas — extracción v0.3

Fecha: 2026-10-16

## Resultado

La extracción temporal del código desde `Herramienta Adaptativa.docx` compiló sintácticamente con `compileall`, pero la batería inicial no quedó limpia: **7 pruebas pasaron y 3 fallaron**.

## Fallos detectados

1. `test_evidencia_declara_ausencia`: el buscador no devuelve una entrada marcada como `sin_evidencia_suficiente` para el caso de prueba sin evidencia.
2. `test_V02_evaluador_produce_estado`: el evaluador calcula 53 niños en vez de los 40 declarados en la situación de prueba.
3. `test_V02_alternativa_evaluable`: el test trata `tacuarembo_alternativas.json` como una lista, pero la extracción produce un objeto JSON.

## Estado epistemológico

Esto es una prueba inicial de la extracción, no una auditoría funcional completa. Los fallos pueden proceder de la implementación, de la forma del escenario extraído o de una discrepancia entre pruebas y especificación. No se afirma que el prototipo esté validado.

## Próximo paso técnico

Resolver cada discrepancia contra el documento fuente y volver a ejecutar toda la batería antes de marcar la carga como apta para pruebas de aceptación.
