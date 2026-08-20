---
id: seguridad-jwt-jws
titulo: JWT y JWS
area: seguridad
tags: [jwt, jws, jwks, rs256, hs256, claims, token-exchange]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://cloud.google.com/apigee/docs/api-platform/reference/policies/verify-jwt-policy
revisado: 2026-08-20
---

# JWT y JWS

## Las seis políticas

| Política | Verifica firma | Uso |
|---|---|---|
| `<GenerateJWT>` | — (firma) | Emitir un JWT |
| `<VerifyJWT>` | ✅ **Sí** | Validar un JWT entrante |
| `<DecodeJWT>` | ❌ **No** | Inspeccionar claims sin validar |
| `<GenerateJWS>` | — (firma) | Emitir un JWS (payload no-JSON o detached) |
| `<VerifyJWS>` | ✅ **Sí** | Validar un JWS |
| `<DecodeJWS>` | ❌ **No** | Inspeccionar sin validar |

> [!CAUTION]
> **`DecodeJWT` y `DecodeJWS` NO verifican la firma.**
> Tomar cualquier decisión de autorización basándose solo en `DecodeJWT` es una vulnerabilidad crítica: cualquiera puede fabricar un JWT con los claims que quiera. Usa `DecodeJWT` únicamente para *inspección previa* (por ejemplo, leer el `iss` para elegir qué JWKS usar) y **siempre** seguido de `VerifyJWT`.

## VerifyJWT contra un IdP externo (caso más común)

```xml
<VerifyJWT continueOnError="false" enabled="true" name="VJWT-IdP">
    <DisplayName>Verificar JWT del IdP</DisplayName>
    <Algorithm>RS256</Algorithm>
    <Source>auth.token</Source>
    <PublicKey>
        <JWKS uri="https://idp.example.com/.well-known/jwks.json"/>
    </PublicKey>
    <Issuer>https://idp.example.com/</Issuer>
    <Audience>https://api.empresa.com</Audience>
    <AdditionalClaims>
        <Claim name="tenant" type="string" ref="peticion.tenant_esperado"/>
    </AdditionalClaims>
    <TimeAllowance>30s</TimeAllowance>
</VerifyJWT>
```

Extraer primero el token del header `Bearer`:

```xml
<ExtractVariables continueOnError="false" enabled="true" name="EV-Bearer">
    <Source>request</Source>
    <Header name="Authorization">
        <Pattern ignoreCase="true">Bearer {token}</Pattern>
    </Header>
    <VariablePrefix>auth</VariablePrefix>
    <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>
</ExtractVariables>
```

### Qué valida VerifyJWT

1. **Firma** contra la clave pública (JWKS, PEM o secreto compartido).
2. **`exp`** — no expirado (con la tolerancia de `<TimeAllowance>`).
3. **`nbf`** — ya es válido.
4. **`iss`** — coincide con `<Issuer>`.
5. **`aud`** — coincide con `<Audience>`.
6. **Claims adicionales** declarados en `<AdditionalClaims>`.

> [!TIP]
> Apigee **cachea el JWKS automáticamente** y respeta las cabeceras de caché del endpoint. No hace falta que lo cachees tú con `PopulateCache`.

### Fuentes de clave pública

```xml
<!-- JWKS remoto (recomendado: soporta rotación automática de claves) -->
<PublicKey>
    <JWKS uri="https://idp.example.com/.well-known/jwks.json"/>
</PublicKey>

<!-- JWKS desde una variable de flujo (p. ej. cargado de un KVM) -->
<PublicKey>
    <JWKS ref="jwks.contenido"/>
</PublicKey>

<!-- Clave PEM estática -->
<PublicKey>
    <Value ref="public.clave_pem"/>
</PublicKey>

<!-- Secreto compartido, para HS256 -->
<SecretKey>
    <Value ref="private.secreto_hmac"/>
</SecretKey>
```

## Algoritmos

| Familia | Algoritmos | Tipo de clave | Cuándo |
|---|---|---|---|
| RSA | `RS256`, `RS384`, `RS512` | Par pública/privada | **Recomendado** para tokens de terceros |
| ECDSA | `ES256`, `ES384`, `ES512` | Par de curva elíptica | Igual que RSA, tokens más pequeños |
| RSA-PSS | `PS256`, `PS384`, `PS512` | Par pública/privada | Variante moderna de RSA |
| HMAC | `HS256`, `HS384`, `HS512` | **Secreto compartido** | Solo entre partes que ya comparten un secreto |

> [!WARNING]
> **Nunca uses `HS256` para tokens emitidos por terceros.** El secreto de verificación es el mismo que el de firma: cualquiera que pueda verificar también puede **falsificar**. Para tokens externos, usa siempre algoritmos asimétricos (RS*/ES*/PS*).

> [!WARNING]
> **Fija siempre `<Algorithm>` explícitamente.** No permitas que el algoritmo lo determine el header `alg` del token entrante: ese es el vector del ataque clásico de confusión de algoritmo (`alg: none`, o cambiar RS256 por HS256 usando la clave pública como secreto HMAC).

## Claims resultantes

Tras `VerifyJWT`, los claims quedan disponibles con el prefijo `jwt.<nombre_politica>.`:

```
jwt.VJWT-IdP.claim.sub
jwt.VJWT-IdP.claim.iss
jwt.VJWT-IdP.claim.aud
jwt.VJWT-IdP.claim.exp
jwt.VJWT-IdP.claim.iat
jwt.VJWT-IdP.claim.scope
jwt.VJWT-IdP.claim.<cualquier_claim_custom>
jwt.VJWT-IdP.decoded.claim.<claim>     ← claims complejos decodificados
jwt.VJWT-IdP.header.alg
jwt.VJWT-IdP.header.kid
jwt.VJWT-IdP.valid
```

Autorización por scope:

```xml
<Step>
    <Name>RF-ScopeInsuficiente</Name>
    <Condition>!(jwt.VJWT-IdP.claim.scope Like "*pedidos.write*")</Condition>
</Step>
```

Autorización por rol:

```xml
<Step>
    <Name>RF-Prohibido</Name>
    <Condition>(jwt.VJWT-IdP.claim.rol != "admin") and (proxy.pathsuffix MatchesPath "/admin/**")</Condition>
</Step>
```

## GenerateJWT — token exchange hacia el backend

Patrón muy útil: el cliente se autentica con API key u OAuth contra Apigee, y Apigee emite un **JWT firmado propio** hacia el backend. El backend confía solo en Apigee y no necesita conocer al IdP ni las API keys.

```xml
<GenerateJWT continueOnError="false" enabled="true" name="GJWT-Backend">
    <DisplayName>Emitir JWT para el backend</DisplayName>
    <Algorithm>RS256</Algorithm>
    <PrivateKey>
        <Value ref="private.clave_firma_pem"/>
        <Id>clave-2026-01</Id>
    </PrivateKey>
    <Subject>{client_id}</Subject>
    <Issuer>https://api.empresa.com</Issuer>
    <Audience>backend-pedidos</Audience>
    <ExpiresIn>5m</ExpiresIn>
    <NotBefore>0s</NotBefore>
    <AdditionalClaims>
        <Claim name="producto">{apiproduct.name}</Claim>
        <Claim name="developer">{developer.email}</Claim>
        <Claim name="app">{developer.app.name}</Claim>
        <Claim name="correlation_id">{messageid}</Claim>
    </AdditionalClaims>
    <AdditionalHeaders>
        <Claim name="typ">JWT</Claim>
    </AdditionalHeaders>
    <OutputVariable>jwt.backend</OutputVariable>
</GenerateJWT>
```

Y aplicarlo:

```xml
<AssignMessage continueOnError="false" enabled="true" name="AM-JwtBackend">
    <Set>
        <Headers>
            <Header name="Authorization">Bearer {jwt.backend}</Header>
        </Headers>
    </Set>
    <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>
    <AssignTo createNew="false" transport="http" type="request"/>
</AssignMessage>
```

Colocación: **TargetEndpoint → PreFlow → Request**. Así el token no se genera si la respuesta viene de caché.

> [!TIP]
> Usa un `<ExpiresIn>` **muy corto** (1–5 minutos) para estos tokens internos. Solo tienen que sobrevivir a un salto de red.

> [!IMPORTANT]
> El `<Id>` de la clave privada se emite como claim `kid` en el header del JWT. Es lo que permite al backend elegir la clave pública correcta durante una rotación. **Inclúyelo siempre.**

## JWS vs JWT

| | JWT | JWS |
|---|---|---|
| Payload | Debe ser **JSON** | Cualquier cosa: XML, binario, texto |
| Estructura | `header.payload.signature` | `header.payload.signature` o **detached** (`header..signature`) |
| Uso típico | Autenticación y autorización | Firma de documentos y webhooks |

**JWS detached**: el payload viaja aparte (por ejemplo, en el body HTTP) y el JWS solo lleva la firma. Es el patrón de firma de mensajes de varias normativas financieras (PSD2, Open Banking).

```xml
<VerifyJWS continueOnError="false" enabled="true" name="VJWS-FirmaPeticion">
    <Algorithm>RS256</Algorithm>
    <Source>request.header.x-jws-signature</Source>
    <DetachedContent>{request.content}</DetachedContent>
    <PublicKey>
        <JWKS uri="https://cliente.example.com/jwks.json"/>
    </PublicKey>
</VerifyJWS>
```

## Errores frecuentes

| `fault.name` | Causa |
|---|---|
| `TokenExpired` | `exp` en el pasado |
| `InvalidToken` | Firma inválida o token malformado |
| `InvalidIterator` / `InvalidJsonFormat` | El token no es JSON válido tras decodificar |
| `IssuerMismatch` | El `iss` no coincide con `<Issuer>` |
| `AudienceMismatch` | El `aud` no coincide con `<Audience>` |
| `AlgorithmMismatch` | El `alg` del token no coincide con `<Algorithm>` |
| `NoMatchingPublicKey` | El `kid` del token no existe en el JWKS |
| `KeyIdMissing` | El token no lleva `kid` y el JWKS tiene varias claves |

## Gestión de claves

Nunca hardcodees claves privadas en el bundle. Opciones:

| Opción | Cuándo |
|---|---|
| **KVM cifrado** con `KeyValueMapOperations` → variable `private.*` | Lo habitual |
| **Keystore de Apigee** (`<KeyStore>` / `<KeyAlias>`) | Cuando también se usa para mTLS |
| **Secret Manager** vía `ServiceCallout` + caché | Cuando la organización centraliza secretos ahí |

```xml
<KeyValueMapOperations continueOnError="false" enabled="true"
                       name="KVM-ClaveFirma" mapIdentifier="secretos-firma">
    <Scope>environment</Scope>
    <ExpiryTimeInSecs>3600</ExpiryTimeInSecs>
    <Get assignTo="private.clave_firma_pem" index="1">
        <Key><Parameter>clave_privada_pem</Parameter></Key>
    </Get>
</KeyValueMapOperations>
```

El prefijo `private.` impide que el valor aparezca en las sesiones de Trace.

## Fuentes

- <https://cloud.google.com/apigee/docs/api-platform/reference/policies/verify-jwt-policy>
- <https://cloud.google.com/apigee/docs/api-platform/reference/policies/generate-jwt-policy>
- <https://cloud.google.com/apigee/docs/api-platform/reference/policies/verify-jws-policy>
