# Plan de trabajo: generador de tags PLC

## Objetivo

Convertir nombres PLC heredados o inconsistentes en tags canonicos mediante un proceso determinista, auditable y orientado a revision humana cuando la informacion no sea suficiente.

## Modelo semantico acordado

La informacion reconocida se almacenara primero en una estructura semantica independiente del nombre final. Sus campos son:

```text
system
entity
subentity
attribute
state
action
qualifier
equipment_position
signal_position
role
instance
signal_type
```

Reglas de esta decision:

- La Recognition Engine identifica y estructura conceptos; no compone la tag final.
- La Naming Engine selecciona una plantilla segun el tipo de variable y transforma la estructura en una tag.
- Un campo ausente permanece ausente; no se rellena con una inferencia no justificada.
- `equipment_position` identifica la posicion del equipo o entidad principal.
- `signal_position` identifica la posicion del boton, sensor, footswitch u origen de la senal.
- `instance` se conserva como dato separado cuando el numero identifica un equipo o una unidad.
- `signal_type` se mantiene separado del significado funcional de la variable.
- La obligatoriedad, cardinalidad y compatibilidad de los campos se definiran por plantilla.

Este modelo es una decision de diseno; no implica todavia cambios en Python ni en YAML.

## Plantillas por tipo de variable

Se usaran plantillas diferenciadas para evitar forzar una unica gramatica a comandos, sensores, alarmas y estados de sistema. Las plantillas concretas y sus campos obligatorios quedan pendientes de definicion.

## Regla de ejecucion

- Trabajar una tarea a la vez.
- No implementar la siguiente fase si el criterio de salida de la fase actual no esta cumplido.
- Separar hechos verificados, decisiones de diseno y supuestos temporales.
- No convertir un resultado ambiguo en un tag aprobado automaticamente.
- Mantener el reconocimiento, el naming y la exportacion como responsabilidades separadas.
- Toda regla de dominio debe vivir en YAML; Python debe ejecutar reglas genericas.

---

## Fase 0 - Establecer la linea base

- [x] Ejecutar el flujo actual con una muestra representativa.
- [ ] Guardar los resultados actuales de reconocimiento y naming.
- [ ] Crear una tabla de casos problematicos y resultado esperado.
- [ ] Medir tokens desconocidos, tags vacios, duplicados y colisiones.
- [x] Registrar errores de ejecucion y dependencias necesarias.

**Criterio de salida:** existe una linea base reproducible y una muestra etiquetada con casos normales, compuestos, ambiguos, numericos y de texto libre.

---

## Fase 1 - Definir el contrato del tag canonico

- [ ] Confirmar el orden de los segmentos del tag.
- [ ] Confirmar que campos son obligatorios y cuales opcionales.
- [ ] Confirmar el uso de guiones bajos y camelCase.
- [ ] Definir caracteres permitidos y longitud maxima.
- [ ] Definir el tratamiento de segmentos vacios.
- [ ] Definir si el tag canonico puede contener identificadores numericos.
- [ ] Definir ejemplos validos y ejemplos rechazados.

**Criterio de salida:** el formato canonico esta escrito y puede validarse sin interpretar el nombre original.

---

## Fase 2 - Definir el contrato de salida

- [ ] Confirmar si la salida oficial es CSV, XLSX o ambas.
- [ ] Definir el significado de `canonical_tag`.
- [ ] Definir el significado de `approved_tag`.
- [ ] Definir `review_required` y sus causas.
- [ ] Definir los estados: aprobado, provisional, rechazado y pendiente.
- [ ] Definir los campos de auditoria que se deben conservar.
- [ ] Definir el comportamiento cuando no se puede generar un tag valido.

**Criterio de salida:** una persona puede distinguir sin ambiguedad entre resultado automatico, propuesta y resultado aprobado.

---

## Fase 3 - Auditar y normalizar los datos de entrada

- [ ] Separar entradas PLC estructuradas de descripciones de texto libre.
- [ ] Inventariar separadores, mayusculas, puntuacion y formatos compuestos.
- [ ] Inventariar prefijos tecnicos y tipos de senal reales.
- [ ] Clasificar numeros: canal, instancia, equipo o texto desconocido.
- [ ] Identificar palabras gramaticales y decidir si se ignoran.
- [ ] Agrupar variantes equivalentes del mismo concepto.
- [ ] Crear un conjunto de datos de prueba versionado.

**Criterio de salida:** los formatos de entrada conocidos estan catalogados y cada familia tiene ejemplos verificables.

---

## Fase 4 - Definir el modelo semantico

- [ ] Confirmar las categorias finales.
- [ ] Separar componente fisico, cualificador, medida, rol y estado.
- [ ] Definir una categoria para instancia o identificador cuando sea necesaria.
- [ ] Definir si una categoria admite cero, uno o varios valores.
- [ ] Definir si el orden de los valores tiene significado.
- [ ] Definir como se representan frases y entidades compuestas.
- [ ] Definir como se representa la procedencia de cada valor.
- [ ] Definir confianza, alternativas y motivo de reconocimiento.

**Criterio de salida:** un resultado semantico puede representar correctamente los casos de prueba sin reutilizar `unknown_tokens` para conceptos conocidos.

---

## Fase 5 - Corregir y validar el contrato YAML

- [ ] Hacer que el esquema YAML usado por el codigo coincida con el documentado.
- [ ] Definir tecnicas de tokenizacion y prefijos en YAML.
- [ ] Definir senales y patrones en un unico lugar.
- [ ] Validar que cada alias apunta a un concepto existente.
- [ ] Detectar colisiones de alias entre categorias.
- [ ] Declarar categorias y metadatos de cada concepto.
- [ ] Declarar composiciones especiales que no deban inferirse genericamente.
- [ ] Validar el YAML antes de ejecutar el procesamiento.

**Criterio de salida:** una validacion automatica detecta referencias invalidas, claves incompatibles, alias ambiguos y configuracion sin uso.

---

## Fase 6 - Redisenar la tokenizacion y normalizacion

- [ ] Conservar el token original y su posicion.
- [ ] Implementar separadores configurables.
- [ ] Detectar compuestos como `gen1`, `oiltemp` y `dcpumps`.
- [ ] Detectar puntuacion significativa como `over/under`.
- [ ] Normalizar sin perder la forma original.
- [ ] Resolver alias con trazabilidad.
- [ ] Clasificar identificadores numericos antes de marcarlos como desconocidos.

**Criterio de salida:** la tokenizacion conserva toda la informacion de entrada y produce una secuencia estable para los casos de prueba.

---

## Fase 7 - Implementar reconocimiento contextual

- [ ] Sustituir el primer-match ciego por reglas con prioridad explicita.
- [ ] Implementar reconocimiento de frases y componentes compuestos.
- [ ] Resolver ambiguedades usando contexto local.
- [ ] Registrar candidatos alternativos cuando no haya una decision unica.
- [ ] Detectar categorias incompatibles o duplicadas.
- [ ] Separar reconocimiento de senal, metadatos tecnicos y semantica.
- [ ] Marcar `review_required` cuando la evidencia sea insuficiente.

**Criterio de salida:** el reconocimiento no fuerza una interpretacion unica cuando los datos no la justifican y conserva evidencia suficiente para revisar el resultado.

---

## Fase 8 - Implementar inferencia de sistema

- [ ] Implementar la estrategia declarada en YAML.
- [ ] Aplicar pesos de sistema, componente, modificador y rol.
- [ ] Definir desempates deterministas.
- [ ] Considerar todos los componentes relevantes, no solo el primero.
- [ ] Diferenciar confianza de regla y confianza semantica.
- [ ] Registrar votos, regla aplicada y conflictos.
- [ ] Marcar revision cuando el sistema sea ambiguo.

**Criterio de salida:** la misma entrada produce siempre el mismo sistema, razon y nivel de confianza, y los conflictos no se ocultan.

---

## Fase 9 - Implementar naming canonico

- [ ] Validar la estructura semantica antes de nombrar.
- [ ] Componer componentes solo cuando la regla lo permita.
- [ ] Eliminar duplicados explicables por sinonimos.
- [ ] Preservar instancias y calificadores en campos definidos.
- [ ] Generar un tag canonico valido o devolver ausencia justificada.
- [ ] Generar una propuesta extendida solo si cumple el contrato.
- [ ] No usar texto desconocido sin clasificar como segmento aprobado.

**Criterio de salida:** cada tag generado cumple la gramatica canonica y cada perdida o transformacion de informacion es auditable.

---

## Fase 10 - Anadir controles de calidad

- [ ] Detectar colisiones de tags canonicos.
- [ ] Detectar colisiones de tags extendidos.
- [ ] Detectar tags vacios o incompletos.
- [ ] Detectar sistemas contradictorios.
- [ ] Detectar duplicados semanticos.
- [ ] Medir desconocidos y perdida de informacion.
- [ ] Validar senales no soportadas.
- [ ] Emitir un resumen de errores y advertencias.

**Criterio de salida:** ningun resultado puede pasar a aprobacion sin superar las validaciones definidas.

---

## Fase 11 - Definir el flujo de revision humana

- [ ] Definir que casos requieren revision obligatoria.
- [ ] Mostrar tokens originales, normalizados y clasificados.
- [ ] Mostrar reglas, confianza y alternativas.
- [ ] Permitir corregir el tag aprobado sin sobreescribir el resultado canonico.
- [ ] Registrar la decision del revisor.
- [ ] Registrar candidatos de nuevos alias o conceptos.
- [ ] Separar cambios aprobados de cambios pendientes en el diccionario.

**Criterio de salida:** un revisor puede aprobar, corregir o rechazar cada resultado sin editar datos de diagnostico.

---

## Fase 12 - Alinear la exportacion

- [ ] Corregir la discrepancia entre argumento `output.csv` y salida XLSX.
- [ ] Definir nombres y orden de columnas.
- [ ] Poblar todos los campos declarados o eliminarlos.
- [ ] Exportar el diagnostico de reconocimiento por separado.
- [ ] Mantener el nombre original sin alteraciones.
- [ ] Verificar que Excel y CSV conserven valores y codificacion.

**Criterio de salida:** la salida documentada coincide exactamente con el archivo que genera la herramienta.

---

## Fase 13 - Pruebas y regresion

- [ ] Crear pruebas unitarias para tokenizacion.
- [ ] Crear pruebas unitarias para alias y clasificacion.
- [ ] Crear pruebas para frases y compuestos.
- [ ] Crear pruebas para numeros e instancias.
- [ ] Crear pruebas para senales y prefijos.
- [ ] Crear pruebas para inferencia y desempates.
- [ ] Crear pruebas para naming y validacion.
- [ ] Crear pruebas de colisiones y revision.
- [ ] Convertir la muestra de la Fase 0 en regresion automatica.

**Criterio de salida:** los cambios futuros no alteran silenciosamente resultados ya aprobados.

---

## Fase 14 - Piloto controlado

- [ ] Seleccionar un proyecto o subconjunto representativo.
- [ ] Ejecutar en modo propuesta, sin importar tags automaticamente.
- [ ] Revisar todos los resultados ambiguos y colisiones.
- [ ] Medir precision, cobertura y tasa de revision.
- [ ] Revisar falsos positivos y perdida de informacion.
- [ ] Ajustar YAML y reglas con cambios versionados.
- [ ] Repetir el piloto tras cada ajuste relevante.

**Criterio de salida:** los resultados cumplen el umbral de calidad acordado y existe un procedimiento de rollback o correccion.

---

## Decisiones pendientes de mayor prioridad

1. Gramatica exacta del tag canonico.
2. Significado de numeros e identificadores.
3. Distincion entre componentes, calificadores y medidas.
4. Politica para entradas ambiguas.
5. Catalogo completo de prefijos y senales.
6. Tratamiento de texto libre frente a nombres PLC.
7. Politica de composiciones y sinonimos.
8. Formato oficial de salida y significado de aprobacion.

## Orden recomendado de trabajo inmediato

1. Completar la Fase 0.
2. Resolver las Fases 1 y 2 antes de tocar el algoritmo.
3. Completar la auditoria de entradas de la Fase 3.
4. Definir el modelo de la Fase 4.
5. Validar el contrato YAML en la Fase 5.
6. Implementar una sola fase tecnica cada vez y ejecutar su regresion.
