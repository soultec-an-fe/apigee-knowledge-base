# Cómo contribuir

Este repositorio prioriza que el contenido sea **verificable y parseable por un LLM**. Antes de abrir un PR:

## 1. Frontmatter obligatorio

Todo `.md` dentro de `docs/` y de `ejemplos/` debe empezar con:

```yaml
---
id: area-tema              # kebab-case, único en el repo
titulo: Título legible
area: fundamentos|proxies|politicas|seguridad|publicacion|operacion|devops|ai|practicas|antipatrones|referencia|hybrid|api-hub|seguridad-avanzada|troubleshooting|administracion|adaptadores|edge|ejemplos
tags: [lista, de, keywords]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
fuente: https://cloud.google.com/apigee/docs/...
revisado: YYYY-MM-DD
---
```

## 2. Reglas de estilo

- **Un tema por archivo.** Si un documento supera ~500 líneas, divídelo.
- **Encabezados jerárquicos sin saltos** (`#` → `##` → `###`).
- **Tablas para cualquier enumeración de 3+ elementos** con atributos.
- **XML completo y válido**, nunca fragmentos con `...` en medio de un elemento.
- **Sin capturas de pantalla.** Si algo solo se explica visualmente, descríbelo en texto.
- **Marca la versión**: usa `⚠️ Solo Edge` para funciones legacy.
- **Cita la fuente** al final de cada documento, en la sección `## Fuentes`.

## 3. Verificación

Antes de commitear, confirma contra la documentación oficial vigente en
<https://cloud.google.com/apigee/docs>. Actualiza el campo `revisado:`.

No copies texto literal de Google: sintetiza y enlaza.

## 4. Bundles de ejemplo

Los bundles de `ejemplos/bundles/` deben pasar las dos validaciones antes de commitear:

```bash
python3 scripts/validar_bundles.py
npx apigeelint@2.85.1 -s ejemplos/bundles/<nombre>/apiproxy -f table.js --profile apigeex
```

Las páginas `ejemplos/01-*.md` a `05-*.md` se generan con `scripts/generar_mapa_ejemplos.py`: edita `ejemplos/_catalogo.tsv`, no las páginas.

## 5. Actualizar los índices

Si añades un archivo, añádelo también a `README.md` y a `llms.txt`.
