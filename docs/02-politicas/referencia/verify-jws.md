---
id: politica-verify-jws
titulo: VerifyJWS — referencia completa
area: politicas
tags: [verifyjws, jws, firma, detached, detachedcontent, rfc7515, firma-de-mensajes, extensible]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
elemento_xml: VerifyJWS
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/verify-jws-policy
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/verify-jws-policy
revisado: 2026-10-22
---

# VerifyJWS — referencia completa

> [!NOTE]
> **Tipo:** Extensible (a diferencia de VerifyJWT, que es Standard). **Elemento raíz:** `<VerifyJWS>`.
> **Aplica a:** Apigee X, hybrid y Edge, con el mismo comportamiento.

VerifyJWS **verifica la firma** de un JWS, con payload adjunto o separado, y publica su cabecera (y el payload, si va adjunto) en variables. Si la firma no es válida, corta el flujo.

Caso típico: el cliente firma el cuerpo de su petición y envía la firma separada en una cabecera; el proxy comprueba que el cuerpo recibido es exactamente el firmado y que lo firmó quien dice. Claves y algoritmos en [JWT y JWS en Apigee](jwt-jws-conceptos.md).

## Sintaxis completa

```xml
<VerifyJWS name="VJWS-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <Type>Signed</Type>
  <Algorithm>PS256, RS256</Algorithm>
  <Source>request.header.x-jws-signature</Source>
  <PublicKey>
    <JWKS uri="https://directorio.ejemplo.com/participantes/123/jwks.json"/>
  </PublicKey>
  <DetachedContent>request.content</DetachedContent>
  <AdditionalHeaders>
    <Claim name="tan">https://tan.ejemplo.com</Claim>
  </AdditionalHeaders>
  <KnownHeaders>iat,tan</KnownHeaders>
  <IgnoreCriticalHeaders>false</IgnoreCriticalHeaders>
  <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>
</VerifyJWS>
```

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno; da nombre a `jws.{name}.*`. |
| `continueOnError` | No | `false` | Con `true`, una firma inválida no corta el flujo; comprueba `jws.{name}.valid`. |
| `enabled` | No | `true` | Con `false` no se ejecuta. |
| `async` | No | `false` | **Obsoleto.** |

## Elementos hijos

| Elemento | Obligatorio | Default | Resumen |
|---|---|---|---|
| `<Type>` | No | `Signed` | Único valor: `Signed`. |
| `<Algorithm>` | **Sí** | — | Lista blanca de algoritmos; admite varios separados por comas (RS* con PS*; HS* y ES* no se mezclan con otras familias). |
| `<Source>` | No | `request.header.authorization` | Variable con el JWS. Sin `<Source>`, debe llegar como `Authorization: Bearer <jws>`. |
| `<SecretKey encoding="…">` | Uno de los dos | — | HS*: `<Value ref="private.…"/>`. |
| `<PublicKey>` | Uno de los dos | — | RS*/PS*/ES*: `<Value>` (PEM) o `<JWKS>` (literal, `ref` o `uri`). |
| `<DetachedContent>` | Solo con JWS separado | — | Variable con el payload original, sin codificar. |
| `<AdditionalHeaders>/<Claim>` | No | — | Valores esperados de parámetros de cabecera. |
| `<KnownHeaders>` | No | — | Parámetros `crit` que tu proxy entiende. |
| `<IgnoreCriticalHeaders>` | No | `false` | Ignorar `crit` (solo para pruebas). |
| `<IgnoreUnresolvedVariables>` | No | `false` | Variables sin resolver = vacío. |

### `<PublicKey>`

| Hijo | Forma |
|---|---|
| `<Value>` | PEM literal (alineado a la izquierda) o `ref` a una variable. |
| `<JWKS>` | Literal, `ref` a una variable con el JWKS, o `uri` **fija**. |

> [!NOTE]
> **Diferencias con VerifyJWT y discrepancia.** VerifyJWS **no** documenta `<Certificate>` ni `uriRef`; su página dice expresamente que la URL del JWKS es estática y no se puede tomar de una variable. Sin embargo, la página general de JWS/JWT presenta `uriRef` como opción para las dos familias. Si necesitas JWKS dinámico con JWS, carga el JWKS en una variable (ServiceCallout + caché) y usa `<JWKS ref>`. El JWKS obtenido por URL se cachea **300 s**.

### `<DetachedContent>`

Variable con el payload **exactamente como se firmó**, sin codificar. Reglas:

| Situación | Resultado |
|---|---|
| JWS separado y `<DetachedContent>` presente | Se verifica la firma contra ese contenido. |
| JWS separado y **sin** `<DetachedContent>` | Falla: `InvalidSignature`. |
| JWS adjunto y `<DetachedContent>` presente | Falla: `ContentIsNotDetached`. |

> [!IMPORTANT]
> Verifica el cuerpo **antes** de que cualquier otra política lo transforme (JSONToXML, AssignMessage, eliminación de espacios…). Si el cuerpo llega comprimido o con otra codificación, la firma se calculó sobre los bytes del emisor: acuerda con él exactamente qué se firma.

### `<AdditionalHeaders>`

Cada `<Claim name ref type array>` exige que el parámetro exista en la cabecera con ese valor; si no, `InvalidClaim`. La página advierte que no se usen nombres de claims registrados de JWT.

### `crit`

Cada nombre del array `crit` del JWS debe estar en `<KnownHeaders>`, o la verificación falla (`UnhandledCriticalHeader`). La política no procesa esos parámetros: valídalos tú después (por ejemplo, que un `iat` de la cabecera sea reciente).

## Variables de flujo

Con prefijo `jws.{name}.`:

| Variable | Contenido |
|---|---|
| `valid` | `true` si la firma es válida (solo en VerifyJWS). |
| `decoded.header.{param}` | Valor JSON del parámetro (recomendada). |
| `header.algorithm`, `header.kid`, `header.type`, `header.{param}` | Cabecera. |
| `header-json` | Cabecera completa en JSON. |
| `payload` | Payload, **solo si va adjunto**; vacío con JWS separado. |

> [!NOTE]
> La descripción de `valid` habla de comprobar `exp` y `nbf`, pero un JWS no tiene claims registrados: en la práctica `valid` refleja la firma. Si la cabecera trae marcas de tiempo propias, compruébalas tú.

## Errores

### En runtime

Todos `401`:

| Código | Causa |
|---|---|
| `steps.jws.InvalidJws` | La firma no verifica. |
| `steps.jws.InvalidSignature` | Falta `<DetachedContent>` con un JWS separado. |
| `steps.jws.ContentIsNotDetached` | `<DetachedContent>` con un JWS adjunto. |
| `steps.jws.AlgorithmMismatch`, `AlgorithmInTokenNotPresentInConfiguration`, `NoAlgorithmFoundInHeader` | Algoritmo no permitido o ausente. |
| `steps.jws.KeyIdMissing`, `NoMatchingPublicKey` | Con JWKS: sin `kid`, o `kid` desconocido. |
| `steps.jws.InvalidClaim` | Parámetro de cabecera ausente o distinto. |
| `steps.jws.UnhandledCriticalHeader` | Parámetro `crit` no listado. |
| `steps.jws.FailedToDecode`, `InvalidJsonFormat`, `InvalidPayload`, `MissingPayload` | JWS corrupto o sin payload. |
| `steps.jws.InsufficientKeyLength`, `WrongKeyType`, `InvalidCurve`, `KeyParsingFailed` | Problema con la clave configurada. |
| `steps.jws.UnknownException` | Error desconocido. |

### Al desplegar

`InvalidAlgorithm` y la misma lista de errores de configuración que [GenerateJWS](generate-jws.md#al-desplegar).

### Variables de fallo

`fault.name` (p. ej. `InvalidJws`) y `JWS.failed`.

## Ejemplos

### 1. Firma separada del cuerpo de la petición, clave del participante por JWKS

```xml
<VerifyJWS name="VJWS-Firma-Peticion">
  <Algorithm>PS256</Algorithm>
  <Source>request.header.x-jws-signature</Source>
  <PublicKey>
    <JWKS ref="flujo.jwks_participante"/>
  </PublicKey>
  <DetachedContent>request.content</DetachedContent>
  <KnownHeaders>iat</KnownHeaders>
</VerifyJWS>
```

`flujo.jwks_participante` se cargó antes con una [LookupCache](lookup-cache.md) y, si no estaba, con un ServiceCallout al directorio de participantes, según el `client_id` ya autenticado. Luego conviene comprobar que `jws.VJWS-Firma-Peticion.decoded.header.iat` sea reciente para evitar repeticiones (*replay*).

### 2. JWS adjunto con HMAC

```xml
<VerifyJWS name="VJWS-HS256">
  <Algorithm>HS256</Algorithm>
  <Source>request.formparam.jws</Source>
  <SecretKey encoding="base64">
    <Value ref="private.firma.secreto"/>
  </SecretKey>
</VerifyJWS>
```

El contenido verificado queda en `jws.VJWS-HS256.payload`.

## Diferencias en Apigee Edge

Sin diferencias funcionales documentadas: mismos elementos, variables y errores.

## Antipatrones

- Verificar después de transformar el cuerpo.
- Tomar la URL del JWKS de la cabecera del propio JWS.
- `<IgnoreCriticalHeaders>true</IgnoreCriticalHeaders>` en producción.
- Confiar en `jws.{name}.payload` tras una DecodeJWS (no verifica nada).

## Fuentes

- VerifyJWS policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/verify-jws-policy> (consultada directamente, contenido completo, 2026-10-22).
- Verify JWS policy — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/verify-jws-policy> (consultada directamente, 2026-10-22).
