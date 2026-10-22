---
id: politica-extension-callout
titulo: ExtensionCallout (ConnectorCallout) — referencia completa, solo Edge
area: politicas
tags: [extensioncallout, connectorcallout, extensions, edge, google-cloud]
aplica_a: [apigee-edge]
elemento_xml: ConnectorCallout
tipo_politica: extension
fuente: https://docs.apigee.com/api-platform/reference/policies/extension-callout-policy
revisado: 2026-10-22
---

# ExtensionCallout (ConnectorCallout) — referencia completa, solo Edge

> [!NOTE]
> **Solo Apigee Edge.** **Elemento raíz:** `<ConnectorCallout>`, no `<ExtensionCallout>`: la política se llama ExtensionCallout en la UI, pero el XML usa otro nombre.
> Las *Apigee Extensions* están disponibles en la UI de Edge para clientes de Google Cloud Apigee con plan de soporte **Enterprise**. En Apigee X no existen. Allí se usan ServiceCallout o ExternalCallout con autenticación de Google, o [PublishMessage](publish-message.md) y [MessageLogging](message-logging.md) con `<CloudLogging>`.

ExtensionCallout invoca una **extensión**: un conector ya configurado y desplegado en el entorno hacia un recurso externo, como Cloud Storage, Cloud Logging, Firestore, Speech-to-Text o cualquier servicio HTTP o HTTPS. La extensión guarda la configuración y las credenciales; la política solo indica qué **acción** ejecutar y con qué **entrada**.

**Requisito previo:** la extensión debe estar **añadida, configurada y desplegada** en el entorno, a partir de un paquete instalado en la organización.

## Sintaxis completa

```xml
<ConnectorCallout name="EXC-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <Connector>logging-produccion</Connector>
  <Action>log</Action>
  <Input><![CDATA[{
    "logName": "apigee-auditoria",
    "metadata": {my.log.metadata},
    "message": "{client.ip}"
  }]]></Input>
  <Output parsed="true">salidaExtension</Output>
</ConnectorCallout>
```

## Elementos hijos

| Elemento | Obligatorio | Resumen |
|---|---|---|
| `<Connector>` | **Sí** | Nombre de la extensión **configurada** en el entorno, no el del paquete. Dos extensiones del mismo paquete pueden tener configuraciones distintas. |
| `<Action>` | **Sí** | Acción expuesta por la extensión, como `log` en la de Cloud Logging. Cada extensión documenta las suyas. |
| `<Input>` | Según la acción | JSON con los argumentos de la acción. Es una **plantilla de mensaje**: `{variable}` se sustituye en runtime. |
| `<Output parsed>` | No | Variable donde guardar la respuesta. Con `parsed="true"` (default), el JSON se convierte en variables (`{salida.messageId}`); con `false`, queda el JSON crudo. |

> [!TIP]
> **Comillas en `<Input>`:** `"message": "{client.ip}"` produce una cadena JSON. `"metadata": {my.log.metadata}`, sin comillas, inserta el valor tal cual, y sirve cuando la variable ya contiene un objeto JSON. Google recomienda envolver el JSON en `<![CDATA[ … ]]>` para evitar errores de análisis XML.

## Uso en el PostClientFlow

Se puede invocar desde el PostClientFlow, pero **solo con la extensión de Google Cloud Logging, versión 1.3.7 o posterior**.

- La organización necesita `features.allowExtensionsInPostClientFlow = true`. Viene activado por defecto en Edge Cloud; en Private Cloud se activa con la API *Update organization properties*.
- Se aplican las mismas restricciones que a MessageLogging en ese flujo.
- Sin el flag, el despliegue falla con `AllowExtensionsInPostClientFlow`.

## Variables de flujo

No define variables propias, aparte de la de `<Output>`.

## Errores

### En runtime

| Error | HTTP | Causa |
|---|---|---|
| `ExecutionFailed` | 500 | La extensión respondió con un error. |

### Al desplegar

| Error | Causa |
|---|---|
| `InvalidConnectorInstance` | `<Connector>` vacío. |
| `ConnectorInstanceDoesNotExists` | La extensión no existe en el entorno. |
| `InvalidAction` | `<Action>` ausente o vacío. |
| `AllowExtensionsInPostClientFlow` | ExtensionCallout en el PostClientFlow sin el flag de organización. |

## Equivalencias en Apigee X

| En Edge, con la extensión de… | En X |
|---|---|
| Cloud Logging | [MessageLogging](message-logging.md) con `<CloudLogging>` |
| Pub/Sub | [PublishMessage](publish-message.md) |
| Otros servicios de Google Cloud | [ServiceCallout](service-callout.md) con `<Authentication>` (token de Google) |
| Lógica propia que modifica el contexto | [ExternalCallout](external-callout.md) |

Esta tabla es una síntesis de este repositorio, no una guía oficial de migración.

## Fuentes

- ExtensionCallout policy — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/extension-callout-policy> (consultada directamente, contenido completo, 2026-10-22).
