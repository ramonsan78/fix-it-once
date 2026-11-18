# Proyecto: producción de [NOMBRE DEL CANAL]

Este repositorio produce el contenido del canal con el método "Se corrige una vez". Lee estas reglas al empezar cada sesión.

## Reglas que no se rompen

- Toda pieza nace de una ficha completa en `lotes/<AAAA-MM>/fichas/`. Si falta un dato, pregunta antes de producir.
- Todo lo visual se genera desde `biblia/estilo.yaml`. Nunca inventes reglas de estilo: si algo no está en la biblia, pregunta.
- El texto en pantalla (títulos, letras, citas, miniaturas) sale de las plantillas, nunca de un generador de imágenes.
- Ninguna generación con costo se lanza sin mostrar antes el prompt y el costo y recibir un "sí".
- Nada se publica ni se entrega sin `lotes/<AAAA-MM>/aprobado.json`. El hook de `.claude/settings.json` lo hace cumplir.
- El juez visual (`.claude/agents/juez.md`) descarta y ordena; nunca aprueba. La decisión final es del responsable.
- Cada rechazo del responsable se registra con `registrar-rechazo` en el momento.
- La biblia solo cambia una vez al mes, con `proponer-reglas` y la aprobación del responsable.

## Dónde está cada cosa

- Biblia de estilo: `biblia/`
- Fichas y piezas de cada mes: `lotes/<AAAA-MM>/`
- Límites por formato y regla de nombres: `control/reglas.json`
- Chequeos medibles: `python3 control/chequeos.py lotes/<AAAA-MM>/salida`

## Formatos de este canal

<!-- Ajusta a tus formatos. Deben coincidir con control/reglas.json -->
- Video principal: 2560x1440, duración completa
- Reel: 1080x1920, 20 s o menos
- Cita: 1080x1920, 30 s o menos
- Miniatura: 1920x1080 JPG

## Entrega

<!-- Dónde se entrega y a quién se avisa -->
- Carpeta final: [ruta o carpeta de Drive]
- Aviso: borrador de correo a [persona], solo se envía con el OK del responsable.

## Responsable

[Nombre]. Decide en cuatro momentos: lista del mes, finalistas, corte final y publicación.
