#!/usr/bin/env bash
# Runs the kit's checks script and publishing hook, in both languages, against sample files.
# Pruebas del script de chequeos y del bloqueo de publicación, en los dos idiomas.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$ROOT/tests/tmp"
rm -rf "$TMP" && mkdir -p "$TMP/videos" "$TMP/thumbs-en" "$TMP/thumbs-es"
command -v ffmpeg >/dev/null || { echo "ffmpeg is missing"; exit 1; }

make() { ffmpeg -v error -y "$@"; }
cd "$TMP/videos"
make -f lavfi -i color=c=green:s=2560x1440:r=30 -f lavfi -i sine=f=440 -t 3 -shortest "Luz de la Mañana.mp4"
make -f lavfi -i color=c=green:s=1080x1920:r=30 -f lavfi -i sine=f=440 -t 22 -shortest "Luz de la Mañana - Reel.mp4"
make -f lavfi -i color=c=green:s=1080x1920:r=30 -t 7.2 "Luz de la Mañana - Canva.mp4"
make -f lavfi -i color=c=green:s=1080x1920:r=25 -t 10 "luz - Quote - 01.mp4"
make -f lavfi -i color=c=blue:s=1920x1080 -frames:v 1 "$TMP/thumbs-en/Morning Light - Thumbnail.jpg"
make -f lavfi -i color=c=blue:s=1280x720 -frames:v 1 "$TMP/thumbs-en/Morning Light 2 - Thumbnail.jpg"
make -f lavfi -i color=c=blue:s=1920x1080 -frames:v 1 "$TMP/thumbs-en/Morning Light.jpg"
make -f lavfi -i color=c=blue:s=1920x1080 -frames:v 1 "$TMP/thumbs-es/Luz de la Mañana - Miniatura.jpg"
make -f lavfi -i color=c=blue:s=1280x720 -frames:v 1 "$TMP/thumbs-es/Luz de la Mañana 2 - Miniatura.jpg"
make -f lavfi -i color=c=blue:s=1920x1080 -frames:v 1 "$TMP/thumbs-es/Luz de la Mañana.jpg"

fail=0
check_videos() {
  python3 - "$1" "$2" <<'PY'
import json, sys
report, lang = json.load(open(sys.argv[1])), sys.argv[2]
errs = {(r.get("file") or r.get("archivo")): r.get("errors", r.get("errores")) for r in report}
ok = lambda n: errs[n] == []
assert len(errs) == 4, f"expected 4 videos, got {len(errs)}"
assert ok("Luz de la Mañana.mp4"), "main video should pass"
assert ok("Luz de la Mañana - Canva.mp4"), "canva should pass"
assert len(errs["Luz de la Mañana - Reel.mp4"]) == 1, "reel should fail only on duration"
assert len(errs["luz - Quote - 01.mp4"]) == 3, "quote should fail on name, fps and audio"
print(f"[{lang}] checks, videos: expected results")
PY
}
check_thumbs() {
  python3 - "$1" "$2" "$3" <<'PY'
import json, sys
report, lang, base = json.load(open(sys.argv[1])), sys.argv[2], sys.argv[3]
suffix = " - Thumbnail" if lang == "en" else " - Miniatura"
errs = {(r.get("file") or r.get("archivo")): r.get("errors", r.get("errores")) for r in report}
good, small, nosuffix = f"{base}{suffix}.jpg", f"{base} 2{suffix}.jpg", f"{base}.jpg"
assert errs[good] == [], f"good thumbnail should pass: {errs[good]}"
assert len(errs[small]) == 1 and "1280x720" in errs[small][0], f"small thumbnail should fail on resolution: {errs[small]}"
assert errs[nosuffix], "an image with no format suffix should fail"
print(f"[{lang}] checks, thumbnails: expected results")
PY
}

python3 "$ROOT/es/control/chequeos.py" . --json "$TMP/es.json" >/dev/null || true
check_videos "$TMP/es.json" es || fail=1
python3 "$ROOT/en/checks/checks.py" . --json "$TMP/en.json" >/dev/null || true
check_videos "$TMP/en.json" en || fail=1
python3 "$ROOT/en/checks/checks.py" "$TMP/thumbs-en" --json "$TMP/en-thumbs.json" >/dev/null || true
check_thumbs "$TMP/en-thumbs.json" en "Morning Light" || fail=1
python3 "$ROOT/es/control/chequeos.py" "$TMP/thumbs-es" --json "$TMP/es-thumbs.json" >/dev/null || true
check_thumbs "$TMP/es-thumbs.json" es "Luz de la Mañana" || fail=1

# Unreadable fps must be an error, not a silent pass.
# Si no se pueden leer los fps, debe ser un error, no un aprobado silencioso.
python3 - "$ROOT" "$TMP/videos/Luz de la Mañana.mp4" <<'PY' || fail=1
import importlib.util, json, sys
from pathlib import Path
root, video = Path(sys.argv[1]), Path(sys.argv[2])
for lang, rel, rules, probe in [("en", "en/checks/checks.py", "en/checks/rules.json", "probe"),
                                ("es", "es/control/chequeos.py", "es/control/reglas.json", "sondear")]:
    spec = importlib.util.spec_from_file_location(f"chk_{lang}", root / rel)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    real = getattr(mod, probe)
    def no_fps(v, real=real):
        info = real(v); info["fps"] = None; return info
    setattr(mod, probe, no_fps)
    check = getattr(mod, "check", None) or getattr(mod, "revisar")
    result = check(video, json.load(open(root / rules, encoding="utf-8")))
    errors = result.get("errors", result.get("errores"))
    assert len(errors) == 1 and "fps" in errors[0], f"[{lang}] unreadable fps should be one error: {errors}"
    print(f"[{lang}] checks, unreadable fps: expected result")
PY

python3 "$ROOT/tests/test_hooks.py" || fail=1

rm -rf "$TMP"
if [ "$fail" = 0 ]; then echo "All tests passed / Todas las pruebas pasaron"; else echo "Tests failed"; exit 1; fi
