---
id: seguridad-oauth2
titulo: OAuth 2.0 en Apigee
area: seguridad
tags: [oauth2, access-token, refresh-token, client-credentials, authorization-code, scopes]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://cloud.google.com/apigee/docs/api-platform/security/oauth/oauth-introduction
revisado: 2026-08-20
---

# OAuth 2.0 en Apigee

Apigee puede actuar como **servidor de autorización OAuth 2.0** completo, o simplemente como **resource server** que valida tokens emitidos por un IdP externo.

## Decidir el rol primero

| Situación | Diseño |
|---|---|
| Ya tienes un IdP (Okta, Auth0, Entra ID, Keycloak, Google) | Apigee = **resource server**. Usa [`VerifyJWT`](03-jwt-jws.md) contra el JWKS del IdP. **No** montes OAuth en Apigee |
| No tienes IdP y solo necesitas autenticación máquina-a-máquina | Apigee = **servidor de autorización** con `client_credentials` |
| Necesitas consentimiento de usuario final | Apigee puede hacer `authorization_code`, pero un IdP dedicado lo hace mejor |

> [!IMPORTANT]
> El error más caro que se comete: montar un servidor OAuth completo en Apigee cuando la organización ya tiene un IdP. Duplica la gestión de identidad y crea dos fuentes de verdad sobre quién puede hacer qué.

## Grant types soportados

| Grant | Uso | Requiere secreto |
|---|---|---|
| `client_credentials` | Máquina a máquina | Sí |
| `authorization_code` | App web con backend | Sí |
| `password` | ⚠️ Desaconsejado por el propio OAuth 2.1 | Sí |
| `implicit` | ⚠️ Obsoleto, no usar | No |
| `refresh_token` | Renovación sin re-autenticar | Sí |

## Flujo client credentials — el más común

### 1. Proxy de token

`apiproxy/proxies/default.xml` (ProxyEndpoint del proxy `oauth-v1`):

```xml
<Flows>
    <Flow name="Token">
        <Condition>(proxy.pathsuffix MatchesPath "/token") and (request.verb = "POST")</Condition>
        <Request>
            <Step><Name>OA-GenerarToken</Name></Step>
        </Request>
        <Response/>
    </Flow>
</Flows>
<RouteRule name="sin-target"/>   <!-- el token se genera en el propio proxy -->
```

`policies/OA-GenerarToken.xml`:

```xml
<OAuthV2 continueOnError="false" enabled="true" name="OA-GenerarToken">
    <DisplayName>Generar access token</DisplayName>
    <Operation>GenerateAccessToken</Operation>
    <ExpiresIn>1800000</ExpiresIn>          <!-- 30 minutos, en milisegundos -->
    <SupportedGrantTypes>
        <GrantType>client_credentials</GrantType>
    </SupportedGrantTypes>
    <GrantType>request.formparam.grant_type</GrantType>
    <GenerateResponse enabled="true"/>
</OAuthV2>
```

El cliente llama:

```bash
curl -X POST https://api.empresa.com/oauth/v1/token \
  -u "CONSUMER_KEY:CONSUMER_SECRET" \
  -d "grant_type=client_credentials"
```

Y recibe:

```json
{
  "access_token": "…",
  "token_type": "BearerToken",
  "expires_in": "1799",
  "scope": "pedidos.read pedidos.write",
  "developer.email": "dev@example.com",
  "organization_name": "mi-org",
  "api_product_list": "[producto-basico]"
}
```

### 2. Verificación en los proxies de recurso

```xml
<OAuthV2 continueOnError="false" enabled="true" name="OA-VerificarToken">
    <Operation>VerifyAccessToken</Operation>
    <AccessToken>request.header.authorization</AccessToken>
</OAuthV2>
```

Igual que `VerifyAPIKey`, esto resuelve el contexto de producto: `apiproduct.name`, `developer.email`, `client_id`, y valida que el producto cubre la operación.

## Scopes

Los scopes se definen en el **API product** y se aplican en la verificación:

```xml
<OAuthV2 name="OA-VerificarConScope">
    <Operation>VerifyAccessToken</Operation>
    <AccessToken>request.header.authorization</AccessToken>
    <Scope>pedidos.write</Scope>
</OAuthV2>
```

Autorización por scope y operación:

```xml
<Flow name="CrearPedido">
    <Condition>(proxy.pathsuffix MatchesPath "/pedidos") and (request.verb = "POST")</Condition>
    <Request>
        <Step><Name>OA-VerificarEscritura</Name></Step>
    </Request>
</Flow>
<Flow name="ListarPedidos">
    <Condition>(proxy.pathsuffix MatchesPath "/pedidos") and (request.verb = "GET")</Condition>
    <Request>
        <Step><Name>OA-VerificarLectura</Name></Step>
    </Request>
</Flow>
```

## Enriquecer el token

Añadir atributos propios (tenant, rol, plan) al token en el momento de emisión:

```xml
<SetOAuthV2Info continueOnError="false" enabled="true" name="SO-Enriquecer">
    <AccessToken ref="oauthv2accesstoken.OA-GenerarToken.access_token"/>
    <Attributes>
        <Attribute name="tenant_id" ref="verifyapikey.VAK.tenant_id"/>
        <Attribute name="plan" ref="apiproduct.name"/>
    </Attributes>
</SetOAuthV2Info>
```

Y leerlos en la verificación:

```xml
<Condition>oauthv2accesstoken.OA-VerificarToken.accesstoken.tenant_id = "acme"</Condition>
```

Límite: **18 atributos personalizados por token**.

## Revocación

```xml
<!-- Revocar un token concreto -->
<DeleteOAuthV2Info name="DO-Revocar">
    <AccessToken ref="request.formparam.token"/>
</DeleteOAuthV2Info>

<!-- Revocar todos los tokens de una app, en cascada -->
<RevokeOAuthV2 name="RO-RevocarApp">
    <AppId ref="request.formparam.app_id"/>
    <Cascade>true</Cascade>
</RevokeOAuthV2>

<!-- Revocar todos los tokens de un usuario final -->
<RevokeOAuthV2 name="RO-RevocarUsuario">
    <EndUserId ref="request.formparam.user_id"/>
    <Cascade>true</Cascade>
</RevokeOAuthV2>
```

## Límites y expiración

| Parámetro | Rango permitido |
|---|---|
| Expiración de access token | **≥ 180 segundos, ≤ 30 días** |
| Expiración de refresh token | **≥ 1 día, ≤ 2 años** |
| Tamaño del token | 2 KB |
| Atributos personalizados | 18 |

### Recomendación de duraciones

| Tipo de cliente | Access token | Refresh token |
|---|---|---|
| Máquina a máquina (confiable) | 30–60 min | No emitir |
| App web con backend | 15–30 min | 8–24 h |
| App móvil | 15–30 min | 30–90 días |

> [!CAUTION]
> **Antipatrón documentado: expiración muy larga para tokens OAuth.**
> Un access token de larga duración no se puede revocar de forma efectiva: si se filtra, sigue siendo válido hasta que caduque. Access tokens **cortos**; renovación vía refresh token.

> [!CAUTION]
> **Antipatrón documentado: emitir refresh tokens sin invocar el refresh flow.**
> Si emites refresh tokens pero no expones `RefreshAccessToken`, acumulas tokens inútiles en Cassandra durante hasta 2 años. Emite refresh tokens **solo** si implementas realmente el flujo de refresco.

## Comparativa: OAuth de Apigee vs. VerifyJWT

| Dimensión | OAuthV2 de Apigee | VerifyJWT contra IdP externo |
|---|---|---|
| Almacenamiento del token | Cassandra (opaco) | Ninguno (autocontenido) |
| Validación | Consulta a Cassandra | Criptográfica local + JWKS cacheado |
| Latencia | Mayor | Menor |
| Revocación inmediata | ✅ Sí | ❌ No (hasta expiración) |
| Identidad de usuario final | Limitada | Completa (claims del IdP) |
| Quién gestiona identidades | Apigee | Tu IdP |
| Contexto de API product | ✅ Automático | Manual (mapear claims a productos) |

> [!TIP]
> **Patrón híbrido frecuente:** `VerifyJWT` valida la identidad del IdP, y `VerifyAPIKey` (con la key de la app) resuelve el contexto de producto y cuota. Se obtiene identidad de usuario **y** gobierno de API.

## Fuentes

- <https://cloud.google.com/apigee/docs/api-platform/security/oauth/oauth-introduction>
- <https://cloud.google.com/apigee/docs/api-platform/reference/policies/oauthv2-policy>
- <https://cloud.google.com/apigee/docs/api-platform/reference/limits>
