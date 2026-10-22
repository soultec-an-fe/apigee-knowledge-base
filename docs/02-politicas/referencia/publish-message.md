---
id: politica-publish-message
titulo: PublishMessage — referencia completa
area: politicas
tags: [publishmessage, pubsub, eventos, asincrono, residencia-de-datos, standard]
aplica_a: [apigee-x, apigee-hybrid]
elemento_xml: PublishMessage
tipo_politica: standard
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/publish-message-policy
revisado: 2026-10-22
---

# PublishMessage — referencia completa

> [!NOTE]
> **Tipo:** Standard (se puede desplegar en cualquier tipo de entorno). **Elemento raíz:** `<PublishMessage>`.
> **Aplica a:** Apigee X y hybrid. **No existe en Apigee Edge.**

PublishMessage publica un mensaje en un **tópico de Google Cloud Pub/Sub** desde el flujo del proxy. El mensaje puede ser texto literal, una variable o una plantilla que combine ambos, o el contenido íntegro de un mensaje HTTP. Sirve para emitir eventos (por ejemplo, «pago iniciado») hacia sistemas que los consumen de forma asíncrona.

## Requisitos

- La **API de Pub/Sub** debe estar habilitada en el proyecto.
- La política no tiene elemento `<Authentication>`. El proxy se **despliega con una cuenta de servicio** (autenticación de Google), y Apigee añade el token por debajo.
- Esa cuenta necesita el permiso `pubsub.topics.publish` sobre el tópico, por ejemplo con el rol `roles/pubsub.publisher`.
- La página también pide `roles/iam.serviceAccountTokenCreator` para generar el token de la cuenta del proxy. En hybrid es la cuenta de runtime la que suplanta a la del proxy (ver el error `PermissionDeniedError`).
- **Un solo tópico por política.** Para publicar en varios, usa varias políticas.

## Sintaxis completa

```xml
<PublishMessage name="PM-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <Source>{"evento":"pago.iniciado","id":"{pago.id}"}</Source>
  <Attributes>
    <Attribute name="tipo">pago.iniciado</Attribute>
    <Attribute name="canal">{request.header.x-canal:desconocido}</Attribute>
  </Attributes>
  <CloudPubSub>
    <Topic>projects/mi-proyecto/topics/eventos-pagos</Topic>
    <Endpoint>pubsub.us.rep.googleapis.com:443</Endpoint>
  </CloudPubSub>
  <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>
</PublishMessage>
```

## Elementos hijos

| Elemento | Obligatorio | Default | Resumen |
|---|---|---|---|
| `<Source>` | Uno de los dos | — | Contenido a publicar: literal, `{variable}` o plantilla (por ejemplo, un JSON con variables). |
| `<UseMessageAsSource>` | Uno de los dos | — | Nombre de un **mensaje** (`request`, `response`, `message`) cuyo contenido se publica tal cual. Úsalo para contenido binario que no se puede representar como cadena. |
| `<Attributes>/<Attribute name>` | No | — | Atributos del mensaje de Pub/Sub. Los nombres deben ser únicos y los valores son plantillas, con default `{var:defecto}`. |
| `<CloudPubSub>/<Topic>` | **Sí** | — | `projects/{proyecto}/topics/{tópico}`. Admite variables. Uno solo. |
| `<CloudPubSub>/<Endpoint>` | No | `pubsub.googleapis.com:443` | Endpoint **regional** para residencia de datos, por ejemplo `pubsub.us.rep.googleapis.com:443`. |
| `<IgnoreUnresolvedVariables>` | No | `false` | Con `true`, sigue aunque una variable no resuelva. Es distinto de `continueOnError`, que ignora **cualquier** error. |

> [!IMPORTANT]
> **Residencia de datos con VPC Service Controls:** en ese caso el endpoint regional tiene otra forma, `{ubicación}-pubsub.googleapis.com:443` (por ejemplo `us-pubsub.googleapis.com:443`), no `pubsub.{ubicación}.rep.googleapis.com:443`.

> [!NOTE]
> La sintaxis general de la página oficial trae un `<Attribute>` mal formado (`<Attribute> name=…>`). La forma correcta es la de los ejemplos: `<Attribute name="…">valor</Attribute>`.

## Variables de flujo

| Variable | Valor |
|---|---|
| `publishmessage.message.id` | `messageId` devuelto por Pub/Sub, de tipo cadena. **Solo existe si la publicación tuvo éxito**: leerla tras un fallo produce errores. |

## Errores

### En runtime

Todos devuelven `500`.

| Código | Causa |
|---|---|
| `steps.publishmessage.PermissionDeniedError` | La cuenta de runtime no puede suplantar a la del proxy, o la del proxy no puede publicar en el tópico. |
| `steps.publishmessage.ExecutionError` | Error inesperado al publicar; el detalle va en el mensaje. |
| `steps.publishmessage.MessageVariableNotMessageType` | `<UseMessageAsSource>` no resuelve o no es un mensaje. |

### Variables de fallo

`fault.name` y `publishmessage.{policy_name}.failed`.

> [!NOTE]
> El ejemplo de `fault.name` de la página oficial usa `"UnresolvedVariable"`, que no figura en la tabla de errores de runtime. Condiciona tus FaultRules por los tres códigos de la tabla.

## Ejemplos

### 1. Evento JSON tras una operación exitosa

```xml
<PublishMessage name="PM-Pago-Iniciado" continueOnError="true">
  <Source>{"evento":"pago.iniciado","pagoId":"{pago.id}","monto":"{pago.monto}","ts":"{system.timestamp}"}</Source>
  <Attributes>
    <Attribute name="content-type">application/json</Attribute>
    <Attribute name="tipo">pago.iniciado</Attribute>
  </Attributes>
  <CloudPubSub>
    <Topic>projects/{propertyset.eventos.proyecto}/topics/{propertyset.eventos.topico_pagos}</Topic>
  </CloudPubSub>
</PublishMessage>
```

- Proyecto y tópico salen de un [PropertySet](read-property-set.md), no del código.
- Pon la política con una condición sobre el estado de respuesta, para no publicar eventos de operaciones fallidas.

### 2. Reenviar el cuerpo binario de la petición

```xml
<PublishMessage name="PM-Archivo">
  <UseMessageAsSource>request</UseMessageAsSource>
  <Attributes>
    <Attribute name="nombre">{request.header.x-nombre-archivo:sin-nombre}</Attribute>
  </Attributes>
  <CloudPubSub>
    <Topic>projects/mi-proyecto/topics/archivos-recibidos</Topic>
  </CloudPubSub>
</PublishMessage>
```

## Diferencias en Apigee Edge

No existe en Edge.

## Antipatrones

- **Tomar el proyecto o el tópico de la petición del cliente** (`{request.queryparam.topic}`, como hacen algunos ejemplos oficiales con fines ilustrativos). Un cliente podría publicar en tópicos arbitrarios a los que la cuenta de servicio tenga acceso.
- **Leer `publishmessage.message.id` sin verificar que la publicación tuvo éxito.**
- **Publicar datos sensibles en claro.** Pub/Sub retiene los mensajes y los entrega a todos los suscriptores.
- **`IgnoreUnresolvedVariables=true` con plantillas JSON.** Una variable vacía puede producir un evento incompleto que rompa a los consumidores.

## Fuentes

- PublishMessage policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/publish-message-policy> (consultada directamente, contenido completo, 2026-10-22).
