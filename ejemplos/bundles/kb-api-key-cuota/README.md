---
id: bundle-kb-api-key-cuota
titulo: Bundle kb-api-key-cuota
area: ejemplos
tags: [bundle, verifyapikey, quota, spikearrest, faultrules]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/verify-api-key-policy
revisado: 2026-10-23
---

# Bundle kb-api-key-cuota

API protegida por API key, con un escudo de picos global, la cuota que define el API product y errores JSON coherentes por familia.

## Flujo

| Fase | Paso | Política | Para qué |
|---|---|---|---|
| Petición (PreFlow) | 1 | `SA-Escudo` ([SpikeArrest](../../../docs/02-politicas/referencia/spike-arrest.md)) | 100 peticiones por segundo como techo del proxy, **antes** de gastar una consulta de credencial |
| | 2 | `VAK-Header` ([VerifyAPIKey](../../../docs/02-politicas/referencia/verify-api-key.md)) | Valida la cabecera `x-api-key` |
| | 3 | `Q-Producto` ([Quota](../../../docs/02-politicas/referencia/quota.md)) | Cuota del API product (`UseQuotaConfigInAPIProduct`), con 1000 al mes como respaldo, distribuida y por `client_id` |
| | 4 | `AM-Quitar-API-Key` | No reenvía la key al backend |
| Respuesta (PostFlow) | 5 | `AM-Cabeceras-Cuota` | `X-RateLimit-Limit` y `X-RateLimit-Remaining` |
| Errores | — | `AM-Error-401`, `403`, `429` y `Generico` | 401 para credencial ausente o inválida, 403 para un recurso no cubierto por el producto, 429 para cuota o pico, 500 genérico con el identificador de la petición |

El código HTTP se fija en la FaultRule en lugar de depender del de cada política. El de `QuotaViolation`, por ejemplo, [difiere entre ediciones](../../../docs/02-politicas/referencia/quota.md#errores).

## Preparación

1. Crea un **API product** que incluya el proxy `kb-api-key-cuota` y el entorno, con cuota (por ejemplo, 100 por hora).
2. Crea un developer y una **app** suscrita al producto, y copia su *key*.
3. Despliega el bundle (ver [despliegue](../README.md#despliegue)).

## Pruebas

```bash
HOST=api.tu-dominio.com        # hostname del environment group
KEY=la-key-de-la-app

curl -i "https://$HOST/kb/v1/api-key-cuota/json"                       # 401 invalid_credentials
curl -i -H "x-api-key: $KEY" "https://$HOST/kb/v1/api-key-cuota/json"   # 200 + X-RateLimit-*
for i in $(seq 1 200); do curl -s -o /dev/null -w "%{http_code}\n" -H "x-api-key: $KEY" "https://$HOST/kb/v1/api-key-cuota/json"; done | sort | uniq -c   # aparecen 429 al agotar la cuota
```

## Fuentes

- VerifyAPIKey, Quota y SpikeArrest: ver sus referencias en este repositorio, con las páginas oficiales consultadas el 2026-10-22.
