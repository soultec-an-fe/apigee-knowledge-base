#!/usr/bin/env python3
"""Valida la estructura de los bundles de `ejemplos/bundles/`.

Comprueba, para cada `apiproxy/` o `sharedflowbundle/`:
- que todos los XML están bien formados;
- que existe el descriptor raíz (`{nombre}.xml`) y su `name` coincide con la carpeta del bundle;
- que el atributo `name` de cada política coincide con el nombre de su archivo;
- que cada `<Step><Name>` apunta a una política existente;
- que cada política está referenciada al menos una vez (no hay políticas huérfanas);
- que cada `<RouteRule><TargetEndpoint>` apunta a un TargetEndpoint existente.

Es una validación estructural propia; el *lint* de buenas prácticas lo hace `apigeelint`
(ver `ejemplos/bundles/README.md`).

Uso:
    python3 scripts/validar_bundles.py            # todos los bundles
    python3 scripts/validar_bundles.py RUTA...    # solo esos bundles
"""

from __future__ import annotations

import pathlib
import sys
import xml.etree.ElementTree as ET

RAIZ = pathlib.Path(__file__).resolve().parent.parent
BUNDLES = RAIZ / "ejemplos" / "bundles"
TIPOS = ("apiproxy", "sharedflowbundle")


def validar(bundle: pathlib.Path) -> list[str]:
    errores: list[str] = []
    rel = bundle.relative_to(RAIZ)
    arboles: dict[pathlib.Path, ET.Element] = {}
    for x in sorted(bundle.rglob("*.xml")):
        try:
            arboles[x] = ET.parse(x).getroot()
        except ET.ParseError as e:
            errores.append(f"{x.relative_to(RAIZ)}: XML mal formado: {e}")
    if errores:
        return errores

    nombre = bundle.parent.name
    raiz = bundle / f"{nombre}.xml"
    if raiz not in arboles:
        errores.append(f"{rel}: falta el descriptor {nombre}.xml")
    elif arboles[raiz].get("name") != nombre:
        errores.append(f"{raiz.relative_to(RAIZ)}: name={arboles[raiz].get('name')!r} no coincide con la carpeta {nombre!r}")

    politicas = {}
    for x, r in arboles.items():
        if x.parent.name == "policies":
            politicas[x.stem] = r
            if r.get("name") != x.stem:
                errores.append(f"{x.relative_to(RAIZ)}: name={r.get('name')!r} no coincide con el archivo")

    flujos = [r for x, r in arboles.items() if x.parent.name in ("proxies", "targets", "sharedflows")]
    usadas = set()
    for r in flujos:
        for paso in r.iter("Step"):
            n = paso.findtext("Name", "").strip()
            usadas.add(n)
            if n not in politicas:
                errores.append(f"{rel}: <Step> apunta a una política inexistente: {n!r}")
    for huerfana in sorted(set(politicas) - usadas):
        errores.append(f"{rel}: política sin <Step> que la use: {huerfana}")

    targets = {x.stem for x in arboles if x.parent.name == "targets"}
    for r in flujos:
        for regla in r.iter("RouteRule"):
            t = (regla.findtext("TargetEndpoint") or "").strip()
            if t and t not in targets:
                errores.append(f"{rel}: RouteRule {regla.get('name')!r} apunta a un TargetEndpoint inexistente: {t!r}")
    return errores


def main(argv: list[str]) -> int:
    if argv:
        bundles = [pathlib.Path(a).resolve() for a in argv]
    else:
        bundles = sorted(p for t in TIPOS for p in BUNDLES.glob(f"*/{t}"))
    errores = [e for b in bundles for e in validar(b)]
    for e in errores:
        print(e)
    print(f"{len(bundles)} bundles, {len(errores)} errores")
    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
