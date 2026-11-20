# Se corrige una vez

Kit para producir contenido con IA sin correcciones infinitas. Cada corrección se hace una sola vez, sobre el sistema, y no vuelve a pedirse.

Léete primero la guía (`docs/GUIA.md` en el repositorio): explica el porqué de cada archivo.

## Qué trae

```
se-corrige-una-vez/
├── README.md                     este archivo
├── CLAUDE.md                     instrucciones del proyecto para Claude Code
├── biblia/
│   ├── estilo.yaml               reglas medibles, las que lee la máquina
│   ├── BIBLIA.md                 las mismas reglas explicadas para personas
│   ├── CHANGELOG.md              qué regla cambió, cuándo y por qué
│   └── referencias/
│       ├── si/                   piezas aprobadas
│       └── no/                   piezas rechazadas
│           └── motivos.csv       una fila por rechazo
├── ficha/
│   ├── pieza.json                ficha de una pieza, lista para copiar
│   └── ficha-de-entrada.csv      la misma ficha en columnas, para Google Sheets
├── control/
│   ├── reglas.json               límites por formato y regla de nombres
│   ├── chequeos.py               revisa videos y miniaturas: duración, resolución, fps, audio y nombres
│   ├── bloquear-publicacion.py   hook que impide publicar un lote sin aprobar
│   └── checklist-revision.md     lo que revisa una persona, y solo eso
├── lotes/
│   └── README.md                  cómo se organiza cada lote y su aprobación
└── .claude/
    ├── settings.json             activa el hook de publicación
    ├── agents/juez.md            el juez visual, separado del que genera
    └── skills/
        ├── generar-piezas/
        ├── revisar-piezas/
        ├── registrar-rechazo/
        └── proponer-reglas/
```

## Cómo empezar

1. Copia esta carpeta a un repositorio nuevo (`git init`) y ábrela con Claude Code.
2. Llena `biblia/estilo.yaml` y `biblia/BIBLIA.md`. Los valores de ejemplo son de un canal de música con ilustraciones; reemplázalos por los tuyos.
3. Pon entre 10 y 30 piezas aprobadas en `biblia/referencias/si/` y las rechazadas en `biblia/referencias/no/`, con su motivo en `motivos.csv`.
4. Ajusta `control/reglas.json` a tus formatos y a tu regla de nombres.
5. Edita `CLAUDE.md` con el nombre de tu canal y dónde entregas.
6. Pide a Claude Code: "valida las fichas del lote 2026-12 y genera las variantes". Las skills hacen el resto.

## Requisitos

- Claude Code.
- Python 3.9 o más reciente y FFmpeg (incluye `ffprobe`) para los chequeos.
- Opcional: conectores MCP de tus herramientas de generación (Runway, Krea, ComfyUI), de Adobe y de tu almacenamiento (Google Drive, Dropbox). Sin ellos, las skills preparan los prompts para que los corras tú.

## Una advertencia

La plantilla fija la identidad visual, nunca la estructura ni la idea de cada pieza. YouTube no monetiza los canales cuyo contenido parece hecho con una plantilla o se siente intercambiable de un video a otro: es su política de "contenido inauténtico", llamada "contenido repetitivo" hasta julio de 2025 y aclarada de nuevo en julio de 2026. Revisa la versión vigente en https://support.google.com/youtube/answer/1311392

Licencia: el código va con licencia MIT y los textos con CC BY 4.0. Ver `LICENSE` y `LICENSE-DOCS.md` en la raíz del repositorio original: https://github.com/ramonsan78/fix-it-once
