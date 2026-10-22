---
id: politica-generate-jws
titulo: GenerateJWS — referencia completa
area: politicas
tags: [generatejws, jws, firma, detached, rfc7515, firma-de-mensajes, extensible]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
elemento_xml: GenerateJWS
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/generate-jws-policy
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/generate-jws-policy
revisado: 2026-10-22
---

# GenerateJWS — referencia completa

> [!NOTE]
> **Tipo:** Extensible. **Elemento raíz:** `<GenerateJWS>`.
> **Aplica a:** Apigee X, hybrid y Edge.

GenerateJWS **firma un payload arbitrario** (JSON, texto, binario) y produce un JWS en serialización compacta, con el payload **adjunto** (`cabecera.payload.firma`) o **separado** (`cabecera..firma`). A diferencia de [GenerateJWT](generate-jwt.md), no tiene claims registrados ni payload estructurado: firmas lo que le das.

Caso típico: **firmar el cuerpo de una respuesta o de una petición** para que el receptor compruebe su integridad y origen, enviando la firma en una cabecera (JWS separado). Es el patrón de firma de mensajes de varios estándares de Open Banking.

Algoritmos, claves y el riesgo de inyección de plantillas en [JWT y JWS en Apigee](jwt-jws-conceptos.md).

## Sintaxis completa

```xml
<GenerateJWS name="GJWS-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <Type>Signed</Type>
  <Algorithm>PS256</Algorithm>
  <PrivateKey>
    <Value ref="private.firma.clave_privada"/>
    <Password ref="private.firma.password"/>
    <Id ref="propertyset.firma.kid"/>
  </PrivateKey>
  <Payload ref="response.content"/>
  <DetachContent>true</DetachContent>
  <AdditionalHeaders>
    <Claim name="iat" ref="flujo.iat" type="number"/>
    <Claim name="tan">https://tan.ejemplo.com</Claim>
  </AdditionalHeaders>
  <CriticalHeaders>iat,tan</CriticalHeaders>
  <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>
  <OutputVariable>flujo.firma_jws</OutputVariable>
</GenerateJWS>
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
| `<Type>` | No | `Signed` | Único valor posible: `Signed`. Existe por simetría con las políticas JWT. |
| `<Algorithm>` | **Sí** | — | `HS*`, `RS*`, `PS*`, `ES*` (256/384/512). Otro valor → `InvalidAlgorithm` al desplegar. |
| `<SecretKey encoding="…">` | Uno de los dos | — | HS*: `<Value ref="private.…"/>` y `<Id>` opcional (`kid`). |
| `<PrivateKey>` | Uno de los dos | — | RS*/PS*/ES*: `<Value ref="private.…"/>` (PEM), `<Password ref="private.…"/>`, `<Id>`. |
| `<Payload>` | Sí (en la práctica) | — | Payload sin codificar: `ref` a una variable o literal (admite plantillas). |
| `<DetachContent>` | No | `false` | `true` → JWS con payload separado (`cabecera..firma`). |
| `<AdditionalHeaders>/<Claim>` | No | — | Parámetros propios de la cabecera (`name`, `ref`, `type`, `array`). |
| `<CriticalHeaders>` | No | — | Contenido del parámetro `crit`. |
| `<IgnoreUnresolvedVariables>` | No | `false` | Variables sin resolver = vacío. |
| `<OutputVariable>` | No | `jws.{name}.generated_jws` | Dónde se deja el JWS. |

### `<Payload>`

Contenido **sin codificar** que se firma. Admite plantillas de mensaje: `<Payload>texto-{variable}-texto</Payload>`.

> [!CAUTION]
> Con `ref`, si la variable contiene datos del cliente, un `{private.algo}` inyectado se expandiría dentro del payload firmado. No firmes directamente cabeceras o parámetros de la petición; ver [Inyección de plantillas](jwt-jws-conceptos.md#inyección-de-plantillas).

Para firmar un cuerpo HTTP, la firma se calcula sobre los **bytes exactos** que recibirá el destinatario. Si después de firmar otra política reformatea el JSON (espacios, orden de claves), la verificación fallará.

### `<DetachContent>`

| Valor | Resultado | Cuándo |
|---|---|---|
| `false` (default) | `cabecera.payload.firma` | El JWS viaja solo y lleva su contenido. |
| `true` | `cabecera..firma` | El payload ya viaja aparte (cuerpo HTTP), es grande o binario (imágenes, PDF), o lo exige el estándar. |

Con payload separado, el receptor necesita **el JWS y el payload original**; con [VerifyJWS](verify-jws.md) se pasa en `<DetachedContent>`.

### Firmar como JWT

Si el payload es un JSON válido como conjunto de claims y añades `<Claim name="typ">JWT</Claim>` en `<AdditionalHeaders>`, el resultado es también un JWT firmado. Los claims deben respetar RFC 7519 (por ejemplo, `exp` numérico, `aud` string o array).

### `<CriticalHeaders>`

Define el array `crit`: parámetros que el receptor debe entender o rechazar el JWS (RFC 7515). **No los añade**: decláralos además en `<AdditionalHeaders>`. VerifyJWS los contrasta con su `<KnownHeaders>`.

## Variables de flujo

No publica variables, aparte del JWS en `<OutputVariable>` (por defecto `jws.{name}.generated_jws`).

## Errores

### En runtime

Todos `401`. Relevantes al generar: `steps.jws.GenerationFailed`, `steps.jws.SigningFailed` (clave corta para HS384/HS512), `steps.jws.InsufficientKeyLength`, `steps.jws.WrongKeyType`, `steps.jws.InvalidCurve`, `steps.jws.KeyParsingFailed`, `steps.jws.InvalidJsonFormat` (cabecera), `steps.jws.InvalidPayload`, `steps.jws.MissingPayload`, `steps.jws.UnknownException`. La tabla oficial incluye también códigos que solo aplican al verificar.

### Al desplegar

`InvalidAlgorithm` y una lista de errores de configuración que la página enumera sin describir: `EmptyElementForKeyConfiguration`, `FailedToResolveVariable`, `InvalidConfigurationForActionAndAlgorithmFamily`, `InvalidConfigurationForVerify`, `InvalidEmptyElement`, `InvalidFamiliesForAlgorithm`, `InvalidKeyConfiguration`, `InvalidNameForAdditionalClaim`, `InvalidNameForAdditionalHeader`, `InvalidPublicKeyId`, `InvalidPublicKeyValue`, `InvalidSecretInConfig`, `InvalidTypeForAdditionalClaim`, `InvalidTypeForAdditionalHeader`, `InvalidValueForElement`, `InvalidValueOfArrayAttribute`, `InvalidVariableNameForSecret`, `MissingConfigurationElement`, `MissingElementForKeyConfiguration`, `MissingNameForAdditionalClaim`, `MissingNameForAdditionalHeader`.

### Variables de fallo

`fault.name` y `JWS.failed` (la página usa como ejemplo `jws.{name}.failed`, con otra forma; comprueba en Debug cuál se puebla en tu versión).

## Ejemplos

### 1. Firma separada del cuerpo de la respuesta

El backend responde; el gateway firma el cuerpo y añade la firma en la cabecera `x-jws-signature`.

```xml
<GenerateJWS name="GJWS-Firma-Respuesta">
  <Algorithm>PS256</Algorithm>
  <PrivateKey>
    <Value ref="private.firma.clave_privada"/>
    <Id>firma-banco-2026</Id>
  </PrivateKey>
  <Payload ref="response.content"/>
  <DetachContent>true</DetachContent>
  <OutputVariable>flujo.firma_respuesta</OutputVariable>
</GenerateJWS>
```

```xml
<AssignMessage name="AM-Cabecera-Firma">
  <Set>
    <Headers>
      <Header name="x-jws-signature">{flujo.firma_respuesta}</Header>
    </Headers>
  </Set>
  <AssignTo createNew="false" transport="http" type="response"/>
</AssignMessage>
```

Debe ser lo **último** que toque el cuerpo en el flujo de respuesta.

### 2. JWS adjunto con HMAC

```xml
<GenerateJWS name="GJWS-HS256">
  <Algorithm>HS256</Algorithm>
  <SecretKey encoding="base64">
    <Value ref="private.firma.secreto"/>
  </SecretKey>
  <Payload ref="flujo.mensaje"/>
  <OutputVariable>flujo.jws</OutputVariable>
</GenerateJWS>
```

## Diferencias en Apigee Edge

| Aspecto | Apigee X / hybrid | Apigee Edge |
|---|---|---|
| Elementos, algoritmos y errores | Iguales | Iguales |
| Atributo `encoding` en `<SecretKey>` | Documentado | No documentado en la página de Edge |

## Antipatrones

- Firmar el cuerpo y luego modificarlo en el mismo flujo.
- Payload construido con plantillas a partir de datos del cliente.
- Firmar con HMAC hacia terceros: ambos tienen el mismo secreto, así que no hay no repudio. Con terceros usa PS256 o ES256.

## Fuentes

- GenerateJWS policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/generate-jws-policy> (consultada directamente, contenido completo, 2026-10-22).
- Generate JWS policy — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/generate-jws-policy> (consultada directamente, 2026-10-22).
