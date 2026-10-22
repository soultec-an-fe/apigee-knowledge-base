#!/usr/bin/env python3
"""Inventario de la documentación oficial de Apigee a partir de la navegación de los sitios.

Cada página de devsite (docs.cloud.google.com y docs.apigee.com) trae en su HTML el menú
lateral completo de su "libro" (Guides, Reference, hybrid, API hub...). El script parte de
unas páginas semilla, lee su menú y, cada vez que aparece un prefijo de sección no visto,
visita una página de ese prefijo para leer su menú. Termina cuando no aparecen prefijos
nuevos. Escribe un TSV por edición en `inventario/` con: url, libro, seccion, subseccion.

Por qué no usa sitemaps: en oct-2026 los sitemaps hoja de ambos dominios
(sitemap_N_of_70.xml, sitemap_N_of_3.xml) devolvían HTTP 500 de forma sostenida.

Uso:
    python3 scripts/inventario_oficial.py            # reusa la caché de .cache/inventario
    python3 scripts/inventario_oficial.py --fresco   # descarga todo de nuevo

Solo usa la biblioteca estándar. Determinista para una misma caché (salida ordenada por URL).
"""

from __future__ import annotations

import csv
import pathlib
import re
import sys
import time
import urllib.parse
import urllib.request

UA = "Mozilla/5.0 (apigee-knowledge-base inventario)"
RAIZ = pathlib.Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "inventario"
CACHE = RAIZ / ".cache" / "inventario"  # descargas crudas; se borra con --fresco

X = "https://docs.cloud.google.com/apigee/docs/"
E = "https://docs.apigee.com/"
FUENTES = {
    # edición: (filtro de path, cuántos segmentos forman el "prefijo de sección", semillas)
    "x-hybrid": (
        lambda p: p.startswith("/apigee/docs/"),
        4,  # /apigee/docs/<libro>/<seccion>
        [X + s for s in (
            "api-platform/get-started/what-apigee",
            "api-platform/reference/policies/reference-overview-policy",
            "hybrid/latest/what-is-hybrid",
            "api-hub/what-is-api-hub",
            "api-security/overview",
            "release-notes",
        )],
    ),
    "edge": (
        lambda p: (p.split("/") + ["", ""])[1] in ("api-platform", "private-cloud", "api-monitoring", "release", "hybrid"),
        3,  # /<libro>/<seccion>
        [E + s for s in (
            "api-platform/get-started/what-apigee-edge",
            "api-platform/reference/policies/reference-overview-policy",
            "private-cloud/latest/overview",
            "release/notes/apigee-edge-release-notes",
        )],
    ),
}


def descargar(url: str, intentos: int = 4) -> bytes:
    cache = CACHE / re.sub(r"[^A-Za-z0-9._-]", "_", url)
    if cache.exists():
        return cache.read_bytes()
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for n in range(intentos):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                datos = r.read()
            CACHE.mkdir(parents=True, exist_ok=True)
            cache.write_bytes(datos)
            return datos
        except OSError as e:  # HTTPError, URLError y socket.timeout heredan de OSError
            if n == intentos - 1:
                raise RuntimeError(f"{url}: {e}") from e
            time.sleep(2 ** n)
    raise AssertionError("inalcanzable")


def enlaces(html: str, base: str, filtro) -> set[str]:
    host = urllib.parse.urlparse(base).netloc
    out = set()
    for href in re.findall(r'href="([^"#?]+)"', html):
        url = urllib.parse.urljoin(base, href).rstrip("/")
        p = urllib.parse.urlparse(url)
        if p.netloc == host and filtro(p.path) and not p.path.endswith((".png", ".svg", ".pdf", ".zip")):
            out.add(url)
    return out


def prefijo(url: str, n: int) -> str:
    return "/".join(urllib.parse.urlparse(url).path.split("/")[:n])


def inventariar(edicion: str) -> list[dict]:
    filtro, n, semillas = FUENTES[edicion]
    paginas: set[str] = set()
    vistos: set[str] = set()
    pendientes = list(semillas)
    while pendientes:
        url = pendientes.pop(0)
        vistos.add(prefijo(url, n))
        try:
            html = descargar(url).decode("utf-8", "replace")
        except RuntimeError as e:
            print(f"  aviso: se omite {e}", file=sys.stderr)
            continue
        paginas.add(url.rstrip("/"))
        for u in sorted(enlaces(html, url, filtro)):
            paginas.add(u)
            pre = prefijo(u, n)
            if pre not in vistos:
                vistos.add(pre)
                pendientes.append(u)
    filas = []
    salto = 2 if edicion == "x-hybrid" else 0  # quita "apigee/docs" en X
    for url in sorted(paginas):
        partes = [p for p in urllib.parse.urlparse(url).path.split("/") if p][salto:]
        filas.append({
            "url": url,
            "libro": partes[0] if partes else "",
            "seccion": partes[1] if len(partes) > 2 else "",
            "subseccion": partes[2] if len(partes) > 3 else "",
        })
    return filas


def main() -> int:
    if "--fresco" in sys.argv and CACHE.exists():
        for f in CACHE.iterdir():
            f.unlink()
    SALIDA.mkdir(exist_ok=True)
    for edicion in FUENTES:
        filas = inventariar(edicion)
        destino = SALIDA / f"oficial-{edicion}.tsv"
        with destino.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["url", "libro", "seccion", "subseccion"], delimiter="\t")
            w.writeheader()
            w.writerows(filas)
        print(f"{edicion}: {len(filas)} páginas -> {destino.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
