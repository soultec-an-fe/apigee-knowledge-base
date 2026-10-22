---
id: politica-sanitize-user-prompt
titulo: SanitizeUserPrompt — referencia completa
area: politicas
tags: [sanitizeuserprompt, model-armor, llm, prompt-injection, jailbreak, sdp, ia, extensible]
aplica_a: [apigee-x, apigee-hybrid]
elemento_xml: SanitizeUserPrompt
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/sanitize-user-prompt-policy
revisado: 2026-10-22
---

# SanitizeUserPrompt — referencia completa

> [!NOTE]
> **Tipo:** Extensible. **Elemento raíz:** `<SanitizeUserPrompt>`.
> **Aplica a:** Apigee X y Apigee hybrid **1.15.1 o superior**. **No existe en Apigee Edge.**

SanitizeUserPrompt envía el **prompt del usuario** a **Model Armor** (servicio de seguridad para IA de Google Cloud) **antes** de que llegue al modelo, y lo rechaza si la plantilla de Model Armor detecta contenido dañino: inyección de prompts y *jailbreak*, datos sensibles (SDP, Sensitive Data Protection), contenido de IA responsable (RAI), CSAM o URIs maliciosas. Trabaja en pareja con [SanitizeModelResponse](sanitize-llm-response.md), que revisa la respuesta.

Los filtros y sus umbrales **no** se configuran en la política sino en la **plantilla de Model Armor**; la política solo dice qué plantilla usar y qué texto enviar. Visión de conjunto en [Políticas de IA](../05-politicas-ai.md#model-armor-sanitizeuserprompt-y-sanitizemodelresponse).

## Requisitos previos

| Requisito | Detalle |
|---|---|
| API de Model Armor | Habilitada en el proyecto. |
| Plantilla de Model Armor | Creada **antes** que la política, con los filtros deseados. |
| Endpoint | Configurado el endpoint de la API de Model Armor. |
| Cuenta de servicio del proxy | `roles/modelarmor.user` y `roles/modelarmor.viewer`. |
| Política compañera | Google pide crear la SanitizeModelResponse **antes de desplegar** esta. |

Si el entorno tiene **forward proxy**, las llamadas a Model Armor pasan por él sin configuración adicional (Apigee y hybrid 1.16.10+ o 1.17.0+).

## Sintaxis completa

```xml
<SanitizeUserPrompt name="SUP-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>
  <ModelArmor>
    <TemplateName>projects/{organization.name}/locations/{system.region.name}/templates/plantilla-entrada</TemplateName>
  </ModelArmor>
  <UserPromptSource>{jsonPath('$.contents[-1].parts[-1].text',request.content,true)}</UserPromptSource>
  <FunctionResponseSource>{jsonPath('$.contents[-1].parts[-1].functionResponse.response',request.content,true)}</FunctionResponseSource>
</SanitizeUserPrompt>
```

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno; da nombre a `SanitizeUserPrompt.{name}.*`. |
| `continueOnError` | No | `false` | Con `true`, una detección **no bloquea**: la petición sigue y tú decides con las variables. Ver ejemplo 2. |
| `enabled` | No | `true` | Con `false` no se ejecuta. |
| `async` | No | `false` | **Obsoleto.** |

## Elementos hijos

| Elemento | Obligatorio | Default | Resumen |
|---|---|---|---|
| `<ModelArmor>/<TemplateName>` | **Sí** | — | Plantilla de Model Armor: `projects/{p}/locations/{l}/templates/{t}`. Admite variables (`{organization.name}`, `{system.region.name}`). |
| `<UserPromptSource>` | No | `{jsonPath('$.contents[-1].parts[-1].text',request.content,true)}` | Plantilla que extrae el texto del prompt. Solo valores de texto. |
| `<FunctionResponseSource>` | No | `{jsonPath('$.contents[-1].parts[-1].functionResponse.response',request.content,true)}` | Respaldo cuando `<UserPromptSource>` sale vacío: en turnos de *function calling*, el último contenido es la respuesta de una herramienta. |
| `<IgnoreUnresolvedVariables>` | No | — | Si la plantilla o el texto no resuelven, seguir o fallar. |

### Qué texto enviar

Los defaults son para el formato de Gemini y solo envían el **último** mensaje.

> [!IMPORTANT]
> En conversaciones de varios turnos, un ataque puede estar en un mensaje anterior o en el *system prompt* que mande el cliente. Si tu API acepta el historial completo, valora enviar más contexto. Y no olvides `<FunctionResponseSource>`: las respuestas de herramientas (APIs, bases de datos, páginas web) son **datos externos no confiables** y la vía clásica de *inyección indirecta de prompts*; Google insiste en que hay que sanearlas.

## Variables de flujo

Prefijo `SanitizeUserPrompt.{name}.`. Las más útiles:

| Variable | Contenido |
|---|---|
| `matchesFound` | `true` si **algún** filtro coincidió. |
| `filterMatchState` | `MATCH_FOUND` o `NO_MATCH_FOUND`. |
| `invocationResult` | `SUCCESS` (todos los filtros se ejecutaron), `PARTIAL` (algunos se saltaron o fallaron), `FAILURE` (ninguno se ejecutó). |
| `promptInjectionDetected`, `promptInjectionConfidence` | Detección de inyección/jailbreak y su confianza. |
| `raiMatchesFound` | Coincidencia en filtros de IA responsable. |
| `csamFilterMatched` | Coincidencia en el filtro CSAM. |
| `maliciousURIsDetected`, `maliciousURIs` | URIs maliciosas detectadas y su lista. |
| `{filtro}.executionState` / `{filtro}.matchState` | Por filtro: `raiFilterResult`, `sdpFilterResult.inspectResult`, `sdpFilterResult.deidentifyResult`, `piAndJailbreakFilterResult`, `csamFilterFilterResult`, `maliciousUriFilterResult`. |
| `sanitizationMetadata.errorCode`, `.errorMessage` | Código y mensaje propios, si la plantilla de Model Armor los define. |
| `templateUsed`, `userPrompt`, `responseFromModelArmor`, `requestSentToModelArmor`, `sanitizeOperation` | Diagnóstico. |

> [!WARNING]
> `invocationResult = PARTIAL` o `FAILURE` significa que **no se evaluaron todos los filtros**, aunque `matchesFound` sea `false`. Decide si en ese caso dejas pasar la petición (*fail-open*) o la rechazas (*fail-closed*); para cargas sensibles, rechaza.

`userPrompt` y `responseFromModelArmor` contienen el texto del usuario: no los registres sin filtrar.

## Errores

### En runtime

| Código | HTTP | Causa |
|---|---|---|
| `steps.sanitize.user.prompt.response.FilterMatched` | 400 | El prompt no pasó la plantilla de Model Armor. |
| `steps.sanitize.user.prompt.FailedToExtractUserPrompt` | 500 | No se pudo extraer el prompt con el default. |
| `steps.sanitize.user.prompt.SanitizationResponseParsingFailed` | 500 | No se pudo leer la respuesta de Model Armor. |
| `steps.sanitize.user.prompt.InternalError` | 500 | Error interno. |
| `steps.sanitize.modelarmor.ModelArmorTemplateNameExtractionFailed` | 500 | No se pudo resolver el nombre de la plantilla. |
| `steps.sanitize.modelarmor.AuthenticationFailure` | 500 | La cuenta de servicio no puede llamar a Model Armor. |
| `steps.sanitize.modelarmor.ModelArmorAPIFailed`, `ModelArmorCalloutError` | 500 | Falló la API o la llamada. |
| `steps.sanitize.modelarmor.ServiceUnavailable` | 500 | Model Armor no disponible. |

### Al desplegar

Falta `<ModelArmor>/<TemplateName>` o su valor está vacío.

### Variables de fallo

| Variable | Ejemplo |
|---|---|
| `fault.name` | `fault.name = "FilterMatched"` |
| `SanitizeUserPrompt.{name}.failed` | `SanitizeUserPrompt.SUP-Entrada.failed = true` |

> [!NOTE]
> El ejemplo de respuesta de la página usa `steps.sanitizeuserprompt.UnresolvedVariable` y su FaultRule usa `sanitizeuserprompt.failed` y `SetVariableFailed`: nombres que no coinciden con la tabla. Captura por `fault.name`.

## Ejemplos

### 1. Bloquear prompts peligrosos (comportamiento por defecto)

```xml
<SanitizeUserPrompt name="SUP-Entrada">
  <ModelArmor>
    <TemplateName>projects/{organization.name}/locations/{system.region.name}/templates/entrada-estricta</TemplateName>
  </ModelArmor>
</SanitizeUserPrompt>
```

```xml
<FaultRule name="fr-prompt-bloqueado">
  <Condition>fault.name = "FilterMatched"</Condition>
  <Step>
    <Name>AM-Error-400-Prompt</Name>
  </Step>
</FaultRule>
```

No expliques al usuario qué filtro saltó: le darías pistas para reformular el ataque.

### 2. Decidir tú: bloquear inyección, solo registrar lo demás

```xml
<SanitizeUserPrompt name="SUP-Evaluar" continueOnError="true">
  <ModelArmor>
    <TemplateName>projects/{organization.name}/locations/{system.region.name}/templates/entrada</TemplateName>
  </ModelArmor>
</SanitizeUserPrompt>
```

```xml
<Step>
  <Name>RF-Inyeccion-Detectada</Name>
  <Condition>SanitizeUserPrompt.SUP-Evaluar.promptInjectionDetected = true or SanitizeUserPrompt.SUP-Evaluar.invocationResult != "SUCCESS"</Condition>
</Step>
```

Las demás detecciones (p. ej. RAI) pueden capturarse con [DataCapture](../04-extension.md) para revisión.

## Diferencias en Apigee Edge

No existe en Edge. La alternativa es llamar a un servicio de moderación con ServiceCallout y decidir con su respuesta.

## Antipatrones

- No sanear las respuestas de herramientas (`<FunctionResponseSource>`) en agentes con function calling.
- Ignorar `invocationResult` y dar por limpio un prompt que no se evaluó entero.
- Devolver al usuario el detalle del filtro.
- Plantilla de Model Armor sin el filtro de inyección/jailbreak.

## Fuentes

- SanitizeUserPrompt policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/sanitize-user-prompt-policy> (consultada directamente, contenido completo, 2026-10-22).
