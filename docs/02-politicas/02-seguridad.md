---
id: politicas-seguridad
titulo: Políticas de Seguridad
area: politicas
tags: [verifyapikey, oauthv2, jwt, jws, hmac, threat-protection, accesscontrol]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://cloud.google.com/apigee/docs/api-platform/reference/policies/verify-api-key-policy
revisado: 2026-08-20
---

# Políticas de Seguridad

## VerifyAPIKey

La política más usada. Valida la API key **y**, como efecto secundario crítico, **resuelve el contexto** de app, developer y API product.

```xml
<VerifyAPIKey continueOnError="false" enabled="true" name="VAK-VerificarApiKey">
    <DisplayName>Verificar API key</DisplayName>
    <APIKey ref="request.header.x-api-key"/>
</VerifyAPIKey>
```

Fuentes habituales de la key:

```xml
<APIKey ref="request.header.x-api-key"/>       <!-- recomendado -->
<APIKey ref="request.queryparam.apikey"/>       <!-- evitar: queda en logs y en el historial -->
<APIKey ref="request.formparam.apikey"/>
```

> [!WARNING]
> **No pases API keys en query params** salvo compatibilidad heredada. Acaban en logs de acceso, en el historial del navegador y en cabeceras `Referer`.

### Variables que puebla

Tras un `VerifyAPIKey` exitoso dispones de:

| Variable | Contenido |
|---|---|
| `apiproduct.name` | Producto que autorizó la llamada |
| `apiproduct.developer.quota.limit` / `.interval` / `.timeunit` | Cuota del producto |
| `developer.id` / `developer.email` | Desarrollador |
| `developer.app.name` / `app.name` | App cliente |
| `client_id` | Consumer key |
| `verifyapikey.NOMBRE.*` | Todos los atributos, incluidos los custom attributes |

Los atributos personalizados de la app y del producto también quedan disponibles:

```xml
<Condition>verifyapikey.VAK-VerificarApiKey.nivel_soporte = "premium"</Condition>
```

### Qué valida exactamente

1. Que la key existe y está **aprobada**.
2. Que la app está **aprobada** y no revocada.
3. Que el developer está **activo**.
4. Que **algún** API product asociado a la key incluye este proxy **y** la operación (verbo + ruta) que se está llamando.

Ese punto 4 es la autorización real: la key no da acceso "al proxy", da acceso a lo que declaran sus productos.

### Errores

| `fault.name` | Causa |
|---|---|
| `FailedToResolveAPIKey` | La variable referenciada en `<APIKey ref>` no existe |
| `InvalidApiKey` | La key no existe |
| `InvalidApiKeyForGivenResource` | La key existe pero ningún producto cubre este recurso |
| `DeveloperStatusNotActive` | Developer inactivo |
| `ApplicationNotApproved` | App revocada |
| `keymanagement.service.CompanyStatusNotActive` | Empresa/AppGroup inactivo |

---

## OAuthV2

Política multi-operación: el atributo `<Operation>` decide qué hace.

### Generar access token (client credentials)

```xml
<OAuthV2 continueOnError="false" enabled="true" name="OA-GenerarToken">
    <DisplayName>Generar access token</DisplayName>
    <Operation>GenerateAccessToken</Operation>
    <ExpiresIn>3600000</ExpiresIn>          <!-- milisegundos -->
    <SupportedGrantTypes>
        <GrantType>client_credentials</GrantType>
    </SupportedGrantTypes>
    <GrantType>request.queryparam.grant_type</GrantType>
    <GenerateResponse enabled="true"/>
</OAuthV2>
```

### Generar con refresh token (authorization code)

```xml
<OAuthV2 name="OA-GenerarTokenAuthCode">
    <Operation>GenerateAccessToken</Operation>
    <ExpiresIn>1800000</ExpiresIn>              <!-- 30 min -->
    <RefreshTokenExpiresIn>86400000</RefreshTokenExpiresIn>  <!-- 24 h -->
    <SupportedGrantTypes>
        <GrantType>authorization_code</GrantType>
    </SupportedGrantTypes>
    <GrantType>request.formparam.grant_type</GrantType>
    <Code>request.formparam.code</Code>
    <RedirectUri>request.formparam.redirect_uri</RedirectUri>
    <GenerateResponse enabled="true"/>
</OAuthV2>
```

### Verificar access token

```xml
<OAuthV2 continueOnError="false" enabled="true" name="OA-VerificarToken">
    <Operation>VerifyAccessToken</Operation>
    <AccessToken>request.header.authorization</AccessToken>
    <Scope>read write</Scope>
</OAuthV2>
```

### Refrescar

```xml
<OAuthV2 name="OA-Refrescar">
    <Operation>RefreshAccessToken</Operation>
    <ExpiresIn>1800000</ExpiresIn>
    <RefreshToken>request.formparam.refresh_token</RefreshToken>
    <GenerateResponse enabled="true"/>
</OAuthV2>
```

### Operaciones disponibles

| Operation | Función |
|---|---|
| `GenerateAccessToken` | Emite access token (+ refresh según grant) |
| `GenerateAuthorizationCode` | Emite authorization code |
| `RefreshAccessToken` | Intercambia refresh token por access token nuevo |
| `VerifyAccessToken` | Valida el token en la petición entrante |
| `InvalidateToken` | Invalida un token concreto |
| `ValidateToken` | Valida sin consumir contexto completo |

### Límites de OAuth

| Límite | Valor |
|---|---|
| Expiración de access token | ≥ 180 segundos, ≤ 30 días |
| Expiración de refresh token | ≥ 1 día, ≤ 2 años |
| Tamaño del token | 2 KB |
| Atributos personalizados por token | 18 |

> [!CAUTION]
> **Antipatrón documentado: expiración muy larga para tokens OAuth.**
> Un access token de larga vida no se puede revocar de forma efectiva: si se filtra, sigue siendo válido. Usa access tokens **cortos** (15–60 min) y refresh tokens para renovar.

> [!CAUTION]
> **Antipatrón documentado: emitir refresh tokens sin invocar el refresh flow.**
> Si generas un refresh token pero tu API nunca expone `RefreshAccessToken`, acumulas tokens de refresco en Cassandra que nadie usará ni caducará pronto. Emite refresh tokens **solo** si implementas realmente el flujo de refresco.

### Políticas auxiliares de OAuth

```xml
<!-- Leer metadatos de un token -->
<GetOAuthV2Info name="GO-InfoToken">
    <AccessToken ref="request.header.authorization"/>
</GetOAuthV2Info>

<!-- Añadir atributos personalizados al token -->
<SetOAuthV2Info name="SO-EnriquecerToken">
    <AccessToken ref="access_token"/>
    <Attributes>
        <Attribute name="tenant_id" ref="peticion.tenant"/>
        <Attribute name="nivel">premium</Attribute>
    </Attributes>
</SetOAuthV2Info>

<!-- Revocar -->
<DeleteOAuthV2Info name="DO-RevocarToken">
    <AccessToken ref="request.formparam.token"/>
</DeleteOAuthV2Info>

<!-- Revocación masiva por app o usuario -->
<RevokeOAuthV2 name="RO-RevocarPorApp">
    <AppId ref="request.formparam.app_id"/>
    <Cascade>true</Cascade>
</RevokeOAuthV2>
```

Detalle en [OAuth 2.0](../03-seguridad/02-oauth2.md).

---

## JWT y JWS

### VerifyJWT con JWKS remoto

El caso más común: validar tokens de un IdP externo (Google, Auth0, Okta, Entra ID).

```xml
<VerifyJWT continueOnError="false" enabled="true" name="VJWT-VerificarIdP">
    <DisplayName>Verificar JWT del IdP</DisplayName>
    <Algorithm>RS256</Algorithm>
    <Source>request.header.authorization</Source>
    <PublicKey>
        <JWKS uri="https://idp.example.com/.well-known/jwks.json"/>
    </PublicKey>
    <Issuer>https://idp.example.com/</Issuer>
    <Audience>https://api.empresa.com</Audience>
    <AdditionalClaims>
        <Claim name="scope" type="string">pedidos.read</Claim>
    </AdditionalClaims>
    <TimeAllowance>30s</TimeAllowance>
</VerifyJWT>
```

> [!TIP]
> Apigee **cachea el JWKS** automáticamente y respeta las cabeceras de caché del endpoint. No necesitas cachearlo tú.

Si el header trae `Bearer <token>`, extrae primero:

```xml
<ExtractVariables name="EV-Bearer">
    <Source>request</Source>
    <Header name="Authorization">
        <Pattern ignoreCase="true">Bearer {jwt_token}</Pattern>
    </Header>
    <VariablePrefix>auth</VariablePrefix>
    <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>
</ExtractVariables>
```

y luego `<Source>auth.jwt_token</Source>`.

### GenerateJWT

Para firmar tokens hacia el backend (patrón *token exchange*):

```xml
<GenerateJWT continueOnError="false" enabled="true" name="GJWT-TokenBackend">
    <Algorithm>RS256</Algorithm>
    <PrivateKey>
        <Value ref="private.clave_firma"/>
        <Id>clave-2026-01</Id>
    </PrivateKey>
    <Subject>{client_id}</Subject>
    <Issuer>https://api.empresa.com</Issuer>
    <Audience>backend-pedidos</Audience>
    <ExpiresIn>5m</ExpiresIn>
    <AdditionalClaims>
        <Claim name="producto">{apiproduct.name}</Claim>
        <Claim name="developer">{developer.email}</Claim>
    </AdditionalClaims>
    <OutputVariable>jwt.backend</OutputVariable>
</GenerateJWT>
```

### DecodeJWT

> [!WARNING]
> **`DecodeJWT` NO verifica la firma.** Solo decodifica. Úsala para inspeccionar claims (por ejemplo, leer el `iss` para decidir qué JWKS usar) y **siempre** seguida de un `VerifyJWT`. Tomar decisiones de autorización basadas solo en `DecodeJWT` es una vulnerabilidad crítica.

Detalle completo en [JWT y JWS](../03-seguridad/03-jwt-jws.md).

---

## Threat protection

### JSONThreatProtection

```xml
<JSONThreatProtection continueOnError="false" enabled="true" name="JTP-ProtegerJson">
    <DisplayName>Proteger JSON</DisplayName>
    <ArrayElementCount>100</ArrayElementCount>
    <ContainerDepth>10</ContainerDepth>
    <ObjectEntryCount>50</ObjectEntryCount>
    <ObjectEntryNameLength>64</ObjectEntryNameLength>
    <StringValueLength>2048</StringValueLength>
    <Source>request</Source>
</JSONThreatProtection>
```

### XMLThreatProtection

```xml
<XMLThreatProtection continueOnError="false" enabled="true" name="XTP-ProtegerXml">
    <NameLimits>
        <Element>64</Element>
        <Attribute>64</Attribute>
        <NamespacePrefix>32</NamespacePrefix>
        <ProcessingInstructionTarget>32</ProcessingInstructionTarget>
    </NameLimits>
    <StructureLimits>
        <NodeDepth>10</NodeDepth>
        <AttributeCountPerElement>10</AttributeCountPerElement>
        <NamespaceCountPerElement>5</NamespaceCountPerElement>
        <ChildCount includeComment="true"
                    includeElement="true"
                    includeProcessingInstruction="true"
                    includeText="true">20</ChildCount>
    </StructureLimits>
    <ValueLimits>
        <Text>2048</Text>
        <Attribute>256</Attribute>
        <NamespaceURI>256</NamespaceURI>
        <Comment>512</Comment>
        <ProcessingInstructionData>512</ProcessingInstructionData>
    </ValueLimits>
    <Source>request</Source>
</XMLThreatProtection>
```

Protege contra *XML entity expansion* (billion laughs) y *XML bomb*.

### RegularExpressionProtection

```xml
<RegularExpressionProtection continueOnError="false" enabled="true" name="REP-AntiInyeccion">
    <Source>request</Source>
    <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>
    <URIPath>
        <Pattern>[\s]*(?i)((delete)|(exec)|(drop\s*table)|(insert)|(shutdown)|(update)|(\bor\b))</Pattern>
    </URIPath>
    <QueryParam name="q">
        <Pattern>(?i)((select)|(union)|(script)|(<))</Pattern>
    </QueryParam>
    <JSONPayload>
        <JSONPath JSONPath="$.comentario">
            <Pattern>(?i)&lt;script</Pattern>
        </JSONPath>
    </JSONPayload>
</RegularExpressionProtection>
```

> [!CAUTION]
> **Antipatrón documentado: cuantificadores greedy en RegularExpressionProtection.**
> Patrones como `.*` o `(a+)+` provocan backtracking catastrófico. Un payload malicioso de pocos KB puede bloquear un Message Processor durante segundos: se convierte en un vector de DoS, justo lo contrario de lo que pretendías. Usa cuantificadores posesivos o reluctantes (`.*?`, `.*+`) y anclas explícitas.

> [!IMPORTANT]
> Google recomienda **aplicar siempre políticas de protección de contenido a los proxies de producción**: `JSONThreatProtection`, `XMLThreatProtection`, `RegularExpressionProtection` y `SOAPMessageValidation`.

---

## AccessControl

Listas de permitidos/denegados por IP.

```xml
<AccessControl continueOnError="false" enabled="true" name="AC-SoloRedCorporativa">
    <IPRules noRuleMatchAction="DENY">
        <MatchRule action="ALLOW">
            <SourceAddress mask="24">10.20.30.0</SourceAddress>
            <SourceAddress mask="32">203.0.113.45</SourceAddress>
        </MatchRule>
    </IPRules>
    <ValidateBasedOn>XFF_HEADER</ValidateBasedOn>
</AccessControl>
```

`<ValidateBasedOn>` acepta `XFF_HEADER` (usa `X-Forwarded-For`, necesario detrás de un balanceador) o la IP de conexión directa.

Uso recomendado por Google: **restringir por IP el acceso a entornos de test**.

> [!NOTE]
> Para bloqueo de IPs a escala o mitigación de DDoS, la herramienta correcta es **Cloud Armor** delante del balanceador, no `AccessControl` en el proxy.

---

## HMAC

Verifica integridad de payloads firmados (webhooks entrantes de Stripe, GitHub, etc.).

```xml
<HMAC name="HMAC-VerificarWebhook">
    <Algorithm>HMAC-SHA256</Algorithm>
    <SecretKey ref="private.webhook_secret" encoding="utf-8"/>
    <Message ref="request.content"/>
    <Output>hmac.calculado</Output>
    <Encoding>hex</Encoding>
</HMAC>
```

Y luego comparar en tiempo constante contra la cabecera recibida.

---

## BasicAuthentication

```xml
<!-- Codificar credenciales hacia el backend -->
<BasicAuthentication name="BA-CredencialesBackend">
    <Operation>Encode</Operation>
    <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>
    <User ref="private.backend_user"/>
    <Password ref="private.backend_password"/>
    <AssignTo createNew="false">request.header.Authorization</AssignTo>
</BasicAuthentication>

<!-- Decodificar credenciales del cliente -->
<BasicAuthentication name="BA-DecodificarCliente">
    <Operation>Decode</Operation>
    <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>
    <Source>request.header.Authorization</Source>
    <User>usuario.recibido</User>
    <Password>password.recibido</Password>
</BasicAuthentication>
```

> [!TIP]
> El prefijo `private.` en el nombre de una variable hace que su valor **no aparezca en las sesiones de Trace**. Úsalo siempre para secretos.

---

## AccessEntity

Recupera entidades del perfil (app, developer, producto) como XML para consultarlas con XPath.

```xml
<AccessEntity name="AE-DatosApp">
    <EntityType value="app"/>
    <EntityIdentifier ref="developer.app.id" type="appid"/>
</AccessEntity>
```

> [!TIP]
> Buena práctica de Google: **busca apps por `uuid` (appid) en lugar de por nombre**. Es notablemente más rápido.

---

## VerifyIAM

Verifica autorización basada en IAM de Google Cloud. Útil para APIs internas consumidas por otros servicios de Google Cloud con identidades de servicio.

```xml
<VerifyIAM name="VI-VerificarIAM">
    <Source>request.header.authorization</Source>
</VerifyIAM>
```

## Fuentes

- <https://cloud.google.com/apigee/docs/api-platform/reference/policies/verify-api-key-policy>
- <https://cloud.google.com/apigee/docs/api-platform/reference/policies/oauthv2-policy>
- <https://cloud.google.com/apigee/docs/api-platform/reference/policies/verify-jwt-policy>
- <https://cloud.google.com/apigee/docs/api-platform/reference/policies/json-threat-protection-policy>
