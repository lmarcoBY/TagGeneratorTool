# Diseno de plantillas de tags PLC

Estado: estructura implementada en modo transicion; reglas semanticas pendientes

## Campos semanticos

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

Definiciones principales:

- `system`: sistema funcional al que pertenece la variable.
- `entity`: equipo o elemento principal.
- `subentity`: parte funcional de la entidad.
- `attribute`: propiedad o magnitud observada.
- `state`: estado, condicion o alarma.
- `action`: orden u operacion.
- `qualifier`: informacion que especifica la entidad o su funcion.
- `equipment_position`: posicion del equipo controlado.
- `signal_position`: posicion del boton, sensor o elemento que origina la senal.
- `role`: tipo de interfaz o funcion de la senal.
- `instance`: numero o identificador de instancia.
- `signal_type`: tipo de senal PLC, por ejemplo `DI` o `DO`.
- `token_records`: trazabilidad ordenada de cada token original.

Regla: los campos semanticos se almacenan separados. La forma compacta de la tag se genera despues.

## Trazabilidad de tokens

Cada token se conserva con indice de posicion empezando en `0`:

```text
position
raw
normalized
category
value
omitted
```

Los tokens tecnicos tambien se conservan con `category: technical` y `omitted: true`. La columna `token_records` del CSV contiene esta informacion en JSON para permitir analisis contextual de tokens vecinos.

Estado actual de implementacion:

- La Recognition Engine ya devuelve estos campos bajo `semantic`.
- Los campos antiguos (`components`, `actions`, `sides`, `locations`, etc.) se conservan temporalmente.
- La Naming Engine selecciona una plantilla y genera `template_tag` como candidato.
- `canonical_tag` sigue siendo la salida heredada hasta definir las reglas de mapeo contextual.
- `equipment_position` y `signal_position` permanecen vacios hasta definir reglas que distingan ambas referencias.

---

## Plantilla 1: actuador o comando

### Uso

Variables que representan una orden para mover, abrir, cerrar, tensionar, liberar, activar o desactivar un equipo.

### Campos

| Campo | Obligatorio | Regla |
| --- | --- | --- |
| `system` | Si | Debe estar confirmado o marcado para revision. |
| `entity` | Si | Identifica el equipo controlado. |
| `action` | Si | Identifica la operacion solicitada. |
| `signal_type` | Si | Normalmente `DO` para salida de comando. |
| `subentity` | No | Parte funcional del equipo. |
| `qualifier` | No | Especificacion funcional adicional. |
| `equipment_position` | No | Posicion del equipo controlado. |
| `signal_position` | No | Posicion de la interfaz de mando. |
| `role` | No | `btn`, `fsw` u otro tipo de mando. |
| `instance` | No | Numero o identificador del equipo. |
| `attribute` | No | Solo si la orden actua sobre una propiedad concreta. |
| `state` | No | Solo si la orden incluye un estado. |

### Orden de salida

```text
system_entity_subentity_action_qualifier_equipment_position_signal_position_role_instance_signal_type
```

Se omiten los campos vacios sin cambiar el significado de los restantes.

### Ejemplos

```text
Hyd_bowt_up_DO
Hyd_anchorWindlass_in_DO
Hyd_jibCar_pt_fwd_sbPed_btn_DI
Hyd_halyWinch_aftPt_fast_fsw_DI
```

---

## Plantilla 2: feedback o sensor

### Uso

Variables que informan de una posicion, estado, medida o confirmacion procedente de un equipo o sensor.

### Campos

| Campo | Obligatorio | Regla |
| --- | --- | --- |
| `system` | Si | Debe estar confirmado o marcado para revision. |
| `entity` | Si | Equipo o sensor al que pertenece el feedback. |
| `signal_type` | Si | Normalmente `DI`, `AI` o equivalente. |
| `role` | Si | Por ejemplo `feedback`, `ls`, `psw` o `sw`. |
| `attribute` | Condicional | Obligatorio para una medida o propiedad. |
| `state` | Condicional | Obligatorio para un estado discreto. |
| `subentity` | No | Parte concreta del equipo. |
| `qualifier` | No | Contexto funcional. |
| `equipment_position` | No | Posicion del equipo medido. |
| `signal_position` | No | Posicion del sensor o interfaz. |
| `action` | No | Solo si el feedback se refiere a una operacion. |
| `instance` | No | Numero o identificador. |

### Regla de validacion

Debe existir al menos uno de estos campos:

```text
attribute
state
action
```

### Orden de salida

```text
system_entity_subentity_attribute_state_action_qualifier_equipment_position_signal_position_role_instance_signal_type
```

---

## Plantilla 3: alarma

### Uso

Variables que indican una condicion anormal, fallo, disparo, sobrecarga o nivel limite.

### Campos

| Campo | Obligatorio | Regla |
| --- | --- | --- |
| `system` | Si | Puede ser `Alrm` solo si se confirma como sistema del proyecto. |
| `entity` | Condicional | Obligatorio si la alarma identifica un equipo. |
| `state` | Si | Define la condicion de alarma. |
| `signal_type` | Si | `DI`, `DO` u otro tipo confirmado. |
| `attribute` | No | Magnitud asociada, por ejemplo `level` o `temperature`. |
| `qualifier` | No | Tipo de fluido, servicio o condicion. |
| `equipment_position` | No | Posicion del equipo alarmado. |
| `signal_position` | No | Posicion del sensor o entrada de alarma. |
| `role` | No | `alarm`, `feedback` u otro. |
| `instance` | No | Numero o identificador. |
| `action` | No | Solo si la alarma representa una orden o respuesta. |

### Regla de validacion

Una alarma sin `entity` puede generarse solo si el `system + state + attribute` identifica un objeto sin ambiguedad. En caso contrario, requiere revision.

### Orden de salida

```text
system_entity_subentity_attribute_state_qualifier_equipment_position_signal_position_role_instance_signal_type
```

---

## Plantilla 4: estado de sistema

### Uso

Variables que representan el estado operativo de un sistema o modo general, sin una orden directa a un actuador.

### Campos

| Campo | Obligatorio | Regla |
| --- | --- | --- |
| `system` | Si | Sistema al que pertenece el estado. |
| `attribute` | Si | Propiedad observada, por ejemplo `power`, `mode` o `running`. |
| `state` | Condicional | Estado concreto, por ejemplo `normal`, `enabled` u `online`. |
| `signal_type` | Si | Tipo de senal confirmado. |
| `entity` | No | Equipo concreto si existe. |
| `qualifier` | No | Contexto adicional. |
| `role` | No | `feedback`, `status`, `command`, etc. |
| `equipment_position` | No | Solo si el estado pertenece a un equipo posicionado. |
| `signal_position` | No | Solo si el origen tiene posicion propia. |
| `instance` | No | Numero o identificador. |

### Regla de validacion

Debe existir al menos uno de estos campos:

```text
attribute
state
```

### Orden de salida

```text
system_entity_attribute_state_qualifier_equipment_position_signal_position_role_instance_signal_type
```

---

## Caso especial: spare

Las variables `Spare_In22_DI` y `Spare_Out45_DO` no deben usar una plantilla funcional normal.

```text
system = Spare
instance = In22 o Out45
signal_type = DI o DO
```

Plantilla:

```text
Spare_instance_signal_type
```

---

## Reglas generales pendientes de aprobacion

- [x] Implementar la estructura semantica base.
- [x] Implementar seleccion de plantilla.
- [x] Generar `template_tag` candidato sin eliminar la salida heredada.

- [ ] Confirmar que `system`, `entity`, `action` y `signal_type` son obligatorios en actuadores.
- [ ] Confirmar si `role` es obligatorio en feedbacks.
- [ ] Confirmar cuando una alarma puede existir sin `entity`.
- [ ] Confirmar si una salida `DO` puede tener `role` `ind`.
- [ ] Confirmar el orden exacto de `equipment_position` y `signal_position` en la tag final.
- [ ] Confirmar si `instance` se coloca antes o despues de la posicion.
- [ ] Confirmar si `subentity` se concatena con `entity` o se mantiene como segmento separado.
- [ ] Confirmar si los tags `Spare` deben conservar `In` y `Out`.
- [ ] Definir el comportamiento cuando falta un campo obligatorio.
- [ ] Definir el formato exacto de los tags con campos vacios.
