#!/usr/bin/env python3
"""Genera las páginas de `ejemplos/` a partir del catálogo y del inventario de bundles.

Entradas:
    ejemplos/_catalogo.tsv                 descripción en español, tema y documentos del repo por ejemplo
    inventario/ejemplos-{repo}.tsv         políticas detectadas por `scripts/mapa_ejemplos.py`
    docs/02-politicas/referencia/*.md      `elemento_xml` de cada referencia, para enlazar políticas

Salidas (se sobrescriben siempre; no se editan a mano):
    ejemplos/01-apigee-samples.md, 02-devrel.md, 03-openbank.md, 04-api-platform-samples.md
    ejemplos/05-indice-por-politica.md

Uso:
    python3 scripts/generar_mapa_ejemplos.py
"""

from __future__ import annotations

import collections
import csv
import pathlib
import re

RAIZ = pathlib.Path(__file__).resolve().parent.parent
EJ = RAIZ / "ejemplos"
FECHA = "2026-10-23"

REPOS = {
    "apigee-samples": {
        "archivo": "01-apigee-samples.md",
        "titulo": "GoogleCloudPlatform/apigee-samples",
        "url": "https://github.com/GoogleCloudPlatform/apigee-samples",
        "rama": "main",
        "ediciones": "Apigee X y hybrid",
        "aplica": "[apigee-x, apigee-hybrid]",
        "nota": "Repositorio activo y principal de ejemplos de Google (Apache 2.0). Cada carpeta trae su README y, en la mayoría de los casos, un tutorial de Cloud Shell.",
    },
    "devrel": {
        "archivo": "02-devrel.md",
        "titulo": "apigee/devrel",
        "url": "https://github.com/apigee/devrel",
        "rama": "main",
        "ediciones": "Apigee X y hybrid (algunas herramientas también Edge)",
        "aplica": "[apigee-x, apigee-hybrid]",
        "nota": "Implementaciones de referencia (`references/`), herramientas (`tools/`) y laboratorios (`labs/`) del equipo de DevRel de Apigee (Apache 2.0). Google aclara que no es un producto con soporte oficial.",
    },
    "openbank": {
        "archivo": "03-openbank.md",
        "titulo": "apigee/openbank",
        "url": "https://github.com/apigee/openbank",
        "rama": "main",
        "ediciones": "**Apigee Edge**",
        "aplica": "[apigee-edge]",
        "nota": "Implementación de referencia de Open Banking (Apache 2.0, no es producto oficial). **Está hecha para Apigee Edge**: los sandboxes usan `<HostedTarget/>` (función que no existe en X), y la guía de despliegue usa la API de gestión de Edge (`api.enterprise.apigee.com`) y hosts `*.apigee.net`. Los ejemplos usan el estándar británico **OBIE** (por ejemplo `open-banking/v2.3/atms`) y la cabecera `x-fapi-financial-id`, propia de la época de FAPI 1.0.",
    },
    "api-platform-samples": {
        "archivo": "04-api-platform-samples.md",
        "titulo": "apigee/api-platform-samples",
        "url": "https://github.com/apigee/api-platform-samples",
        "rama": "master",
        "ediciones": "**Apigee Edge** (repositorio archivado)",
        "aplica": "[apigee-edge]",
        "nota": "Repositorio **archivado** (último cambio en abril de 2024), escrito para Apigee Edge. Sigue siendo útil para entender políticas, pero varios ejemplos usan funciones que no existen en X (Node.js, Hosted Targets, OAuth 1.0a) o backends que ya no responden (APIs de Yahoo y Twitter).",
    },
}


def leer_tsv(ruta: pathlib.Path) -> list[dict]:
    with ruta.open(encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def referencias() -> dict[str, str]:
    refs = {}
    for f in (RAIZ / "docs/02-politicas/referencia").glob("*.md"):
        m = re.search(r"^elemento_xml:\s*(\S+)", f.read_text(encoding="utf-8"), re.M)
        if m:
            refs[m.group(1)] = f.name
    return refs


def enlace_politica(p: str, refs: dict[str, str]) -> str:
    return f"[{p}](../docs/02-politicas/referencia/{refs[p]})" if p in refs else f"`{p}`"


def enlace_doc(ruta: str) -> str:
    nombre = pathlib.Path(ruta).stem
    return f"[{nombre}](../{ruta})"


def frontmatter(id_: str, titulo: str, aplica: str, fuente: str, tags: str) -> str:
    return (
        f"---\nid: {id_}\ntitulo: {titulo}\narea: ejemplos\ntags: [{tags}]\naplica_a: {aplica}\n"
        f"fuente: {fuente}\nrevisado: {FECHA}\n---\n\n"
        "<!-- Archivo generado por scripts/generar_mapa_ejemplos.py. No editar a mano. -->\n\n"
    )


def main() -> int:
    refs = referencias()
    catalogo = leer_tsv(EJ / "_catalogo.tsv")
    usos = collections.defaultdict(list)  # política -> [(repo, ejemplo)]

    for repo, meta in REPOS.items():
        inv = leer_tsv(RAIZ / f"inventario/ejemplos-{repo}.tsv")
        politicas = collections.defaultdict(set)
        nbundles = collections.Counter()
        for fila in inv:
            nbundles[fila["ejemplo"]] += 1
            politicas[fila["ejemplo"]].update(filter(None, fila["politicas"].split(",")))

        filas = [c for c in catalogo if c["repo"] == repo]
        sin_catalogo = sorted(set(politicas) - {c["ejemplo"] for c in filas})

        por_tema = collections.defaultdict(list)
        for c in filas:
            por_tema[c["tema"]].append(c)

        out = [frontmatter(f"ejemplos-{repo}", f"Mapa de ejemplos — {meta['titulo']}", meta["aplica"], meta["url"], f"ejemplos, {repo}, samples")]
        out.append(f"# Mapa de ejemplos — {meta['titulo']}\n\n")
        out.append(f"> **Fecha de corte: {FECHA}.** Ediciones: {meta['ediciones']}. Repositorio: <{meta['url']}>.\n\n")
        out.append(meta["nota"] + "\n\n")
        out.append("La columna **Políticas** se extrae automáticamente de los XML de cada bundle (`scripts/mapa_ejemplos.py`); enlaza con la referencia de cada política. Una celda vacía indica que el ejemplo no trae bundles (scripts, Terraform, notebooks, portales).\n\n")
        for tema in sorted(por_tema):
            out.append(f"## {tema}\n\n| Ejemplo | Qué muestra | Políticas | En este repo |\n|---|---|---|---|\n")
            for c in sorted(por_tema[tema], key=lambda x: x["ejemplo"]):
                ej = c["ejemplo"]
                url = f"{meta['url']}/tree/{meta['rama']}/{ej}"
                pols = ", ".join(enlace_politica(p, refs) for p in sorted(politicas.get(ej, ())))
                for p in politicas.get(ej, ()):
                    usos[p].append((repo, ej))
                docs = ", ".join(enlace_doc(d) for d in filter(None, c["docs"].split(",")))
                out.append(f"| [`{ej}`]({url}) | {c['descripcion']} | {pols} | {docs} |\n")
            out.append("\n")
        if sin_catalogo:
            out.append("## Otros bundles del repositorio\n\nEjemplos con bundles que no están descritos en el catálogo (antiguos, auxiliares o de tutoriales):\n\n| Ejemplo | Bundles | Políticas |\n|---|---|---|\n")
            for ej in sin_catalogo:
                for p in politicas[ej]:
                    usos[p].append((repo, ej))
                pols = ", ".join(enlace_politica(p, refs) for p in sorted(politicas[ej]))
                out.append(f"| [`{ej}`]({meta['url']}/tree/{meta['rama']}/{ej}) | {nbundles[ej]} | {pols} |\n")
            out.append("\n")
        out.append(f"## Fuentes\n\n- {meta['titulo']}: <{meta['url']}> (clonado y analizado el {FECHA}).\n")
        (EJ / meta["archivo"]).write_text("".join(out), encoding="utf-8")

    # Índice por política
    out = [frontmatter("ejemplos-indice-politica", "Ejemplos por política", "[apigee-x, apigee-hybrid, apigee-edge]", "https://github.com/GoogleCloudPlatform/apigee-samples", "ejemplos, politicas, indice")]
    out.append("# Ejemplos por política\n\n")
    out.append(f"> **Fecha de corte: {FECHA}.** Qué ejemplos oficiales usan cada política, para ver una configuración real después de leer su referencia. ⚠️ indica un repositorio para Apigee Edge.\n\n")
    out.append("| Política | Ejemplos |\n|---|---|\n")
    for p in sorted(usos, key=str.lower):
        vistos = []
        for repo, ej in sorted(set(usos[p]), key=lambda x: (list(REPOS).index(x[0]), x[1])):
            marca = " ⚠️" if repo in ("openbank", "api-platform-samples") else ""
            vistos.append(f"[`{ej}`]({REPOS[repo]['url']}/tree/{REPOS[repo]['rama']}/{ej}){marca}")
        out.append(f"| {enlace_politica(p, refs)} | {', '.join(vistos)} |\n")
    out.append("\n## Fuentes\n\n" + "".join(f"- {m['titulo']}: <{m['url']}>.\n" for m in REPOS.values()))
    (EJ / "05-indice-por-politica.md").write_text("".join(out), encoding="utf-8")
    print("ok:", ", ".join(m["archivo"] for m in REPOS.values()), "05-indice-por-politica.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
