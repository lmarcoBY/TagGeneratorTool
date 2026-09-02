# Revision del Master Dictionary

## Estado

Se ha anadido una taxonomia semantica nueva en `Master_Dictionary_v1.0.yaml`. Las categorias antiguas se mantienen temporalmente para compatibilidad con el codigo existente.

## Categorias semanticas anadidas

- `systems`
- `signal_types`
- `entities`
- `subentities`
- `attributes`
- `states`
- `actions`
- `qualifiers`
- `equipment_positions`
- `signal_positions`
- `roles`
- `instances`
- `composite_positions`
- `reclassification`

## Reclasificaciones principales

| Categoria antigua | Categoria semantica | Tokens representativos |
| --- | --- | --- |
| `components` | `entities` | `anchor`, `winch`, `pump`, `filter`, `tank`, `engine` |
| `components` | `subentities` | `arm`, `car`, `chain`, `pto`, `vlv`, `sheet` |
| `components` | `attributes` | `pressure`, `temperature`, `level`, `flow`, `power`, `speed` |
| `modifiers` | `states` | `high`, `low`, `full`, `fault`, `overload`, `running`, `on`, `off` |
| `components`/`modifiers` | `qualifiers` | `main`, `inner`, `primary`, `secondary`, `oil`, `cooling` |
| `locations` | `equipment_positions` | `pt`, `sb`, `fwd`, `aft`, `mid`, `msi` |
| `locations` | `signal_positions` | `ped`, `coam`, `mast`, `er`, `fp`, `laz` |
| `roles` | `roles` | `btn`, `fsw`, `ls`, `psw`, `sw`, `feedback`, `ind`, `alarm` |

## Composicion de entidades

Las entidades compuestas no se almacenan como conceptos independientes en el diccionario. Se forman posteriormente a partir de tokens clasificados como `entity`, `subentity`, `qualifier`, `attribute` y posiciones.

Ejemplos:

```text
entity winch + qualifier haly -> halyWinch
entity furler + qualifier jib -> jibFurler
entity winch + qualifier mooring -> mooringWinch
entity filter + qualifier oil -> oilFilter
entity tank + qualifier oil + attribute level -> oilLevel
```

### Entidades

```text
anchorWindlass
anchorArm
bowThruster
dinghyWinch
halyWinch
jibFurler
mainSheetWinch
mooringWinch
pressureFilter
pressFilter
oilFilter
oilLevel
greyWaterTank
blackWaterTank
```

### Posiciones

```text
aftPt
aftSb
fwdPt
fwdSb
ptPed
sbPed
ptMast
sbMast
ptMsi
sbMsi
ptCoam
sbCoam
sbSide
```

Las posiciones compuestas tampoco son entidades. Se forman con partes clasificadas segun el contexto: `equipment_position` para el equipo y `signal_position` para el origen de la senal.

## Regla entity/subentity

Un concepto puede aparecer en `entities` y `subentities` cuando el dominio lo usa en dos niveles distintos. Por ejemplo, `winch`, `windlass`, `furler`, `thruster` y `filter` pueden ser equipos independientes o partes funcionales de una entidad compuesta.

La categoria final no se decide solo por el token. Se decide por su posicion y contexto:

```text
entity winch + qualifier haly -> halyWinch
entity winch + qualifier mooring -> mooringWinch
entity filter + qualifier oil -> oilFilter
entity tank + qualifier oil + attribute level -> oilLevel
```

Esta reutilizacion contextual es intencionada. Un duplicado dentro de la misma categoria no es valido.

## Problemas conceptuales que siguen pendientes

- El mismo token puede cambiar de categoria segun el contexto. Ejemplos: `open`, `stop`, `enable`, `on`, `in`.
- `GenFwd`, `GenAft` y `Alrm` aparecen en las tags corregidas, pero su uso como sistema o entidad debe formalizarse.
- Los identificadores `HC01`, `HC02`, `In22` y `Out45` requieren distinguir panel, instancia y canal tecnico.
- Las posiciones compuestas deben separar `equipment_position` de `signal_position`.
- `fast`, `slow`, `cw` y `ccw` pueden ser qualifier, action o state segun la plantilla.
- `running`, `feedback`, `alarm` y `ind` no son equivalentes: los primeros pueden ser estados y los ultimos roles.
- Las composiciones de la lista corregida todavia deben validarse en la Naming Engine.
- La lista antigua sigue activa y puede producir clasificaciones diferentes a la taxonomia semantica.

## Siguiente paso recomendado

Definir reglas de mapeo por plantilla, no seguir trasladando tokens individualmente:

1. Para cada plantilla, definir que categoria puede ocupar cada campo.
2. Definir prioridad contextual para tokens ambiguos.
3. Definir composiciones de entidad y posicion en la Naming Engine.
4. Probar las reglas contra `onyx_vars_corrected`.
5. Solo despues retirar progresivamente las categorias antiguas.
