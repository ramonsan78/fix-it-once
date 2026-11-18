# Lotes

Un lote es la producción de un mes de un canal. Se construye, se revisa y se renderiza junto.

```
lotes/
└── 2026-12/
    ├── fichas/           una ficha pieza.json por pieza
    ├── origen/           audio, textos y fondos que llegan
    ├── candidatas/       variantes generadas, antes del filtro
    ├── finalistas/       las 2 o 3 que pasan los filtros, por pieza
    ├── salida/           videos e imágenes finales
    ├── reporte.json      resultado de control/chequeos.py
    └── aprobado.json     lo crea el responsable al aprobar; sin él no se publica
```

## aprobado.json

Lo escribe el responsable (o Claude, cuando el responsable lo dice expresamente en el chat):

```json
{
  "lote": "2026-12",
  "aprobado_por": "Nombre",
  "fecha": "2026-12-18",
  "piezas": ["2026-12-celebremos", "2026-12-viene-tocando"],
  "notas": ""
}
```

El hook `control/bloquear-publicacion.py` revisa que este archivo exista antes de cualquier publicación o entrega del lote.
