---
id: politica-json-to-xml
titulo: JSONToXML — referencia completa
area: politicas
tags: [jsontoxml, json, xml, transformacion, soap, mediacion, standard]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
elemento_xml: JSONToXML
tipo_politica: standard
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/json-xml-policy
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/json-xml-policy
revisado: 2026-10-22
---

# JSONToXML — referencia completa

> [!NOTE]
> **Tipo:** Standard. **Elemento raíz:** `<JSONToXML>`.
> **Aplica a:** Apigee X, hybrid y Edge, con el mismo comportamiento.

JSONToXML convierte un cuerpo **JSON** en **XML**. El caso clásico es exponer una API JSON delante de un backend que solo habla XML o SOAP: JSONToXML en el flujo de petición, [XMLToJSON](xml-json.md) en el de respuesta y, si la estructura no encaja, una [XSLTransform](xsl-transform.md) en medio.

> [!IMPORTANT]
> **Solo se ejecuta si el `Content-Type` del mensaje de origen es `application/json`.** Con otro tipo, la política se **salta en silencio**: el mensaje sigue como JSON hacia un backend que espera XML.

## Sintaxis completa

```xml
<JSONToXML name="J2X-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <Source>request</Source>
  <OutputVariable>request</OutputVariable>
  <Options>
    <OmitXmlDeclaration>false</OmitXmlDeclaration>
    <NamespaceBlockName>#namespaces</NamespaceBlockName>
    <DefaultNamespaceNodeName>$default</DefaultNamespaceNodeName>
    <NamespaceSeparator>:</NamespaceSeparator>
    <AttributeBlockName>#attrs</AttributeBlockName>
    <AttributePrefix>@</AttributePrefix>
    <ObjectRootElementName>Root</ObjectRootElementName>
    <ArrayRootElementName>Array</ArrayRootElementName>
    <ArrayItemElementName>Item</ArrayItemElementName>
    <Indent>false</Indent>
    <TextNodeName>#text</TextNodeName>
    <NullValue>NULL</NullValue>
    <InvalidCharsReplacement>_</InvalidCharsReplacement>
  </Options>
</JSONToXML>
```

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno; da nombre a `jsontoxml.{name}.failed`. |
| `continueOnError` | No | `false` | Con `true`, un JSON inválido no corta el flujo. |
| `enabled` | No | `true` | Con `false` no se ejecuta. |
| `async` | No | `false` | **Obsoleto.** |

## Elementos hijos

| Elemento | Default | Resumen |
|---|---|---|
| `<Source>` | `message` | Mensaje (o variable string) con el JSON. |
| `<OutputVariable>` | el mismo que `<Source>` | Dónde dejar el XML. Obligatorio si `<Source>` es una variable de tipo string. Fija `Content-Type: text/xml;charset=UTF-8`. |
| `<Options>/<OmitXmlDeclaration>` | `false` | `true` omite `<?xml …?>`; útil si el XML se incrusta en otro documento (p. ej. dentro de un sobre SOAP). Siempre UTF-8 y XML 1.0. |
| `<NamespaceBlockName>`, `<DefaultNamespaceNodeName>`, `<NamespaceSeparator>` | — | Generan espacios de nombres a partir de una propiedad del JSON (ver ejemplo). |
| `<ObjectRootElementName>` | — | Nombre del elemento raíz cuando el JSON es un objeto sin nombre (todo JSON lo es). |
| `<ArrayRootElementName>`, `<ArrayItemElementName>` | — | Nombres para un array raíz y sus elementos. |
| `<AttributeBlockName>` | — | Las propiedades dentro de este objeto pasan a ser **atributos** XML. |
| `<AttributePrefix>` | — | Las propiedades que empiezan por este prefijo pasan a ser atributos. |
| `<TextNodeName>` | — | La propiedad con este nombre se convierte en el **texto** del elemento padre. |
| `<NullValue>` | `NULL` | Valor que se interpreta como nulo y produce un elemento vacío. |
| `<InvalidCharsReplacement>` | — | Sustituye caracteres que no son válidos en nombres XML (`First%%%Name` → `First_Name`). |
| `<Indent>` | `false` | Indentar la salida. |

### Espacios de nombres

Con `#namespaces`, `$default` y `:` como en la sintaxis de arriba, este JSON:

```json
{"pago": {"#namespaces": {"$default": "urn:banco:pagos", "c": "urn:banco:comun"}, "monto": 100, "c:moneda": "COP"}}
```

produce:

```xml
<pago xmlns="urn:banco:pagos" xmlns:c="urn:banco:comun">
  <monto>100</monto>
  <c:moneda>COP</c:moneda>
</pago>
```

Como JSON no tiene espacios de nombres, el **cliente** tiene que enviarlos en el JSON. Si no quieres exponer eso, genera el XML con una plantilla (AssignMessage o XSLTransform).

## Variables de flujo

No publica variables de éxito.

## Errores

### En runtime

Todos `500`:

| Código | Causa |
|---|---|
| `steps.jsontoxml.ExecutionFailed` | JSON vacío, inválido o mal formado. |
| `steps.jsontoxml.InCompatibleTypes` | `<Source>` y `<OutputVariable>` de tipos distintos (deben ser ambos `message` o ambos `string`). |
| `steps.jsontoxml.InvalidSourceType` | `<Source>` no es de tipo `message` ni `string`. |
| `steps.jsontoxml.OutputVariableIsNotAvailable` | `<Source>` es string y falta `<OutputVariable>`. |
| `steps.jsontoxml.SourceUnavailable` | `<Source>` fuera de alcance o inexistente. |

La respuesta de ejemplo de la página usa el prefijo `steps.json2xml.`; captura por `fault.name`. Un JSON inválido del cliente debería responderse con **400**: tradúcelo en una FaultRule.

### Al desplegar

Ninguno propio.

### Variables de fallo

`fault.name` y `jsontoxml.{name}.failed`.

## Ejemplo: API JSON delante de un servicio XML

```xml
<JSONToXML name="J2X-Peticion">
  <Source>request</Source>
  <OutputVariable>request</OutputVariable>
  <Options>
    <OmitXmlDeclaration>true</OmitXmlDeclaration>
    <ObjectRootElementName>SolicitudPago</ObjectRootElementName>
    <InvalidCharsReplacement>_</InvalidCharsReplacement>
  </Options>
</JSONToXML>
```

Antes, una [JSONThreatProtection](json-threat-protection.md); después, si el backend exige otro esquema, una [XSLTransform](xsl-transform.md).

## Diferencias en Apigee Edge

Sin diferencias funcionales documentadas.

## Antipatrones

- No controlar el `Content-Type`: la conversión se salta sin error.
- Exponer al cliente la mecánica de espacios de nombres o atributos (`#attrs`, `@`) como parte del contrato.
- Convertir sin protección previa contra payloads desmesurados.

## Fuentes

- JSONToXML policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/json-xml-policy> (consultada directamente, contenido completo, 2026-10-22).
- JSON to XML policy — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/json-xml-policy> (consultada directamente, 2026-10-22).
