---
name: generar-piezas
description: Genera las variantes visuales de las piezas de un lote a partir de sus fichas y de la biblia de estilo. Úsala cuando el responsable pida producir, generar o preparar las imágenes o fondos de un lote o de una pieza.
---

# Generar piezas

Genera solo lo que cambia en cada pieza (la imagen o el fondo). El texto, la tipografía y la marca salen de las plantillas, nunca de un generador.

## Antes de generar

1. Lee `biblia/estilo.yaml` completo. Anota la versión: cada pieza la registra.
2. Lee las fichas de `lotes/<lote>/fichas/`. Valida cada una:
   - título según la regla de nombres de `control/reglas.json`;
   - cada cita aparece literal en el texto de origen;
   - los archivos de origen existen;
   - la emoción existe en `por_emocion`. Si no existe, no la inventes: marca la ficha y pregunta.
   Si una ficha falla, avisa de todas las fallas juntas y no generes esa pieza.
3. Revisa qué herramienta de generación está conectada (MCP de Runway, Krea, ComfyUI, Adobe Firefly u otra).

## Cómo armar cada prompt

```
<prompt_base de estilo.yaml>, <tratamiento de la emoción en por_emocion>,
<escena: dos o tres imágenes concretas que aparecen en el texto de la pieza>
```

- Usa las imágenes de `biblia/referencias/si/` como referencias de estilo si la herramienta lo permite.
- Agrega el `prompt_negativo` donde la herramienta lo acepte.
- Prompts cortos y en orden de prioridad: los prompts largos empeoran el resultado.
- Formato del `composicion.formato` de la biblia.

## Generar

1. **Muestra el plan y el costo antes de gastar.** Una tabla: pieza, prompt, número de variantes (`filtro.variantes_por_pieza`), herramienta y costo estimado en créditos. Espera un "sí" explícito del responsable.
2. Genera y guarda en `lotes/<lote>/candidatas/<id-pieza>/`, con nombres `v01.png`, `v02.png`, etc.
3. Guarda junto a ellas `generacion.json` con: prompt exacto, herramienta, modelo y versión, semilla si existe, versión de la biblia y fecha. Sirve para repetir o auditar.

Si no hay ninguna herramienta conectada, escribe los prompts en `lotes/<lote>/candidatas/<id-pieza>/prompts.md` para que el responsable los corra a mano, y dilo.

## Después

Pasa el lote a la skill `revisar-piezas`. No muestres las candidatas crudas al responsable salvo que lo pida.
