---
id: politica-decode-jws
titulo: DecodeJWS — referencia completa
area: politicas
tags: [decodejws, jws, decodificar, kid, extensible]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
elemento_xml: DecodeJWS
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/decode-jws-policy
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/decode-jws-policy
revisado: 2026-10-22
---

# DecodeJWS — referencia completa

> [!NOTE]
> **Tipo:** Extensible (DecodeJWT, en cambio, es Standard). **Elemento raíz:** `<DecodeJWS>`.
> **Aplica a:** Apigee X, hybrid y Edge, con el mismo comportamiento.

DecodeJWS **lee la cabecera** de un JWS, adjunto o separado, y la publica en variables, **sin verificar la firma**. Sirve para conocer el `kid`, el `alg` u otro parámetro antes de llamar a [VerifyJWS](verify-jws.md) con la clave correcta.

> [!CAUTION]
> Nada de lo que publica esta política es fiable hasta que una VerifyJWS confirme la firma.

## Sintaxis completa

```xml
<DecodeJWS name="DJWS-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <Source>variable.con.el.jws</Source>
</DecodeJWS>
```

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno; da nombre a `jws.{name}.*`. |
| `continueOnError` | No | `false` | Con `true`, un JWS mal formado no corta el flujo. |
| `enabled` | No | `true` | Con `false` no se ejecuta. |
| `async` | No | `false` | **Obsoleto.** |

## Elementos hijos

| Elemento | Obligatorio | Default | Resumen |
|---|---|---|---|
| `<DisplayName>` | No | `name` | Etiqueta en la UI. |
| `<Source>` | No | `request.header.authorization` | Variable con el JWS. Sin `<Source>`, debe llegar como `Authorization: Bearer <jws>`. |

## Variables de flujo

Con prefijo `jws.{name}.`: `decoded.header.{param}` (recomendada), `header.algorithm`, `header.kid`, `header.type`, `header.{param}`, `header-json` y `payload` (solo con payload adjunto). **No** publica `valid`.

## Errores

### En runtime

Todos `401`: `steps.jws.FailedToDecode`, `steps.jws.FailedToResolveVariable` (la variable de `<Source>` no existe), `steps.jws.InvalidJsonFormat`, `steps.jws.NoAlgorithmFoundInHeader`, `steps.jws.UnknownException`. La tabla oficial lista además códigos de verificación (`InvalidJws`, `InvalidSignature`, `InvalidClaim`…) que no deberían darse al solo decodificar.

### Al desplegar

`InvalidAlgorithm` y la lista genérica de errores de configuración de las políticas JWS (ver [GenerateJWS](generate-jws.md#al-desplegar)).

### Variables de fallo

`fault.name` y `JWS.failed`.

## Ejemplos

### 1. Leer el `kid` para buscar la clave del firmante

```xml
<DecodeJWS name="DJWS-Kid">
  <Source>request.header.x-jws-signature</Source>
</DecodeJWS>
```

```xml
<KeyValueMapOperations name="KVM-Clave-Firmante" mapIdentifier="claves-firmantes">
  <Scope>environment</Scope>
  <Get assignTo="flujo.clave_firmante">
    <Key>
      <Parameter ref="jws.DJWS-Kid.decoded.header.kid"/>
    </Key>
  </Get>
</KeyValueMapOperations>
```

Después, una [VerifyJWS](verify-jws.md) con `<PublicKey><Value ref="flujo.clave_firmante"/></PublicKey>`, y una RaiseFault si el `kid` no estaba registrado.

## Diferencias en Apigee Edge

Sin diferencias funcionales documentadas.

## Antipatrones

- Tomar decisiones de autorización con la cabecera decodificada.
- Confiar en `jws.{name}.payload` sin verificar.

## Fuentes

- DecodeJWS policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/decode-jws-policy> (consultada directamente, contenido completo, 2026-10-22).
- DecodeJWS policy — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/decode-jws-policy> (consultada directamente, 2026-10-22).
