---
id: politica-xml-threat-protection
titulo: XMLThreatProtection — referencia completa
area: politicas
tags: [xmlthreatprotection, xml, soap, dos, parser, limites, seguridad, extensible]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
elemento_xml: XMLThreatProtection
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/xml-threat-protection-policy
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/xml-threat-protection-policy
revisado: 2026-10-22
---

# XMLThreatProtection — referencia completa

> [!NOTE]
> **Tipo:** Extensible. **Elemento raíz:** `<XMLThreatProtection>`.
> **Aplica a:** Apigee X, hybrid y Edge, con el mismo comportamiento.

XMLThreatProtection rechaza documentos XML que superen límites de **nombres**, **estructura** y **valores**, o que estén mal formados, antes de que lleguen a un parser costoso. Es la contraparte XML de [JSONThreatProtection](json-threat-protection.md) y protege APIs XML y SOAP.

> [!IMPORTANT]
> **Solo se ejecuta si `Content-Type` es `application/xml`**, según la página oficial (que no menciona `text/xml`, el tipo habitual de SOAP 1.1). Comprueba en Debug si se ejecuta con el tipo que usan tus clientes y rechaza antes los tipos de contenido que no aceptas.

> [!NOTE]
> La página de la política **no menciona** la protección contra expansión de entidades (*billion laughs*) ni contra entidades externas (XXE). Sus límites de profundidad, número de hijos y longitud de texto mitigan documentos desmesurados, pero no lo trates como una protección XXE documentada: asegúrate de que el parser de tu backend tenga las entidades externas desactivadas.

## Sintaxis completa

```xml
<XMLThreatProtection name="XTP-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <Source>request</Source>
  <NameLimits>
    <Element>64</Element>
    <Attribute>64</Attribute>
    <NamespacePrefix>32</NamespacePrefix>
    <ProcessingInstructionTarget>32</ProcessingInstructionTarget>
  </NameLimits>
  <StructureLimits>
    <NodeDepth>12</NodeDepth>
    <AttributeCountPerElement>10</AttributeCountPerElement>
    <NamespaceCountPerElement>5</NamespaceCountPerElement>
    <ChildCount includeComment="true" includeElement="true" includeProcessingInstruction="true" includeText="true">50</ChildCount>
  </StructureLimits>
  <ValueLimits>
    <Text>4096</Text>
    <Attribute>256</Attribute>
    <NamespaceURI>256</NamespaceURI>
    <Comment>512</Comment>
    <ProcessingInstructionData>512</ProcessingInstructionData>
  </ValueLimits>
</XMLThreatProtection>
```

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno; da nombre a `xmlattack.{name}.failed`. |
| `continueOnError` | No | `false` | No lo pongas en `true`. |
| `enabled` | No | `true` | Con `false` no se ejecuta. |
| `async` | No | `false` | **Obsoleto.** |

## Elementos hijos

Todos los límites son enteros; si se omiten, el default es `-1` (**sin límite**).

### `<NameLimits>`: longitud de nombres

| Elemento | Limita la longitud de |
|---|---|
| `<Element>` | Cualquier nombre de elemento (`book`, `title`…) |
| `<Attribute>` | Cualquier nombre de atributo (`category`) |
| `<NamespacePrefix>` | Cualquier prefijo de espacio de nombres (`ns1`) |
| `<ProcessingInstructionTarget>` | El destino de una instrucción de procesamiento (`xml-stylesheet`) |

### `<StructureLimits>`: forma del documento

| Elemento | Limita |
|---|---|
| `<NodeDepth>` | Profundidad máxima de nodos |
| `<AttributeCountPerElement>` | Atributos por elemento (sin contar las declaraciones de espacio de nombres) |
| `<NamespaceCountPerElement>` | Declaraciones `xmlns` por elemento |
| `<ChildCount>` | Hijos por elemento |

`<ChildCount>` tiene atributos para decidir qué cuenta como hijo, todos `true` por defecto: `includeComment`, `includeElement`, `includeProcessingInstruction` e `includeText`.

> [!NOTE]
> **Inconsistencias de nombres en la página.** Los encabezados dicen `<StructuralLimits>` pero el XML (y el esquema) usan **`<StructureLimits>`**. La tabla de atributos de `<ChildCount>` dice `includeProcessingInstructions` (en plural), mientras todos los ejemplos usan `includeProcessingInstruction`. Y el ejemplo de `<NamespaceCountPerElement>` explica un límite de 2 con una configuración de 3. Usa los nombres de los ejemplos XML.

### `<ValueLimits>`: longitud de valores

| Elemento | Limita la longitud de |
|---|---|
| `<Text>` | Cualquier nodo de texto |
| `<Attribute>` | Cualquier valor de atributo |
| `<NamespaceURI>` | Cualquier URI de espacio de nombres |
| `<Comment>` | Cualquier comentario |
| `<ProcessingInstructionData>` | El contenido de una instrucción de procesamiento |

### `<Source>`

`request` (default), `response` o `message`.

## Variables de flujo

No publica variables de éxito.

## Errores

### En runtime

| Código | HTTP | Causa |
|---|---|---|
| `steps.xmlthreatprotection.ExecutionFailed` | 500 | Se superó algún límite (nombre de elemento, hijos, profundidad, atributos…). |
| `steps.xmlthreatprotection.InvalidXMLPayload` | 500 | El cuerpo no es un XML válido. |
| `steps.xmlthreatprotection.SourceUnavailable` | 500 | `<Source>` fuera de alcance o inválido. |
| `steps.xmlthreatprotection.NonMessageVariable` | 500 | `<Source>` no es de tipo mensaje. |

### La propiedad `features.isPolicyHttpStatusEnabled`

Por defecto, JSONThreatProtection y XMLThreatProtection devuelven **500** y `ExecutionFailed`. Con la propiedad de organización `features.isPolicyHttpStatusEnabled=true`:

| Flujo | HTTP | Código de error |
|---|---|---|
| Petición | **400** | Específico (p. ej. `TextExceeded`), en lugar de `ExecutionFailed` |
| Respuesta | 500 | Específico |

En Apigee X la activa el soporte de Google Cloud. Si actualizas propiedades de organización con la API, incluye **todas** las existentes, o se borrarán.

### Al desplegar

No tiene errores de despliegue propios.

### Variables de fallo

| Variable | Ejemplo |
|---|---|
| `fault.name` | `fault.name = "ExecutionFailed"` |
| `xmlattack.{name}.failed` | `xmlattack.XTP-Soap.failed = true` |

## Ejemplos

### 1. API SOAP

```xml
<XMLThreatProtection name="XTP-Soap">
  <Source>request</Source>
  <NameLimits>
    <Element>100</Element>
    <Attribute>50</Attribute>
    <NamespacePrefix>20</NamespacePrefix>
    <ProcessingInstructionTarget>20</ProcessingInstructionTarget>
  </NameLimits>
  <StructureLimits>
    <NodeDepth>15</NodeDepth>
    <AttributeCountPerElement>10</AttributeCountPerElement>
    <NamespaceCountPerElement>10</NamespaceCountPerElement>
    <ChildCount includeComment="false" includeElement="true" includeProcessingInstruction="true" includeText="true">100</ChildCount>
  </StructureLimits>
  <ValueLimits>
    <Text>10000</Text>
    <Attribute>500</Attribute>
    <NamespaceURI>256</NamespaceURI>
    <Comment>0</Comment>
    <ProcessingInstructionData>0</ProcessingInstructionData>
  </ValueLimits>
</XMLThreatProtection>
```

`<Comment>0</Comment>` y `<ProcessingInstructionData>0</ProcessingInstructionData>` rechazan cualquier comentario o instrucción de procesamiento con contenido, que no tienen motivo para llegar en una petición SOAP.

### 2. Respuesta 400 genérica

```xml
<FaultRule name="fr-xml-malicioso">
  <Condition>xmlattack.XTP-Soap.failed = true</Condition>
  <Step>
    <Name>AM-Error-400-Payload</Name>
  </Step>
</FaultRule>
```

## Diferencias en Apigee Edge

| Aspecto | Apigee X / hybrid | Apigee Edge |
|---|---|---|
| Elementos y errores | Iguales | Iguales |
| Validar contra XSD | Con [MessageValidation](../03-mediacion.md) | La página de Edge lo presenta como uno de los enfoques de protección (también con MessageValidation) |
| `features.isPolicyHttpStatusEnabled` | Soporte de Google Cloud | Soporte de Edge (Public Cloud) o API de gestión (Private Cloud) |

## Antipatrones

- Sin límites declarados (todo queda en `-1`).
- Confiar en ella como protección XXE.
- No controlar el `Content-Type`.
- Devolver el 500 por defecto al cliente.

## Fuentes

- XMLThreatProtection policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/xml-threat-protection-policy> (consultada directamente, contenido completo, 2026-10-22).
- XML Threat Protection policy — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/xml-threat-protection-policy> (consultada directamente, 2026-10-22).
