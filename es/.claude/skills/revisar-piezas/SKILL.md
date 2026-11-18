---
name: revisar-piezas
description: Filtra un lote antes de que lo vea el responsable. Corre los chequeos medibles y el juez visual, y deja 2 o 3 finalistas por pieza en una galería. Úsala después de generar variantes o de renderizar, y siempre antes de pedir una aprobación.
---

# Revisar piezas

El responsable solo debe ver lo que requiere su criterio. Esta skill descarta todo lo demás.

## Imágenes candidatas

1. Para cada pieza con candidatas en `lotes/<lote>/candidatas/<id-pieza>/`, lanza el agente `juez` (`.claude/agents/juez.md`) con esa carpeta y la ficha. Un agente distinto del que generó, siempre.
2. Copia las finalistas a `lotes/<lote>/finalistas/<id-pieza>/` junto con su `juicio.md`.
3. Si el juez no dejó ninguna finalista para una pieza, no la muestres: informa qué regla falló y propone regenerar con un ajuste concreto.

## Videos renderizados

1. Corre `python3 control/chequeos.py lotes/<lote>/salida --json lotes/<lote>/reporte.json`.
2. Si algo falla, arréglalo antes de mostrar nada. Solo si no puedes arreglarlo, explica el fallo al responsable en una línea por archivo.

## La galería

Arma una sola página para el lote (un artefacto de Claude o un HTML en `lotes/<lote>/galeria.html`) con:

- una fila por pieza: título, emoción y sus 2 o 3 finalistas lado a lado, en el orden del juez;
- debajo de cada finalista, la línea del juez;
- un espacio para que el responsable marque la elegida y escriba una frase por cada rechazo.

Luego pide la revisión con un solo mensaje: cuántas piezas, cuántas finalistas y qué decisiones hacen falta. No preguntes pieza por pieza.

## Cuando el responsable responde

- Elegidas: muévelas a `lotes/<lote>/elegidas/`.
- Cada rechazo con motivo: pásalo a la skill `registrar-rechazo` en el momento.
