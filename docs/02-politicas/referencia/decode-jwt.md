---
id: politica-decode-jwt
titulo: DecodeJWT — referencia completa
area: politicas
tags: [decodejwt, jwt, decodificar, kid, iss, standard]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
elemento_xml: DecodeJWT
tipo_politica: standard
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/decode-jwt-policy
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/decode-jwt-policy
revisado: 2026-10-22
---

# DecodeJWT — referencia completa

> [!NOTE]
> **Tipo:** Standard. **Elemento raíz:** `<DecodeJWT>`.
> **Aplica a:** Apigee X, hybrid y Edge, con el mismo comportamiento.

DecodeJWT **lee** la cabecera y el payload de un JWT y los publica en variables, **sin verificar la firma** ni las fechas. Funciona con cualquier algoritmo. Con un JWT cifrado solo puede leer la **cabecera sin cifrar**.

Para qué sirve: conocer un dato del token **antes** de verificarlo, por ejemplo el `iss` para elegir qué JWKS usar, o el `kid` para cargar la clave correcta. Después siempre debe venir una [VerifyJWT](verify-jwt.md).

> [!CAUTION]
> **Nunca** autorices con datos de una DecodeJWT: cualquiera puede fabricar un JWT con los claims que quiera. La variable `valid` no se publica en esta política precisamente por eso.

## Sintaxis completa

```xml
<DecodeJWT name="DJWT-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <Source>variable.con.el.jwt</Source>
</DecodeJWT>
```

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno; da nombre a `jwt.{name}.*`. |
| `continueOnError` | No | `false` | Con `true`, un token mal formado no corta el flujo. |
| `enabled` | No | `true` | Con `false` no se ejecuta. |
| `async` | No | `false` | **Obsoleto.** |

## Elementos hijos

| Elemento | Obligatorio | Default | Resumen |
|---|---|---|---|
| `<DisplayName>` | No | `name` | Etiqueta en la UI. |
| `<Source>` | No | `request.header.authorization` | Variable con el JWT. Sin `<Source>`, el token debe llegar como `Authorization: Bearer <jwt>`. Vacío → despliegue fallido (`InvalidEmptyElement`). |

## Variables de flujo

Las mismas que [VerifyJWT](verify-jwt.md#variables-de-flujo), con prefijo `jwt.{name}.`, **excepto `valid`**: `decoded.claim.*`, `decoded.header.*`, `claim.*`, `header.*`, `header-json`, `payload-json`, `payload-claim-names`, `is_expired`, `seconds_remaining`, `time_remaining_formatted`, `expiry_formatted`.

## Errores

### En runtime

| Código | HTTP | Causa |
|---|---|---|
| `steps.jwt.FailedToDecode` | 401 | El token está mal formado o no se puede decodificar. |
| `steps.jwt.FailedToResolveVariable` | 401 | La variable de `<Source>` no existe. |
| `steps.jwt.InvalidToken` | 401 | La variable de `<Source>` está fuera de alcance o no resuelve. |

### Al desplegar

| Error | Causa |
|---|---|
| `InvalidEmptyElement` | `<Source>` vacío. |

### Variables de fallo

`fault.name` y `JWT.failed`.

## Ejemplos

### 1. Elegir la clave por `kid` antes de verificar

```xml
<DecodeJWT name="DJWT-Kid"/>
```

```xml
<KeyValueMapOperations name="KVM-Clave-Por-Kid" mapIdentifier="claves-publicas">
  <Scope>environment</Scope>
  <Get assignTo="flujo.clave_publica">
    <Key>
      <Parameter ref="jwt.DJWT-Kid.decoded.header.kid"/>
    </Key>
  </Get>
</KeyValueMapOperations>
```

```xml
<VerifyJWT name="VJWT-Por-Kid">
  <Algorithm>RS256</Algorithm>
  <PublicKey>
    <Value ref="flujo.clave_publica"/>
  </PublicKey>
  <Issuer>urn://emisor</Issuer>
  <Audience>urn://api</Audience>
</VerifyJWT>
```

### 2. Enrutar a la VerifyJWT de cada emisor

```xml
<Step><Name>DJWT-Emisor</Name></Step>
<Step>
  <Name>VJWT-IdP-Corporativo</Name>
  <Condition>jwt.DJWT-Emisor.decoded.claim.iss = "https://login.corp.ejemplo.com"</Condition>
</Step>
<Step>
  <Name>VJWT-IdP-Clientes</Name>
  <Condition>jwt.DJWT-Emisor.decoded.claim.iss = "https://cuenta.ejemplo.com"</Condition>
</Step>
<Step>
  <Name>RF-Emisor-Desconocido</Name>
  <Condition>jwt.DJWT-Emisor.decoded.claim.iss != "https://login.corp.ejemplo.com" and jwt.DJWT-Emisor.decoded.claim.iss != "https://cuenta.ejemplo.com"</Condition>
</Step>
```

## Diferencias en Apigee Edge

Sin diferencias funcionales documentadas.

## Antipatrones

- Autorizar con los claims decodificados sin VerifyJWT posterior.
- Usar el `jku` o `x5u` decodificado para buscar la clave sin lista blanca.

## Fuentes

- DecodeJWT policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/decode-jwt-policy> (consultada directamente, contenido completo, 2026-10-22).
- DecodeJWT policy — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/decode-jwt-policy> (consultada directamente, 2026-10-22).
