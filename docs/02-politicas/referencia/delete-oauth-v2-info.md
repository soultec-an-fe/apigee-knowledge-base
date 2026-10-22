---
id: politica-delete-oauth-v2-info
titulo: DeleteOAuthV2Info — referencia completa
area: politicas
tags: [deleteoauthv2info, oauth2, access-token, authorization-code, borrado, extensible]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
elemento_xml: DeleteOAuthV2Info
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/delete-oauth-v2-info
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/delete-oauth-v2-info
revisado: 2026-10-22
---

# DeleteOAuthV2Info — referencia completa

> [!NOTE]
> **Tipo:** Extensible. **Elemento raíz:** `<DeleteOAuthV2Info>`.
> **Aplica a:** Apigee X, hybrid y Edge, con el mismo comportamiento.

DeleteOAuthV2Info **borra** un access token o un código de autorización. A diferencia de revocar, borrar no deja rastro: un token borrado no se puede reaprobar ni consultar después.

| Necesidad | Política |
|---|---|
| Invalidar un token concreto de forma reversible (logout, RFC 7009) | [OAuthV2](oauthv2.md#revocación-y-reaprobación-tokenstoken) con `InvalidateToken` |
| Revocar todos los tokens de una app o de un usuario | [RevokeOAuthV2](revoke-oauth-v2.md) |
| Eliminar un token o un código definitivamente | **DeleteOAuthV2Info** |

Un caso de uso natural es borrar un código de autorización ya consumido o abandonado.

## Sintaxis completa

```xml
<DeleteOAuthV2Info name="DOI-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <AccessToken ref="variable.con.el.token"/>
  <!-- o bien: <AuthorizationCode ref="variable.con.el.codigo"/> -->
</DeleteOAuthV2Info>
```

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno. La página restringe los caracteres a `A-Z0-9._\-$ %`. |
| `continueOnError` | No | `false` | Con `true`, el flujo sigue aunque falle. |
| `enabled` | No | `true` | Con `false` no se ejecuta. |
| `async` | No | `false` | La página de esta política lo describe como optimización interna; en el resto de la documentación figura como **obsoleto**. No lo uses. |

## Elementos hijos

| Elemento | Obligatorio | Resumen |
|---|---|---|
| `<DisplayName>` | No | Etiqueta en la UI. |
| `<AccessToken ref>` | Uno de los dos | Variable con el access token a borrar (o el literal). |
| `<AuthorizationCode ref>` | Uno de los dos | Variable con el código a borrar (o el literal). |

La plantilla oficial incluye un `<Attributes/>` vacío que la página no documenta; no tiene efecto conocido.

## Variables de flujo

La página no documenta variables de éxito.

## Errores

### En runtime

| Código de fallo | HTTP | Causa |
|---|---|---|
| `steps.oauth.v2.invalid_access_token` | 401 | El access token es inválido. |
| `steps.oauth.v2.invalid_request-authorization_code_invalid` | 401 | El código es inválido. |
| `steps.oauth.v2.InvalidAPICallAsNoApiProductMatchFound` | 401 | El recurso no está en el API product del token. |

### Al desplegar

La página remite a los mensajes de la UI.

### Variables de fallo

| Variable | Ejemplo |
|---|---|
| `fault.name` | `fault.name = "invalid_access_token"` |
| `oauthV2.{name}.failed` | `oauthV2.DOI-Token.failed = true` |
| `oauthV2.{name}.fault.name` | `invalid_access_token` |
| `oauthV2.{name}.fault.cause` | `Invalid Access Token` |

## Ejemplos

### 1. Borrar el token en el logout

```xml
<DeleteOAuthV2Info name="DOI-Logout">
  <AccessToken ref="flujo.access_token"/>
</DeleteOAuthV2Info>
```

`flujo.access_token` se extrae antes de la cabecera `Authorization`, quitando el prefijo `Bearer `.

> [!NOTE]
> Por el cacheo de verificación de tokens (hasta 180 s), un token borrado puede seguir aceptándose unos instantes en otros message processors. La página de DeleteOAuthV2Info no lo menciona; aplica la misma prudencia que con la revocación.

### 2. Borrar un código de autorización

```xml
<DeleteOAuthV2Info name="DOI-Codigo">
  <AuthorizationCode ref="request.queryparam.code"/>
</DeleteOAuthV2Info>
```

## Diferencias en Apigee Edge

Sin diferencias documentadas.

## Antipatrones

- Usar DeleteOAuthV2Info como mecanismo de revocación estándar: se pierde la trazabilidad y la posibilidad de reaprobar. Para RFC 7009, `InvalidateToken`.
- Permitir que cualquier cliente borre tokens ajenos: el endpoint que use esta política debe comprobar que el token pertenece a quien lo pide.

## Fuentes

- DeleteOAuthV2Info policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/delete-oauth-v2-info> (consultada directamente, contenido completo, 2026-10-22).
- DeleteOAuthV2Info policy — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/delete-oauth-v2-info> (consultada directamente, 2026-10-22).
