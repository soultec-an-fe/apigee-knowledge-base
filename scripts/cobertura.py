#!/usr/bin/env python3
"""Matriz de cobertura: inventario oficial (inventario/*.tsv) frente a lo que cita docs/.

Una página oficial cuenta como "citada" si su URL aparece en algún archivo de docs/
(frontmatter `fuente:`/`fuente_edge:` o sección de Fuentes). Es una métrica conservadora:
un documento puede cubrir un tema sin citar todas sus páginas.

Normalización antes de contar:
- hybrid: solo la versión más alta (vN.M) y las páginas sin versión; las demás versiones
  son copias de las mismas guías.
- Edge Private Cloud: solo la versión más alta (v4.NN.NN).
- reference/apis (API REST de gestión, autogenerada) y release/notes se cuentan como
  bloques, no página a página.

Uso:
    python3 scripts/cobertura.py            # escribe inventario/cobertura.tsv y lo resume
"""

from __future__ import annotations

import collections
import csv
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
INV = RAIZ / "inventario"
DOCS = RAIZ / "docs"
VERSION = re.compile(r"^v(\d+(?:\.\d+)+)$")


def clave_version(v: str) -> tuple[int, ...]:
    return tuple(int(x) for x in VERSION.match(v).group(1).split("."))


def leer(edicion: str) -> list[dict]:
    with (INV / f"oficial-{edicion}.tsv").open() as f:
        return list(csv.DictReader(f, delimiter="\t"))


def normalizar(filas: list[dict], libro_versionado: str) -> list[dict]:
    versiones = {f["seccion"] for f in filas if f["libro"] == libro_versionado and VERSION.match(f["seccion"])}
    ultima = max(versiones, key=clave_version) if versiones else None
    out = []
    for f in filas:
        if f["libro"] == libro_versionado and VERSION.match(f["seccion"]) and f["seccion"] != ultima:
            continue
        out.append(f)
    return out


def tema(f: dict, edicion: str) -> str:
    libro, sec = f["libro"], f["seccion"]
    if edicion == "x-hybrid" and libro == "reference":
        return "reference/apis (API REST, bloque)"
    if edicion == "edge" and libro == "release":
        return "release (notas, bloque)"
    if libro in ("hybrid", "private-cloud") and VERSION.match(sec):
        return f"{libro} ({sec})"
    return f"{libro}/{sec}" if sec else libro


def urls_citadas() -> set[str]:
    citadas = set()
    for md in DOCS.rglob("*.md"):
        for u in re.findall(r"https?://[^\s)>\]`\"']+", md.read_text()):
            u = u.rstrip(".,;").split("#")[0].split("?")[0].rstrip("/")
            u = u.replace("://cloud.google.com/apigee/docs/", "://docs.cloud.google.com/apigee/docs/")
            citadas.add(u)
    return citadas


def main() -> int:
    citadas = urls_citadas()
    filas_out = []
    for edicion, versionado in (("x-hybrid", "hybrid"), ("edge", "private-cloud")):
        conteo: dict[str, list[int]] = collections.defaultdict(lambda: [0, 0])
        for f in normalizar(leer(edicion), versionado):
            t = tema(f, edicion)
            conteo[t][0] += 1
            conteo[t][1] += f["url"] in citadas
        for t, (total, cit) in sorted(conteo.items(), key=lambda kv: -kv[1][0]):
            filas_out.append({"edicion": edicion, "tema": t, "paginas": total, "citadas": cit,
                              "pct": f"{100 * cit / total:.0f}"})
    with (INV / "cobertura.tsv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["edicion", "tema", "paginas", "citadas", "pct"], delimiter="\t")
        w.writeheader()
        w.writerows(filas_out)
    for ed in ("x-hybrid", "edge"):
        sub = [r for r in filas_out if r["edicion"] == ed]
        tot, cit = sum(r["paginas"] for r in sub), sum(r["citadas"] for r in sub)
        print(f"{ed}: {cit}/{tot} páginas citadas ({100 * cit / tot:.1f} %) en {len(sub)} temas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
