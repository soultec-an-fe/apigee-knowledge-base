---
id: politica-set-dialogflow-response
titulo: SetDialogflowResponse — referencia completa
area: politicas
tags: [setdialogflowresponse, dialogflow, cx, webhook, ccai, extensible]
aplica_a: [apigee-x, apigee-hybrid]
elemento_xml: SetDialogflowResponse
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/set-dialogflow-response-policy
revisado: 2026-10-22
---

# SetDialogflowResponse — referencia completa

> [!NOTE]
> **Tipo:** Extensible. **Elemento raíz:** `<SetDialogflowResponse>`.
> **Aplica a:** Apigee X y hybrid. **No existe en Apigee Edge.** Solo **Dialogflow CX**.

SetDialogflowResponse toma la respuesta de tus backends y construye el **`WebhookResponse`** que espera un agente de Dialogflow CX: frases que el agente dirá al usuario (`fulfillmentResponse.messages`) y parámetros de sesión (`sessionInfo.parameters`). Es la pareja de [ParseDialogflowRequest](parse-dialogflow-request.md).

## Sintaxis completa

```xml
<SetDialogflowResponse name="SDR-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <Source>respuestaReclamo</Source>
  <DialogflowVersion>CX</DialogflowVersion>
  <NaturalLanguageResponse>
    <MergeBehavior>APPEND</MergeBehavior>
    <Phrases>
      <Phrase>
        <JSONPath>$.mensaje</JSONPath>
      </Phrase>
      <Phrase>
        <Value>¿Hay algo más en lo que pueda ayudarte?</Value>
      </Phrase>
    </Phrases>
  </NaturalLanguageResponse>
  <Parameters>
    <Parameter name="estadoReclamo">
      <JSONPath>$.estado</JSONPath>
    </Parameter>
    <Parameter name="tiempoRespuesta">
      <Header name="X-Tiempo"/>
    </Parameter>
    <Parameter name="canal">
      <Ref>flujo.canal</Ref>
    </Parameter>
  </Parameters>
  <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>
</SetDialogflowResponse>
```

## Elementos hijos

| Elemento | Obligatorio | Default | Resumen |
|---|---|---|---|
| `<Source>` | No | `message` | Mensaje del que leer (p. ej. la respuesta de un ServiceCallout). Si no es un mensaje → error. |
| `<DialogflowVersion>` | No | `CX` | Único valor: `CX`. |
| `<NaturalLanguageResponse>` | No | — | Lo que dirá el agente. |
| `.../<MergeBehavior>` | No | `APPEND` | `APPEND` añade a los mensajes pendientes; `REPLACE` los sustituye. |
| `.../<Phrases>/<Phrase>` | — | — | Una frase, en orden. Su valor sale de **uno** de `<Header name>`, `<JSONPath>`, `<Ref>` o `<Value>`. |
| `<Parameters>/<Parameter name>` | — | — | Un parámetro de sesión, con el valor de **uno** de `<Header name>`, `<JSONPath>`, `<Ref>` o `<Value>`. |
| `<IgnoreUnresolvedVariables>` | No | **`true`** | Seguir aunque algo no resuelva. |

| Fuente de valor | Lee |
|---|---|
| `<Header name>` | Una cabecera del mensaje de `<Source>`. |
| `<JSONPath>` | Un campo del cuerpo JSON. |
| `<Ref>` | Una variable de flujo. |
| `<Value>` | Texto fijo. |

> [!WARNING]
> Con el default `<IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>`, un campo que falta en la respuesta del backend produce una frase vacía, y el agente se queda callado o responde a medias. Ponlo en `false` y gestiona el error con una respuesta de respaldo.

## Errores

### En runtime

Todos `500`: `steps.setdialogflowresponse.ExecutionFailed`, `InvalidSourceType`, `MalformedInput`, `SourceMessageNotAvailable`, `UnresolvedHeader` (cabecera inexistente), `UnresolvedJSONPath` (ruta inexistente) y `UnresolvedVariable`.

### Al desplegar

| Error | Causa |
|---|---|
| `UnsupportedOperation` | `<DialogflowVersion>` distinto de `CX`. |

## Ejemplo de `WebhookResponse` generado

```json
{
  "fulfillmentResponse": {
    "mergeBehavior": "APPEND",
    "messages": [{"text": {"text": ["Tu reclamo está en revisión", "¿Hay algo más en lo que pueda ayudarte?"]}}]
  },
  "sessionInfo": {"parameters": {"estadoReclamo": "EN_REVISION", "canal": "voz"}}
}
```

## Diferencias en Apigee Edge

No existe en Edge.

## Antipatrones

- Dejar `<IgnoreUnresolvedVariables>` en `true` sin una frase de respaldo.
- Poner en `<Value>` o en parámetros datos sensibles que el agente luego repetirá en voz alta o registrará.

## Fuentes

- SetDialogflowResponse policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/set-dialogflow-response-policy> (consultada directamente, contenido completo, 2026-10-22).
