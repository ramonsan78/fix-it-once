---
name: registrar-rechazo
description: Registra un rechazo del responsable en biblia/referencias/no/motivos.csv, con su categoría, para que no vuelva a repetirse. Úsala cada vez que el responsable rechace una pieza, una toma, un frame o una miniatura y diga por qué.
---

# Registrar un rechazo

Un rechazo que no se anota se repite. Esta skill convierte la frase del responsable en una fila útil.

## Pasos

1. **Copia la pieza rechazada** a `biblia/referencias/no/` con el nombre `no_<motivo-corto>_<MMDD>.png` (o el formato que tenga). Ejemplo: `no_letra-ilegible_1204.png`.
2. **Clasifica el motivo** en una de tres categorías:
   - **defecto**: error objetivo que cualquiera vería (cara deformada, texto cortado, color fuera de paleta, duración pasada);
   - **preferencia**: gusto del responsable que se puede volver regla (cielo demasiado frío para una canción alegre);
   - **capricho**: rechazo puntual sin patrón ("no me gusta el ángulo").
   Si dudas entre preferencia y capricho, pregúntale al responsable en una línea.
3. **Relaciónalo con una regla** de `biblia/estilo.yaml` si existe (por ejemplo `composicion.zona_texto`). Si no existe ninguna, deja la columna vacía: es candidata a regla nueva.
4. **Agrega la fila** a `biblia/referencias/no/motivos.csv`:
   ```
   archivo,motivo,categoria,fecha,regla_relacionada
   ```
   El motivo va con las palabras del responsable, sin reinterpretarlo.
5. **Si es un defecto medible** (duración, resolución, nombre, color), propone en una línea agregarlo a `control/reglas.json` o a `control/chequeos.py`.

## Lo que no haces

- No cambias `estilo.yaml` ni `BIBLIA.md`. Las reglas nuevas se proponen una vez al mes con `proponer-reglas`.
- No discutes el rechazo. Se registra tal cual.
