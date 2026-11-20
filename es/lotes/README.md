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

Lo escribe el responsable, a mano. Claude puede mostrarle el contenido para pegar, pero nunca crea ni edita este archivo: el hook lo bloquea.

```json
{
  "lote": "2026-12",
  "aprobado_por": "Nombre",
  "fecha": "2026-12-18",
  "piezas": ["2026-12-luz-de-la-manana", "2026-12-camino-a-casa"],
  "notas": ""
}
```

Antes de cualquier publicación o entrega del lote, el hook `control/bloquear-publicacion.py` revisa que este archivo exista y esté completo: `lote` coincide con la carpeta, `aprobado_por` tiene nombre, `fecha` es AAAA-MM-DD y `piezas` lista al menos una pieza. El hook no revisa qué pieza entrega cada comando: eso sigue siendo decisión del responsable.
