---
id: politica-hmac
titulo: HMAC — referencia completa
area: politicas
tags: [hmac, firma, sha256, webhook, integridad, rfc2104, standard]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
elemento_xml: HMAC
tipo_politica: standard
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/hmac-policy
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/hmac-policy
revisado: 2026-10-22
---

# HMAC — referencia completa

> [!NOTE]
> **Tipo:** Standard. **Elemento raíz:** `<HMAC>`.
> **Aplica a:** Apigee X, hybrid y Edge, con el mismo comportamiento.

La política HMAC **calcula** un código de autenticación de mensaje (HMAC, RFC 2104) sobre un mensaje y una clave secreta y, opcionalmente, lo **verifica** contra un valor esperado. El mismo cálculo sirve para firmar y para verificar: verificar es calcular y comparar.

Usos típicos:

- verificar **webhooks** entrantes firmados por un tercero (cabecera tipo `X-Signature: sha256=…`);
- firmar peticiones hacia un backend o socio que exige HMAC;
- esquemas de autenticación propios (firma sobre método, ruta, fecha y nonce).

## Sintaxis completa

```xml
<HMAC name="HMAC-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <Algorithm>SHA-256</Algorithm>
  <SecretKey encoding="utf8" ref="private.hmac.secreto"/>
  <Message>{request.verb}
{request.uri}
{request.header.x-fecha}
{request.content}</Message>
  <VerificationValue encoding="base64" ref="request.header.x-firma"/>
  <Output encoding="base64">flujo.hmac_calculado</Output>
  <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>
</HMAC>
```

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno; da nombre a `hmac.{name}.*`. |
| `continueOnError` | No | `false` | Con `true`, una firma inválida no corta el flujo. |
| `enabled` | No | `true` | Con `false` no se ejecuta. |
| `async` | No | `false` | **Obsoleto.** |

## Elementos hijos

| Elemento | Obligatorio | Default | Resumen |
|---|---|---|---|
| `<Algorithm>` | **Sí** | — | `SHA-1`, `SHA-224`, `SHA-256`, `SHA-384`, `SHA-512`, `MD-5`. Sin distinguir mayúsculas ni guion (`sha256` = `SHA-256`). |
| `<SecretKey encoding ref>` | **Sí** | `encoding` = UTF-8 | Variable con la clave (debe empezar por `private.`). |
| `<Message>` | **Sí** | — | Mensaje a firmar: plantilla de mensaje o `ref`. |
| `<VerificationValue encoding>` | No | — | Valor esperado; si está, la política **verifica**. |
| `<Output encoding>` | No | `hmac.{name}.output`, `base64` | Dónde y cómo se escribe el HMAC calculado. |
| `<IgnoreUnresolvedVariables>` | No | — | Afecta solo a las variables de la plantilla de `<Message>`. |

> [!WARNING]
> No uses `SHA-1` ni `MD-5` salvo que el otro extremo no admita nada mejor: Google los incluye por completitud y desaconseja usarlos. Usa `SHA-256` o superior.

> [!NOTE]
> **Discrepancia.** El texto de la página de X lista `SHA-384` entre los algoritmos, pero el error de despliegue `InvalidValueForElement` enumera solo `SHA-1`, `SHA-224`, `SHA-256`, `SHA-512` y `MD-5`. La página de Edge sí incluye `SHA-384` en los valores válidos. Prueba el despliegue si lo necesitas.

### `<SecretKey>`

`ref` es obligatorio y la variable debe empezar por `private.`; poner la clave como texto en la política hace fallar el despliegue (`InvalidSecretInConfig`), igual que una variable sin el prefijo (`InvalidVariableName`). Codificaciones: `utf8` (default), `hex`/`base16`, `base64` (sin distinguir mayúsculas; guiones indiferentes). Para `<SecretKey>` la página no lista `base64url`, a diferencia de `<Output>` y `<VerificationValue>`.

La misma clave puede representarse de tres formas: `Secret123` en UTF-8, `536563726574313233` en hex o `U2VjcmV0MTIz` en base64. Si cada extremo decodifica distinto, obtendrá claves distintas y HMAC distintos.

### `<Message>`

Plantilla de mensaje: texto fijo, variables `{…}` y funciones estáticas (p. ej. `{timeFormatUTCMs(formato,system.timestamp)}`). **Los espacios y saltos de línea cuentan.**

> [!IMPORTANT]
> Esto produce un HMAC **distinto** del que esperas, porque incluye los saltos de línea y la sangría alrededor del contenido:
>
> ```xml-sintaxis
> <Message>
>     {request.content}
> </Message>
> ```
>
> Escríbelo pegado: `<Message>{request.content}</Message>`. Y verifica **antes** de cualquier política que modifique el cuerpo.

### `<VerificationValue>` y `<Output>`

| Elemento | Codificaciones | Notas |
|---|---|---|
| `<VerificationValue>` | `hex`/`base16`, `base64`, `base64url` | Literal o `ref`. No tiene por qué usar la misma codificación que `<Output>`. |
| `<Output>` | `hex`/`base16`, `base64` (default), `base64url` | Un mismo HMAC en hex (`27f17e…`) y en base64 (`J/F+Ec…`) representa el mismo valor. |

Si `<VerificationValue>` está y no coincide, la política falla con `HmacVerificationFailed`. Si la variable de verificación está vacía, `EmptyVerificationValue`. `<IgnoreUnresolvedVariables>` **no** aplica a `<SecretKey>` ni a `<VerificationValue>`: deben resolver siempre.

## Variables de flujo

| Variable | Contenido |
|---|---|
| `hmac.{name}.message` | El mensaje efectivo, tras evaluar la plantilla. **Imprescindible para depurar** diferencias de espacios. |
| `hmac.{name}.output` | El HMAC calculado, si `<Output>` no indica otra variable. |
| `hmac.{name}.outputencoding` | Codificación de la salida. |

## Errores

### En runtime

Todos `401`:

| Código | Causa |
|---|---|
| `steps.hmac.HmacVerificationFailed` | El HMAC calculado no coincide con `<VerificationValue>`. |
| `steps.hmac.HmacCalculationFailed` | No se pudo calcular. |
| `steps.hmac.UnresolvedVariable` | Una variable no existe o está fuera de alcance. |
| `steps.hmac.EmptySecretKey` | La variable de la clave está vacía. |
| `steps.hmac.EmptyVerificationValue` | La variable del valor esperado está vacía. |

### Al desplegar

`steps.hmac.MissingConfigurationElement`, `steps.hmac.InvalidValueForElement` (algoritmo), `steps.hmac.InvalidSecretInConfig` (clave en texto), `steps.hmac.InvalidVariableName` (sin `private.`).

### Variables de fallo

| Variable | Ejemplo |
|---|---|
| `fault.name` | `fault.name = "HmacVerificationFailed"` |
| `hmac.{name}.failed` | `hmac.HMAC-Webhook.failed = true` |

## Ejemplos

### 1. Verificar un webhook `sha256=<hex>`

El emisor firma el cuerpo con HMAC-SHA256 y manda `X-Firma: sha256=<hex>`. Primero se quita el prefijo con ExtractVariables o JavaScript y se deja el hex en `flujo.firma_recibida`.

```xml
<HMAC name="HMAC-Webhook">
  <Algorithm>SHA-256</Algorithm>
  <SecretKey ref="private.webhook.secreto"/>
  <Message>{request.content}</Message>
  <VerificationValue encoding="hex" ref="flujo.firma_recibida"/>
</HMAC>
```

> [!TIP]
> Para evitar repeticiones (*replay*), incluye una marca de tiempo en el mensaje firmado y rechaza las peticiones antiguas; la política no lo hace por ti.

### 2. Firmar peticiones hacia un socio

```xml
<HMAC name="HMAC-Firmar-Socio">
  <Algorithm>SHA-256</Algorithm>
  <SecretKey encoding="base64" ref="private.socio.secreto"/>
  <Message>{request.verb}
{proxy.pathsuffix}
{flujo.fecha_iso}</Message>
  <Output encoding="base64">flujo.firma_socio</Output>
</HMAC>
```

Después, una AssignMessage añade `X-Fecha: {flujo.fecha_iso}` y `X-Firma: {flujo.firma_socio}` a la petición al target.

## Diferencias en Apigee Edge

Sin diferencias funcionales documentadas. La página de Edge no incluye la sección de problemas comunes (espacios y codificaciones), pero el comportamiento es el mismo.

## Antipatrones

- SHA-1 o MD-5.
- Sangría o saltos de línea accidentales en `<Message>`.
- Verificar el cuerpo después de transformarlo.
- Claves en texto o en variables sin `private.`.
- No proteger contra *replay*.

## Fuentes

- HMAC policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/hmac-policy> (consultada directamente, contenido completo, 2026-10-22).
- HMAC policy — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/hmac-policy> (consultada directamente, 2026-10-22).
- RFC 2104 (HMAC): <https://www.rfc-editor.org/rfc/rfc2104>
