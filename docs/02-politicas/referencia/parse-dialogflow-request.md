---
id: politica-parse-dialogflow-request
titulo: ParseDialogflowRequest — referencia completa
area: politicas
tags: [parsedialogflowrequest, dialogflow, cx, webhook, ccai, extensible]
aplica_a: [apigee-x, apigee-hybrid]
elemento_xml: ParseDialogflowRequest
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/parse-dialogflow-request-policy
revisado: 2026-10-22
---

# ParseDialogflowRequest — referencia completa

> [!NOTE]
> **Tipo:** Extensible. **Elemento raíz:** `<ParseDialogflowRequest>`.
> **Aplica a:** Apigee X y hybrid. **No existe en Apigee Edge.** Solo **Dialogflow CX**.

Con Dialogflow CX (o Contact Center AI), un agente conversacional llama a un **webhook** para obtener datos (estado de un reclamo, saldo…). Si el webhook es un proxy de Apigee, ParseDialogflowRequest lee el `WebhookRequest` del agente y deja sus datos en variables, para que el resto del proxy llame a los backends sin conocer el formato de Dialogflow. Su pareja, [SetDialogflowResponse](set-dialogflow-response.md), construye el `WebhookResponse`.

Para usarla, la URL de *fulfillment* del agente debe apuntar al ProxyEndpoint, que debe ser **accesible públicamente** (requisito de Dialogflow para webhooks).

Solo analiza tres partes del `WebhookRequest`: `fulfillmentInfo.tag`, `sentimentAnalysisResult` y `sessionInfo`.

## Sintaxis completa

```xml
<ParseDialogflowRequest name="PDR-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <VariablePrefix>reclamos</VariablePrefix>
  <DialogflowVersion>CX</DialogflowVersion>
</ParseDialogflowRequest>
```

## Elementos hijos

| Elemento | Obligatorio | Default | Resumen |
|---|---|---|---|
| `<VariablePrefix>` | No | — | Se añade **después** de `google.dialogflow.`: `google.dialogflow.{prefijo}.…`. |
| `<DialogflowVersion>` | No | `CX` | Único valor soportado: `CX`. Otro → `UnsupportedOperation` al desplegar. |

## Variables de flujo

Con `<VariablePrefix>reclamos</VariablePrefix>`:

| Variable | Origen en el `WebhookRequest` |
|---|---|
| `google.dialogflow.reclamos.fulfillment.tag` | `fulfillmentInfo.tag`: qué pide el agente (p. ej. `consultar-reclamo`). |
| `google.dialogflow.reclamos.session.id` | Último segmento de `sessionInfo.session`. |
| `google.dialogflow.reclamos.session.project.id` | Proyecto, extraído de `sessionInfo.session`. |
| `google.dialogflow.reclamos.session.agent.id` | Agente, extraído de `sessionInfo.session`. |
| `google.dialogflow.reclamos.session.parameters.{p}` | Cada parámetro de la sesión (p. ej. `claimId`). |
| `google.dialogflow.reclamos.sentimentAnalysisResultScore` | Puntaje de sentimiento. |
| `google.dialogflow.reclamos.sentimentAnalysisResultMagnitude` | Magnitud de sentimiento. |

## Errores

### En runtime

| Código | HTTP | Causa |
|---|---|---|
| `steps.parsedialogflowrequest.InvalidSessionInfo` | 500 | `sessionInfo.session` con un formato no válido. |
| `steps.parsedialogflowrequest.MalformedInput` | 500 | JSON inválido o mal formado. |

### Al desplegar

| Error | Causa |
|---|---|
| `UnsupportedOperation` | `<DialogflowVersion>` distinto de `CX`. |

### Variables de fallo

`fault.name` y `ParseDialogflowRequest.{name}.failed`.

## Ejemplo: enrutar por *tag*

```xml
<Flows>
  <Flow name="consultar-reclamo">
    <Condition>google.dialogflow.reclamos.fulfillment.tag = "consultar-reclamo"</Condition>
    <Request>
      <Step><Name>SC-Estado-Reclamo</Name></Step>
    </Request>
  </Flow>
</Flows>
```

> [!IMPORTANT]
> Que el endpoint sea público no significa que deba ser abierto: autentica las llamadas del agente (Dialogflow CX admite autenticación en webhooks, por ejemplo con tokens de Google o cabeceras propias) y valida en el proxy que vienen de **tu** proyecto y agente (`session.project.id`, `session.agent.id`). Esta recomendación no viene de la página de la política.

## Diferencias en Apigee Edge

No existe en Edge.

## Fuentes

- ParseDialogflowRequest policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/parse-dialogflow-request-policy> (consultada directamente, contenido completo, 2026-10-22).
