---
id: politica-xsl-transform
titulo: XSLTransform — referencia completa
area: politicas
tags: [xsltransform, xsl, xslt, saxon, xml, soap, transformacion, mediacion, extensible]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
elemento_xml: XSL
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/xsl-transform-policy
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/xsl-transform-policy
revisado: 2026-10-22
---

# XSLTransform — referencia completa

> [!NOTE]
> **Tipo:** Extensible. **Elemento raíz:** `<XSL>` (la política se llama XSLTransform, pero el elemento XML es `<XSL>`).
> **Aplica a:** Apigee X, hybrid y Edge, con el mismo comportamiento.

XSLTransform aplica una hoja de estilos **XSLT** a un mensaje XML y produce otro XML, HTML o texto. Se usa para adaptar formatos XML entre sistemas (por ejemplo, el XML genérico de [JSONToXML](json-xml.md) al esquema exacto de un servicio SOAP).

| Aspecto | Detalle |
|---|---|
| Procesador | **Saxon**, con XSLT **1.0 y 2.0** |
| No soportado | `<xsl:include>` y `<xsl:import>`: cada hoja debe ser autocontenida |
| Entidades externas | No soporta leer, cargar ni manipular entidades externas XML (XXE) |
| `Content-Type` | Solo transforma si el mensaje es XML (`text/xml`, `application/xml`); si no, se salta |

## Sintaxis completa

```xml
<XSL name="XSL-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <Source>request</Source>
  <ResourceURL>xsl://adaptar-pago.xsl</ResourceURL>
  <Parameters ignoreUnresolvedVariables="false">
    <Parameter name="canal" value="api"/>
    <Parameter name="usuario" ref="flujo.usuario_autenticado"/>
  </Parameters>
  <OutputVariable>flujo.xml_transformado</OutputVariable>
</XSL>
```

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno; caracteres permitidos `A-Z0-9._\-$ %`. |
| `continueOnError` | No | `false` | Con `true`, un fallo de transformación no corta el flujo. |
| `enabled` | No | `true` | Con `false` no se ejecuta. |
| `async` | No | `false` | **Obsoleto.** |

## Elementos hijos

| Elemento | Obligatorio | Resumen |
|---|---|---|
| `<ResourceURL>` | **Sí** | Hoja de estilos guardada en el proxy, en `/resources/xsl`: `xsl://archivo.xsl`. Vacío → `XSLEmptyResourceUrl`; otro tipo de recurso → `XSLInvalidResourceType`. |
| `<Source>` | No (default `message`) | Mensaje a transformar. Si el XML está en la respuesta, pon `response` y adjunta la política en el flujo de respuesta. |
| `<OutputVariable>` | No | Variable **no mensaje** donde guardar el resultado. Sin ella, el resultado **sustituye el cuerpo** del mensaje. No puede ser `message`, `request` ni `response`. |
| `<Parameters ignoreUnresolvedVariables>` | No | Valores para los `<xsl:param>` de la hoja. Default `false`: una variable sin resolver es un error. |
| `<Parameters>/<Parameter name ref value>` | — | `name` coincide con el `<xsl:param name>` de la hoja; el valor sale de `ref` (variable) **o** de `value` (literal), no de ambos. |

En la hoja, cada parámetro se declara con un valor por defecto, por ejemplo `<xsl:param name="canal" select="''"/>`.

## Variables de flujo

No publica variables de éxito, aparte de `<OutputVariable>`.

## Errores

### En runtime

| Código | HTTP | Causa |
|---|---|---|
| `steps.xsl.XSLSourceMessageNotAvailable` | 500 | `<Source>` fuera de alcance o inexistente. |
| `steps.xsl.XSLEvaluationFailed` | 500 | XML de entrada ausente o mal formado, o la hoja falla al aplicarse. El mensaje de error indica la causa. |

### Al desplegar

| Error | Causa |
|---|---|
| `XSLEmptyResourceUrl` | `<ResourceURL>` vacío. |
| `XSLInvalidResourceType` | El recurso no es de tipo `xsl`. |

## Ejemplo: adaptar el XML genérico al sobre SOAP del backend

```xml
<XSL name="XSL-Sobre-Soap">
  <Source>request</Source>
  <ResourceURL>xsl://sobre-soap-pagos.xsl</ResourceURL>
  <Parameters>
    <Parameter name="canal" value="API"/>
    <Parameter name="idPeticion" ref="messageid"/>
  </Parameters>
</XSL>
```

```xml
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
                xmlns:pag="urn:banco:pagos">
  <xsl:param name="canal" select="''"/>
  <xsl:param name="idPeticion" select="''"/>
  <xsl:template match="/SolicitudPago">
    <soap:Envelope>
      <soap:Body>
        <pag:RegistrarPago canal="{$canal}" id="{$idPeticion}">
          <pag:Monto><xsl:value-of select="monto"/></pag:Monto>
          <pag:Moneda><xsl:value-of select="moneda"/></pag:Moneda>
        </pag:RegistrarPago>
      </soap:Body>
    </soap:Envelope>
  </xsl:template>
</xsl:stylesheet>
```

## Diferencias en Apigee Edge

Sin diferencias funcionales documentadas (también Saxon, XSLT 1.0 y 2.0, sin `include` ni `import`).

## Antipatrones

- Hojas que dependen de `<xsl:include>` o `<xsl:import>` (no funcionan).
- Transformaciones muy pesadas en cada petición: considera si el backend o una capa de integración debería hacerlas.
- Parámetros con datos del cliente que se insertan sin escapar en el resultado.

## Fuentes

- XSLTransform policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/xsl-transform-policy> (consultada directamente, contenido completo, 2026-10-22).
- XSL Transform policy — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/xsl-transform-policy> (consultada directamente, 2026-10-22).
