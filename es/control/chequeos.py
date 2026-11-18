#!/usr/bin/env python3
"""Chequeos medibles de un lote de videos.

Revisa cada video de una carpeta contra control/reglas.json:
nombre, resolución, fps, duración y presencia de audio.
No opina sobre estética: eso es trabajo del juez y del responsable.

Uso:
    python3 control/chequeos.py lotes/2026-12/salida
    python3 control/chequeos.py lotes/2026-12/salida --reglas control/reglas.json --json reporte.json

Sale con código 0 si todo pasa y 1 si algún video falla.
Requiere ffprobe (viene con FFmpeg).
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

EXTENSIONES = {".mp4", ".mov"}


def cargar_reglas(ruta):
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def sondear(video):
    """Devuelve ancho, alto, fps, duración y si hay audio, según ffprobe."""
    cmd = [
        "ffprobe", "-v", "error", "-print_format", "json",
        "-show_streams", "-show_format", str(video),
    ]
    salida = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    datos = json.loads(salida)
    video_s = next((s for s in datos.get("streams", []) if s.get("codec_type") == "video"), None)
    audio = any(s.get("codec_type") == "audio" for s in datos.get("streams", []))
    duracion = float(datos.get("format", {}).get("duration", 0) or 0)
    ancho = alto = None
    fps = None
    if video_s:
        ancho, alto = video_s.get("width"), video_s.get("height")
        num, _, den = (video_s.get("avg_frame_rate") or "0/1").partition("/")
        try:
            fps = round(float(num) / float(den or 1), 3)
        except ZeroDivisionError:
            fps = None
    return {"ancho": ancho, "alto": alto, "fps": fps, "duracion_s": round(duracion, 3), "audio": audio}


def detectar_formato(nombre, formatos):
    """Elige el formato cuyo sufijo coincide con el nombre; el sufijo más largo gana."""
    base = Path(nombre).stem
    candidatos = []
    for clave, f in formatos.items():
        sufijo = f.get("sufijo", "")
        if sufijo and base.endswith(sufijo):
            candidatos.append((len(sufijo), clave))
    if candidatos:
        return max(candidatos)[1]
    sin_sufijo = [k for k, f in formatos.items() if not f.get("sufijo")]
    return sin_sufijo[0] if sin_sufijo else None


def revisar(video, reglas):
    errores = []
    nombre = video.name
    patron = reglas.get("nombre_archivo", {}).get("patron")
    if patron and not re.match(patron, nombre):
        errores.append("el nombre no cumple la regla de nombres")

    clave = detectar_formato(nombre, reglas["formatos"])
    if clave is None:
        return {"archivo": nombre, "formato": None, "errores": ["no coincide con ningún formato"]}
    formato = reglas["formatos"][clave]

    try:
        info = sondear(video)
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return {"archivo": nombre, "formato": clave, "errores": ["ffprobe no pudo leer el archivo"]}

    if (info["ancho"], info["alto"]) != (formato["ancho"], formato["alto"]):
        errores.append(f"resolución {info['ancho']}x{info['alto']}, se esperaba {formato['ancho']}x{formato['alto']}")

    fps_esperado = reglas.get("fps")
    if fps_esperado and info["fps"] and abs(info["fps"] - fps_esperado) > 0.01:
        errores.append(f"fps {info['fps']}, se esperaba {fps_esperado}")

    tol = reglas.get("tolerancia_duracion_s", 0.1)
    if formato.get("duracion_max_s") is not None and info["duracion_s"] > formato["duracion_max_s"] + tol:
        errores.append(f"dura {info['duracion_s']} s, el máximo es {formato['duracion_max_s']} s")
    if formato.get("duracion_exacta_s") is not None and abs(info["duracion_s"] - formato["duracion_exacta_s"]) > tol:
        errores.append(f"dura {info['duracion_s']} s, debe durar {formato['duracion_exacta_s']} s")

    if formato.get("audio") and not info["audio"]:
        errores.append("no tiene audio")
    if formato.get("audio") is False and info["audio"]:
        errores.append("tiene audio y este formato va sin audio")

    return {"archivo": nombre, "formato": clave, **info, "errores": errores}


def main():
    raiz = Path(__file__).resolve().parent
    p = argparse.ArgumentParser(description="Chequeos medibles de un lote de videos.")
    p.add_argument("carpeta", help="carpeta con los videos del lote")
    p.add_argument("--reglas", default=str(raiz / "reglas.json"), help="ruta a reglas.json")
    p.add_argument("--json", help="guarda el reporte completo en este archivo")
    args = p.parse_args()

    if not shutil.which("ffprobe"):
        sys.exit("Falta ffprobe. Instala FFmpeg y vuelve a intentar.")

    carpeta = Path(args.carpeta)
    if not carpeta.is_dir():
        sys.exit(f"No existe la carpeta {carpeta}")

    reglas = cargar_reglas(args.reglas)
    videos = sorted(v for v in carpeta.rglob("*") if v.suffix.lower() in EXTENSIONES)
    if not videos:
        sys.exit(f"No hay videos en {carpeta}")

    resultados = [revisar(v, reglas) for v in videos]
    fallidos = [r for r in resultados if r["errores"]]

    for r in resultados:
        estado = "FALLA" if r["errores"] else "ok"
        print(f"[{estado}] {r['archivo']} ({r['formato'] or 'sin formato'})")
        for e in r["errores"]:
            print(f"        - {e}")
    print(f"\n{len(resultados) - len(fallidos)} de {len(resultados)} videos pasan los chequeos.")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(resultados, f, ensure_ascii=False, indent=2)
        print(f"Reporte guardado en {args.json}")

    sys.exit(1 if fallidos else 0)


if __name__ == "__main__":
    main()
