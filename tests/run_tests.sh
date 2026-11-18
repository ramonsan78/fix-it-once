#!/usr/bin/env bash
# Runs the kit's checks script and publishing hook, in both languages, against sample videos.
# Pruebas del script de chequeos y del bloqueo de publicación, en los dos idiomas.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$ROOT/tests/tmp"
rm -rf "$TMP" && mkdir -p "$TMP/videos"
cd "$TMP/videos"

make() { ffmpeg -v error -y "$@"; }
make -f lavfi -i color=c=green:s=2560x1440:r=30 -f lavfi -i sine=f=440 -t 3 -shortest "Celebremos que Hay un Dios.mp4"
make -f lavfi -i color=c=green:s=1080x1920:r=30 -f lavfi -i sine=f=440 -t 22 -shortest "Celebremos que Hay un Dios - Reel.mp4"
make -f lavfi -i color=c=green:s=1080x1920:r=30 -t 7.2 "Celebremos que Hay un Dios - Canva.mp4"
make -f lavfi -i color=c=green:s=1080x1920:r=25 -t 10 "celebremos - Quote - 01.mp4"

fail=0
check_report() {
  python3 - "$1" "$2" <<'PY'
import json, sys
report, lang = json.load(open(sys.argv[1])), sys.argv[2]
errs = {(r.get("file") or r.get("archivo")): r.get("errors", r.get("errores")) for r in report}
ok = lambda n: errs[n] == []
bad = lambda n: len(errs[n]) > 0
assert ok("Celebremos que Hay un Dios.mp4"), "main video should pass"
assert ok("Celebremos que Hay un Dios - Canva.mp4"), "canva should pass"
assert len(errs["Celebremos que Hay un Dios - Reel.mp4"]) == 1, "reel should fail only on duration"
assert len(errs["celebremos - Quote - 01.mp4"]) == 3, "quote should fail on name, fps and audio"
print(f"[{lang}] checks: expected results")
PY
}

python3 "$ROOT/es/control/chequeos.py" . --json "$TMP/es.json" >/dev/null || true
check_report "$TMP/es.json" es || fail=1
python3 "$ROOT/en/checks/checks.py" . --json "$TMP/en.json" >/dev/null || true
check_report "$TMP/en.json" en || fail=1

hook() { # script dir batchword command expected_exit
  local script="$1" proj="$2" cmd="$3" want="$4"
  set +e
  echo "{\"tool_input\":{\"command\":\"$cmd\"}}" | CLAUDE_PROJECT_DIR="$proj" python3 "$script" 2>/dev/null
  local got=$?
  set -e
  if [ "$got" != "$want" ]; then echo "hook FAIL: '$cmd' got $got want $want"; fail=1; fi
}

P="$TMP/proj"; mkdir -p "$P/lotes/2026-12" "$P/batches/2026-12"
hook "$ROOT/es/control/bloquear-publicacion.py" "$P" "ls -la" 0
hook "$ROOT/es/control/bloquear-publicacion.py" "$P" "rclone copy salida drive:" 2
hook "$ROOT/es/control/bloquear-publicacion.py" "$P" "rclone copy lotes/2026-12/salida drive:" 2
echo '{}' > "$P/lotes/2026-12/aprobado.json"
hook "$ROOT/es/control/bloquear-publicacion.py" "$P" "rclone copy lotes/2026-12/salida drive:" 0
hook "$ROOT/en/checks/block-publishing.py" "$P" "ls -la" 0
hook "$ROOT/en/checks/block-publishing.py" "$P" "rclone copy batches/2026-12/output drive:" 2
echo '{}' > "$P/batches/2026-12/approved.json"
hook "$ROOT/en/checks/block-publishing.py" "$P" "rclone copy batches/2026-12/output drive:" 0
echo "hooks: done"

rm -rf "$TMP"
if [ "$fail" = 0 ]; then echo "All tests passed / Todas las pruebas pasaron"; else echo "Tests failed"; exit 1; fi
