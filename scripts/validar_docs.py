#!/usr/bin/env python3
"""Valida los Markdown de docs/: frontmatter obligatorio, XML bien formado y enlaces internos.

Uso:
    python3 scripts/validar_docs.py            # todo docs/
    python3 scripts/validar_docs.py RUTA...    # solo esos archivos

Sale con código 1 si hay errores. Solo usa la biblioteca estándar.

Reglas (ver CONTRIBUTING.md):
- Frontmatter con id, titulo, area, tags, aplica_a, fuente, revisado; `id` único en el repo.
- Cada bloque ```xml debe ser XML bien formado. Un bloque con varios elementos raíz se
  valida envuelto en un contenedor. Los marcadores tipo `[false|true]` de una sintaxis
  esquemática no son XML válido: esos bloques se marcan con ```xml-sintaxis y se omiten.
- Los enlaces relativos [texto](ruta.md#ancla) deben apuntar a un archivo existente.
"""

from __future__ import annotations

import pathlib
import re
import sys
import xml.etree.ElementTree as ET

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DOCS = RAIZ / "docs"
CAMPOS = ("id", "titulo", "area", "tags", "aplica_a", "fuente", "revisado")
BLOQUE_XML = re.compile(r"^```xml\n(.*?)^```", re.S | re.M)
ENLACE = re.compile(r"\]\((?!https?://|mailto:|#)([^)#\s]+)(#[^)\s]*)?\)")


def frontmatter(texto: str) -> dict[str, str] | None:
    if not texto.startswith("---\n"):
        return None
    fin = texto.find("\n---\n", 4)
    if fin < 0:
        return None
    campos = {}
    for linea in texto[4:fin].splitlines():
        if ":" in linea and not linea.startswith(" "):
            k, v = linea.split(":", 1)
            campos[k.strip()] = v.split("#", 1)[0].strip()
    return campos


def validar(ruta: pathlib.Path, ids: dict[str, pathlib.Path]) -> list[str]:
    errores = []
    rel = ruta.relative_to(RAIZ)
    texto = ruta.read_text()

    fm = frontmatter(texto)
    if fm is None:
        errores.append(f"{rel}: sin frontmatter")
    else:
        for c in CAMPOS:
            if not fm.get(c):
                errores.append(f"{rel}: frontmatter sin '{c}'")
        if fm.get("id"):
            if fm["id"] in ids:
                errores.append(f"{rel}: id '{fm['id']}' repetido (también en {ids[fm['id']].relative_to(RAIZ)})")
            ids[fm["id"]] = ruta

    for m in BLOQUE_XML.finditer(texto):
        linea = texto[: m.start()].count("\n") + 1
        try:
            ET.fromstring(f"<raiz>{m.group(1)}</raiz>")
        except ET.ParseError as e:
            errores.append(f"{rel}:{linea}: XML mal formado: {e}")

    for m in ENLACE.finditer(texto):
        destino = (ruta.parent / m.group(1)).resolve()
        if not destino.exists():
            linea = texto[: m.start()].count("\n") + 1
            errores.append(f"{rel}:{linea}: enlace roto -> {m.group(1)}")
    return errores


def main(argv: list[str]) -> int:
    rutas = [pathlib.Path(a).resolve() for a in argv] or sorted(DOCS.rglob("*.md"))
    ids: dict[str, pathlib.Path] = {}
    if argv:  # ids del resto del repo, para detectar duplicados
        for otra in DOCS.rglob("*.md"):
            fm = frontmatter(otra.read_text())
            if fm and fm.get("id") and otra.resolve() not in rutas:
                ids[fm["id"]] = otra
    errores = [e for r in rutas for e in validar(r, ids)]
    for e in errores:
        print(e)
    print(f"{len(rutas)} archivos, {len(errores)} errores")
    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
