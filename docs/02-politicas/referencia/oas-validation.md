---
id: politica-oas-validation
titulo: OASValidation — referencia completa
area: politicas
tags: [oasvalidation, openapi, oas3, contrato, validacion, esquema, seguridad, standard]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
elemento_xml: OASValidation
tipo_politica: standard
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/oas-validation-policy
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/oas-validation-policy
revisado: 2026-10-22
---

# OASValidation — referencia completa

> [!NOTE]
> **Tipo:** Standard. **Elemento raíz:** `<OASValidation>`.
> **Aplica a:** Apigee X, hybrid y Edge, con el mismo comportamiento.

OASValidation valida peticiones o respuestas contra una especificación **OpenAPI 3.0** (JSON o YAML) guardada en el proxy: ruta, verbo, parámetros y, opcionalmente, el cuerpo. Usada en la petición, convierte el contrato en una **lista de permitidos**: lo que no está en la especificación se rechaza. Ver [Threat protection](../../03-seguridad/05-threat-protection.md#oasvalidation-como-control-de-seguridad).

La página no menciona OpenAPI 3.1 ni Swagger 2.0: asume 3.0.

> [!CAUTION]
> **Dos defaults que dejan pasar casi todo:**
>
> 1. `<ValidateMessageBody>` vale **`false`**: por defecto solo se comprueba que el cuerpo **exista** si es obligatorio, **no** su contenido.
> 2. El cuerpo solo se valida si el `Content-Type` es **`application/json`**; con cualquier otro, la validación del cuerpo **pasa automáticamente** sin mirar el contenido.
>
> Y los parámetros no declarados (`<AllowUnspecifiedParameters>`) se **permiten** por defecto. Para usarla como control de seguridad, activa `<ValidateMessageBody>`, pon los `<AllowUnspecifiedParameters>` en `false` y rechaza antes los `Content-Type` que tu API no acepta.

## Qué se valida

| Componente | Petición | Respuesta |
|---|---|---|
| Basepath | Usa el del proxy; **ignora** el de la especificación | — |
| Ruta | La ruta sin basepath coincide con algún `path` | La ruta **del target** (ojo si difiere de la del proxy) |
| Verbo | Definido para esa ruta | Definido para esa ruta |
| Parámetros | Obligatorios presentes (path, header, query, cookie); valores conforme al esquema; opcionalmente, ningún parámetro no declarado | — |
| Cuerpo | Presencia si es obligatorio; contenido con `<ValidateMessageBody>` | Presencia; cabeceras de respuesta declaradas y su esquema; contenido con `<ValidateMessageBody>` |

> [!IMPORTANT]
> En la **respuesta**, la ruta que se compara es la que Apigee llama en el **target**, no la del proxy. Si reescribes rutas, la especificación usada para validar respuestas tiene que reflejar las rutas del backend.

## Sintaxis completa

```xml
<OASValidation name="OAS-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <Source>request</Source>
  <OASResource>oas://pagos-v1.yaml</OASResource>
  <Options>
    <ValidateMessageBody>true</ValidateMessageBody>
    <AllowUnspecifiedParameters>
      <Header>true</Header>
      <Query>false</Query>
      <Cookie>false</Cookie>
    </AllowUnspecifiedParameters>
  </Options>
</OASValidation>
```

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno; da nombre a `OASValidation.{name}.failed`. |
| `continueOnError` | No | `false` | Con `true`, una violación del contrato no corta el flujo. |
| `enabled` | No | `true` | Con `false` no se ejecuta. |

## Elementos hijos

| Elemento | Obligatorio | Default | Resumen |
|---|---|---|---|
| `<OASResource>` | **Sí** | — | `oas://archivo.yaml` (o `.json`, `.yml`), en `apiproxy/resources/oas`. Admite plantilla de mensaje (`{variable}`). Solo se guarda **con la revisión del proxy**. |
| `<Source>` | No | `request` | `request`, `response` o `message`. |
| `<Options>/<ValidateMessageBody>` | No | `false` | Validar el contenido del cuerpo contra el esquema. |
| `<Options>/<AllowUnspecifiedParameters>/<Header>` | No | `true` | Permitir cabeceras no declaradas. |
| `.../<Query>` | No | `true` | Permitir query params no declarados. |
| `.../<Cookie>` | No | `true` | Permitir cookies no declaradas. |

> [!TIP]
> Con `<Header>false</Header>` hay que declarar en la especificación **todas** las cabeceras que llegan, incluidas las que añaden navegadores, balanceadores y SDK (`User-Agent`, `Accept-Encoding`, `X-Forwarded-For`, trazas…). Normalmente se deja `Header` en `true` y se cierran `Query` y `Cookie`.

## Funcionalidades OpenAPI soportadas

Si la especificación usa algo no soportado, **el despliegue falla**.

| Categoría | Soportado | No soportado |
|---|---|---|
| Formatos | `boolean`, `date`, `date-time`, `double`, `email`, `float`, `int32`/`int64`, `ipv4`/`ipv6`, `md5`, `sha1`/`sha256`/`sha512`, `string`, `uri`, `uri-template`, `uuid` | `binary`, `byte`, `password` |
| Cuerpo de petición y respuesta | `application/json`, `application/hal+json`, `application/x-www-form-urlencoded` (sin objeto `encoding`) | `application/xml`, `text/xml`, `text/plain`, `multipart/form-data` |
| Parámetros | `in` (`query`, `header`, `path`), `required`, `schema`, `allowEmptyValue`, `style` (`deepObject` solo con strings, `form`, `matrix`, `label`, `pipeDelimited`, `simple`, `spaceDelimited`) | `allowReserved`, `deprecated`, `example(s)`, `content` |
| Operaciones | `parameters`, `requestBody`, `responses`, `security` (parcial) | `callbacks`, `deprecated`, `servers` |
| Esquemas | `$ref`, `allOf`, `anyOf`, `oneOf`, `not`, `enum`, `format`, `pattern`, `required`, `nullable`, `items`, límites (`maximum`, `maxLength`, `maxItems`, `maxProperties`… y sus mínimos, `exclusive*`, `multipleOf`, `uniqueItems`), `properties`, `additionalProperties` (solo la variante booleana), `title`, `type` | `deprecated`, `example`, `readOnly`, `writeOnly`, `xml` |
| Esquemas de seguridad | `type` (`apiKey`, `http`), `name`, `in` (`header`, `query`) | `bearerFormat`, `flows`, `openIdConnectUrl`, `scheme` |
| Servidores | `url`, `variables` | Varios servidores |

> [!NOTE]
> `allOf` se **ignora** si `additionalProperties` es `false`. Y `security` con soporte parcial **no sustituye** a la autenticación: valida la presencia de la credencial donde la especificación dice, no su validez. Autentica siempre con VerifyAPIKey, OAuthV2 o VerifyJWT.

### Expresiones regulares en `pattern`

Apigee valida los `pattern` de la especificación al guardar o importar el proxy, pero **solo** si usan el subconjunto recomendado por JSON Schema (sin *lookarounds*, retrorreferencias ni escapes octales). Si un patrón usa algo fuera de ese subconjunto:

- Apigee **suspende** la validación del resto del documento al guardar.
- Los errores (del patrón o del documento) aparecen **en runtime**.
- Si el runtime no soporta la característica (p. ej. condicionales de grupo `(?(1)…)`), la política falla al ejecutarse.

Quédate en el subconjunto recomendado: `^\w{3}-\d{4}$` sí; `^(?![a-z])…` funciona pero suspende la validación al guardar.

## Variables de flujo

No publica variables de éxito.

## Errores

### En runtime

| Código | HTTP | Causa |
|---|---|---|
| `steps.oasvalidation.Failed` | **400** | La **petición** no cumple la especificación. |
| `steps.oasvalidation.Failed` | 500 | La **respuesta** no cumple la especificación. |
| `steps.oasvalidation.SourceMessageNotAvailable` | 500 | `<Source>` fuera de alcance o inexistente. |
| `steps.oasvalidation.NonMessageVariable` | 500 | `<Source>` no es de tipo mensaje. |

La página también menciona `policies.oasvalidation.Failed` en un ejemplo; captura por `fault.name`.

### Al desplegar

| Error | Causa |
|---|---|
| `ResourceDoesNotExist` | La especificación de `<OASResource>` no existe. |
| `ResourceCompileFailed` | La especificación no es un OpenAPI 3.0 bien formado o usa funcionalidades no soportadas. |
| `BadResourceURL` | El archivo no es JSON/YAML o la URL está mal escrita. |

### Variables de fallo

| Variable | Contenido |
|---|---|
| `fault.name` | `Failed`, etc. |
| `fault.reason` | Motivo legible, p. ej. `POST operation not allowed on path '/persons/13'`. |
| `fault.category` | `Step` |
| `fault.subcategory` | `OASValidationFailure` |
| `OASValidation.{name}.failed` | `true` |

> [!TIP]
> `fault.reason` es útil para devolver al desarrollador un error **400** explicativo (qué campo falla), algo que sí conviene en errores de contrato, a diferencia de los de seguridad.

## Ejemplos

### 1. Contrato estricto para un API de pagos

```xml
<OASValidation name="OAS-Pagos">
  <Source>request</Source>
  <OASResource>oas://pagos-v1.yaml</OASResource>
  <Options>
    <ValidateMessageBody>true</ValidateMessageBody>
    <AllowUnspecifiedParameters>
      <Header>true</Header>
      <Query>false</Query>
      <Cookie>false</Cookie>
    </AllowUnspecifiedParameters>
  </Options>
</OASValidation>
```

Precedida por una comprobación de `Content-Type` (`415` si no es `application/json` en operaciones con cuerpo) y por [JSONThreatProtection](json-threat-protection.md).

### 2. Respuesta 400 con el motivo

```xml
<AssignMessage name="AM-Error-400-Contrato">
  <Set>
    <StatusCode>400</StatusCode>
    <Payload contentType="application/json">{"codigo":"CONTRATO_INVALIDO","detalle":"{escapeJSON(fault.reason)}"}</Payload>
  </Set>
  <AssignTo createNew="false" transport="http" type="response"/>
</AssignMessage>
```

### 3. Especificación elegida en runtime

```xml
<OASValidation name="OAS-Por-Version">
  <OASResource>oas://{flujo.version_api}.yaml</OASResource>
</OASValidation>
```

`flujo.version_api` debe venir de una lista cerrada, no de la petición sin validar.

## Diferencias en Apigee Edge

Sin diferencias funcionales documentadas. La sección sobre `pattern` y expresiones regulares solo aparece en la página de X.

## Antipatrones

- Confiar en la validación con los defaults (`ValidateMessageBody=false`, parámetros libres).
- No controlar el `Content-Type`: el cuerpo pasa sin validar.
- Validar respuestas con la especificación del proxy cuando las rutas del backend difieren.
- `pattern` con *lookarounds* o retrorreferencias.
- Tratar `security` de la especificación como autenticación.

## Fuentes

- OASValidation policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/oas-validation-policy> (consultada directamente, contenido completo, 2026-10-22).
- OASValidation policy — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/oas-validation-policy> (consultada directamente, 2026-10-22).
