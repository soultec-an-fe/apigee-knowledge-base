---
id: politica-extract-variables
titulo: ExtractVariables — referencia completa
area: politicas
tags: [extractvariables, mediacion, jsonpath, xpath, uri, cabeceras, variables, extensible]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
elemento_xml: ExtractVariables
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/extract-variables-policy
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/extract-variables-policy
revisado: 2026-10-22
---

# ExtractVariables — referencia completa

> [!NOTE]
> **Tipo:** Extensible. **Elemento raíz:** `<ExtractVariables>`.
> **Aplica a:** Apigee X, hybrid y Edge, con el mismo comportamiento.

ExtractVariables **saca valores** de un mensaje (ruta, query params, cabeceras, form params, cuerpo JSON o XML) o de cualquier variable, y los guarda en variables de flujo para usarlos después (condiciones, AssignMessage, claves de caché, Analytics). Es la contraparte de lectura de [AssignMessage](assign-message.md).

Antes de usarla, comprueba si la variable ya existe: Apigee publica muchas automáticamente (`request.header.*`, `request.queryparam.*`, `proxy.pathsuffix`…; ver [Variables de flujo](../../01-proxies/04-variables-de-flujo.md)). Y no hace falta para leer la respuesta de un ServiceCallout: sus variables de respuesta ya están disponibles.

## Sintaxis completa

```xml
<ExtractVariables name="EV-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <Source clearPayload="false">request</Source>
  <VariablePrefix>flujo</VariablePrefix>
  <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>
  <URIPath>
    <Pattern ignoreCase="true">/cuentas/{cuenta_id}/movimientos</Pattern>
  </URIPath>
  <QueryParam name="desde">
    <Pattern>{fecha_desde}</Pattern>
  </QueryParam>
  <Header name="Authorization">
    <Pattern>Bearer {token}</Pattern>
  </Header>
  <FormParam name="grant_type">
    <Pattern>{grant}</Pattern>
  </FormParam>
  <Variable name="request.header.x-firma">
    <Pattern>sha256={firma_hex}</Pattern>
  </Variable>
  <JSONPayload>
    <Variable name="monto" type="double">
      <JSONPath>$.transferencia.monto</JSONPath>
    </Variable>
  </JSONPayload>
  <XMLPayload stopPayloadProcessing="false">
    <Namespaces>
      <Namespace prefix="s">http://schemas.xmlsoap.org/soap/envelope/</Namespace>
    </Namespaces>
    <Variable name="operacion" type="string">
      <XPath>local-name(/s:Envelope/s:Body/*[1])</XPath>
    </Variable>
  </XMLPayload>
</ExtractVariables>
```

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno; da nombre a `extractvariables.{name}.failed`. |
| `continueOnError` | No | `false` | Con `true`, el flujo sigue aunque falle (p. ej. cuerpo vacío o JSON inválido). |
| `enabled` | No | `true` | Con `false` no se ejecuta. |
| `async` | No | `false` | **Obsoleto.** |

## Elementos hijos

| Elemento | Obligatorio | Default | Resumen |
|---|---|---|---|
| `<Source clearPayload>` | No | `message` | Mensaje o variable de origen. `clearPayload="true"` vacía el cuerpo de origen tras extraer, para liberar memoria. |
| `<VariablePrefix>` | No | — | Prefijo de las variables creadas: `{prefijo}.{nombre}`. |
| `<IgnoreUnresolvedVariables>` | No | `false` | Variables sin resolver = vacías, en lugar de error. |
| `<URIPath>` | Uno al menos | — | Patrones contra `proxy.pathsuffix` (la ruta **sin** el basepath). Solo petición. |
| `<QueryParam name>` | Uno al menos | — | Un query param. Solo petición. |
| `<Header name>` | Uno al menos | — | Una cabecera (petición o respuesta). |
| `<FormParam name>` | Uno al menos | — | Un form param; solo con `Content-Type: application/x-www-form-urlencoded`. |
| `<Variable name>` | Uno al menos | — | Cualquier variable de flujo. |
| `<JSONPayload>/<Variable name type>/<JSONPath>` | Uno al menos | — | Valores de un JSON; solo con `Content-Type: application/json`. |
| `<XMLPayload>/<Variable name type>/<XPath>` | Uno al menos | — | Valores de un XML; solo con `text/xml`, `application/xml` o `application/*+xml`. |

Sin ningún elemento de extracción, el despliegue falla con `NothingToExtract`.

> [!IMPORTANT]
> `<JSONPayload>` y `<XMLPayload>` dependen del `Content-Type` del mensaje. Si un backend responde JSON con `text/plain`, la extracción no ocurre y **las variables no se crean**, sin error. Si no controlas la cabecera, lee el cuerpo con `<Source>` apuntando a una variable o corrige antes el `Content-Type` con AssignMessage.

### Patrones (`<Pattern>`) para ruta, parámetros, cabeceras y variables

El patrón es una plantilla: el texto fijo debe coincidir y cada `{nombre}` captura un valor. `ignoreCase="true"` ignora mayúsculas (default `false`).

| Regla | Detalle |
|---|---|
| Varios `<Pattern>` | Se prueban todos; si coinciden varios, gana el de **más segmentos**; a igualdad, el primero. Si no coincide ninguno, **no se crea** la variable. |
| Varias variables en un patrón | `/a/{seg1}/c/{seg2}` |
| Comodines en `<URIPath>` | `*` = un segmento; `**` = varios segmentos. |
| Comodín en cabeceras y parámetros | `*` = cualquier número de caracteres: `*;charset={encoding}`. |
| Llaves literales | Se escapan con `%`: `%{usuario%} {nombre}`. |
| Valores repetidos | La 1.ª instancia sin índice, la 2.ª `name="w.2"`, la 3.ª `w.3`… En cabeceras, `name="h.values"` captura todas. |

### `<JSONPayload>` y `<XMLPayload>`

Cada `<Variable>` es una extracción independiente. `type` admite `string`, `boolean`, `integer`, `long`, `float`, `double` y `nodeset` (devuelve un fragmento JSON o XML). Si la ruta no existe en el documento, la variable **no se crea** (en JSON, la tabla de errores habla también de `InvalidJSONPath`).

| | JSONPath | XPath |
|---|---|---|
| Admite plantillas de mensaje | Sí (`{variable}` dentro de la expresión) | No |
| Versión | JSONPath de Apigee | XPath **1.0** |
| Espacios de nombres | — | Declarar en `<Namespaces>/<Namespace prefix>`; usar un prefijo no declarado → `XPathCompilationFailed` |
| Parar al primer acierto | — | `stopPayloadProcessing="true"` en `<XMLPayload>` |

> [!NOTE]
> La tabla de atributos de `<XMLPayload>/<Variable>` dice que el `type` por defecto es `Boolean`, lo que no encaja con el resto de la documentación ni con el comportamiento esperado. Declara siempre `type`.

### Orden y sobrescritura

La política se ejecuta en orden; si varias extracciones escriben en la **misma** variable, gana la **última**. Se puede aprovechar para "token por query param o, si no, por cabecera": pon primero la fuente de menor prioridad.

### Alcance de las variables

Las variables extraídas son **globales** desde ese momento: PreFlow y PostFlow de ProxyEndpoint y TargetEndpoint, flujos de error y PostClientFlow (para MessageLogging).

> [!TIP]
> Si una variable extraída no aparece en Debug, la documentación sugiere probar sin `<VariablePrefix>`.

## Variables de flujo

Las que la política crea según su configuración (`{prefijo}.{nombre}`).

## Errores

### En runtime

Todos `500`:

| Código | Causa |
|---|---|
| `steps.extractvariables.ExecutionFailed` | Cuerpo JSON o XML vacío, inválido o mal formado. |
| `steps.extractvariables.SourceMessageNotAvailable` | `<Source>` fuera de alcance o inexistente. |
| `steps.extractvariables.InvalidJSONPath` | JSONPath inválida para el documento. |
| `steps.extractvariables.JsonPathParsingFailure` | No se pudo parsear la JSONPath o leer el `<Source>` (típicamente, variable inexistente). |
| `steps.extractvariables.SetVariableFailed` | No se pudo asignar la variable, p. ej. nombres anidados que chocan (`a.b` y `a.b.c`). |
| `steps.extractvariables.ImmutableVariable` | La variable de destino es de solo lectura. |
| `steps.extractvariables.UnableToCast` | No se pudo convertir el valor al `type` pedido. |

> [!TIP]
> Un cuerpo inválido **del cliente** genera un 500 con `ExecutionFailed`. Tradúcelo a 400 en una FaultRule.

### Al desplegar

`NothingToExtract`, `NONEmptyPrefixMappedToEmptyURI`, `DuplicatePrefix`, `NoXPathsToEvaluate`, `EmptyXPathExpression`, `NoJSONPathsToEvaluate`, `EmptyJSONPathExpression`, `MissingName`, `PatternWithoutVariable`, `InvalidPattern`, `CannotBeConvertedToNodeset`, `JSONPathCompilationFailed`, `XPathCompilationFailed`, `InstantiationFailed`.

### Variables de fallo

| Variable | Ejemplo |
|---|---|
| `fault.name` | `fault.name = "ExecutionFailed"` |
| `extractvariables.{name}.failed` | `extractvariables.EV-Transferencia.failed = true` |

## Ejemplos

### 1. ID de la ruta y token de la cabecera

```xml
<ExtractVariables name="EV-Cuenta-Y-Token">
  <Source>request</Source>
  <VariablePrefix>flujo</VariablePrefix>
  <URIPath>
    <Pattern ignoreCase="true">/cuentas/{cuenta_id}</Pattern>
    <Pattern ignoreCase="true">/cuentas/{cuenta_id}/**</Pattern>
  </URIPath>
  <Header name="Authorization">
    <Pattern>Bearer {access_token}</Pattern>
  </Header>
</ExtractVariables>
```

Crea `flujo.cuenta_id` y `flujo.access_token`.

### 2. Campos del cuerpo JSON para una condición de negocio

```xml
<ExtractVariables name="EV-Transferencia">
  <Source>request</Source>
  <VariablePrefix>transferencia</VariablePrefix>
  <JSONPayload>
    <Variable name="monto" type="double">
      <JSONPath>$.monto</JSONPath>
    </Variable>
    <Variable name="moneda" type="string">
      <JSONPath>$.moneda</JSONPath>
    </Variable>
  </JSONPayload>
</ExtractVariables>
```

```xml
<Step>
  <Name>RF-Monto-Excede-Limite</Name>
  <Condition>transferencia.monto > 10000000</Condition>
</Step>
```

### 3. Datos de la respuesta de un ServiceCallout guardada en una variable

```xml
<ExtractVariables name="EV-Riesgo">
  <Source>respuestaRiesgo</Source>
  <VariablePrefix>riesgo</VariablePrefix>
  <JSONPayload>
    <Variable name="puntaje" type="integer">
      <JSONPath>$.score</JSONPath>
    </Variable>
  </JSONPayload>
</ExtractVariables>
```

### 4. Atributo de un perfil obtenido con AccessEntity

```xml
<ExtractVariables name="EV-Perfil-App">
  <Source>AccessEntity.AE-App</Source>
  <VariablePrefix>app</VariablePrefix>
  <XMLPayload>
    <Variable name="segmento" type="string">
      <XPath>/App/Attributes/Attribute[Name='segmento']/Value</XPath>
    </Variable>
  </XMLPayload>
</ExtractVariables>
```

## Diferencias en Apigee Edge

Sin diferencias funcionales documentadas.

## Antipatrones

- Extraer lo que Apigee ya expone como variable.
- Depender de la extracción JSON/XML sin controlar el `Content-Type`.
- Nombres de variable que chocan al anidar (`cliente` y `cliente.id`).
- Usar valores extraídos del cuerpo como identidad (p. ej. `cliente_id` del JSON) sin contrastarlos con la identidad autenticada.

## Fuentes

- ExtractVariables policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/extract-variables-policy> (consultada directamente, contenido completo, 2026-10-22).
- Extract Variables policy — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/extract-variables-policy> (consultada directamente, 2026-10-22).
