---
id: politica-xml-to-json
titulo: XMLToJSON — referencia completa
area: politicas
tags: [xmltojson, xml, json, soap, transformacion, treatasarray, striplevels, mediacion, standard]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
elemento_xml: XMLToJSON
tipo_politica: standard
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/xml-json-policy
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/xml-json-policy
revisado: 2026-10-22
---

# XMLToJSON — referencia completa

> [!NOTE]
> **Tipo:** Standard. **Elemento raíz:** `<XMLToJSON>`.
> **Aplica a:** Apigee X, hybrid y Edge, con el mismo comportamiento.

XMLToJSON convierte un cuerpo **XML** en **JSON**. Normalmente va en el flujo de respuesta, para devolver JSON al cliente desde un backend XML o SOAP; es la pareja de [JSONToXML](json-xml.md).

> [!IMPORTANT]
> **Solo se ejecuta si el `Content-Type` del origen es `application/xml`** (según la página; el texto no menciona `text/xml`, habitual en SOAP 1.1). Si no coincide, la política se salta y el cliente recibe XML. Comprueba en Debug el `Content-Type` real de tu backend.

## Sintaxis completa

Hay que usar **`<Options>` o `<Format>`**, uno de los dos y no ambos.

```xml
<XMLToJSON name="X2J-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <Source>response</Source>
  <OutputVariable>response</OutputVariable>
  <Options>
    <RecognizeNumber>true</RecognizeNumber>
    <RecognizeBoolean>true</RecognizeBoolean>
    <RecognizeNull>true</RecognizeNull>
    <NullValue>NULL</NullValue>
    <NamespaceBlockName>#namespaces</NamespaceBlockName>
    <DefaultNamespaceNodeName>&amp;</DefaultNamespaceNodeName>
    <NamespaceSeparator>***</NamespaceSeparator>
    <TextAlwaysAsProperty>true</TextAlwaysAsProperty>
    <TextNodeName>TEXT</TextNodeName>
    <AttributeBlockName>FOO_BLOCK</AttributeBlockName>
    <AttributePrefix>BAR_</AttributePrefix>
    <OutputPrefix>PREFIX_</OutputPrefix>
    <OutputSuffix>_SUFFIX</OutputSuffix>
    <StripLevels>2</StripLevels>
    <TreatAsArray>
      <Path unwrap="true">raiz/elementos/elemento</Path>
    </TreatAsArray>
  </Options>
  <!-- o bien: <Format>yahoo</Format> -->
</XMLToJSON>
```

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno; da nombre a `xmltojson.{name}.failed`. |
| `continueOnError` | No | `false` | Con `true`, un XML inválido no corta el flujo. |
| `enabled` | No | `true` | Con `false` no se ejecuta. |
| `async` | No | `false` | **Obsoleto.** |

## Elementos hijos

| Elemento | Default | Resumen |
|---|---|---|
| `<Source>` | `message` | Mensaje (o variable string) con el XML. |
| `<OutputVariable>` | el de `<Source>` | Dónde dejar el JSON; pone `Content-Type: application/json`. Obligatorio si `<Source>` es string. |
| `<Options>` o `<Format>` | — | Uno de los dos es obligatorio (`EitherOptionOrFormat`). |

### Tipos de datos

| Opción | `true` | `false` |
|---|---|---|
| `<RecognizeNumber>` | `<b>100</b>` → `"b": 100` | `"b": "100"` |
| `<RecognizeBoolean>` | `<b>true</b>` → `"b": true` | `"b": "true"` |
| `<RecognizeNull>` | `<b></b>` → `"b": null` (o el valor de `<NullValue>`) | `"b": {}` |

> [!WARNING]
> `<RecognizeNumber>true</RecognizeNumber>` convierte en número todo lo que lo parezca: códigos con ceros a la izquierda (`"007"` → `7`), números de cuenta o identificadores largos que pierden precisión en JavaScript. Si tus datos tienen identificadores numéricos, déjalo en `false` y tipa en el cliente, o convierte campo a campo.

### Espacios de nombres

Por defecto se **descartan**. Para conservarlos hay que declarar **los tres**: `<NamespaceBlockName>`, `<DefaultNamespaceNodeName>` y `<NamespaceSeparator>`.

### Texto: `<TextAlwaysAsProperty>` y `<TextNodeName>`

| XML | `TextAlwaysAsProperty` = `false` | `true` (con `TextNodeName` = `#text`) |
|---|---|---|
| `<a>valor</a>` | `"a": "valor"` | `"a": {"#text": "valor"}` |
| `<a>v1<b>v2</b></a>` | `"a": {"#text": "v1", "b": "v2"}` | `"a": {"#text": "v1", "b": {"#text": "v2"}}` |

### Atributos XML: `<AttributeBlockName>` y `<AttributePrefix>`

`<a x="1"/>` con bloque `attrs` y prefijo `@` → `"a": {"attrs": {"@x": "1"}}`. Solo bloque → `{"attrs": {"x": "1"}}`; solo prefijo → `{"@x": "1"}`; ninguno → `{"x": "1"}`.

### `<OutputPrefix>` y `<OutputSuffix>`

Texto que se añade antes y después del JSON. `<OutputPrefix>{ "resultado": </OutputPrefix>` con `<OutputSuffix>}</OutputSuffix>` envuelve la salida en un objeto. Es concatenación de texto: con un prefijo mal pensado se genera **JSON inválido**.

### `<StripLevels>`

Elimina niveles superiores del resultado, típico para quitar `Envelope` y `Body` de una respuesta SOAP. Solo se puede quitar hasta el **primer elemento con varios hijos**: valores mayores no quitan más.

### `<TreatAsArray>/<Path unwrap>`

Por defecto, un elemento repetido se convierte en array, pero si aparece **una sola vez** se convierte en un valor simple: el mismo campo cambia de tipo según la respuesta. `<Path>` (ruta jerárquica `a/b/c`, **no** JSONPath) fuerza array siempre. `unwrap="true"` además elimina ese nivel del JSON para aplanarlo.

> [!TIP]
> Declara `<TreatAsArray>` para **toda** colección del contrato. Los clientes que reciben a veces un objeto y a veces un array fallan de forma intermitente y difícil de diagnosticar.

### `<Format>`

Plantillas predefinidas de opciones: `xml.com`, `yahoo`, `google`, `badgerFish`. Un valor desconocido hace fallar el despliegue (`UnknownFormat`).

| Formato | Opciones |
|---|---|
| `xml.com` | `RecognizeNull`, `TextNodeName` = `#text`, `AttributePrefix` = `@` |
| `yahoo` | `RecognizeNumber`, `TextNodeName` = `content` |
| `google` | `TextNodeName` = `$t`, `NamespaceSeparator` = `$`, `TextAlwaysAsProperty` |
| `badgerFish` | `TextNodeName` = `$`, `TextAlwaysAsProperty`, `AttributePrefix` = `@`, `NamespaceSeparator` = `:`, `NamespaceBlockName` = `@xmlns`, `DefaultNamespaceNodeName` = `$` |

## Variables de flujo

No publica variables de éxito.

## Errores

### En runtime

| Código | Causa |
|---|---|
| `steps.xmltojson.ExecutionFailed` | XML vacío, inválido o mal formado. |
| `steps.xmltojson.InCompatibleTypes` | `<Source>` y `<OutputVariable>` de tipos distintos. |
| `steps.xmltojson.InvalidSourceType` | `<Source>` no es `message` ni `string`. |
| `steps.xmltojson.OutputVariableIsNotAvailable` | `<Source>` string sin `<OutputVariable>`. |
| `steps.xmltojson.SourceUnavailable` | `<Source>` fuera de alcance o inexistente. |

> [!NOTE]
> La tabla oficial pone "ExecutionFailed" en la columna de código HTTP de todos los errores (error de la página); la página de JSONToXML indica `500` para los equivalentes. La respuesta de ejemplo usa el prefijo `steps.xml2json.`.

### Al desplegar

| Error | Causa |
|---|---|
| `EitherOptionOrFormat` | No hay ni `<Options>` ni `<Format>`. |
| `UnknownFormat` | `<Format>` con un valor desconocido. |

### Variables de fallo

`fault.name` y `xmltojson.{name}.failed`.

## Ejemplo: respuesta SOAP a JSON limpio

```xml
<XMLToJSON name="X2J-Respuesta-Soap">
  <Source>response</Source>
  <Options>
    <RecognizeNumber>false</RecognizeNumber>
    <RecognizeBoolean>true</RecognizeBoolean>
    <RecognizeNull>true</RecognizeNull>
    <StripLevels>3</StripLevels>
    <TreatAsArray>
      <Path unwrap="true">ConsultaCuentasResult/Cuentas/Cuenta</Path>
    </TreatAsArray>
  </Options>
</XMLToJSON>
```

Comprueba en Debug la ruta exacta de `<Path>` tras aplicar `<StripLevels>`; la documentación no aclara si `<Path>` se evalúa antes o después de quitar niveles.

## Diferencias en Apigee Edge

Sin diferencias funcionales documentadas.

## Antipatrones

- Sin `<TreatAsArray>` en colecciones: el tipo del campo cambia según el número de elementos.
- `RecognizeNumber` con identificadores numéricos largos o con ceros a la izquierda.
- `<OutputPrefix>`/`<OutputSuffix>` que generan JSON inválido.
- No controlar el `Content-Type` del backend.

## Fuentes

- XMLToJSON policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/xml-json-policy> (consultada directamente, contenido completo, 2026-10-22).
- XML to JSON policy — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/xml-json-policy> (consultada directamente, 2026-10-22).
