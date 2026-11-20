#!/usr/bin/env python3
"""Hook de Claude Code: impide publicar o entregar un lote sin la aprobación del responsable.

Se activa antes de comandos de terminal, ediciones de archivos y llamadas a conectores MCP
(ver .claude/settings.json).

Hace tres cosas:
1. Bloquea cualquier comando o llamada MCP que publique o entregue, salvo que el lote que
   nombra tenga un lotes/<AAAA-MM>/aprobado.json válido.
2. Impide que Claude cree o modifique aprobado.json. Solo lo escribe el responsable.
3. Revisa el contenido de la aprobación, no solo que el archivo exista.

Es una barrera contra errores, no una frontera de seguridad: un agente con terminal siempre
puede encontrar un camino que los patrones no prevén. El control real sigue siendo el OK del
responsable. Ajusta las listas de abajo a las herramientas que de verdad usas para publicar
o entregar.
"""

import json
import os
import re
import shlex
import sys
from datetime import date
from pathlib import Path

LOTES = "lotes"
ARCHIVO_APROBACION = "aprobado.json"
PATRON_LOTE = re.compile(r"lotes/(\d{4}-\d{2})")

# Comandos que publican o entregan por sí solos, o con uno de estos subcomandos.
COMANDOS_PUBLICAR = {
    "rclone": {"copy", "copyto", "sync", "move", "moveto", "rcat", "bisync"},
    "gsutil": {"cp", "mv", "rsync"},
    "gcloud": {"cp", "mv", "rsync"},          # gcloud storage cp ...
    "aws": {"cp", "mv", "sync"},              # aws s3 cp ...
    "az": {"upload", "upload-batch"},         # az storage blob upload ...
    "scp": None,                              # None: siempre publica
    "sftp": None,
    "gdrive": {"upload", "files"},
    "youtube-upload": None,
}
# Herramientas que publican solo si el destino es remoto (host:ruta) o una carpeta de entrega.
COMANDOS_COPIA = {"cp", "mv", "rsync", "ditto"}
# Carpetas sincronizadas que cuentan como entrega. Agrega las tuyas (por ejemplo la carpeta compartida del cliente).
CARPETAS_ENTREGA = ["Google Drive", "GoogleDrive", "My Drive", "Dropbox", "OneDrive",
                    "Library/CloudStorage", "iCloud Drive"]
# Tus propios scripts de publicación: su nombre empieza con una de estas palabras.
PREFIJOS_SCRIPT = ("publicar", "subir", "entregar", "publish", "upload", "deliver")
INTERPRETES = {"python", "python3", "node", "bash", "sh", "zsh", "deno", "bun", "npx"}
# Comandos de solo lectura que pueden tocar aprobado.json.
SOLO_LECTURA = {"cat", "ls", "head", "tail", "less", "more", "stat", "test", "[", "jq", "grep", "wc", "file", "diff"}
# Acciones MCP que escriben, envían o comparten. Se comparan con el nombre de la acción.
MCP_PUBLICAR = re.compile(
    r"(upload|create_file|update_file|copy|move|share|publish|send|post|insert|create_folder|"
    r"commit|create_shared_link|file_request)", re.IGNORECASE)


def bloquear(mensaje):
    print("Bloqueado: " + mensaje, file=sys.stderr)
    sys.exit(2)


def segmentos(comando):
    """Divide un comando de shell en comandos simples (por ; && || | y saltos de línea)."""
    parts = re.split(r"\|\||&&|;|\||\n", comando)
    out = []
    for part in parts:
        try:
            tokens = shlex.split(part, comments=True)
        except ValueError:
            tokens = part.split()
        while tokens and (re.match(r"^\w+=", tokens[0]) or tokens[0] in {"sudo", "env", "time", "nohup", "exec"}):
            tokens = tokens[1:]
        if tokens:
            out.append((part, tokens))
    return out


def es_carpeta_entrega(arg):
    expanded = os.path.expanduser(arg)
    return any(folder in expanded for folder in CARPETAS_ENTREGA)


def publica(tokens):
    name = os.path.basename(tokens[0])
    args = tokens[1:]
    if name in COMANDOS_PUBLICAR:
        subs = COMANDOS_PUBLICAR[name]
        return subs is None or any(a in subs for a in args)
    if name == "curl":
        return any(a in {"-T", "--upload-file", "-F", "--form"} or a.startswith("--data-binary") for a in args)
    if name in COMANDOS_COPIA:
        targets = [a for a in args if not a.startswith("-")]
        dest = targets[-1] if targets else ""
        remote = name in {"rsync", "scp"} and re.match(r"^[\w.-]+@?[\w.-]*:", dest or "")
        return bool(remote) or es_carpeta_entrega(dest)
    script = tokens[1] if name in INTERPRETES and len(tokens) > 1 else tokens[0]
    return os.path.basename(script).lower().startswith(PREFIJOS_SCRIPT)


def revisar_aprobacion(raiz, lote):
    ruta = raiz / LOTES / lote / ARCHIVO_APROBACION
    if not ruta.is_file():
        return f"el responsable no aprobó el lote {lote}: falta {LOTES}/{lote}/{ARCHIVO_APROBACION}."
    try:
        datos = json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return f"{LOTES}/{lote}/{ARCHIVO_APROBACION} no es un JSON válido."
    problemas = []
    if datos.get("lote") != lote:
        problemas.append(f'"lote" debe ser "{lote}"')
    if not str(datos.get("aprobado_por", "")).strip():
        problemas.append('"aprobado_por" está vacío')
    try:
        date.fromisoformat(str(datos.get("fecha", "")))
    except ValueError:
        problemas.append('"fecha" debe ser AAAA-MM-DD')
    piezas = datos.get("piezas")
    if not isinstance(piezas, list) or not piezas:
        problemas.append('"piezas" debe listar al menos una pieza aprobada')
    if problemas:
        return f"la aprobación del lote {lote} está incompleta: " + "; ".join(problemas) + "."
    return None


def exigir_aprobacion(raiz, texto, que):
    lotes = sorted(set(PATRON_LOTE.findall(texto)))
    if not lotes:
        bloquear(f"{que} publica o entrega, pero no nombra el lote ({LOTES}/AAAA-MM). "
                 "Incluye la ruta del lote para verificar su aprobación.")
    for lote in lotes:
        problema = revisar_aprobacion(raiz, lote)
        if problema:
            bloquear(problema + " Pide la aprobación del responsable antes de publicar o entregar.")


def main():
    try:
        evento = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    raiz = Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
    herramienta = evento.get("tool_name", "Bash")
    entrada = evento.get("tool_input") or {}
    solo_responsable = (f"solo el responsable crea o edita {ARCHIVO_APROBACION}. "
                        "Muéstrale el contenido y deja que lo guarde.")

    # 1. Claude nunca escribe el archivo de aprobación.
    if herramienta in {"Write", "Edit", "MultiEdit", "NotebookEdit"}:
        destino = entrada.get("file_path") or entrada.get("notebook_path") or ""
        if os.path.basename(destino) == ARCHIVO_APROBACION:
            bloquear(solo_responsable)
        sys.exit(0)

    # 2. Conectores MCP (Drive, Dropbox, YouTube, email...).
    if herramienta.startswith("mcp__"):
        accion = herramienta.split("__")[-1]
        if MCP_PUBLICAR.search(accion):
            exigir_aprobacion(raiz, json.dumps(entrada, ensure_ascii=False), "esta acción del conector")
        sys.exit(0)

    # 3. Comandos de terminal.
    if herramienta != "Bash":
        sys.exit(0)
    comando = entrada.get("command", "")
    for crudo, tokens in segmentos(comando):
        nombre = os.path.basename(tokens[0])
        if ARCHIVO_APROBACION in crudo and nombre not in SOLO_LECTURA:
            bloquear(solo_responsable)
        if publica(tokens):
            exigir_aprobacion(raiz, crudo, "este comando")
    sys.exit(0)


if __name__ == "__main__":
    main()
