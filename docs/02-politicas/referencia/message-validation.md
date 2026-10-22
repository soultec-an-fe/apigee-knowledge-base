---
id: politica-message-validation
titulo: MessageValidation (SOAPMessageValidation) — referencia completa
area: politicas
tags: [messagevalidation, soapmessagevalidation, xsd, wsdl, soap, validacion, xml, json, standard]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
elemento_xml: MessageValidation
tipo_politica: standard
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/message-validation-policy
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/message-validation-policy
revisado: 2026-10-22
---

# MessageValidation (SOAPMessageValidation) — referencia completa

> [!NOTE]
> **Tipo:** Standard. **Elemento raíz:** `<MessageValidation>`; en la UI aparece como **SOAPMessageValidation**.
> **Aplica a:** Apigee X, hybrid y Edge.

MessageValidation valida mensajes contra un **contrato XML**, con tres modos según cómo se configure:

| Modo | Configuración | Comprueba |
|---|---|---|
| XSD | `<ResourceURL>xsd://…</ResourceURL>`, sin `<SOAPMessage>` ni `<Element>` | Que el XML cumpla el esquema. |
| WSDL / SOAP | `<ResourceURL>wsdl://…</ResourceURL>` + `<SOAPMessage version>` + `<Element>` | Que el sobre SOAP y el elemento del `Body` cumplan el WSDL. |
| Buena formación | Sin `<ResourceURL>`, `<SOAPMessage>` ni `<Element>` | Que el JSON (`application/json`) o el XML (`application/xml`) estén **bien formados**: una raíz, sin caracteres ilegales, etiquetas bien anidadas y cerradas. |

Para contratos **OpenAPI** (REST/JSON) usa [OASValidation](oas-validation.md).

## Sintaxis completa

```xml
<MessageValidation name="MV-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <Source>request</Source>
  <ResourceURL>wsdl://servicio-pagos.wsdl</ResourceURL>
  <SOAPMessage version="1.1"/>
  <Element namespace="urn:banco:pagos">RegistrarPago</Element>
</MessageValidation>
```

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno. |
| `continueOnError` | No | `false` | Con `true`, un mensaje inválido pasa. |
| `enabled` | No | `true` | Con `false` no se ejecuta. |

## Elementos hijos

| Elemento | Obligatorio | Default | Resumen |
|---|---|---|---|
| `<Source>` | No | `message` | Mensaje a validar: `request`, `response` o un mensaje propio creado antes. |
| `<ResourceURL>` | No | — | `xsd://archivo.xsd` o `wsdl://archivo.wsdl`, **dentro del proxy**. No admite URLs HTTP/HTTPS externas. |
| `<SOAPMessage version>` | No | — | `1.1`, `1.2` o `1.1/1.2`. |
| `<Element namespace>` | No | `namespace` = `http://sample.com` | Primer hijo del `Body` SOAP a validar. Se pueden poner varios `<Element>`. |

### XSD con varios archivos

Si el esquema incluye o importa otros, el `schemaLocation` debe usar el prefijo `xsd://` y apuntar a recursos del propio proxy:

```xml
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema" elementFormDefault="qualified">
  <xs:include schemaLocation="xsd://comun.xsd"/>
  <xs:include schemaLocation="xsd://pago.xsd"/>
</xs:schema>
```

No se pueden incluir XSD externos.

### WSDL

- El WSDL debe definir **al menos un esquema**; si no, la política falla.
- Profundidad máxima de importaciones anidadas: **10**.
- La página de Edge aclara que solo se validan mensajes de estilo **document**; el estilo **RPC** no está soportado. La de X no lo menciona.

> [!IMPORTANT]
> Como el resto de políticas de contenido, depende del `Content-Type`: el modo de buena formación solo comprueba JSON con `application/json` y XML con `application/xml`. Rechaza antes los tipos de contenido que no aceptas.

## Variables de flujo

No publica variables de éxito.

## Errores

### En runtime

Todos `500`:

| Código | Causa |
|---|---|
| `steps.messagevalidation.Failed` | El mensaje no cumple el XSD/WSDL, o el JSON/XML está mal formado. |
| `steps.messagevalidation.SourceMessageNotAvailable` | `<Source>` fuera de alcance o nulo. |
| `steps.messagevalidation.NonMessageVariable` | `<Source>` no es de tipo mensaje. |

Un mensaje inválido **del cliente** devuelve 500: tradúcelo a 400 en una FaultRule.

### Al desplegar

| Error | Causa |
|---|---|
| `InvalidResourceType` | Tipo de recurso no soportado en `<ResourceURL>`. |
| `ResourceCompileFailed` | El XSD o WSDL tiene errores y no compila. |
| `RootElementNameUnspecified` | `<Element>` vacío. |
| `InvalidRootElementName` | `<Element>` con un nombre XML inválido. |

## Ejemplos

### 1. Validar un XML contra XSD

```xml
<MessageValidation name="MV-Xsd-Pedido">
  <Source>request</Source>
  <ResourceURL>xsd://pedido.xsd</ResourceURL>
</MessageValidation>
```

### 2. Comprobar solo buena formación del JSON

```xml
<MessageValidation name="MV-Json-Bien-Formado">
  <Source>request</Source>
</MessageValidation>
```

### 3. 400 en lugar de 500

```xml
<FaultRule name="fr-mensaje-invalido">
  <Condition>fault.name = "Failed"</Condition>
  <Step>
    <Name>AM-Error-400-Contrato</Name>
  </Step>
</FaultRule>
```

## Diferencias en Apigee Edge

| Aspecto | Apigee X / hybrid | Apigee Edge |
|---|---|---|
| Nombre en la UI | SOAPMessageValidation | "SOAP Message Validation" |
| Estilo RPC del WSDL | No mencionado | No soportado (solo document) |
| Resto | Igual | Igual |

## Antipatrones

- Validar JSON REST con esta política en lugar de OASValidation.
- XSD que importan esquemas externos (no funciona).
- Devolver el 500 por defecto al cliente.

## Fuentes

- SOAPMessageValidation policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/message-validation-policy> (consultada directamente, contenido completo, 2026-10-22).
- Message Validation policy — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/message-validation-policy> (consultada directamente, 2026-10-22).
