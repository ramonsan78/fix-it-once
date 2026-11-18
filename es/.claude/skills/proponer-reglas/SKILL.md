---
name: proponer-reglas
description: Una vez al mes, revisa los rechazos registrados y propone cambios a la biblia de estilo, al CHANGELOG y a los chequeos, para que el responsable los apruebe en una sola sesión. Úsala al cerrar cada mes o cuando el responsable pida actualizar la biblia.
---

# Proponer reglas

La biblia cambia una vez al mes, nunca a mitad de semana. Esta skill prepara ese cambio para que el responsable lo decida en diez minutos.

## Pasos

1. **Lee los rechazos del mes** en `biblia/referencias/no/motivos.csv` (filtra por fecha) y las sugerencias de los `juicio.md` del juez en `lotes/<lote>/finalistas/`.
2. **Agrupa por patrón.** Un patrón es el mismo motivo, con otras palabras, en dos o más piezas.
3. **Decide qué propone cada patrón:**
   - **defecto repetido** → un chequeo nuevo en `control/reglas.json` o `control/chequeos.py`, o ejemplos nuevos para el juez;
   - **preferencia repetida** → una regla nueva o ajustada en `estilo.yaml` y su explicación en `BIBLIA.md`;
   - **caprichos** → no proponen nada. Menciónalos solo si se repiten tres veces o más.
4. **Escribe la propuesta** en la sección "Pendientes" de `biblia/CHANGELOG.md`, una línea por cambio con su origen:
   ```
   - Zona de texto pasa de 25% a 30% del alto.
     Origen: 4 rechazos por letra sobre vegetación densa (1104, 1111, 1118, 1125).
   ```
5. **Muestra al responsable** una tabla corta: cambio, origen, qué archivo toca. Pide un sí o un no por fila.

## Cuando el responsable aprueba

1. Aplica cada cambio aprobado en `estilo.yaml` y en `BIBLIA.md` a la vez, para que nunca digan cosas distintas.
2. Sube la versión (1.0 → 1.1) en `estilo.yaml` y mueve los cambios de "Pendientes" a una entrada nueva del `CHANGELOG` con la fecha.
3. Los cambios rechazados se borran de "Pendientes" y no se vuelven a proponer salvo que aparezcan rechazos nuevos.
4. Si el cambio es grande (otra paleta, otra técnica), sugiere reentrenar el modelo de estilo, si existe uno, y probarlo aparte antes de usarlo.
