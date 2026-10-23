---
id: bundle-kb-cache-respuestas
titulo: Bundle kb-cache-respuestas
area: ejemplos
tags: [bundle, responsecache, cache, skipcachelookup]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/response-cache
revisado: 2026-10-23
---

# Bundle kb-cache-respuestas

Caché de respuestas `GET` durante 5 minutos, con clave por recurso y query, sin cachear errores y con *bypass* bajo demanda.

## Flujo

La **misma** política `RC-Catalogo` ([ResponseCache](../../../docs/02-politicas/referencia/response-cache.md)) se adjunta dos veces, que es el máximo permitido:

| Fase | Qué hace |
|---|---|
| PreFlow de petición | **Busca** en caché. Si encuentra la respuesta, la devuelve sin llamar al backend. |
| PostFlow de respuesta | **Guarda** la respuesta |

| Ajuste | Valor | Motivo |
|---|---|---|
| Clave | `kb-catalogo` + `proxy.pathsuffix` + `request.querystring` | `/productos?pagina=2` y `/productos?pagina=3` son entradas distintas. Ver [claves de caché](../../../docs/02-politicas/referencia/claves-de-cache.md). |
| `TimeoutInSeconds` | 300 | Datos de catálogo que toleran 5 minutos de antigüedad |
| `ExcludeErrorResponse` | `true` | No cachear errores, que es un [antipatrón](../../../docs/09-antipatrones/01-catalogo-antipatrones.md) |
| `SkipCachePopulation` | `response.status.code != 200` | Refuerzo explícito: solo se guardan los 200 |
| `SkipCacheLookup` | `Cache-Control: no-cache` | El cliente puede forzar ir al backend |

`AM-Cabecera-Cache` añade `X-Cache-Hit` (`true` o `false`) para diagnóstico.

> [!CAUTION]
> **No uses esta clave en APIs con datos por usuario.** Dos usuarios con la misma ruta y query recibirían la misma respuesta. En ese caso añade un `<KeyFragment>` con la identidad, por ejemplo `client_id` o el `sub` de un JWT, o no caches.

## Pruebas

```bash
HOST=api.tu-dominio.com
curl -s -D - -o /dev/null "https://$HOST/kb/v1/cache/json" | grep -i x-cache-hit                            # false (primera vez)
curl -s -D - -o /dev/null "https://$HOST/kb/v1/cache/json" | grep -i x-cache-hit                            # true
curl -s -D - -o /dev/null -H "Cache-Control: no-cache" "https://$HOST/kb/v1/cache/json" | grep -i x-cache-hit # false
```

## Fuentes

- ResponseCache: ver la [referencia](../../../docs/02-politicas/referencia/response-cache.md), con las páginas oficiales consultadas el 2026-10-22.
