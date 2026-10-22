#!/usr/bin/env python3
"""Extrae el cuerpo de una página de documentación de Apigee a texto legible.

Sirve para LEER la fuente oficial al redactar o verificar un documento del repo. La salida
queda en `.cache/paginas/` (ignorado por git): el repo no publica texto copiado de Google,
solo síntesis propia con enlace a la fuente (ver CONTRIBUTING.md).

Uso:
    python3 scripts/extraer_pagina.py URL [URL ...]
    python3 scripts/extraer_pagina.py --stdout URL

Conserva encabezados (#), tablas (celdas separadas por " | "), listas y bloques de código
(``` ... ```), que es lo que hace falta para sintetizar una referencia de política.
"""

from __future__ import annotations

import html
import html.parser
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from inventario_oficial import RAIZ, descargar  # noqa: E402

DESTINO = RAIZ / ".cache" / "paginas"
BLOQUE = {"p", "div", "section", "article", "br", "dt", "dd", "h1", "h2", "h3", "h4", "h5", "h6"}


IGNORADAS = ("script", "style", "devsite-feedback", "devsite-thumb-rating")
VACIAS = {"br", "img", "hr", "input", "meta", "link", "wbr", "source", "col"}


class Extractor(html.parser.HTMLParser):
    """El fin del artículo lo marca solo la profundidad de <div>: devsite deja <p>, <li>
    y <td> sin cerrar, y usar una pila de todas las etiquetas cortaba páginas largas."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.dentro = 0          # 1 dentro de devsite-article-body, -1 capturando el h1
        self.divs = 0            # profundidad de <div> dentro del artículo
        self.ignorar = 0         # dentro de script/style/devsite-feedback...
        self.pre = 0
        self.code = 0
        self.out: list[str] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        clase = a.get("class") or ""
        if not self.dentro and tag == "div" and "devsite-article-body" in clase:
            self.dentro, self.divs = 1, 1
            return
        if not self.dentro:
            if tag == "h1" and "devsite-page-title" in clase:
                self.out.append("\n# ")
                self.dentro = -1  # captura solo el título
            return
        if self.dentro == -1:
            return
        if tag == "div":
            self.divs += 1
        if tag in IGNORADAS:
            self.ignorar += 1
        if self.ignorar or tag in VACIAS and tag != "br":
            return
        if tag == "pre":
            self.pre += 1
            self.out.append("\n```\n")
        elif tag in ("h2", "h3", "h4", "h5", "h6"):
            self.out.append("\n\n" + "#" * int(tag[1]) + " ")
        elif tag == "li":
            self.out.append("\n- ")
        elif tag == "tr":
            self.out.append("\n| ")
        elif tag in ("td", "th"):
            pass
        elif tag == "code" and not self.pre:
            self.code += 1
            self.out.append("`")
        elif tag in BLOQUE:
            self.out.append("\n")

    def handle_endtag(self, tag):
        if self.dentro == -1:
            if tag == "h1":
                self.out.append("\n")
                self.dentro = 0
            return
        if not self.dentro:
            return
        if tag in IGNORADAS:
            self.ignorar = max(0, self.ignorar - 1)
            return
        if tag == "div":
            self.divs -= 1
            if self.divs == 0:
                self.dentro = 0
                return
        if self.ignorar:
            return
        if tag == "pre" and self.pre:
            self.pre -= 1
            self.out.append("\n```\n")
        elif tag in ("td", "th"):
            self.out.append(" | ")
        elif tag == "code" and self.code and not self.pre:
            self.code -= 1
            self.out.append("`")

    def handle_data(self, data):
        if self.dentro == -1:
            self.out.append(data.strip())
        elif self.dentro and not self.ignorar:
            self.out.append(data if self.pre else re.sub(r"\s+", " ", data))


def extraer(url: str) -> str:
    p = Extractor()
    p.feed(descargar(url).decode("utf-8", "replace"))
    texto = "".join(p.out)
    texto = re.sub(r"[ \t]+\n", "\n", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return f"<!-- fuente: {url} -->\n{html.unescape(texto).strip()}\n"


def main(argv: list[str]) -> int:
    a_stdout = "--stdout" in argv
    urls = [a for a in argv if not a.startswith("--")]
    if not urls:
        print(__doc__)
        return 2
    DESTINO.mkdir(parents=True, exist_ok=True)
    for url in urls:
        texto = extraer(url)
        if a_stdout:
            sys.stdout.write(texto)
        else:
            nombre = re.sub(r"[^A-Za-z0-9._-]", "_", url.split("//", 1)[-1]) + ".md"
            (DESTINO / nombre).write_text(texto)
            print(f"{len(texto):>7} {url}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
