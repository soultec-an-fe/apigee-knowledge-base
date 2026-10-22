---
id: politica-generate-jwt
titulo: GenerateJWT — referencia completa
area: politicas
tags: [generatejwt, jwt, jwe, firma, cifrado, claims, rfc7519, extensible]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
elemento_xml: GenerateJWT
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/generate-jwt-policy
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/generate-jwt-policy
revisado: 2026-10-22
---

# GenerateJWT — referencia completa

> [!NOTE]
> **Tipo:** Extensible. **Elemento raíz:** `<GenerateJWT>`.
> **Aplica a:** Apigee X, hybrid y Edge. Los JWT **cifrados** son solo de X/hybrid.

GenerateJWT crea un JWT **firmado** (con `<Algorithm>`) o **cifrado** (con `<Algorithms>`), con los claims que configures, y lo deja en una variable. Usos típicos: pasar al backend una aserción firmada de la identidad ya verificada por Apigee, emitir un token para otro sistema, o firmar datos que viajarán por canales no confiables.

Algoritmos, formatos de clave, JWKS y el riesgo de inyección de plantillas se explican en [JWT y JWS en Apigee](jwt-jws-conceptos.md).

## Sintaxis completa

### Firmado

```xml
<GenerateJWT name="GJWT-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <Type>Signed</Type>
  <Algorithm>RS256</Algorithm>
  <PrivateKey>
    <Value ref="private.jwt.clave_privada"/>
    <Password ref="private.jwt.clave_password"/>
    <Id ref="propertyset.jwt.kid"/>
  </PrivateKey>
  <Subject ref="client_id"/>
  <Issuer>https://api.ejemplo.com</Issuer>
  <Audience>urn://backend-pagos</Audience>
  <ExpiresIn>5m</ExpiresIn>
  <NotBefore>0s</NotBefore>
  <Id/>
  <AdditionalClaims>
    <Claim name="tenant" ref="flujo.tenant"/>
    <Claim name="roles" ref="flujo.roles" type="string" array="true"/>
  </AdditionalClaims>
  <AdditionalHeaders>
    <Claim name="x5t">valor</Claim>
  </AdditionalHeaders>
  <CriticalHeaders>x5t</CriticalHeaders>
  <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>
  <OutputVariable>flujo.jwt_backend</OutputVariable>
</GenerateJWT>
```

### Cifrado (solo X/hybrid)

```xml
<GenerateJWT name="GJWT-Cifrado">
  <Type>Encrypted</Type>
  <Algorithms>
    <Key>RSA-OAEP-256</Key>
    <Content>A256GCM</Content>
  </Algorithms>
  <PublicKey>
    <JWKS uri="https://socio.example.com/.well-known/jwks.json"/>
    <Id>clave-cifrado-2026</Id>
  </PublicKey>
  <Compress>true</Compress>
  <Subject ref="flujo.usuario"/>
  <ExpiresIn>10m</ExpiresIn>
  <OutputVariable>flujo.jwe</OutputVariable>
</GenerateJWT>
```

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno; da nombre a la variable de salida por defecto. |
| `continueOnError` | No | `false` | Con `true`, el flujo sigue aunque falle. |
| `enabled` | No | `true` | Con `false` no se ejecuta. |
| `async` | No | `false` | **Obsoleto.** |

## Elementos hijos

| Elemento | Obligatorio | Default | Resumen |
|---|---|---|---|
| `<Type>` | No | deducido | `Signed` o `Encrypted`; documenta la intención y exige el elemento de algoritmo que corresponde. |
| `<Algorithm>` | Uno de los dos | — | Firma: `HS*`, `RS*`, `PS*`, `ES*` (256/384/512). |
| `<Algorithms>/<Key>` y `<Content>` | Uno de los dos | — | Cifrado: algoritmo de clave y de contenido (ambos obligatorios). |
| `<SecretKey>` | Según algoritmo | — | HS* (firma) o AES-KW/GCMKW (cifrado). |
| `<PrivateKey>` | Según algoritmo | — | RS*, PS*, ES* (firma). |
| `<PublicKey>` | Según algoritmo | — | RSA-OAEP-256 o ECDH-ES* (cifrado). |
| `<PasswordKey>` | Según algoritmo | — | PBES2-* (cifrado). |
| `<DirectKey>` | Según algoritmo | — | `dir` (cifrado). |
| `<Subject>`, `<Issuer>`, `<Audience>` | No | — | Claims `sub`, `iss`, `aud` (literal o `ref`). `<Audience>` admite una lista separada por comas. |
| `<ExpiresIn>` | No | — | Vida del token → claim `exp`. |
| `<NotBefore>` | No | — | Claim `nbf`, absoluto o relativo. |
| `<Id>` | No | — | Claim `jti`. Vacío (`<Id/>`) genera un UUID aleatorio. |
| `<AdditionalClaims>` | No | — | Claims propios en el payload. |
| `<AdditionalHeaders>` | No | — | Parámetros propios en la cabecera. |
| `<CriticalHeaders>` | No | — | Contenido del parámetro `crit` de la cabecera. |
| `<Compress>` | No | — | Comprimir antes de cifrar (solo cifrado). |
| `<IgnoreUnresolvedVariables>` | No | `false` | Con `true`, una variable que no resuelve se trata como vacía. |
| `<OutputVariable>` | No | `jwt.{name}.generated_jwt` | Dónde se deja el JWT. |
| `<CustomClaims>` | — | — | Lo inserta la UI pero **no funciona y se ignora**; usa `<AdditionalClaims>`. |

### Claves

| Algoritmo | Elemento | Hijos |
|---|---|---|
| `HS256/384/512` | `<SecretKey encoding="…">` | `<Value ref="private.…"/>` (obligatorio), `<Id>` (opcional, va al `kid`) |
| `RS*`, `PS*`, `ES*` | `<PrivateKey>` | `<Value ref="private.…"/>` (PEM, obligatorio), `<Password ref="private.…"/>` (si la clave está cifrada), `<Id>` (`kid`) |
| `RSA-OAEP-256`, `ECDH-ES*` | `<PublicKey>` | **Uno** de `<Value>` (PEM), `<Certificate>` (PEM X.509) o `<JWKS>` (literal, `ref`, `uri` o `uriRef`); con `<JWKS>`, `<Id>` es **obligatorio** para elegir la clave |
| `A*KW`, `A*GCMKW` | `<SecretKey>` | `<Value>`, `<Id>` |
| `PBES2-*` | `<PasswordKey>` | `<Value ref="private.…"/>`, `<Id>`, `<SaltLength>` (default 8 bytes), `<PBKDF2Iterations>` (default 10.000) |
| `dir` | `<DirectKey>` | `<Value encoding="hex|base16|base64|base64url" ref="private.…"/>` (default base64), `<Id>` |

- `encoding` de `<SecretKey>`: sin el atributo, el secreto se toma como UTF-8.
- La clave privada RSA debe ser RSA para RS*/PS*; para ES*, una clave EC de la curva que toca. Si no, `WrongKeyType` o `InvalidCurve`.
- Usar `<PrivateKey>` con HS* o `<SecretKey>` con RS* hace fallar el despliegue (`InvalidConfigurationForActionAndAlgorithm`).

### `<ExpiresIn>` y `<NotBefore>`

`<ExpiresIn>` es una **duración** (no una fecha): número con unidad `ms` (por defecto, si no hay unidad), `s`, `m`, `h` o `d`. `10d` = `864000s`. Literal **o** `ref`, no ambos.

`<NotBefore>` acepta un tiempo relativo (`10s`, `60m`, `12h`) o absoluto en uno de estos formatos (otro formato hace fallar el despliegue con `InvalidTimeFormat`):

| Formato | Ejemplo |
|---|---|
| `yyyy-MM-dd'T'HH:mm:ss.SSSZ` | `2026-10-22T11:00:21.269-0500` |
| RFC 1123 | `Thu, 22 Oct 2026 11:00:21 COT` |
| RFC 850 | `Thursday, 22-Oct-26 11:00:21 COT` |
| ANSI C | `Thu Oct 22 11:00:21 2026` |

`iat` lo pone siempre la política.

> [!TIP]
> Para JWT que solo viajan del gateway al backend, usa vidas **muy cortas** (1-5 minutos) y un `<Audience>` específico del backend: limita el daño si se interceptan y evita que se reutilicen contra otro servicio.

### `<AdditionalClaims>` y `<AdditionalHeaders>`

Cada `<Claim>` admite:

| Atributo | Obligatorio | Qué hace |
|---|---|---|
| `name` | Sí | Nombre. No puede ser un claim registrado (`iss`, `sub`, `aud`, `iat`, `exp`, `nbf`, `jti`; el error de despliegue incluye también `kid`). En cabeceras, no puede ser `alg` ni `typ`. |
| `ref` | No | Variable con el valor. Si hay también literal, el literal es el **valor por defecto** si la variable no resuelve. |
| `type` | No | `string` (default), `number`, `boolean`, `map`. |
| `array` | No | `true` si el valor es una lista. |

`<AdditionalClaims ref="variable"/>` toma **todos** los claims de un objeto JSON en una variable, con nombres decididos en runtime.

Si un `ref` no resuelve y no hay literal: con `<IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>` el claim **no se genera**; con `false`, la política falla.

> [!CAUTION]
> Con `type="map"`, el valor de `ref` se procesa como **plantilla de mensaje**. Si contiene datos del cliente, un `{private.algo}` inyectado se expandiría y filtraría secretos dentro del token. Ver [Inyección de plantillas](jwt-jws-conceptos.md#inyección-de-plantillas).

### `<CriticalHeaders>`

Define el array `crit` de la cabecera: nombres de parámetros que el receptor **debe** entender o rechazar el token. **No añade** esos parámetros: hay que añadirlos además con `<AdditionalHeaders>`. VerifyJWT los contrasta con su `<KnownHeaders>`.

## Variables de flujo

La política **no publica variables**, aparte del JWT en `<OutputVariable>` (por defecto `jwt.{name}.generated_jwt`).

## Errores

### En runtime

Todos devuelven **401** (incluidos los de generación; traduce a 500 en tu FaultRule si el fallo es de configuración).

| Código | Causa típica en generación |
|---|---|
| `steps.jwt.GenerationFailed` | No se pudo generar el JWT. |
| `steps.jwt.SigningFailed` | Clave demasiado corta para HS384/HS512. |
| `steps.jwt.InsufficientKeyLength` | Clave HMAC por debajo de 32/48/64 bytes. |
| `steps.jwt.EncryptionFailed` | Falló el cifrado. |
| `steps.jwt.InvalidConfiguration` | `<Algorithm>` y `<Algorithms>` a la vez. |
| `steps.jwt.InvalidPrivateKey`, `InvalidPublicKey`, `InvalidSecretKey`, `InvalidPasswordKey` | La clave no cumple los requisitos. |
| `steps.jwt.KeyParsingFailed` | No se pudo leer la clave. |
| `steps.jwt.WrongKeyType`, `steps.jwt.InvalidCurve` | Tipo de clave o curva incompatible con el algoritmo. |
| `steps.jwt.InvalidJsonFormat` | JSON inválido en cabecera o payload (p. ej. en `<AdditionalClaims ref>`). |
| `steps.jwt.UnknownException` | Error desconocido. |

La tabla oficial de GenerateJWT repite también los errores de verificación (`TokenExpired`, `InvalidToken`, `JwtAudienceMismatch`…), que no se producen al generar.

### Al desplegar

`InvalidNameForAdditionalClaim`, `InvalidTypeForAdditionalClaim`, `MissingNameForAdditionalClaim`, `InvalidNameForAdditionalHeader`, `InvalidTypeForAdditionalHeader`, `InvalidValueOfArrayAttribute`, `InvalidConfigurationForActionAndAlgorithm`, `InvalidValueForElement` (algoritmo no soportado), `MissingConfigurationElement`, `InvalidKeyConfiguration` (falta `<Value>`), `EmptyElementForKeyConfiguration` (`ref` vacío), `InvalidVariableNameForSecret` e `InvalidSecretInConfig` (variable sin prefijo `private.`), `InvalidTimeFormat`.

### Variables de fallo

| Variable | Ejemplo |
|---|---|
| `fault.name` | `fault.name = "GenerationFailed"` |
| `JWT.failed` | `JWT.failed = true` (la misma para todas las políticas JWT) |

## Ejemplos

### 1. Aserción de identidad hacia el backend

Tras verificar el token del cliente, el gateway firma un JWT corto con los datos que el backend necesita y lo envía en una cabecera. El backend solo confía en la firma del gateway.

```xml
<GenerateJWT name="GJWT-Identidad-Backend">
  <Algorithm>ES256</Algorithm>
  <PrivateKey>
    <Value ref="private.gateway.clave_ec"/>
    <Id>gateway-2026-10</Id>
  </PrivateKey>
  <Issuer>https://gateway.ejemplo.com</Issuer>
  <Audience>urn://core-pagos</Audience>
  <Subject ref="accesstoken.usuario_id"/>
  <ExpiresIn>2m</ExpiresIn>
  <Id/>
  <AdditionalClaims>
    <Claim name="client_id" ref="client_id"/>
    <Claim name="scope" ref="scope"/>
  </AdditionalClaims>
  <OutputVariable>flujo.jwt_identidad</OutputVariable>
</GenerateJWT>
```

```xml
<AssignMessage name="AM-Cabecera-Identidad">
  <Set>
    <Headers>
      <Header name="X-Identidad">{flujo.jwt_identidad}</Header>
    </Headers>
  </Set>
  <AssignTo createNew="false" transport="http" type="request"/>
</AssignMessage>
```

### 2. Firma HMAC con secreto en base64url

```xml
<GenerateJWT name="GJWT-HS256">
  <Algorithm>HS256</Algorithm>
  <SecretKey encoding="base64url">
    <Value ref="private.jwt.secreto"/>
  </SecretKey>
  <Issuer>urn://emisor</Issuer>
  <ExpiresIn>15m</ExpiresIn>
</GenerateJWT>
```

El secreto decodificado debe medir al menos 32 bytes.

## Diferencias en Apigee Edge

| Aspecto | Apigee X / hybrid | Apigee Edge |
|---|---|---|
| JWT cifrado (`<Algorithms>`, `<PublicKey>`, `<PasswordKey>`, `<DirectKey>`, `<Compress>`) | Sí | No |
| Atributo `encoding` en `<SecretKey>` | Sí | No documentado |
| Algoritmos de firma | HS, RS, PS, ES | HS, RS, PS, ES |
| Errores | Incluye `EncryptionFailed`, `InvalidConfiguration`, `Invalid*Key` | Sin los de cifrado |

## Antipatrones

- JWT de vida larga hacia el backend, o sin `<Audience>`.
- Claims con `type="map"` alimentados con datos del cliente.
- Secretos o claves privadas en variables sin el prefijo `private.` (no despliega) o en PropertySets en lugar de KVM cifrado.
- Usar `<CustomClaims>` (se ignora).
- Meter datos sensibles en un JWT **firmado**: cualquiera puede leer el payload. Si deben ser secretos, cífralo.

## Fuentes

- GenerateJWT policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/generate-jwt-policy> (consultada directamente, contenido completo, 2026-10-22).
- Generate JWT policy — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/generate-jwt-policy> (consultada directamente, 2026-10-22).
