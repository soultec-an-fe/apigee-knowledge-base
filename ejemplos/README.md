---
id: ejemplos-indice
titulo: Ejemplos — mapa de los repositorios oficiales y bundles propios
area: ejemplos
tags: [ejemplos, samples, bundles, apigee-samples, devrel, openbank, api-platform-samples]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
fuente: https://github.com/GoogleCloudPlatform/apigee-samples
revisado: 2026-10-23
---

# Ejemplos — mapa de los repositorios oficiales y bundles propios

> **Fecha de corte: 23 de octubre de 2026.**

Esta carpeta tiene dos partes:

1. **Mapa de los ejemplos oficiales.** No copia el código de Google: indica qué muestra cada ejemplo, qué políticas usa (extraídas de sus XML) y qué documento de este repo lo explica.
2. **[Bundles propios](bundles/README.md).** Proxies completos escritos para este repositorio, validados con un script propio y con `apigeelint`.

## Repositorios oficiales

| Repositorio | Ediciones | Estado | Ejemplos con bundles | Bundles | Mapa |
|---|---|---|---|---|---|
| [GoogleCloudPlatform/apigee-samples](https://github.com/GoogleCloudPlatform/apigee-samples) | X y hybrid | Activo | 49 (de 53 descritos) | 62 | [01-apigee-samples.md](01-apigee-samples.md) |
| [apigee/devrel](https://github.com/apigee/devrel) | X y hybrid | Activo | 30 (de 44 descritos) | 52 | [02-devrel.md](02-devrel.md) |
| [apigee/openbank](https://github.com/apigee/openbank) | ⚠️ **Edge** | Activo | 13 | 13 | [03-openbank.md](03-openbank.md) |
| [apigee/api-platform-samples](https://github.com/apigee/api-platform-samples) | ⚠️ **Edge** | **Archivado** (abril de 2024) | 70 | 78 | [04-api-platform-samples.md](04-api-platform-samples.md) |

Por política, el [índice por política](05-indice-por-politica.md) lista qué ejemplos usan cada una. Es útil para ver una configuración real después de leer su [referencia](../docs/02-politicas/referencia/00-indice.md).

> [!WARNING]
> **`apigee/openbank` está hecho para Apigee Edge**, aunque se siga actualizando:
> - los sandboxes usan `<HostedTarget/>`, que no existe en X;
> - el despliegue usa la API de gestión de Edge;
> - sigue el estándar británico OBIE de la época de FAPI 1.0.
>
> Para un Open Banking actual sobre Apigee X con **FAPI 2.0**, sirve como referencia de **arquitectura**: DCR, eIDAS, consentimientos, shared flows de tokens. No sirve como código para desplegar tal cual.

## Cómo usar los ejemplos

- **Lee primero la referencia de la política y después el ejemplo.** Los ejemplos de Google son didácticos: a menudo simplifican (claves en claro, `IgnoreUnresolvedVariables=true`, CORS abierto) para que funcionen a la primera. Antes de copiar algo a producción, revísalo contra los **Antipatrones** de cada referencia.
- **Ediciones:** los ejemplos de X y hybrid no funcionan tal cual en Edge, ni al revés.
- **Licencias:** los cuatro repositorios son **Apache 2.0**. Si reutilizas su código, conserva el aviso de licencia.

## Cómo se genera el mapa

El mapa es reproducible: las páginas `01` a `05` **no se editan a mano**.

```bash
# 1. Clonar los repos fuera de este repositorio (solo se leen; no se ejecuta nada de ellos)
git clone --depth 1 https://github.com/GoogleCloudPlatform/apigee-samples.git /tmp/ej/apigee-samples
git clone --depth 1 https://github.com/apigee/devrel.git /tmp/ej/devrel
git clone --depth 1 https://github.com/apigee/openbank.git /tmp/ej/openbank
git clone --depth 1 https://github.com/apigee/api-platform-samples.git /tmp/ej/api-platform-samples

# 2. Inventariar bundles y políticas
python3 -I scripts/mapa_ejemplos.py /tmp/ej/apigee-samples apigee-samples --salida inventario/ejemplos-apigee-samples.tsv
python3 -I scripts/mapa_ejemplos.py /tmp/ej/devrel devrel --niveles 2 --salida inventario/ejemplos-devrel.tsv
python3 -I scripts/mapa_ejemplos.py /tmp/ej/openbank openbank --niveles 2 --salida inventario/ejemplos-openbank.tsv
python3 -I scripts/mapa_ejemplos.py /tmp/ej/api-platform-samples api-platform-samples --niveles 2 --salida inventario/ejemplos-api-platform-samples.tsv

# 3. Regenerar las páginas
python3 scripts/generar_mapa_ejemplos.py
```

Las descripciones en español, el tema y los documentos relacionados de cada ejemplo están en [`_catalogo.tsv`](_catalogo.tsv). Cuando Google añada un ejemplo nuevo, añade su fila ahí. Mientras no tenga fila, aparece en «Otros bundles del repositorio», sin descripción.

## Fuentes

- GoogleCloudPlatform/apigee-samples: <https://github.com/GoogleCloudPlatform/apigee-samples> (README y árbol del repositorio, 2026-10-23).
- apigee/devrel: <https://github.com/apigee/devrel> (README y árbol del repositorio, 2026-10-23).
- apigee/openbank: <https://github.com/apigee/openbank> (README, guía `docs-src/docs.md` y bundles, 2026-10-23).
- apigee/api-platform-samples: <https://github.com/apigee/api-platform-samples> (READMEs de `sample-proxies/`, 2026-10-23).
