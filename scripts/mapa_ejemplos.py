#!/usr/bin/env python3
"""Inventaría los bundles de un repositorio de ejemplos de Apigee clonado en local.

Recorre el árbol buscando bundles (`apiproxy/` o `sharedflowbundle/`), lee el elemento raíz de
cada XML de `policies/` y escribe una fila TSV por bundle:

    repo  ejemplo  tipo  bundle  politicas

`politicas` es la lista de elementos raíz distintos (p. ej. `VerifyAPIKey,Quota,AssignMessage`),
que es lo que se usa para cruzar cada ejemplo con `docs/02-politicas/referencia/`.

Uso:
    python3 scripts/mapa_ejemplos.py RUTA_REPO NOMBRE_REPO [--niveles N] [--salida inventario/ejemplos-NOMBRE.tsv]

`--niveles` indica cuántos niveles de carpeta forman el nombre del ejemplo: 1 en
GoogleCloudPlatform/apigee-samples (`basic-quota/`), 2 en repos que agrupan por carpeta
(`references/identity-facade/`, `sample-proxies/apikey/`, `apiproxies/identity-v1/`).

El repositorio se clona fuera de este repo (por ejemplo, en un directorio temporal); este
script solo lee archivos y nunca ejecuta nada del repositorio de ejemplos.
"""

from __future__ import annotations

import argparse
import pathlib
import sys
import xml.etree.ElementTree as ET

TIPOS = {"apiproxy": "proxy", "sharedflowbundle": "sharedflow"}


def raiz_xml(archivo: pathlib.Path) -> str | None:
    try:
        return ET.parse(archivo).getroot().tag
    except (ET.ParseError, OSError):
        return None


def bundles(repo: pathlib.Path):
    for carpeta in sorted(repo.rglob("*")):
        if carpeta.is_dir() and carpeta.name in TIPOS and ".git" not in carpeta.parts:
            yield carpeta


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("repo", type=pathlib.Path)
    ap.add_argument("nombre")
    ap.add_argument("--niveles", type=int, default=1)
    ap.add_argument("--salida", type=pathlib.Path)
    args = ap.parse_args()

    filas = ["repo\tejemplo\ttipo\tbundle\tpoliticas"]
    for b in bundles(args.repo):
        relativo = b.parent.relative_to(args.repo)
        ejemplo = "/".join(relativo.parts[: args.niveles]) or "."
        politicas = sorted({r for p in (b / "policies").glob("*.xml") if (r := raiz_xml(p))})
        filas.append(f"{args.nombre}\t{ejemplo}\t{TIPOS[b.name]}\t{relativo}\t{','.join(politicas)}")

    texto = "\n".join(filas) + "\n"
    if args.salida:
        args.salida.parent.mkdir(parents=True, exist_ok=True)
        args.salida.write_text(texto, encoding="utf-8")
        print(f"{len(filas) - 1} bundles -> {args.salida}")
    else:
        sys.stdout.write(texto)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
