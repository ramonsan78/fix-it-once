#!/usr/bin/env python3
"""Hook de Claude Code: impide publicar o entregar un lote sin aprobación.

Se activa antes de cada comando de terminal (ver .claude/settings.json).
Si el comando publica o entrega (subidas, rclone, scripts de publicación),
exige que exista lotes/<AAAA-MM>/aprobado.json para el lote nombrado en el comando.
Si no existe, bloquea el comando y le explica a Claude por qué.

Ajusta PATRON_PUBLICAR a las herramientas que uses para publicar o entregar.
"""

import json
import os
import re
import sys
from pathlib import Path

PATRON_PUBLICAR = re.compile(r"(publicar|rclone\s+(copy|sync|move)|youtube|upload)", re.IGNORECASE)
PATRON_LOTE = re.compile(r"lotes/(\d{4}-\d{2})")


def main():
    try:
        evento = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    comando = (evento.get("tool_input") or {}).get("command", "")
    if not PATRON_PUBLICAR.search(comando):
        sys.exit(0)

    raiz = Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
    lotes = PATRON_LOTE.findall(comando)
    if not lotes:
        print(
            "Bloqueado: este comando publica o entrega, pero no nombra el lote (lotes/AAAA-MM). "
            "Incluye la ruta del lote para verificar su aprobación.",
            file=sys.stderr,
        )
        sys.exit(2)

    faltan = [l for l in sorted(set(lotes)) if not (raiz / "lotes" / l / "aprobado.json").is_file()]
    if faltan:
        print(
            "Bloqueado: el responsable no aprobó el lote " + ", ".join(faltan) +
            ". Falta lotes/<lote>/aprobado.json. Pide la aprobación antes de publicar o entregar.",
            file=sys.stderr,
        )
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
