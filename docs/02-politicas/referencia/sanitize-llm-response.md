---
id: politica-sanitize-llm-response
titulo: SanitizeModelResponse — referencia completa
area: politicas
tags: [sanitizemodelresponse, model-armor, llm, respuesta, sdp, rai, ia, extensible]
aplica_a: [apigee-x, apigee-hybrid]
elemento_xml: SanitizeModelResponse
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/sanitize-llm-response-policy
revisado: 2026-10-22
---

# SanitizeModelResponse — referencia completa

> [!NOTE]
> **Tipo:** Extensible. **Elemento raíz:** `<SanitizeModelResponse>` (la URL de la página dice `sanitize-llm-response`).
> **Aplica a:** Apigee X y Apigee hybrid **1.15.1 o superior**. **No existe en Apigee Edge.**

SanitizeModelResponse envía la **respuesta del modelo** a Model Armor **antes** de devolverla al cliente, y la bloquea si la plantilla detecta contenido dañino u ofensivo, datos sensibles o URIs maliciosas. Es la mitad de salida de [SanitizeUserPrompt](sanitize-user-prompt.md): mismos requisitos (API de Model Armor, plantilla, `roles/modelarmor.user` y `roles/modelarmor.viewer`), mismas variables y mismo modelo de decisión. Aquí solo se documenta lo que cambia.

## Sintaxis completa

```xml
<SanitizeModelResponse name="SMR-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>
  <ModelArmor>
    <TemplateName>projects/{organization.name}/locations/{system.region.name}/templates/plantilla-salida</TemplateName>
  </ModelArmor>
  <UserPromptSource>{jsonPath('$.contents[-1].parts[-1].text',request.content,true)}</UserPromptSource>
  <LLMResponseSource>{jsonPath('$.candidates[-1].content.parts',response.content,true)}</LLMResponseSource>
  <FunctionCallSource>{jsonPath('$.candidates[-1].content.parts[-1].functionCall.args',response.content,true)}</FunctionCallSource>
</SanitizeModelResponse>
```

Se adjunta en el **flujo de respuesta**.

## Atributos del elemento raíz

Los mismos que [SanitizeUserPrompt](sanitize-user-prompt.md#atributos-del-elemento-raíz).

## Elementos hijos

| Elemento | Obligatorio | Default | Resumen |
|---|---|---|---|
| `<ModelArmor>/<TemplateName>` | **Sí** | — | Plantilla de Model Armor. Puede ser distinta de la de entrada (p. ej. más estricta con datos personales). |
| `<LLMResponseSource>` | Sí (según la tabla) | `{jsonPath('$.candidates[-1].content.parts',response.content,true)}` | Texto de la respuesta del modelo a evaluar. |
| `<UserPromptSource>` | Sí (según la tabla) | `{jsonPath('$.contents[-1].parts[-1].text',request.content,true)}` | Prompt original, como contexto para la evaluación. |
| `<FunctionCallSource>` | No | `{jsonPath('$.candidates[-1].content.parts[-1].functionCall.args',response.content,true)}` | Respaldo cuando el modelo devuelve una **llamada a función** en lugar de texto: se evalúan sus argumentos. |
| `<IgnoreUnresolvedVariables>` | No | — | Seguir o fallar si algo no resuelve. |

> [!NOTE]
> **Discrepancias de la página.** La tabla dice que `<TemplateName>` cuelga directamente de `<SanitizeModelResponse>`, pero la sintaxis y los ejemplos lo ponen dentro de `<ModelArmor>` (usa esto último). Marca `<UserPromptSource>` y `<LLMResponseSource>` como obligatorios aunque tienen valor por defecto. Y el ejemplo de `<LLMResponseSource>` copia una ruta de petición (`$.input.prompt.text` sobre `request.content`).

> [!TIP]
> Evaluar `<FunctionCallSource>` importa en agentes: un modelo manipulado puede intentar llamar a una herramienta con argumentos dañinos (exfiltrar datos, borrar registros). Bloquearlo aquí evita que tu orquestador ejecute esa llamada.

### Streaming

La página no menciona respuestas en streaming (SSE). La política necesita la respuesta completa en `response.content`; con `EventFlow` no se documenta su comportamiento.

## Variables de flujo

Las mismas que [SanitizeUserPrompt](sanitize-user-prompt.md#variables-de-flujo), con prefijo `SanitizeModelResponse.{name}.`. `modelResponse` contiene el texto evaluado y `sanitizeOperation` vale `SANITIZE_MODEL_RESPONSE`.

## Errores

### En runtime

| Código | HTTP | Causa |
|---|---|---|
| `steps.sanitize.model.response.FilterMatched` | 400 | La respuesta no pasó la plantilla. |
| `steps.sanitize.model.response.FailedToExtractLLMResponse` | 500 | No se pudo extraer la respuesta con el default. |
| `steps.sanitize.model.response.FailedToExtractUserPrompt` | 500 | No se pudo extraer el prompt. |
| `steps.sanitize.model.response.SanitizationResponseParsingFailed` | 500 | No se pudo leer la respuesta de Model Armor. |
| `steps.sanitize.model.response.ModelArmorTemplateNameExtractionFailed` | 500 | No se resolvió la plantilla. |
| `steps.sanitize.model.response.AuthenticationFailure` | 500 | Sin permisos sobre Model Armor. |
| `steps.sanitize.model.response.ModelArmorAPIFailed`, `ModelArmorCalloutError` | 500 | Falló la API o la llamada. |
| `steps.sanitize.model.response.ServiceUnavailable` | 500 | Model Armor no disponible. |
| `steps.sanitize.model.response.InternalError` | 500 | Error interno. |

> [!NOTE]
> Aquí los errores de Model Armor llevan el prefijo `steps.sanitize.model.response.`, mientras que en SanitizeUserPrompt son `steps.sanitize.modelarmor.`. Captura por `fault.name`, que es igual en las dos.

Un `FilterMatched` en la **respuesta** devuelve 400 al cliente, aunque el problema no sea de su petición. Considera sustituirlo por una respuesta neutra ("No puedo ayudarte con eso") con un 200 o un 422, según tu contrato.

### Variables de fallo

`fault.name` y `SanitizeModelResponse.{name}.failed`.

## Ejemplo: respuesta neutra cuando se bloquea la salida

```xml
<SanitizeModelResponse name="SMR-Salida" continueOnError="true">
  <ModelArmor>
    <TemplateName>projects/{organization.name}/locations/{system.region.name}/templates/salida</TemplateName>
  </ModelArmor>
</SanitizeModelResponse>
```

```xml
<Step>
  <Name>AM-Respuesta-Neutra</Name>
  <Condition>SanitizeModelResponse.SMR-Salida.matchesFound = true or SanitizeModelResponse.SMR-Salida.invocationResult != "SUCCESS"</Condition>
</Step>
```

`AM-Respuesta-Neutra` reemplaza el cuerpo por un mensaje genérico con el formato que espera el cliente.

## Diferencias en Apigee Edge

No existe en Edge.

## Antipatrones

- Revisar solo la entrada y no la salida.
- No evaluar las llamadas a función en agentes.
- Cachear (con [SemanticCachePopulate](semantic-cache-populate.md)) respuestas **antes** de sanearlas.

## Fuentes

- SanitizeModelResponse policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/sanitize-llm-response-policy> (consultada directamente, contenido completo, 2026-10-22).
