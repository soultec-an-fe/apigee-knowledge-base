---
id: bundle-kb-jwt-idp
titulo: Bundle kb-jwt-idp
area: ejemplos
tags: [bundle, verifyjwt, jwks, oidc, idp, scope]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/verify-jwt-policy
revisado: 2026-10-23
---

# Bundle kb-jwt-idp

Valida **access tokens JWT** emitidos por un proveedor de identidad externo (Okta, Entra ID, Keycloak, Auth0…), exige un scope para las operaciones de escritura y propaga la identidad al backend.

## Flujo

| Fase | Política | Para qué |
|---|---|---|
| PreFlow | `VJWT-IdP` ([VerifyJWT](../../../docs/02-politicas/referencia/verify-jwt.md)) | RS256 con **JWKS** remoto; `iss` y `aud` fijos; `sub`, `exp` e `iat` obligatorios; **vida máxima de 1 h**; 30 s de tolerancia de reloj. Lee el token de `Authorization: Bearer`. |
| PreFlow | `AM-Propagar-Identidad` | Quita `Authorization` y añade `X-Usuario` con el `sub` |
| Flujo `escritura` (POST, PUT, DELETE) | `RF-403-Scope` | 403 si el claim `scope` no contiene `api:escribir` (regex con `~~`) |
| Errores | `AM-Error-401` | Cualquier fallo de JWT (`JWT.failed = true`) da 401 `invalid_token` |

## Antes de desplegar

Cambia en `policies/VJWT-IdP.xml` los tres valores de ejemplo por los de tu IdP:

| Elemento | Valor de ejemplo | Dónde se encuentra |
|---|---|---|
| `<JWKS uri>` | `https://idp.ejemplo.com/.well-known/jwks.json` | `jwks_uri` del documento `/.well-known/openid-configuration` del IdP |
| `<Issuer>` | `https://idp.ejemplo.com/` | `issuer` del mismo documento; **debe coincidir carácter a carácter**, incluida la barra final |
| `<Audience>` | `api://kb-ejemplo` | La audiencia que el IdP pone en los access tokens de tu API |

> [!WARNING]
> Si tu IdP emite el scope como **array** (`scp: ["a","b"]`) en lugar de como cadena separada por espacios (`scope: "a b"`), ajusta la condición de `RF-403-Scope`. La forma del claim no es estándar entre IdP.

## Pruebas

```bash
HOST=api.tu-dominio.com
TOKEN=un-access-token-del-idp

curl -i -H "Authorization: Bearer $TOKEN" "https://$HOST/kb/v1/jwt-idp/json"            # 200 si el token es válido
curl -i -X POST -H "Authorization: Bearer $TOKEN" "https://$HOST/kb/v1/jwt-idp/echo"    # 403 si falta api:escribir
curl -i -H "Authorization: Bearer x.y.z" "https://$HOST/kb/v1/jwt-idp/json"             # 401 invalid_token
```

## Fuentes

- VerifyJWT: ver la [referencia](../../../docs/02-politicas/referencia/verify-jwt.md) y los [conceptos JWT/JWS](../../../docs/02-politicas/referencia/jwt-jws-conceptos.md), con las páginas oficiales consultadas el 2026-10-22.
