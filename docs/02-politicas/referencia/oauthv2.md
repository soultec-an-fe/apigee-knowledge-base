---
id: politica-oauthv2
titulo: OAuthV2 — referencia completa
area: politicas
tags: [oauthv2, oauth2, access-token, refresh-token, verifyaccesstoken, generateaccesstoken, jwt, rfc6749, rfc9068, extensible]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
elemento_xml: OAuthV2
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/oauthv2-policy
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/oauthv2-policy
revisado: 2026-10-23
---

# OAuthV2 — referencia completa

> [!NOTE]
> **Tipo:** Extensible. **Elemento raíz:** `<OAuthV2>`.
> **Aplica a:** Apigee X, hybrid y Edge. Las operaciones de tokens JWT, `<CacheExpiryInSeconds>` y `<RFCCompliantRequestResponse>` son solo de X/hybrid (ver [Diferencias en Apigee Edge](#diferencias-en-apigee-edge)).

OAuthV2 es la política con la que Apigee actúa como **servidor de autorización OAuth 2.0** (emite códigos y tokens) y como **servidor de recursos** (verifica tokens). Una misma política hace **una sola operación**, elegida con `<Operation>`, así que un flujo completo usa varias instancias: por ejemplo, el grant *authorization code* necesita cuatro (generar código, generar token, verificar token, refrescar token).

Para la visión de conjunto (grant types, scopes, duraciones recomendadas) ver [OAuth 2.0 en Apigee](../../03-seguridad/02-oauth2.md). Las políticas relacionadas son [GetOAuthV2Info](get-oauth-v2-info.md), [SetOAuthV2Info](set-oauth-v2-info.md), [DeleteOAuthV2Info](delete-oauth-v2-info.md) y [RevokeOAuthV2](revoke-oauth-v2.md).

> [!TIP]
> Para autorizar con identidades de Google Cloud IAM en vez de tokens emitidos por Apigee, existe la política Standard [VerifyIAM](verify-iam.md).

## Operaciones

| `<Operation>` | Qué hace | Flujo típico |
|---|---|---|
| `GenerateAuthorizationCode` | Emite un código de autorización. | Authorization code, paso 1 |
| `GenerateAccessToken` | Emite un access token opaco (y refresh token, salvo en client credentials). | Todos los grants salvo implícito |
| `GenerateAccessTokenImplicitGrant` | Emite un access token para el grant implícito. | Implícito |
| `RefreshAccessToken` | Canjea un refresh token por un access token nuevo. | Refresh |
| `VerifyAccessToken` | Valida el access token de una petición. | Proxies de recurso |
| `InvalidateToken` | Revoca un token concreto. | Logout, revocación (RFC 7009) |
| `ValidateToken` | Reaprueba un token revocado que no haya vencido. | Soporte |
| `GenerateJWTAccessToken` | Como `GenerateAccessToken`, pero el access token es un **JWT** firmado (RFC 9068). Solo X/hybrid. | Todos los grants |
| `GenerateJWTAccessTokenImplicitGrant` | JWT para el grant implícito. Solo X/hybrid. | Implícito |
| `VerifyJWTAccessToken` | Verifica un access token JWT. Solo X/hybrid. | Proxies de recurso |
| `RefreshJWTAccessToken` | Refresca y emite un JWT nuevo. Solo X/hybrid. | Refresh |

Si se omite `<Operation>`, Apigee deduce la operación de `<SupportedGrantTypes>`; si tampoco hay grant types, solo funciona `authorization_code`. En la práctica declara **siempre** `<Operation>`: sin ella el despliegue falla con `OperationRequired`, y la UI la exige por esquema.

> [!WARNING]
> El grant **implícito** y el grant **password** (*resource owner password credentials*) están desaconsejados por las buenas prácticas actuales de OAuth (RFC 9700, *OAuth 2.0 Security Best Current Practice*). Apigee los sigue soportando; para apps nuevas usa authorization code con PKCE o client credentials. Esta valoración no es de la documentación de Apigee sino del estándar.

## Sintaxis

Cada operación usa un subconjunto de elementos. Ejemplo para `GenerateAccessToken` con client credentials:

```xml
<OAuthV2 name="OA-Generar-Token" continueOnError="false" enabled="true">
  <DisplayName>Generar token</DisplayName>
  <Operation>GenerateAccessToken</Operation>
  <ExpiresIn ref="propertyset.oauth.access_ttl_ms">1800000</ExpiresIn>
  <SupportedGrantTypes>
    <GrantType>client_credentials</GrantType>
  </SupportedGrantTypes>
  <GrantType>request.formparam.grant_type</GrantType>
  <Scope>request.formparam.scope</Scope>
  <Attributes>
    <Attribute name="tenant" ref="app.tenant" display="false"/>
  </Attributes>
  <RFCCompliantRequestResponse>true</RFCCompliantRequestResponse>
  <GenerateResponse enabled="true"/>
</OAuthV2>
```

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno. Da nombre a las variables `oauthv2accesstoken.{name}.*`, `oauthV2.{name}.*`, etc. |
| `continueOnError` | No | `false` | Con `true`, el flujo sigue aunque la política falle. Ver `<GenerateErrorResponse>`. |
| `enabled` | No | `true` | Con `false` no se ejecuta. |
| `async` | No | `false` | **Obsoleto.** |

## Elementos por operación

`G` = generación (`GenerateAccessToken`, `GenerateAuthorizationCode`, implícito, refresh), `V` = verificación, `R` = revocación/aprobación, `J` = operaciones JWT.

| Elemento | Default | Operaciones | Resumen |
|---|---|---|---|
| `<Operation>` | ver arriba | Todas | Operación a ejecutar. |
| `<SupportedGrantTypes>/<GrantType>` | `authorization_code` e `implicit` | G | Grants aceptados por este endpoint. |
| `<GrantType>` | `request.formparam.grant_type` | G | Dónde está el `grant_type` de la petición. |
| `<ClientId>` | `request.formparam.client_id` | G | Dónde está el `client_id`. Solo admite ese valor. |
| `<Code>` | `request.formparam.code` | G (authorization code) | Dónde está el código de autorización. |
| `<RedirectUri>` | `request.formparam.redirect_uri` | G (code, implícito) | Dónde está el `redirect_uri`. |
| `<ResponseType>` | `request.formparam.response_type` | G (code, implícito) | `code` o `token`. |
| `<State>` | — | G | Dónde está el `state` (anti-CSRF). |
| `<Scope>` | — | G y V | En G: variable con los scopes pedidos. En V: lista fija de scopes exigidos. |
| `<UserName>`, `<PassWord>` | `request.formparam.username` / `password` | G (password) | Dónde están las credenciales del usuario. |
| `<RefreshToken>` | `request.formparam.refresh_token` | G (refresh) | Dónde está el refresh token. |
| `<AppEndUser>` | — | G | ID del usuario final que se guarda en el token. |
| `<Attributes>/<Attribute>` | — | G | Atributos personalizados del token o del código (máx. 18). |
| `<ExpiresIn>` | valor del sistema | G | Vida del access token o del código, en **milisegundos**. |
| `<RefreshTokenExpiresIn>` | 30 días (X) / 2 años (Edge) | G | Vida del refresh token, en milisegundos. |
| `<ReuseRefreshToken>` | `false` | G (refresh) | Reutilizar el refresh token en vez de rotarlo. |
| `<GenerateResponse>` | `true` en X / `false` en Edge | G | Devolver la respuesta al cliente o solo poblar variables. |
| `<GenerateErrorResponse>` | `false` | G | Devolver respuesta de error aun con `continueOnError="true"`. |
| `<RFCCompliantRequestResponse>` | `false` | G (X/hybrid) | Respuestas conformes a RFC 6749/6750. |
| `<AccessToken>` | cabecera `Authorization` | V | Variable donde está el token. |
| `<AccessTokenPrefix>` | — (Edge: `Bearer`) | V | Prefijo a quitar del valor de `<AccessToken>`. |
| `<CacheExpiryInSeconds>` | 180 | V (X/hybrid) | TTL de la caché de verificación. |
| `<Tokens>/<Token>` | — | R | Token a revocar o reaprobar. |
| `<Algorithm>` | — | J | `HS256/384/512` o `RS256/384/512`. |
| `<SecretKey>/<Value ref>` | — | J (HS*) | Clave HMAC. |
| `<PrivateKey>/<Value ref>` | — | J (RS*, generar y refrescar) | Clave privada RSA en PEM. |
| `<PublicKey>/<Value ref>` | — | J (RS*, verificar) | Clave pública o certificado. |
| `<ExternalAuthorization>` | `false` | G | No validar `client_id`/`secret` contra Apigee (tokens de terceros). |
| `<ExternalAccessToken>`, `<ExternalRefreshToken>`, `<ExternalAuthorizationCode>` | — | G | Dónde están el token, refresh o código **externos**. |
| `<StoreToken>` | `false` | G | Persistir el token externo. |

### Generación de tokens

#### `<SupportedGrantTypes>` y `<GrantType>`

`<SupportedGrantTypes>` lista los grants aceptados: `client_credentials`, `authorization_code`, `password`, `implicit`. Un grant inválido hace fallar el despliegue (`InvalidGrantType`); uno incompatible con la operación, `GrantTypesNotApplicableForOperation`. `<GrantType>` (hijo directo de `<OAuthV2>`) indica **dónde** leer el parámetro `grant_type` de la petición; Apigee comprueba que su valor esté en la lista.

> [!WARNING]
> La documentación reconoce un **bug**: los errores de grant type no soportado (`UnSupportedGrantType`) no siempre se lanzan bien y el proxy **no entra en el flujo de error**. Valida el `grant_type` tú mismo antes de la política si dependes de ese rechazo.

#### Ubicación de los parámetros

`<ClientId>`, `<Code>`, `<RedirectUri>`, `<ResponseType>`, `<State>`, `<Scope>`, `<UserName>`, `<PassWord>`, `<RefreshToken>` y `<AppEndUser>` reciben el **nombre de una variable**. Por defecto los parámetros se esperan como `application/x-www-form-urlencoded` en el cuerpo (`request.formparam.*`), como pide RFC 6749. Se pueden mover a cabeceras o query params, una ubicación por parámetro. `<ClientId>` es la excepción: **solo** admite `request.formparam.client_id`.

> [!CAUTION]
> No muevas credenciales (`client_secret`, `password`, `refresh_token`) a **query params**: quedan en logs de acceso, historiales y cabeceras `Referer`. El `client_id` y el `client_secret` deberían llegar en `Authorization: Basic` o en el cuerpo.

#### Grant password: `<UserName>` y `<PassWord>`

La política **solo comprueba que estén presentes**; no valida la contraseña. Tienes que autenticar al usuario contra tu proveedor de identidad (p. ej. con ServiceCallout) **antes** de que la política emita el token.

#### `<RedirectUri>` y la URL de callback de la app

| Caso | Resultado |
|---|---|
| La app tiene Callback URL registrada y la petición trae `redirect_uri` | Deben coincidir; si no, error. |
| La app tiene Callback URL y la petición no trae `redirect_uri` | Se usa la registrada. |
| La app **no** tiene Callback URL | `redirect_uri` es obligatorio y **se acepta cualquier URL**. Riesgo de seguridad: solo con clientes de confianza. |

> [!IMPORTANT]
> Por defecto la comparación es de **prefijo** (*forward match*), no exacta: `https://app.com/cb` acepta `https://app.com/cb/lo-que-sea`. Para exigir coincidencia exacta hay que activar la propiedad de organización `features.isStrictOAuthUriValidation = true`, que en X/hybrid solo puede activar el soporte de Google Cloud. Para OAuth con terceros, pídela: la coincidencia exacta es lo que recomienda el estándar actual.

#### `<Scope>` en generación

Variable con los scopes solicitados (separados por espacio). El token recibe los scopes pedidos que la app tiene permitidos por sus API products. Ver [Scopes](../../03-seguridad/02-oauth2.md#scopes).

#### `<Attributes>`

Hasta **18** atributos personalizados por token o código. Cada `<Attribute>` tiene `name`, `ref` (si la variable resuelve, gana sobre el literal) y `display` (default `true`). Los atributos de un código de autorización **se heredan** en el access token que se genere con él. Después se leen como `accesstoken.{atributo}` tras `VerifyAccessToken`.

> [!WARNING]
> `display="false"` **no se persiste**: oculta el atributo en esta respuesta, pero al refrescar el token, o al canjear un código, el atributo vuelve a aparecer en la respuesta. Para mantenerlo oculto, vuelve a declararlo con `display="false"` en la política de refresco o filtra la respuesta con JavaScript/AssignMessage.

#### `<ExpiresIn>` y `<RefreshTokenExpiresIn>`

Ambos en **milisegundos** en la política, pero `expires_in` en la respuesta y en las variables está en **segundos**. Admiten literal y `ref` (gana la variable). Valores no positivos hacen fallar el despliegue (`InvalidValueForExpiresIn`, `InvalidValueForRefreshTokenExpiresIn`); usarlos en una operación que no los admite, `ExpiresInNotApplicableForOperation` / `RefreshTokenExpiresInNotApplicableForOperation`.

| Valor | Apigee X / hybrid | Apigee Edge |
|---|---|---|
| Default de `<RefreshTokenExpiresIn>` | 2.592.000.000 ms = **30 días** (desde el 31-may-2023) | 63.072.000.000 ms = **2 años** (desde el 5-ago-2024) |
| `-1` | No documentado | Vence según el máximo del sistema; el token muestra `"expires_in": "0"` |

Mínimo efectivo: los access tokens se cachean **al menos 180 segundos** desde su último acceso, así que un `<ExpiresIn>` menor de 180 s no hace vencer antes el token. No hay forma de forzar el vencimiento de un token ya emitido; para invalidarlo, revócalo. Ver los límites en [Límites](../../10-referencia/01-limites.md).

#### `<ReuseRefreshToken>`

Con `false` (default), cada refresco emite un refresh token **nuevo** (rotación). Con `true`, se reutiliza el mismo hasta que vence. La rotación es lo recomendable: limita el daño de un refresh token filtrado.

#### `<GenerateResponse>` y `<GenerateErrorResponse>`

| Elemento | `true` | `false` |
|---|---|---|
| `<GenerateResponse>` | La política responde directamente al cliente con el JSON del token. | No responde; puebla variables (`oauthv2accesstoken.{name}.*`) para que construyas tu propia respuesta. |
| `<GenerateErrorResponse>` | Con `continueOnError="true"`, devuelve igualmente la respuesta de error. | (default) Con `continueOnError="true"`, solo puebla variables. |

Con `<GenerateResponse>true</GenerateResponse>`, un error se devuelve **directamente**, sin pasar por el flujo de error, y las variables de fallo no se pueblan. Si necesitas un formato de error propio, usa `false`.

#### `<RFCCompliantRequestResponse>` (solo X/hybrid)

Por defecto la respuesta de token **no cumple** RFC 6749/6750. Con `true`:

| Aspecto | `false` / ausente (default) | `true` |
|---|---|---|
| `Cache-Control` | No se envía | `Cache-Control: no-store` y `Pragma: no-cache` en respuestas con tokens o credenciales |
| `token_type` | `"BearerToken"` | `"Bearer"` |
| `expires_in`, `refresh_token_expires_in` | Strings (`"3600"`) | Números (`3600`) |
| Error de refresh token vencido | `{"ErrorCode": "InvalidRequest", "Error": "Refresh Token expired"}` | `{"error": "invalid_grant", "error_description": "refresh token expired"}` |

> [!IMPORTANT]
> Para APIs consumidas por clientes OAuth estándar (librerías, perfiles como FAPI), declara `<RFCCompliantRequestResponse>true</RFCCompliantRequestResponse>`: muchas librerías rechazan `token_type: "BearerToken"` o un `expires_in` en string. Aun así, la respuesta incluye propiedades extra (`api_product_list`, `developer.email`, `organization_name`…), que el RFC permite. Si no quieres exponerlas, usa `<GenerateResponse enabled="false"/>` y arma la respuesta con AssignMessage.

### Verificación de tokens

#### `<AccessToken>` y `<AccessTokenPrefix>`

Por defecto `VerifyAccessToken` lee `Authorization: Bearer <token>`. Con `<AccessToken>` se indica otra variable; en ese caso, **por defecto no se espera prefijo** y se toma el valor entero. Si la variable sí lleva un prefijo, decláralo en `<AccessTokenPrefix>`: la política lo quita junto con el espacio, y si el prefijo no está, falla. `<AccessTokenPrefix>` solo tiene efecto junto con `<AccessToken>`.

> [!CAUTION]
> Aceptar el token en query param (`<AccessToken>request.queryparam.token</AccessToken>`) es posible pero lo expone en logs y en `Referer`. RFC 6750 lo desaconseja.

#### `<Scope>` en generación

Los scopes que puede tener un token salen de los **API products de la app**: Apigee arma la unión de los scopes de todos sus productos. Si el cliente pide un scope que no está en esa lista, no lo obtiene.

> [!WARNING]
> **Sin scope pedido, el token recibe todos.** Si el cliente no envía `scope`, o lo envía vacío, o la operación `GenerateAccessToken` no tiene `<Scope>`, Apigee emite el token con **todos** los scopes de todos los productos de la app. Para aplicar mínimo privilegio, exige que la petición traiga `scope` (condición + [RaiseFault](raise-fault.md)) o reparte los permisos en productos distintos. Fuente: *Working with OAuth2 scopes* (consultada el 2026-10-23).

#### `<Scope>` en verificación

Lista **fija** de scopes separados por espacios; no admite variables. La verificación pasa si el token tiene **al menos uno** de los scopes listados (`<Scope>READ WRITE</Scope>` acepta un token con solo `READ`). Si ninguno coincide, `InsufficientScope` (`403`). Para exigir **todos**, encadena varias políticas o comprueba la variable `scope` con una condición.

#### `<CacheExpiryInSeconds>` (solo X/hybrid)

La primera verificación de un token lo lee del almacén persistente y cachea el resultado (estado, productos, atributos). Las siguientes, hasta el TTL, leen de memoria. Default y máximo: **180 s**; rango 1-180. Admite `ref`. Bajarlo acorta la ventana en la que un token revocado sigue funcionando, a costa de rendimiento.

> [!WARNING]
> Revocar un token (con `InvalidateToken`, [RevokeOAuthV2](revoke-oauth-v2.md) o la API) **no tiene efecto inmediato**: puede seguir aceptándose hasta 180 s (o el `<CacheExpiryInSeconds>` configurado).

#### Productos y recursos

`VerifyAccessToken` también comprueba que el proxy y el recurso pedido estén en algún API product del token. Si no, `InvalidAPICallAsNoApiProductMatchFound` (`401`). Las variables `apiproduct.*` se pueblan solas si los productos tienen bien configurados entornos, proxies y recursos; si no, hay que fijar `flow.resource.name`.

### Revocación y reaprobación: `<Tokens>/<Token>`

```xml
<Tokens>
  <Token type="accesstoken" cascade="true">request.formparam.token</Token>
</Tokens>
```

| Atributo | Obligatorio | Valores | Efecto |
|---|---|---|---|
| `type` | Sí | `accesstoken`, `refreshtoken` | Tipo del token de la variable. Con `refreshtoken`, si no se encuentra como refresh token, Apigee lo busca como access token. |
| `cascade` | No | `true` (default), `false` | Propaga la operación al token asociado. |

Combinaciones en `InvalidateToken`:

| Quieres revocar | Configuración |
|---|---|
| Access token y su refresh token | `type="accesstoken"` (con cualquier `cascade`: por seguridad, el refresh token queda inutilizable) |
| Solo el refresh token, sin tocar el access token | `type="refreshtoken" cascade="false"` |
| Solo el access token, conservando el refresh token | **No soportado** |

- Revocar un token ya revocado no da error: no hace nada.
- **No se pueden revocar access tokens JWT**, ni con OAuthV2 el refresh token asociado a un JWT (da error en runtime). El refresh token de un JWT sí se puede revocar con [RevokeOAuthV2](revoke-oauth-v2.md).
- `ValidateToken` reaprueba un token revocado que no haya vencido; con `cascade="true"`, también el asociado.
- Falta `<Token>` → despliegue fallido (`TokenValueRequired`).

### Tokens JWT (solo X/hybrid)

Las operaciones `*JWT*` emiten access tokens en formato JWT según **RFC 9068**, en lugar de un token opaco. El **refresh token sigue siendo opaco**.

| Parte | Contenido |
|---|---|
| Cabecera | `typ: "at+JWT"` (siempre) y `alg` |
| Claims que pone Apigee | `iss` (`https://{dominio}/{basepath}` del proxy), `jti` (UUID), `exp`, `iat` |
| Claims de la configuración | `sub` (`client_id`, o el usuario final en grants password y code; se controla con `<AppEndUser>`), `client_id`, `scope` |

| Algoritmo | Generar / refrescar | Verificar |
|---|---|---|
| `HS256`, `HS384`, `HS512` | `<SecretKey><Value ref/></SecretKey>` | `<SecretKey>` |
| `RS256`, `RS384`, `RS512` | `<PrivateKey><Value ref/></PrivateKey>` | `<PublicKey><Value ref/></PublicKey>` |

- Longitud mínima de la clave HMAC: **32 bytes** (HS256), **48** (HS384), **64** (HS512). Una clave más corta da error en runtime (`InsufficientKeyLength`).
- La variable de `ref` de una clave secreta o privada **debe empezar por `private.`** (`InvalidVariableNameForKey` si no). Guárdalas en un KVM con alcance de entorno. La pública puede ir en un PropertySet.
- El token debe tener `typ` = `at+JWT` para verificarse (`InvalidTypeInJWTHeader`).
- Errores de despliegue específicos: `InvalidValueForAlgorithm`, `MissingKeyConfiguration`, `EmptyValueElementForKeyConfiguration`, `InvalidKeyConfiguration` (clave que no corresponde a la familia del algoritmo), `EmptyRefAttributeForKeyconfiguration`.

> [!NOTE]
> **Discrepancia en `<PrivateKey>`.** La descripción dice que se usa con algoritmos RSA (RS256/384/512), pero la fila "Presence" de la misma página dice "obligatorio cuando el algoritmo es HS256, HS384 o HS512". La guía de JWT OAuth y el error `InvalidKeyConfiguration` confirman que `<PrivateKey>` es para **RSA** y `<SecretKey>` para **HMAC**.

> [!TIP]
> Un access token JWT permite que otros servicios lo validen sin llamar a Apigee, pero **no se puede revocar**: su vida debe ser corta. Si necesitas revocación inmediata, usa tokens opacos.

### Tokens de terceros

Con `<ExternalAuthorization>true</ExternalAuthorization>`, Apigee no valida `client_id`/`client_secret` contra su almacén y puede **importar** un token emitido por otro servidor de autorización (indicado con `<ExternalAccessToken>`, `<ExternalRefreshToken>` o `<ExternalAuthorizationCode>`). Con `<StoreToken>true</StoreToken>` el token externo se persiste y luego se puede verificar con `VerifyAccessToken` como si fuera propio.

## Variables de flujo

### Tras `VerifyAccessToken`

| Grupo | Variables principales |
|---|---|
| Token | `access_token`, `client_id`, `grant_type`, `token_type`, `issued_at` (ms epoch), `expires_in` (s), `status`, `scope`, `accesstoken.{atributo}`, `organization_name`, `revoke_reason` (solo hybrid; `REVOKED_BY_APP`, `REVOKED_BY_ENDUSER`, `REVOKED_BY_APP_ENDUSER`, `TOKEN_REVOKED`) |
| API product | `apiproduct.name`, `apiproduct.{atributo}` |
| App | `app.name`, `app.id`, `app.status`, `app.callbackUrl`, `app.scopes`, `app.apiproducts`, `app.appType`, `app.{atributo}`… |
| Desarrollador (`app.appType` = `Developer`) | `developer.id`, `developer.email`, `developer.status`, `developer.{atributo}`… |
| AppGroup (`app.appType` = `AppGroup`) | `appgroup.name`, `appgroup.displayName`, `appgroup.id`, `appOwnerStatus`, atributos del AppGroup |

> [!WARNING]
> `developer.id`, `developer.app.id` y `appgroup.id` son identificadores internos que pueden cambiar; no los uses como identificador de Quota, clave de KVM ni identidad enviada al backend. Ver [VerifyAPIKey — Variables de flujo](verify-api-key.md#variables-de-flujo). `developer.apps` añade mucha latencia si el desarrollador tiene más de 10 apps. Con `VerifyJWTAccessToken`, `grant_type` y `revoke_reason` no se pueblan.

### Tras `GenerateAuthorizationCode`

Prefijo `oauthv2authcode.{name}.`: `code`, `redirect_uri`, `scope`, `client_id`.

### Tras `GenerateAccessToken` y `RefreshAccessToken`

Prefijo `oauthv2accesstoken.{name}.`: `access_token`, `client_id`, `expires_in` (s), `scope`, `status`, `token_type` (`BearerToken`), `developer.email`, `organization_name`, `api_product_list`, `refresh_token`, `refresh_token_expires_in`, `refresh_token_issued_at`, `refresh_token_status`, `refresh_count`. Las variables de refresh token no aplican a client credentials, que no emite refresh token.

### Tras `GenerateAccessTokenImplicitGrant`

`oauthv2accesstoken.{name}.access_token` y `oauthv2accesstoken.{name}.expires_in`.

## Errores

### En runtime

| Código de fallo | HTTP | Causa | Operaciones |
|---|---|---|---|
| `steps.oauth.v2.access_token_expired` | 401 | Token vencido. | Verify, Invalidate |
| `steps.oauth.v2.access_token_not_approved` | 401 | Token revocado. | Verify |
| `steps.oauth.v2.apiproduct_doesnot_exist` | 401 | El API product pedido no está entre los del token. | Verify |
| `steps.oauth.v2.InvalidAccessToken` | 401 | Falta la palabra `Bearer` en `Authorization`. | Verify |
| `steps.oauth.v2.InvalidAPICallAsNoApiProductMatchFound` | 401 | El proxy o recurso no está en el API product del token. | Verify |
| `steps.oauth.v2.InsufficientScope` | 403 | Ningún scope exigido está en el token. | Verify |
| `steps.oauth.v2.invalid_client` | 401 | `client_id` inválido con `<GenerateResponse>true`. | Generate, Refresh |
| `steps.oauth.v2.InvalidClientIdentifier` | 500 | `client_id` inválido con `<GenerateResponse>false`. | Generate, Refresh |
| `steps.oauth.v2.InvalidRequest` | 400 | Parámetros faltantes o incorrectos (código genérico). | Generate*, Refresh |
| `steps.oauth.v2.FailedToResolveAccessToken` | 500 | La variable de `<AccessToken>` no resolvió. | (según la tabla) Generate |
| `steps.oauth.v2.FailedToResolveAuthorizationCode` | 500 | La variable de `<Code>` no resolvió. | GenerateAuthorizationCode |
| `steps.oauth.v2.FailedToResolveClientId` | 500 | La variable de `<ClientId>` no resolvió. | Generate*, Refresh |
| `steps.oauth.v2.FailedToResolveRefreshToken` | 500 | La variable de `<RefreshToken>` no resolvió. | Refresh |
| `steps.oauth.v2.FailedToResolveToken` | 500 | La variable de `<Tokens>` no resolvió. | Validate, Invalidate |
| `steps.oauth.v2.InvalidParameter` | 500 | Se indicó access token y código a la vez. | GenerateAuthorizationCode, implícito |
| `steps.oauth.v2.InvalidTokenType` | 500 | `type` de `<Token>` incorrecto. | Validate, Invalidate |
| `steps.oauth.v2.MissingParameter` | 500 | `response_type=token` sin grant types. | GenerateAuthorizationCode, implícito |
| `steps.oauth.v2.UnSupportedGrantType` | 500 | Grant no listado en `<SupportedGrantTypes>` (ver el bug arriba). | Generate*, Refresh |

> [!TIP]
> Google recomienda capturar **a la vez** `invalid_client` e `InvalidClientIdentifier`, porque el nombre depende de `<GenerateResponse>`. Fíjate también en que un `client_id` inválido con `<GenerateResponse>false</GenerateResponse>` devuelve `500`: corrígelo a `401` en tu FaultRule.

Errores de las operaciones JWT de verificación (todos `401`, prefijo `oauth.v2.`): `JWTSigningFailed`, `InvalidValueForJWTAlgorithm`, `InsufficientKeyLength`, `JWTAlgorithmMismatch`, `JWTDecodingFailed`, `MissingMandatoryClaimsInJWT`, `InvalidJWTSignature`, `InvalidTypeInJWTHeader`. En generación y refresco de JWT, los errores siguen el formato de RFC 6749 §5.2.

### Al desplegar

`InvalidValueForExpiresIn`, `InvalidValueForRefreshTokenExpiresIn`, `InvalidGrantType`, `ExpiresInNotApplicableForOperation`, `RefreshTokenExpiresInNotApplicableForOperation`, `GrantTypesNotApplicableForOperation`, `OperationRequired`, `InvalidOperation`, `TokenValueRequired`, más los de JWT descritos arriba.

### Variables de fallo

Solo se pueblan con `<GenerateResponse>false</GenerateResponse>` (con `true`, el error se devuelve directamente).

| Variable | Ejemplo |
|---|---|
| `fault.name` | `fault.name = "InvalidRequest"` |
| `oauthV2.{name}.failed` | `oauthV2.OA-Generar-Token.failed = true` |
| `oauthV2.{name}.fault.name` | `InvalidRequest`. En `VerifyAccessToken` el nombre lleva el prefijo `keymanagement.service.` (p. ej. `keymanagement.service.invalid_access_token`). |
| `oauthV2.{name}.fault.cause` | `Required param : grant_type` |

> [!NOTE]
> Las variables de fallo empiezan por `oauthV2` con **V mayúscula**, a diferencia de las de éxito (`oauthv2accesstoken`). El ejemplo de FaultRule de la propia página usa `invalid_access_token`, que no aparece en la tabla de errores de X pero sí en la de Edge (`steps.oauth.v2.invalid_access_token`). Para el detalle de los códigos HTTP de cada error, ver la [referencia de códigos HTTP de OAuth](../../10-referencia/02-codigos-de-error.md).

## Ejemplos

### 1. Endpoint de token client credentials conforme a RFC

```xml
<OAuthV2 name="OA-Token-CC">
  <Operation>GenerateAccessToken</Operation>
  <SupportedGrantTypes>
    <GrantType>client_credentials</GrantType>
  </SupportedGrantTypes>
  <GrantType>request.formparam.grant_type</GrantType>
  <Scope>request.formparam.scope</Scope>
  <ExpiresIn>1800000</ExpiresIn>
  <RFCCompliantRequestResponse>true</RFCCompliantRequestResponse>
  <GenerateResponse enabled="true"/>
</OAuthV2>
```

El cliente envía `client_id:client_secret` en `Authorization: Basic` y `grant_type=client_credentials` en el cuerpo form-urlencoded.

### 2. Verificación con scope y TTL de caché reducido

```xml
<OAuthV2 name="OA-Verificar-Pagos">
  <Operation>VerifyAccessToken</Operation>
  <Scope>pagos:escribir</Scope>
  <CacheExpiryInSeconds>30</CacheExpiryInSeconds>
</OAuthV2>
```

### 3. Authorization code: generar código y canjearlo

```xml
<OAuthV2 name="OA-Generar-Codigo">
  <Operation>GenerateAuthorizationCode</Operation>
  <ExpiresIn>300000</ExpiresIn>
  <AppEndUser>flujo.usuario_autenticado</AppEndUser>
  <Attributes>
    <Attribute name="consentimiento_id" ref="flujo.consentimiento_id" display="false"/>
  </Attributes>
  <GenerateResponse enabled="true"/>
</OAuthV2>
```

```xml
<OAuthV2 name="OA-Canjear-Codigo">
  <Operation>GenerateAccessToken</Operation>
  <SupportedGrantTypes>
    <GrantType>authorization_code</GrantType>
  </SupportedGrantTypes>
  <ExpiresIn>600000</ExpiresIn>
  <RefreshTokenExpiresIn>86400000</RefreshTokenExpiresIn>
  <RFCCompliantRequestResponse>true</RFCCompliantRequestResponse>
  <GenerateResponse enabled="true"/>
</OAuthV2>
```

`flujo.usuario_autenticado` debe venir de tu propio login (la política no autentica al usuario). `consentimiento_id` se hereda en el access token y se lee luego como `accesstoken.consentimiento_id`.

> [!NOTE]
> OAuthV2 **no implementa PKCE** (`code_challenge`/`code_verifier`) por sí sola. Si lo necesitas (FAPI, apps públicas), guarda el `code_challenge` como atributo del código y verifica el `code_verifier` en el canje con JavaScript antes de `OA-Canjear-Codigo`. Esta observación no está en la página de la política; contrástala con los ejemplos de [apigee/devrel](https://github.com/apigee/devrel).

### 4. Refresco con rotación

```xml
<OAuthV2 name="OA-Refrescar">
  <Operation>RefreshAccessToken</Operation>
  <ExpiresIn>600000</ExpiresIn>
  <ReuseRefreshToken>false</ReuseRefreshToken>
  <RFCCompliantRequestResponse>true</RFCCompliantRequestResponse>
  <GenerateResponse enabled="true"/>
</OAuthV2>
```

### 5. Endpoint de revocación (RFC 7009)

```xml
<OAuthV2 name="OA-Revocar">
  <Operation>InvalidateToken</Operation>
  <Tokens>
    <Token type="accesstoken" cascade="true">request.formparam.token</Token>
  </Tokens>
</OAuthV2>
```

### 6. Access token JWT firmado con RSA (X/hybrid)

```xml
<OAuthV2 name="OA-Token-JWT">
  <Operation>GenerateJWTAccessToken</Operation>
  <SupportedGrantTypes>
    <GrantType>client_credentials</GrantType>
  </SupportedGrantTypes>
  <Algorithm>RS256</Algorithm>
  <PrivateKey>
    <Value ref="private.oauth.rsa_privada"/>
  </PrivateKey>
  <ExpiresIn>600000</ExpiresIn>
  <GenerateResponse enabled="true"/>
</OAuthV2>
```

```xml
<OAuthV2 name="OA-Verificar-JWT">
  <Operation>VerifyJWTAccessToken</Operation>
  <Algorithm>RS256</Algorithm>
  <PublicKey>
    <Value ref="propertyset.oauth.rsa_publica"/>
  </PublicKey>
</OAuthV2>
```

### 7. Respuesta de error uniforme

```xml
<FaultRule name="fr-oauth">
  <Condition>oauthV2.OA-Verificar-Pagos.failed = true</Condition>
  <Step>
    <Name>AM-Error-401-Token</Name>
    <Condition>fault.name != "InsufficientScope"</Condition>
  </Step>
  <Step>
    <Name>AM-Error-403-Scope</Name>
    <Condition>fault.name = "InsufficientScope"</Condition>
  </Step>
</FaultRule>
```

## Almacenamiento y ciclo de vida

- En X y hybrid, los access y refresh tokens se guardan **hasheados** en Cassandra por defecto: si la base de datos se viera comprometida, los tokens no serían utilizables.
- Los tokens se **purgan** 3 días (259.200 s) después de que hayan vencido el access token y, si existe, su refresh token.
- Cada organización viene con un proxy `oauth` de ejemplo con un endpoint de token preconfigurado.
- Con QPS muy bajos y muchos message processors, `VerifyAPIKey` y `OAuthV2` pueden tener latencias p90+ elevadas por mal aprovechamiento de la caché.

## Diferencias en Apigee Edge

| Aspecto | Apigee X / hybrid | Apigee Edge |
|---|---|---|
| Operaciones JWT (`*JWTAccessToken*`), `<Algorithm>`, claves | Sí | **No** |
| `<CacheExpiryInSeconds>` | Sí (1-180 s) | No |
| `<RFCCompliantRequestResponse>` | Sí | No (la respuesta nunca es conforme) |
| Default de `<GenerateResponse>` | `true` | `false` |
| `<AccessTokenPrefix>` | Cualquier prefijo, junto con `<AccessToken>` | Solo `Bearer` |
| `<ExpiresIn>` / `<RefreshTokenExpiresIn>` = `-1` | No documentado | Máximo del sistema |
| Default de `<RefreshTokenExpiresIn>` | 30 días | 2 años; en Private Cloud, propiedades `conf_keymanagement_oauth_*_expiry_time_in_millis` del message processor |
| Variables de propietario | Developer o **AppGroup** | Developer o **Company** (migran a AppGroup automáticamente) |
| Tokens hasheados | Por defecto | No mencionado para Edge |
| `features.isStrictOAuthUriValidation` | Lo activa soporte | Soporte (Cloud) o API de gestión (Private Cloud) |
| Errores | Tabla de X | Incluye además `invalid_access_token` y `apiresource_doesnot_exist` |

## Antipatrones

- Access tokens de vida larga (no se pueden revocar de forma efectiva) o refresh tokens emitidos sin exponer el flujo de refresco.
- Dejar `<RFCCompliantRequestResponse>` en `false` en APIs para clientes OAuth estándar.
- Aceptar `redirect_uri` sin Callback URL registrada, o depender de la coincidencia por prefijo.
- Credenciales o tokens en query params.
- Grant password o implícito en apps nuevas.
- Suponer que la revocación es inmediata.
- Claves HMAC cortas o claves privadas fuera de un KVM `private.`.

Ver también el [catálogo de antipatrones](../../09-antipatrones/01-catalogo-antipatrones.md).

## Fuentes

- OAuthV2 policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/oauthv2-policy> (consultada directamente, contenido completo, 2026-10-22).
- OAuthV2 policy — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/oauthv2-policy> (consultada directamente, 2026-10-22).
- Using JWT OAuth tokens: <https://docs.cloud.google.com/apigee/docs/api-platform/security/oauth/using-jwt-oauth> (consultada directamente, 2026-10-22).
- Validating and invalidating access tokens: <https://docs.cloud.google.com/apigee/docs/api-platform/security/oauth/validating-and-invalidating-access-tokens> (consultada directamente, 2026-10-22).
- RFC 6749 (OAuth 2.0), RFC 6750 (Bearer), RFC 7009 (revocación), RFC 9068 (JWT access tokens), RFC 9700 (Security BCP): <https://www.rfc-editor.org/>
- Working with OAuth2 scopes: <https://docs.cloud.google.com/apigee/docs/api-platform/security/oauth/working-scopes> (consultada directamente, contenido completo, 2026-10-23).
