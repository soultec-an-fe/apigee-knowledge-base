---
id: bundle-kb-oauth-client-credentials
titulo: Bundle kb-oauth-client-credentials
area: ejemplos
tags: [bundle, oauthv2, client-credentials, scope, routerule]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/oauthv2-policy
revisado: 2026-10-23
---

# Bundle kb-oauth-client-credentials

Un proxy con dos funciones: **emitir tokens** OAuth 2.0 con *client credentials* (sin backend, gracias a una RouteRule vacía) y **proteger un recurso** que exige el scope `recursos:leer`.

## Flujo

| Ruta | Paso | Política | Para qué |
|---|---|---|---|
| `POST /token` | 1 | `OA-Generar-Token` ([OAuthV2](../../../docs/02-politicas/referencia/oauthv2.md) `GenerateAccessToken`) | Token de 30 minutos (`ExpiresIn` 1 800 000 ms), respuesta compatible con la RFC 6749 (`RFCCompliantRequestResponse`), scope pedido en el formulario |
| | — | RouteRule `sin-backend-para-token` | **Sin `<TargetEndpoint>`**: la respuesta la genera Apigee |
| `GET /recursos/**` | 1 | `OA-Verificar-Lectura` (`VerifyAccessToken` con `<Scope>recursos:leer</Scope>`) | Token válido **y** con el scope |
| | 2 | `AM-Quitar-Authorization` | El backend no recibe el token |
| Target (PreFlow) | — | `AM-No-Copiar-Sufijo` | `target.copy.pathsuffix = false`: el backend de prueba es siempre `/json` |
| Cualquier otra ruta | — | `RF-404` | 404 JSON |
| Errores | — | `AM-Error-401`, `AM-Error-403` | `WWW-Authenticate: Bearer error="…"`, como pide la RFC 6750 |

## Preparación

1. Crea un **API product** que incluya el proxy, con el scope **`recursos:leer`** en *OAuth scopes*.
2. Crea una app suscrita y copia su *key* (`client_id`) y su *secret*.

## Pruebas

```bash
HOST=api.tu-dominio.com
ID=client-id-de-la-app
SECRETO=client-secret-de-la-app

TOKEN=$(curl -s -u "$ID:$SECRETO" -d "grant_type=client_credentials&scope=recursos:leer" \
  "https://$HOST/kb/v1/oauth-cc/token" | python3 -c 'import json,sys; print(json.load(sys.stdin)["access_token"])')

curl -i -H "Authorization: Bearer $TOKEN" "https://$HOST/kb/v1/oauth-cc/recursos/1"   # 200
curl -i "https://$HOST/kb/v1/oauth-cc/recursos/1"                                     # 401 invalid_token
```

> [!WARNING]
> **Si el cliente no envía `scope`** (o lo envía vacío), Apigee emite el token con **todos** los scopes de todos los productos de la app. Para aplicar mínimo privilegio, valida en el flujo `emitir-token` que llegue un `scope`, por ejemplo con una condición y un RaiseFault, o separa los permisos en productos distintos.

> [!CAUTION]
> El `client_secret` viaja en `Authorization: Basic`. Usa siempre HTTPS, y no expongas este endpoint a apps que no puedan guardar un secreto (móviles, SPA): para ellas existe *authorization code* con PKCE (ver [OAuth 2.0](../../../docs/03-seguridad/02-oauth2.md)).

## Fuentes

- OAuthV2: ver la [referencia](../../../docs/02-politicas/referencia/oauthv2.md), con las páginas oficiales consultadas el 2026-10-22.
