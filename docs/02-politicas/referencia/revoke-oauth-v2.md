---
id: politica-revoke-oauth-v2
titulo: RevokeOAuthV2 — referencia completa
area: politicas
tags: [revokeoauthv2, oauth2, revocacion, app-id, end-user, cascade, extensible]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
elemento_xml: RevokeOAuthV2
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/revoke-oauth-v2-policy
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/revoke-oauth-v2-policy
revisado: 2026-10-22
---

# RevokeOAuthV2 — referencia completa

> [!NOTE]
> **Tipo:** Extensible. **Elemento raíz:** `<RevokeOAuthV2>`.
> **Aplica a:** Apigee X, hybrid y Edge Public Cloud. **No está disponible en Edge for Private Cloud.**

RevokeOAuthV2 revoca **en bloque** todos los access tokens de una **app** (por su ID), de un **usuario final**, o de la combinación de ambos, opcionalmente solo los emitidos antes de un instante. Es la pieza para "cerrar sesión en todos los dispositivos", "revocar el acceso de esta app de terceros" o responder a una credencial comprometida.

| Necesidad | Política |
|---|---|
| Revocar un token concreto | [OAuthV2](oauthv2.md#revocación-y-reaprobación-tokenstoken) con `InvalidateToken` |
| Revocar todos los tokens de una app o de un usuario | **RevokeOAuthV2** |
| Revocar el refresh token de un access token JWT | **RevokeOAuthV2** (OAuthV2 no puede) |

> [!CAUTION]
> Una sola ejecución puede revocar **muchísimos tokens**, y según la documentación la revocación **no se puede deshacer**. Valida bien el ID que recibe la política y protege el endpoint que la usa.

> [!WARNING]
> Como toda revocación, no es inmediata: por la caché de verificación, un token revocado puede seguir aceptándose hasta 180 s.

## Requisito: el usuario final dentro del token

El access token guarda el ID de la app en `application_name`, así que revocar por app siempre funciona. Pero **por defecto no guarda el usuario final**. Para revocar por usuario hay que emitir los tokens con [`<AppEndUser>`](oauthv2.md#ubicación-de-los-parámetros) en la política OAuthV2; el valor queda en el campo `app_enduser` del token.

```xml
<OAuthV2 name="OA-Generar-Con-Usuario">
  <Operation>GenerateAccessToken</Operation>
  <SupportedGrantTypes>
    <GrantType>authorization_code</GrantType>
  </SupportedGrantTypes>
  <AppEndUser>flujo.usuario_id</AppEndUser>
  <GenerateResponse enabled="true"/>
</OAuthV2>
```

## Sintaxis completa

```xml
<RevokeOAuthV2 name="RO-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <AppId ref="variable.con.app_id"/>
  <EndUserId ref="variable.con.usuario"/>
  <RevokeBeforeTimestamp ref="variable.con.epoch_ms"/>
  <Cascade>false</Cascade>
</RevokeOAuthV2>
```

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno. |
| `continueOnError` | No | `false` | Con `true`, el flujo sigue aunque falle. |
| `enabled` | No | `true` | Con `false` no se ejecuta. |

## Elementos hijos

| Elemento | Obligatorio | Default | Resumen |
|---|---|---|---|
| `<DisplayName>` | No | `name` | Etiqueta en la UI. |
| `<AppId>` | Al menos uno de los dos | `request.formparam.app_id` | ID de la app (UUID, el `application_name` del token). Literal o `ref`. |
| `<EndUserId>` | Al menos uno de los dos | `request.formparam.enduser_id` | ID del usuario final (`app_enduser`). Literal o `ref`. |
| `<RevokeBeforeTimestamp>` | No | momento de ejecución | Revoca solo los tokens emitidos **antes** de este instante (epoch UTC en **milisegundos**, entero de 64 bits). |
| `<Cascade>` | No | `false` | Revocar también los refresh tokens. |

Con `<AppId>` y `<EndUserId>` a la vez, se revocan los tokens de ese usuario **en esa app**. Si ambos quedan vacíos, error `EmptyAppAndEndUserId`.

### `<RevokeBeforeTimestamp>`

No puede estar en el futuro (`InvalidFutureTimestamp`) ni ser anterior al 1 de enero de 2014 (`InvalidEarlyTimestamp`). Útil para "revocar todo lo emitido antes del incidente" sin tocar tokens emitidos después de rotar credenciales.

### `<Cascade>`

| Tipo de access token | `true` | `false` (default) |
|---|---|---|
| Opaco | Revoca access token **y** refresh token | Revoca solo el access token; el refresh token sigue válido |
| JWT | Revoca solo el **refresh token** (un JWT no se puede revocar) | Nada útil: el JWT no se revoca |

> [!IMPORTANT]
> Con el default `false`, el cliente puede usar su refresh token para obtener un access token nuevo justo después de la revocación. Para cortar el acceso de verdad, usa `<Cascade>true</Cascade>`.

## Cómo obtener los IDs

| ID | Dónde |
|---|---|
| App ID | Campo `application_name` del token; o la API de gestión `organizations.developers.apps.list` / `apps.get` |
| Usuario final | El valor que tu sistema de identidad pasó a `<AppEndUser>` al emitir el token |

## Variables de flujo

La política **no publica variables**.

## Errores

### En runtime

| Código de fallo | HTTP | Causa |
|---|---|---|
| `steps.oauth.v2.InvalidFutureTimestamp` | 500 | `<RevokeBeforeTimestamp>` en el futuro. |
| `steps.oauth.v2.InvalidEarlyTimestamp` | 500 | Anterior al 1-ene-2014. |
| `steps.oauth.v2.InvalidTimestamp` | 500 | Timestamp inválido. |
| `steps.oauth.v2.EmptyAppAndEndUserId` | 500 | Faltan `<AppId>` y `<EndUserId>`. |

### Al desplegar

La página remite a los mensajes de la UI.

### Variables de fallo

| Variable | Ejemplo |
|---|---|
| `fault.name` | `fault.name = "InvalidFutureTimestamp"` |
| `oauthV2.{name}.failed` | `oauthV2.RO-Usuario.failed = true` |
| `oauthV2.{name}.fault.name` | `EmptyAppAndEndUserId` |
| `oauthV2.{name}.fault.cause` | Descripción del fallo |

## Ejemplos

### 1. "Cerrar sesión en todos los dispositivos"

El usuario autenticado (no un parámetro que mande el cliente) se toma del token verificado.

```xml
<RevokeOAuthV2 name="RO-Todos-Los-Dispositivos">
  <EndUserId ref="flujo.usuario_autenticado"/>
  <Cascade>true</Cascade>
</RevokeOAuthV2>
```

### 2. Revocar el acceso de una app de terceros para un usuario

Típico en Open Banking: el usuario retira el consentimiento a una app concreta desde el portal de su banco.

```xml
<RevokeOAuthV2 name="RO-Retirar-Consentimiento">
  <AppId ref="admin.app_id"/>
  <EndUserId ref="flujo.usuario_autenticado"/>
  <Cascade>true</Cascade>
</RevokeOAuthV2>
```

### 3. Incidente: revocar todo lo emitido para una app antes de rotar su secreto

```xml
<RevokeOAuthV2 name="RO-Incidente">
  <AppId ref="admin.app_id"/>
  <RevokeBeforeTimestamp ref="admin.momento_rotacion_ms"/>
  <Cascade>true</Cascade>
</RevokeOAuthV2>
```

## Diferencias en Apigee Edge

| Aspecto | Apigee X / hybrid | Apigee Edge |
|---|---|---|
| Disponibilidad | Sí | Edge Public Cloud sí; **Edge for Private Cloud no** |
| JWT access tokens | `<Cascade>` revoca su refresh token | Edge no tiene tokens JWT de OAuth |
| Elementos y errores | Iguales | Iguales |

## Antipatrones

- `<Cascade>false</Cascade>` cuando el objetivo es cortar el acceso.
- Tomar `<EndUserId>` o `<AppId>` de un parámetro del cliente sin comprobar que le pertenece.
- Emitir tokens sin `<AppEndUser>` y descubrir después que no se pueden revocar por usuario.

## Fuentes

- RevokeOAuthV2 policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/revoke-oauth-v2-policy> (consultada directamente, contenido completo, 2026-10-22).
- Revoke OAuth V2 policy — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/revoke-oauth-v2-policy> (consultada directamente, 2026-10-22).
- Enable retrieval and revocation of OAuth 2.0 access tokens by end user ID, app id, or both: <https://docs.cloud.google.com/apigee/docs/api-platform/security/oauth/enable-retrieval-and-revocation-oauth-20-access-tokens-end-user-id-app-id-or-both>
