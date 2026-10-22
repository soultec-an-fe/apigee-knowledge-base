---
id: politica-verify-jwt
titulo: VerifyJWT — referencia completa
area: politicas
tags: [verifyjwt, jwt, jwe, jwks, oidc, firma, claims, rfc7519, standard]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
elemento_xml: VerifyJWT
tipo_politica: standard
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/verify-jwt-policy
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/verify-jwt-policy
revisado: 2026-10-22
---

# VerifyJWT — referencia completa

> [!NOTE]
> **Tipo:** Standard (cualquier tipo de entorno). **Elemento raíz:** `<VerifyJWT>`.
> **Aplica a:** Apigee X, hybrid y Edge. Descifrar JWT cifrados, `<MaxLifespan>`, `<RequiredClaims>` y `uriRef` son solo de X/hybrid.

VerifyJWT **verifica la firma** de un JWT (o lo **descifra**, si está cifrado), comprueba `exp` y `nbf` si existen, y opcionalmente que `sub`, `iss`, `aud` y otros claims tengan los valores esperados. Si todo es correcto, publica todos los claims en variables; si no, corta el flujo con un error.

Es la política para aceptar **tokens de un proveedor de identidad externo** (ID tokens de OpenID Connect, access tokens JWT de Auth0, Okta, Entra ID, Keycloak…) o JWT firmados por un socio. Algoritmos, claves y JWKS en [JWT y JWS en Apigee](jwt-jws-conceptos.md).

> [!IMPORTANT]
> Una política VerifyJWT segura comprueba **siempre**, además de la firma, el **emisor** (`<Issuer>`) y la **audiencia** (`<Audience>`). Sin ellos, cualquier token válido del mismo proveedor (emitido para otra aplicación) sería aceptado.

## Sintaxis completa

```xml
<VerifyJWT name="VJWT-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <Type>Signed</Type>
  <Algorithm>RS256, PS256</Algorithm>
  <Source>request.header.x-id-token</Source>
  <PublicKey>
    <JWKS uri="https://idp.ejemplo.com/.well-known/jwks.json"/>
  </PublicKey>
  <Issuer>https://idp.ejemplo.com</Issuer>
  <Audience>api-pagos</Audience>
  <Subject ref="flujo.sub_esperado"/>
  <Id ref="flujo.jti_esperado"/>
  <AdditionalClaims>
    <Claim name="tenant" ref="flujo.tenant"/>
  </AdditionalClaims>
  <AdditionalHeaders>
    <Claim name="x5t" ref="flujo.x5t"/>
  </AdditionalHeaders>
  <RequiredClaims>sub,iss,exp</RequiredClaims>
  <MaxLifespan useIssueTime="true">1h</MaxLifespan>
  <TimeAllowance>30s</TimeAllowance>
  <KnownHeaders>x5t</KnownHeaders>
  <IgnoreCriticalHeaders>false</IgnoreCriticalHeaders>
  <IgnoreIssuedAt>false</IgnoreIssuedAt>
  <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>
</VerifyJWT>
```

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno; da nombre a `jwt.{name}.*`. |
| `continueOnError` | No | `false` | Con `true`, un token inválido no corta el flujo. Si lo usas, comprueba `jwt.{name}.valid` antes de confiar en los claims. |
| `enabled` | No | `true` | Con `false` no se ejecuta. |
| `async` | No | `false` | **Obsoleto.** |

## Elementos hijos

| Elemento | Obligatorio | Default | Resumen |
|---|---|---|---|
| `<Type>` | No | deducido | `Signed` o `Encrypted`. |
| `<Algorithm>` | Uno de los dos | — | Firma; admite varios separados por comas (con restricciones). |
| `<Algorithms>/<Key>` (y `<Content>` opcional) | Uno de los dos | — | Cifrado (solo X/hybrid). |
| `<Source>` | No | `request.header.authorization` (quitando `Bearer`) | Variable con el JWT. |
| `<SecretKey>` | Según algoritmo | — | HS* o AES-KW. |
| `<PublicKey>` | Según algoritmo | — | RS*, PS*, ES*: `<Value>`, `<Certificate>` o `<JWKS>`. |
| `<PrivateKey>` | Según algoritmo | — | Descifrar RSA-OAEP-256 o ECDH-ES*. |
| `<PasswordKey>`, `<DirectKey>` | Según algoritmo | — | Descifrar PBES2-* o `dir`. |
| `<Issuer>`, `<Audience>`, `<Subject>`, `<Id>` | No | — | Valor esperado de `iss`, `aud`, `sub`, `jti`. |
| `<AdditionalClaims>`, `<AdditionalHeaders>` | No | — | Valores esperados de claims y parámetros propios. |
| `<RequiredClaims>` | No | — | Claims que deben **existir**, sin comprobar su valor (solo X/hybrid). |
| `<MaxLifespan>` | No | — | Vida máxima aceptada del token (solo X/hybrid). |
| `<TimeAllowance>` | No | `0s` | Margen de desfase de reloj para `exp` y `nbf`. |
| `<KnownHeaders>` | No | — | Parámetros `crit` que tu proxy entiende. |
| `<IgnoreCriticalHeaders>` | No | `false` | Ignorar `crit`. |
| `<IgnoreIssuedAt>` | No | `false` | No rechazar tokens con `iat` en el futuro. |
| `<IgnoreUnresolvedVariables>` | No | `false` | Variables que no resuelven = cadena vacía. |
| `<CustomClaims>` | — | — | Lo inserta la UI, **no funciona**; usa `<AdditionalClaims>`. |

### `<Algorithm>`

Es una **lista blanca**: el `alg` de la cabecera del token debe estar en ella, o la verificación falla (`AlgorithmMismatch`, `AlgorithmInTokenNotPresentInConfiguration`). Esto protege del ataque clásico de cambiar `alg` a `none` o a HS256 con la clave pública como secreto. Se pueden combinar `RS*` y `PS*`; no se puede mezclar HS* ni ES* con otras familias.

### `<Source>`

Sin `<Source>`, la política lee `Authorization` y **quita el prefijo `Bearer `**. Con `<Source>`, toma el valor **tal cual**, sin quitar `Bearer`: si apuntas `<Source>` a `request.header.authorization`, el token incluiría el prefijo y fallaría. Un `<Source>` vacío hace fallar el despliegue (`InvalidEmptyElement`); una variable inexistente, el runtime.

### Claves de verificación

| Algoritmo | Elemento |
|---|---|
| `HS*` | `<SecretKey encoding="…"><Value ref="private.…"/></SecretKey>` (sin `<Id>`: con él, el despliegue falla con `InvalidConfigurationForVerify`) |
| `RS*`, `PS*`, `ES*` | `<PublicKey>` con **uno** de: `<Value>` (PEM o variable), `<Certificate>` (PEM X.509 o variable), `<JWKS>` (literal, `ref`, `uri` o `uriRef`) |
| `RSA-OAEP-256`, `ECDH-ES*` | `<PrivateKey><Value ref="private.…"/><Password ref="private.…"/></PrivateKey>` |
| `A*KW`, `A*GCMKW` | `<SecretKey>` |
| `PBES2-*` | `<PasswordKey>` con `<Value>`, `<SaltLength>` y `<PBKDF2Iterations>`, que deben coincidir con los del token (`InvalidSaltLength`, `InvalidIterationCount`) |
| `dir` | `<DirectKey>` |

> [!WARNING]
> Con `<Certificate>`, Apigee **no valida** la cadena de confianza ni las fechas del certificado. Con `<JWKS uri>`, el JWKS se cachea **300 s**. Un JWKS inaccesible da `InvalidKeyConfiguration`; Google sugiere probar la conectividad con un proxy *passthrough* hacia el endpoint JWKS.

### Comprobación de claims

| Elemento | Comprueba | Error si falla |
|---|---|---|
| `<Issuer>` | `iss` igual al valor | `JwtIssuerMismatch` |
| `<Audience>` | `aud` (string o array) contiene el valor | `JwtAudienceMismatch` |
| `<Subject>` | `sub` igual al valor | `JwtSubjectMismatch` |
| `<Id>` | `jti` igual al valor | `InvalidClaim` |
| `<AdditionalClaims>/<Claim>` | Claim propio igual al valor (con `type` y `array`) | `InvalidClaim` |
| `<AdditionalHeaders>/<Claim>` | Parámetro de cabecera igual al valor | `InvalidClaim` |
| `<RequiredClaims>` | Los claims listados existen | (fallo en runtime) |

Todos admiten literal, `ref`, o ambos (el literal es el respaldo si la variable está vacía). `<AdditionalClaims ref="variable"/>` compara contra todos los claims de un objeto JSON.

> [!NOTE]
> **Discrepancias.** La página de VerifyJWT dice que `<Claim>` "admite plantillas de mensaje", mientras que la página general afirma que las políticas Verify **no** aplican plantillas al resolver `ref`. Y la descripción de `<Id>` dice que, vacío, "generará un jti aleatorio", texto copiado de GenerateJWT que no tiene sentido al verificar. No dependas de ninguno de los dos comportamientos.

### Tiempo: `<TimeAllowance>`, `<MaxLifespan>`, `<IgnoreIssuedAt>`

- `<TimeAllowance>`: margen para `exp` y `nbf` por desfase de relojes (`s`, `m`, `h`, `d`). Con `30s`, un token vencido hace 20 s se acepta. Default `0`.
- `<MaxLifespan>` (X/hybrid): rechaza tokens cuya vida (`exp` − `nbf`, o `exp` − `iat` con `useIssueTime="true"`) supere el valor (`s`, `m`, `h`, `d`, `w`). Si falta `exp` o el campo de inicio, también falla. Útil para no aceptar tokens "eternos" de un emisor mal configurado. Solo una vez por política.
- `<IgnoreIssuedAt>`: por defecto se rechaza un `iat` en el futuro; con `true` se ignora.

### `crit`: `<KnownHeaders>` e `<IgnoreCriticalHeaders>`

Si el token trae `crit`, cada nombre listado debe estar en `<KnownHeaders>`, o la verificación falla (`UnhandledCriticalHeader`). La política **no procesa** esos parámetros: solo confirma que los declaraste. `<IgnoreCriticalHeaders>true</IgnoreCriticalHeaders>` desactiva la comprobación; Google lo sugiere solo para pruebas.

## Variables de flujo

Con prefijo `jwt.{name}.`, tras verificar (también tras DecodeJWT):

| Variable | Contenido |
|---|---|
| `valid` | `true` si firma, `exp` y `nbf` son correctos. **Solo en VerifyJWT.** |
| `decoded.claim.{claim}` | Valor JSON del claim (**recomendada**). P. ej. `decoded.claim.sub`, `decoded.claim.iat` (segundos). |
| `decoded.header.{param}` | Valor JSON de un parámetro de cabecera (recomendada). |
| `claim.{claim}` | Valor como texto (compatibilidad). |
| `claim.subject`, `claim.issuer`, `claim.audience` | `sub`, `iss`, `aud` (string o array). |
| `claim.expiry`, `claim.issuedat`, `claim.notbefore` | En **milisegundos** epoch. |
| `header.algorithm`, `header.kid`, `header.type`, `header.{param}` | Cabecera. |
| `header-json`, `payload-json` | Cabecera y payload completos en JSON. |
| `payload-claim-names` | Lista de claims del payload. |
| `is_expired`, `seconds_remaining`, `time_remaining_formatted`, `expiry_formatted` | Estado de vencimiento. |

> [!WARNING]
> Cuidado con las unidades: `claim.expiry` está en **milisegundos**, `decoded.claim.exp` en **segundos**.

## Errores

### En runtime

Todos `401`. Los propios de la verificación:

| Código | Causa |
|---|---|
| `steps.jwt.InvalidToken` | Firma inválida. |
| `steps.jwt.TokenExpired` | Vencido (fuera del `<TimeAllowance>`). |
| `steps.jwt.TokenNotYetValid` | `nbf` en el futuro. |
| `steps.jwt.JwtIssuerMismatch`, `JwtAudienceMismatch`, `JwtSubjectMismatch` | Claim registrado distinto. |
| `steps.jwt.InvalidClaim` | Claim o cabecera faltante o con otro valor. |
| `steps.jwt.AlgorithmMismatch`, `AlgorithmInTokenNotPresentInConfiguration`, `NoAlgorithmFoundInHeader` | Algoritmo no permitido o ausente. |
| `steps.jwt.KeyIdMissing`, `NoMatchingPublicKey` | Con JWKS: el token no trae `kid`, o el `kid` no está en el JWKS. |
| `steps.jwt.InvalidKeyConfiguration` | JWKS inválido o inaccesible. |
| `steps.jwt.FailedToDecode`, `InvalidJsonFormat` | Token corrupto. |
| `steps.jwt.UnhandledCriticalHeader` | Parámetro `crit` no listado en `<KnownHeaders>`. |
| `steps.jwt.InvalidSaltLength`, `InvalidIterationCount` | Parámetros de PBES2 distintos. |
| `steps.jwt.InsufficientKeyLength`, `WrongKeyType`, `InvalidCurve`, `KeyParsingFailed`, `Invalid*Key` | Problemas de la clave configurada. |

### Al desplegar

Los mismos de [GenerateJWT](generate-jwt.md#al-desplegar) relativos a claims y claves, más `InvalidConfigurationForVerify` (`<Id>` dentro de `<SecretKey>`), `InvalidEmptyElement` (`<Source>` vacío) e `InvalidPublicKeyValue` (JWKS literal mal formado).

### Variables de fallo

`fault.name` (p. ej. `TokenExpired`) y `JWT.failed`.

> [!TIP]
> Responde **401** con `WWW-Authenticate: Bearer error="invalid_token"` y un mensaje genérico; no devuelvas al cliente el motivo exacto (vencido, firma, audiencia…), que ayuda a un atacante. Regístralo en tus logs.

## Ejemplos

### 1. Access token JWT de un proveedor OIDC

```xml
<VerifyJWT name="VJWT-IdP">
  <Algorithm>RS256</Algorithm>
  <PublicKey>
    <JWKS uri="https://login.ejemplo.com/.well-known/jwks.json"/>
  </PublicKey>
  <Issuer>https://login.ejemplo.com/</Issuer>
  <Audience>api://pagos</Audience>
  <RequiredClaims>sub,exp,iat</RequiredClaims>
  <MaxLifespan useIssueTime="true">1h</MaxLifespan>
  <TimeAllowance>30s</TimeAllowance>
</VerifyJWT>
```

Después, `jwt.VJWT-IdP.decoded.claim.sub` identifica al usuario y `jwt.VJWT-IdP.decoded.claim.scope` permite autorizar por scope con una condición.

### 2. Varios emisores de confianza con `uriRef` (X/hybrid)

Una DecodeJWT lee el `iss`; una consulta a un KVM devuelve su URL de JWKS **solo si el emisor está registrado**; si no, se rechaza antes de verificar.

```xml
<DecodeJWT name="DJWT-Leer-Emisor"/>
```

```xml
<KeyValueMapOperations name="KVM-Emisores" mapIdentifier="emisores-confiables">
  <Scope>environment</Scope>
  <Get assignTo="flujo.jwks_uri">
    <Key>
      <Parameter ref="jwt.DJWT-Leer-Emisor.decoded.claim.iss"/>
    </Key>
  </Get>
</KeyValueMapOperations>
```

```xml
<VerifyJWT name="VJWT-Multi-Emisor">
  <Algorithm>RS256, PS256</Algorithm>
  <PublicKey>
    <JWKS uriRef="flujo.jwks_uri"/>
  </PublicKey>
  <Issuer ref="jwt.DJWT-Leer-Emisor.decoded.claim.iss"/>
  <Audience>api://pagos</Audience>
</VerifyJWT>
```

Con un `RaiseFault` condicionado a `flujo.jwks_uri = null` entre la KVM y la VerifyJWT.

### 3. JWT firmado por un socio con certificado

```xml
<VerifyJWT name="VJWT-Socio">
  <Algorithm>PS256</Algorithm>
  <Source>request.header.x-jws-socio</Source>
  <PublicKey>
    <Certificate ref="propertyset.socios.certificado_banco_x"/>
  </PublicKey>
  <Issuer>urn://banco-x</Issuer>
  <Audience>urn://nuestro-banco</Audience>
  <MaxLifespan>5m</MaxLifespan>
</VerifyJWT>
```

Recuerda que Apigee no valida la caducidad del certificado: gestiona su rotación tú.

## Diferencias en Apigee Edge

| Aspecto | Apigee X / hybrid | Apigee Edge |
|---|---|---|
| Tipo de política | Standard | (sin clasificación) |
| JWT cifrado (`<Algorithms>`, `<PrivateKey>`, `<PasswordKey>`, `<DirectKey>`) | Sí | No |
| `<RequiredClaims>`, `<MaxLifespan>` | Sí | No |
| `uriRef` en `<JWKS>` | Sí | No |
| Caché del JWKS | 300 s | 300 s; en Private Cloud, activar SNI en los MPs si el endpoint lo exige |
| Varios algoritmos en `<Algorithm>` | Sí | Sí |

## Antipatrones

- Verificar sin `<Issuer>` ni `<Audience>`.
- Usar DecodeJWT para autorizar.
- `<Source>request.header.authorization</Source>` (no quita `Bearer`).
- `<TimeAllowance>` de minutos.
- `uriRef` alimentado con datos del propio token sin lista blanca.
- `continueOnError="true"` sin comprobar `valid`.

## Fuentes

- VerifyJWT policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/verify-jwt-policy> (consultada directamente, contenido completo, 2026-10-22).
- Verify JWT policy — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/verify-jwt-policy> (consultada directamente, 2026-10-22).
