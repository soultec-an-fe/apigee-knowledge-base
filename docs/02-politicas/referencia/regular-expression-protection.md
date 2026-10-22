---
id: politica-regular-expression-protection
titulo: RegularExpressionProtection — referencia completa
area: politicas
tags: [regularexpressionprotection, regex, inyeccion, sqli, xss, seguridad, extensible]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
elemento_xml: RegularExpressionProtection
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/regular-expression-protection
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/regular-expression-protection
revisado: 2026-10-22
---

# RegularExpressionProtection — referencia completa

> [!NOTE]
> **Tipo:** Extensible. **Elemento raíz:** `<RegularExpressionProtection>`.
> **Aplica a:** Apigee X, hybrid y Edge, con el mismo comportamiento.

RegularExpressionProtection extrae valores de la petición o la respuesta (ruta, query params, cabeceras, form params, variables, partes de un XML o un JSON) y los compara con **expresiones regulares de amenazas**. Si **alguna** coincide, la política falla con `ThreatDetected`. Es una lista de patrones prohibidos.

> [!WARNING]
> Es defensa en profundidad, no la defensa principal: ninguna regex detiene todos los ataques de contenido. Contra SQLi, consultas parametrizadas en el backend; contra XSS, escapar la salida. Para APIs con contrato, validar contra el contrato ([OASValidation](../03-mediacion.md)) suele proteger más que una lista de patrones. Ver la [guía de threat protection](../../03-seguridad/05-threat-protection.md).

## Sintaxis completa

```xml
<RegularExpressionProtection name="REP-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <Source>request</Source>
  <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>
  <URIPath>
    <Pattern>PATRON</Pattern>
  </URIPath>
  <QueryParam name="q">
    <Pattern>PATRON</Pattern>
  </QueryParam>
  <Header name="x-filtro">
    <Pattern>PATRON</Pattern>
  </Header>
  <FormParam name="comentario">
    <Pattern>PATRON</Pattern>
  </FormParam>
  <Variable name="flujo.texto_libre">
    <Pattern>PATRON</Pattern>
  </Variable>
  <XMLPayload>
    <Namespaces>
      <Namespace prefix="s">http://schemas.xmlsoap.org/soap/envelope/</Namespace>
    </Namespaces>
    <XPath>
      <Expression>//s:Body//text()</Expression>
      <Type>nodeset</Type>
      <Pattern>PATRON</Pattern>
    </XPath>
  </XMLPayload>
  <JSONPayload escapeSlashCharacter="true">
    <JSONPath>
      <Expression>$..comentario</Expression>
      <Pattern>PATRON</Pattern>
    </JSONPath>
  </JSONPayload>
</RegularExpressionProtection>
```

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno. |
| `continueOnError` | No | `false` | La página sugiere `true` para capturar el error y responder a medida; con una FaultRule se consigue lo mismo sin dejar pasar la amenaza. |
| `enabled` | No | `true` | Con `false` no se ejecuta. |
| `async` | No | `false` | **Obsoleto.** |

## Elementos hijos

| Elemento | Inspecciona | Atributos |
|---|---|---|
| `<Source>` | Mensaje de origen. Si se omite: `message` (petición o respuesta según el flujo). | — |
| `<IgnoreUnresolvedVariables>` | Con `false` (default), una variable sin resolver da error; con `true`, se toma como vacía. | — |
| `<URIPath>` | La ruta de la petición. | — |
| `<QueryParam>` | Un query param. | `name` (obligatorio) |
| `<Header>` | Una cabecera de petición o respuesta. | `name` (obligatorio) |
| `<FormParam>` | Un parámetro de formulario. Solo si `Content-Type` es `application/x-www-form-urlencoded`. | `name` (obligatorio) |
| `<Variable>` | Cualquier variable de flujo. | `name` (obligatorio) |
| `<XMLPayload>/<XPath>` | Resultado de una XPath 1.0 sobre el XML. Requiere `Content-Type` XML (`application/xml`, `text/xml`). | — |
| `<JSONPayload>/<JSONPath>` | Resultado de una JSONPath sobre el JSON. Requiere `Content-Type` JSON. | `escapeSlashCharacter` en `<JSONPayload>` (default `true`) |

Cada elemento lleva **uno o más** `<Pattern>`; basta que coincida uno. Debe haber al menos un elemento que inspeccionar (`NothingToEnforce`) y patrones en cada uno (`NoPatternsToEnforce`).

> [!IMPORTANT]
> Como en las políticas de threat protection, `<XMLPayload>` y `<JSONPayload>` dependen del `Content-Type`: un cliente que mande el JSON como `text/plain` evita la inspección del cuerpo. Una API puede declarar ambos elementos; solo se aplica el que corresponde al `Content-Type`. Para cubrir el cuerpo sin depender de la cabecera, inspecciona `<Variable name="request.content">`.

### `<XPath>`: `<Expression>`, `<Type>`, `<Pattern>`

`<Type>` decide **cuántos valores** se comprueban:

| `<Type>` | Efecto |
|---|---|
| `string` (default) | La XPath se convierte en **un solo** string. Con `//*/@*` (todos los atributos) se comprobaría **solo uno**, sin saber cuál. |
| `nodeset` | Se comprueba **cada** nodo devuelto. Lo que normalmente quieres con expresiones que devuelven varios valores. |
| `boolean`, `int`, `long`, `float`, `double` | Conversiones a esos tipos. |

Los prefijos usados en la XPath se declaran en `<Namespaces>/<Namespace prefix>`.

### Escribir los patrones

- Sintaxis de `java.util.regex` (Java).
- Los caracteres reservados de XML (`"`, `&`, `'`, `<`, `>`) se escapan (`&lt;`) o se envuelve el patrón en `<![CDATA[ … ]]>`.
- `(?i)` al principio para no distinguir mayúsculas: `(?i)(drop\s+table)`.
- En `<JSONPayload>`, con `escapeSlashCharacter="true"` (default), las `/` del patrón se escapan automáticamente.

> [!CAUTION]
> **Antipatrón documentado por Google: cuantificadores greedy.** `.*`, `.+` y anidamientos como `(a+)+` causan *backtracking* catastrófico: un payload de pocos KB puede ocupar segundos de CPU, y la política de seguridad se convierte en el vector de DoS. Ancla los patrones, evita `.*` al principio y al final (la búsqueda ya es parcial) y nunca anides cuantificadores.

### Patrones de ejemplo de Google

| Amenaza | Patrón |
|---|---|
| Inyección SQL | `[\s]*((delete)\|(exec)\|(drop\s*table)\|(insert)\|(shutdown)\|(update)\|(\bor\b))` |
| Server-Side Include | `<!--#(include\|exec\|echo\|config\|printenv)\s+.*` |
| XPath abreviada | `(/(@?[\w_?\w:\*]+(\[[^]]+\])*)?)+` |
| XPath expandida | `/?(ancestor(-or-self)?\|descendant(-or-self)?\|following(-sibling))` |
| JavaScript | `<\s*script\b[^>]*>[^<]+<\s*/\s*script\s*>` |

(En la tabla, `\|` es `|`: va escapado solo por el formato Markdown.)

Úsalos como punto de partida y pruébalos contra tráfico real: el de SQL bloquea, por ejemplo, cualquier texto con la palabra "update" o "or" aislada.

## Variables de flujo

No publica variables de éxito.

## Errores

### En runtime

La página no indica el código HTTP de cada error.

| Código | Mensaje |
|---|---|
| `ThreatDetected` | `Regular Expression Threat Detected in {0}: regex: {1} input: {2}` |
| `ExecutionFailed` | Fallo al ejecutar la política. |
| `InstantiationFailed` | Fallo al instanciarla. |
| `NonMessageVariable` | `<Source>` no es un mensaje. |
| `SourceMessageNotAvailable` | El mensaje de `<Source>` no está disponible. |
| `VariableResolutionFailed` | No se pudo resolver una variable. |

> [!WARNING]
> El mensaje de `ThreatDetected` incluye **la regex que coincidió y la entrada del atacante**. Devolverlo tal cual le enseña al atacante qué filtro tiene que esquivar y refleja su payload en la respuesta. Responde siempre con un **400 genérico**, como recomienda el propio ejemplo de Google en GitHub.

### Al desplegar

`CannotBeConvertedToNodeset`, `DuplicatePrefix`, `EmptyJSONPathExpression`, `EmptyXPathExpression`, `InvalidRegularExpression`, `JSONPathCompilationFailed`, `NONEmptyPrefixMappedToEmptyURI`, `NoPatternsToEnforce`, `NothingToEnforce`, `XPathCompilationFailed`.

### Variables de fallo

| Variable | Ejemplo |
|---|---|
| `fault.name` | `fault.name = "ThreatDetected"` |
| `regularexpressionprotection.{name}.failed` | `regularexpressionprotection.REP-Busqueda.failed = true` |

## Ejemplos

### 1. Parámetro de búsqueda y campo de texto libre del JSON

```xml
<RegularExpressionProtection name="REP-Busqueda">
  <Source>request</Source>
  <QueryParam name="q">
    <Pattern>(?i)\b(union\s+select|insert\s+into|drop\s+table)\b</Pattern>
    <Pattern><![CDATA[(?i)<\s*script\b]]></Pattern>
  </QueryParam>
  <JSONPayload>
    <JSONPath>
      <Expression>$..comentario</Expression>
      <Pattern><![CDATA[(?i)<\s*script\b]]></Pattern>
      <Pattern>(?i)javascript\s*:</Pattern>
    </JSONPath>
  </JSONPayload>
</RegularExpressionProtection>
```

### 2. Caracteres especiales en un formulario

```xml
<RegularExpressionProtection name="REP-Formulario">
  <Source>request</Source>
  <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>
  <FormParam name="nombre">
    <Pattern><![CDATA[[<>"%;=&]]]></Pattern>
  </FormParam>
</RegularExpressionProtection>
```

### 3. 400 genérico

```xml
<FaultRule name="fr-amenaza">
  <Condition>fault.name = "ThreatDetected"</Condition>
  <Step>
    <Name>AM-Error-400-Generico</Name>
  </Step>
</FaultRule>
```

## Diferencias en Apigee Edge

Sin diferencias funcionales documentadas. La página de Edge añade un patrón de ejemplo para inyección de excepciones Java y vídeos.

## Antipatrones

- Cuantificadores greedy o anidados.
- `<Type>string</Type>` con XPath que devuelven varios nodos.
- Depender de `<JSONPayload>` sin controlar el `Content-Type`.
- Devolver el mensaje de `ThreatDetected` al cliente.
- Usarla como sustituto de consultas parametrizadas o de validación por contrato.

## Fuentes

- RegularExpressionProtection policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/regular-expression-protection> (consultada directamente, contenido completo, 2026-10-22).
- Regular Expression Protection policy — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/regular-expression-protection> (consultada directamente, 2026-10-22).
- Antipattern: Use greedy quantifiers in the RegularExpressionProtection policy: <https://docs.cloud.google.com/apigee/docs/api-platform/antipatterns/greedy-quantifiers>
