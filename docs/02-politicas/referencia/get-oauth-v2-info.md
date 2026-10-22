---
id: politica-get-oauth-v2-info
titulo: GetOAuthV2Info — referencia completa
area: politicas
tags: [getoauthv2info, oauth2, access-token, refresh-token, authorization-code, client-id, introspeccion, extensible]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
elemento_xml: GetOAuthV2Info
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/get-oauth-v2-info-policy
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/get-oauth-v2-info-policy
revisado: 2026-10-22
---

# GetOAuthV2Info — referencia completa

> [!NOTE]
> **Tipo:** Extensible. **Elemento raíz:** `<GetOAuthV2Info>`.
> **Aplica a:** Apigee X, hybrid y Edge, con el mismo comportamiento.

GetOAuthV2Info **lee el perfil** de un access token, refresh token, código de autorización o client ID, y lo vuelca en variables de flujo, **sin verificar** la petición en curso. Usos típicos:

- un endpoint de **introspección** (`/tokeninfo`, similar a RFC 7662) que devuelve el estado y los atributos de un token;
- leer los atributos de un código o un refresh token antes de canjearlo;
- obtener los datos de una app a partir de su `client_id` (p. ej. su Callback URL) en un flujo de login propio.

Cuando ya ejecutaste `OAuthV2/VerifyAccessToken`, las variables del token ya existen: no hace falta esta política.

## Sintaxis completa

En cada instancia se usa **uno** de los cuatro elementos de entrada.

```xml
<GetOAuthV2Info name="GOI-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <AccessToken ref="request.formparam.token"/>
  <IgnoreAccessTokenStatus>false</IgnoreAccessTokenStatus>
  <!-- o bien: -->
  <!-- <RefreshToken ref="request.formparam.refresh_token"/> -->
  <!-- <AuthorizationCode ref="request.formparam.code"/> -->
  <!-- <ClientId ref="request.queryparam.client_id"/> -->
</GetOAuthV2Info>
```

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno; forma parte del nombre de todas las variables de salida. |
| `continueOnError` | No | `false` | Con `true`, un token inválido no corta el flujo y puedes responder tú (p. ej. `{"active": false}`). |
| `enabled` | No | `true` | Con `false` no se ejecuta. |
| `async` | No | `false` | **Obsoleto.** |

## Elementos hijos

| Elemento | Qué recibe | Variables que pueblan |
|---|---|---|
| `<AccessToken>` | Variable (`ref`) o literal con el access token | `oauthv2accesstoken.{name}.*` |
| `<IgnoreAccessTokenStatus>` | `true`/`false` (default `false`) | — |
| `<RefreshToken>` | Variable o literal con el refresh token | `oauthv2refreshtoken.{name}.*` |
| `<AuthorizationCode>` | Variable o literal con el código | `oauthv2authcode.{name}.*` |
| `<ClientId>` | Variable o literal con el client ID | `oauthv2client.{name}.*` |

> [!NOTE]
> La documentación indica como default de los cuatro elementos `request.formparam.access_token`, lo que parece un copia-pega de la fila de `<AccessToken>`. Declara siempre `ref` explícitamente.

### `<AccessToken>` y `<IgnoreAccessTokenStatus>`

El access token debe ser **válido**: si está vencido o revocado, la política falla (`access_token_expired`, `invalid_access_token`). Con `<IgnoreAccessTokenStatus>true</IgnoreAccessTokenStatus>` devuelve la información aunque esté vencido o revocado, lo que permite construir una introspección que responda `active: false` en vez de un error. Este elemento solo afecta a access tokens; refresh tokens y códigos se devuelven siempre, sea cual sea su estado.

### `<RefreshToken>`

Funciona igual con refresh tokens emitidos junto a access tokens opacos o junto a access tokens JWT.

### Requisito de API product

> [!IMPORTANT]
> El recurso con el que se llama al proxy que contiene esta política debe estar incluido en el API product con el que se **generó** el token. Si el endpoint es `/tokeninfo`, `/tokeninfo` tiene que estar en ese producto; si no, falla con `InvalidAPICallAsNoApiProductMatchFound` (`401`).

## Variables de flujo

### Con `<AccessToken>` (`oauthv2accesstoken.{name}.`)

`access_token`, `client_id`, `scope`, `status`, `expires_in` (s), `developer.id`, `developer.email`, `developer.app.name`, `developer.app.id`, `organization_name`, `api_product_list`, `refresh_token`, `refresh_token_status`, `refresh_token_expires_in` (s), `refresh_token_issued_at`, `refresh_count`, `accesstoken.{atributo}` y `revoke_reason` (solo hybrid).

### Con `<RefreshToken>` (`oauthv2refreshtoken.{name}.`)

Las mismas que las del access token, con el prefijo `oauthv2refreshtoken`. Los atributos personalizados quedan en `oauthv2refreshtoken.{name}.accesstoken.{atributo}`.

### Con `<AuthorizationCode>` (`oauthv2authcode.{name}.`)

`code`, `scope`, `redirect_uri`, `client_id`, `{atributo}`.

### Con `<ClientId>` (`oauthv2client.{name}.`)

`client_id`, **`client_secret`**, `redirection_uris` (así, con esa ortografía), `developer.email`, `developer.app.name`, `developer.id`, `{atributo_de_la_app}`.

> [!CAUTION]
> Con `<ClientId>`, la política deja el **`client_secret` de la app en una variable**. No lo devuelvas en ninguna respuesta, no lo registres con MessageLogging y oculta la variable en Debug con una máscara de datos (*debug mask*).

## Errores

### En runtime

| Código de fallo | HTTP | Causa |
|---|---|---|
| `steps.oauth.v2.access_token_expired` | 500 | Access token vencido. |
| `steps.oauth.v2.invalid_access_token` | 500 | Access token inválido. |
| `steps.oauth.v2.refresh_token_expired` | 500 | Refresh token vencido. |
| `steps.oauth.v2.invalid_refresh_token` | 500 | Refresh token inválido. |
| `steps.oauth.v2.authorization_code_expired` | 500 | Código vencido. |
| `steps.oauth.v2.invalid_request-authorization_code_invalid` | 500 | Código inválido. |
| `steps.oauth.v2.invalid_client-invalid_client_id` | 500 | Client ID inválido. |
| `steps.oauth.v2.InvalidAPICallAsNoApiProductMatchFound` | 401 | El recurso no está en el API product del token. |

Un token inválido devuelve **500**, no 401: si la política sirve un endpoint público, traduce el código en una FaultRule.

### Al desplegar

La página remite a los mensajes que muestra la UI; no lista códigos.

### Variables de fallo

| Variable | Ejemplo |
|---|---|
| `fault.name` | `fault.name = "invalid_access_token"` |
| `oauthV2.{name}.failed` | `oauthV2.GOI-Token.failed = true` |
| `oauthV2.{name}.fault.name` | `invalid_client-invalid_client_id` |
| `oauthV2.{name}.fault.cause` | `ClientId is Invalid` |

El `errorcode` de la respuesta usa el prefijo `keymanagement.service.` (p. ej. `keymanagement.service.invalid_client-invalid_client_id`).

## Ejemplos

### 1. Endpoint de introspección que nunca falla

```xml
<GetOAuthV2Info name="GOI-Introspeccion" continueOnError="true">
  <AccessToken ref="request.formparam.token"/>
  <IgnoreAccessTokenStatus>true</IgnoreAccessTokenStatus>
</GetOAuthV2Info>
```

Después, una AssignMessage arma la respuesta. Si la política falló o `status` no es `approved`, devuelve `{"active": false}`; si no, devuelve `active`, `scope`, `client_id` y `exp`, calculado a partir de `expires_in`.

> [!WARNING]
> Protege el endpoint de introspección (p. ej. con [VerifyAPIKey](verify-api-key.md) o Basic con credenciales de servicio): si es público, permite comprobar si un token robado sigue vivo.

### 2. Leer el consentimiento guardado en un código antes de canjearlo

```xml
<GetOAuthV2Info name="GOI-Codigo">
  <AuthorizationCode ref="request.formparam.code"/>
</GetOAuthV2Info>
```

El atributo personalizado `consentimiento_id` del código queda en `oauthv2authcode.GOI-Codigo.consentimiento_id`.

### 3. Datos públicos de la app para una pantalla de consentimiento

```xml
<GetOAuthV2Info name="GOI-App">
  <ClientId ref="request.queryparam.client_id"/>
</GetOAuthV2Info>
```

Usa `oauthv2client.GOI-App.developer.app.name` y `redirection_uris`; **nunca** `client_secret`.

## Diferencias en Apigee Edge

| Aspecto | Apigee X / hybrid | Apigee Edge |
|---|---|---|
| Elementos, variables y errores | Iguales | Iguales |
| `revoke_reason` | Solo hybrid | — |
| Refresh tokens de JWT | Soportados | Edge no tiene tokens JWT de OAuth |

## Antipatrones

- Exponer `oauthv2client.{name}.client_secret`.
- Introspección pública sin autenticar.
- Usarla en vez de `VerifyAccessToken` para autorizar peticiones: no comprueba scopes ni productos del recurso en curso como lo hace la verificación.

## Fuentes

- GetOAuthV2Info policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/get-oauth-v2-info-policy> (consultada directamente, contenido completo, 2026-10-22).
- GetOAuthV2Info policy — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/get-oauth-v2-info-policy> (consultada directamente, 2026-10-22).
