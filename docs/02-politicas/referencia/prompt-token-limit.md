---
id: politica-prompt-token-limit
titulo: PromptTokenLimit — referencia completa
area: politicas
tags: [prompttokenlimit, llm, tokens, rate-limiting, picos, ia, useeffectivecount, extensible]
aplica_a: [apigee-x, apigee-hybrid]
elemento_xml: PromptTokenLimit
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/prompt-token-limit-policy
revisado: 2026-10-22
---

# PromptTokenLimit — referencia completa

> [!NOTE]
> **Tipo:** Extensible. **Elemento raíz:** `<PromptTokenLimit>`.
> **Aplica a:** Apigee X y Apigee hybrid **1.16.1 o superior**. **No existe en Apigee Edge.**

PromptTokenLimit es un [SpikeArrest](spike-arrest.md) que cuenta **tokens del prompt** en vez de peticiones. Extrae el texto del prompt de la petición, calcula cuántos tokens tiene y lo descuenta de una tasa por segundo o por minuto. Si se supera la tasa, responde `429` **antes** de llamar al modelo.

| | PromptTokenLimit | [LLMTokenQuota](llm-token-quota.md) |
|---|---|---|
| Propósito | Operativo: frenar **ráfagas** de tokens | Comercial: cupo por app en **horas, días o meses** |
| Qué cuenta | Tokens del **prompt** (entrada), calculados por Apigee | Tokens que el LLM informa en la **respuesta** |
| Cuándo rechaza | En la misma petición, antes del modelo | En la petición siguiente a agotar el cupo |
| Unidades | `ps`, `pm` | `minute` … `month` |

Se usan juntas: PromptTokenLimit para proteger el backend y LLMTokenQuota para el contrato.

## Sintaxis completa

```xml
<PromptTokenLimit name="PTL-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <Properties/>
  <UserPromptSource>{jsonPath('$.contents[-1].parts[-1].text',request.content,true)}</UserPromptSource>
  <Identifier ref="client_id"/>
  <Rate ref="variable.con.tasa">1000pm</Rate>
  <UseEffectiveCount>true</UseEffectiveCount>
  <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>
</PromptTokenLimit>
```

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno; da nombre a `ratelimit.{name}.*`. |
| `continueOnError` | No | `false` | Con `true`, el flujo sigue aunque falle. |
| `enabled` | No | `true` | Con `false` no se ejecuta. |

## Elementos hijos

| Elemento | Obligatorio | Tipo | Default | Resumen |
|---|---|---|---|---|
| `<DisplayName>` | No | String | `name` | Etiqueta en la UI. |
| `<UserPromptSource>` | No | Plantilla | ver discrepancia | De dónde sale el texto del prompt. |
| `<Identifier ref>` | No (ver nota) | String | — | Agrupa la tasa por cliente. |
| `<Rate>` | **Sí** | `Nps` / `Npm` | — | Tokens permitidos por segundo o minuto. |
| `<UseEffectiveCount>` | No | Boolean | `false` | Algoritmo. **En X/hybrid, `true`.** |
| `<IgnoreUnresolvedVariables>` | No | Boolean | `false` | Qué hacer si una variable no resuelve. |

`<MessageWeight>` **no está soportado** (`MessageWeightNotSupported`): el peso es el número de tokens.

### `<UserPromptSource>`

[Plantilla de mensaje](../../01-proxies/04-variables-de-flujo.md) que debe resolver al **texto** del prompt. Apigee cuenta los tokens de ese texto; si no lo puede extraer, falla con `FailedToExtractUserPrompt` (`400`), y si no puede calcular los tokens, con `FailedToCalculateUserPromptTokens` (`500`).

| Formato de petición | Plantilla |
|---|---|
| Gemini, último mensaje del usuario | `{jsonPath('$.contents[-1].parts[-1].text',request.content,true)}` |
| Lista completa de mensajes (estilo OpenAI) | `{jsonPath('$.messages',request.content,true)}` |

> [!WARNING]
> **Discrepancia sobre el valor por defecto.** La tabla del elemento dice que no tiene default; la plantilla que inserta la UI usa la ruta de Gemini (`$.contents[-1].parts[-1].text`); y el ejemplo 4 de la página afirma que el default es `{jsonPath('$.messages',request.content,true)}`. **Declara siempre `<UserPromptSource>`** con la ruta de tu proveedor.

Elige bien qué cuentas: con `$.contents[-1]...` solo se cuenta el **último** mensaje; con el historial completo (`$.messages`) se cuenta el contexto entero que se envía al modelo, que es lo que de verdad cuesta.

La documentación no indica qué tokenizador usa Apigee; el número puede diferir del que informa el proveedor. Trátalo como una estimación para control de tráfico, no para facturar.

### `<Identifier>`

Agrupa el conteo por el valor de una variable (p. ej. `client_id`). Sin él, **una sola tasa para todo el proxy**.

> [!NOTE]
> La tabla de atributos marca `ref` como obligatorio, mientras que el texto dice que dejar el elemento vacío aplica una tasa única. Si no necesitas agrupar, omite el elemento entero en vez de dejar `ref=""`.
>
> El ejemplo oficial usa `developer.id`, que la página de VerifyAPIKey desaconseja como identificador por no ser estable. Usa `client_id` o un atributo propio. (Ese ejemplo, además, tiene un error de sintaxis: `<Rate>42pm</Rate/>`.)

Truco del ejemplo 3 de Google para limitar el **tamaño de cada petición** (ventana de contexto) en vez de un ritmo: usar un identificador **único por petición** (p. ej. `messageid`). Así cada petición tiene su propio contador y `<Rate>` actúa como tope de tokens por petición.

### `<Rate>`

Formato: entero positivo distinto de cero seguido de `ps` o `pm`. Igual que en SpikeArrest:

| Forma | Comportamiento |
|---|---|
| `<Rate>1000pm</Rate>` | Tasa fija. |
| `<Rate ref="variable"/>` | Tasa tomada en runtime; si la variable no existe, error. |
| `<Rate ref="variable">1000pm</Rate>` | Gana la variable si tiene valor; si no, el literal. |

> [!WARNING]
> Como en SpikeArrest, no tomes la tasa de una cabecera que mande el cliente: podría subirse el límite. Usa un atributo del API product, un KVM o un PropertySet.

### `<UseEffectiveCount>`

| Valor | Algoritmo | Conteo |
|---|---|---|
| `true` | Ventana deslizante; permite ráfagas mientras no superen la tasa total | Distribuido entre los message processors de la región |
| `false` (default) | Token bucket con suavizado: `30pm` → 1 token cada 2 s | Local a cada message processor |

> [!IMPORTANT]
> Google indica que el suavizado (`false`) **no está soportado** en organizaciones de Apigee ni en hybrid con cargas de producción, aunque sea el default. Declara `<UseEffectiveCount>true</UseEffectiveCount>`.
>
> Con el suavizado, una tasa en tokens es casi inutilizable: con `600pm` se permite 1 token cada 100 ms, y un prompt de 50 tokens no cabría en ningún intervalo. Este es otro motivo para usar `true`.

El elemento admite `ref` para tomar el valor de una variable. Como en SpikeArrest, Apigee calcula internamente `messagesPerPeriod`, `periodInMicroseconds` y `maxBurstMessageCount` por message processor; solo sirven para interpretar Debug.

### `<IgnoreUnresolvedVariables>`

Con `true`, las variables que no resuelven se ignoran y el procesamiento sigue; con `false` (default), producen error.

## Variables de flujo

| Variable | Tipo | Contenido |
|---|---|---|
| `ratelimit.{name}.userPromptTokenCount` | String | Tokens calculados para el prompt extraído. |
| `ratelimit.{name}.resolvedUserPrompt` | String | Texto del prompt extraído. |
| `ratelimit.{name}.userPromptSource` | String | Plantilla configurada. |
| `ratelimit.{name}.failed` | Boolean | `true` solo ante un **fallo interno**. |

> [!WARNING]
> `ratelimit.{name}.resolvedUserPrompt` contiene el texto completo del prompt. No lo registres en MessageLogging ni lo devuelvas en cabeceras: puede llevar datos personales.
>
> Como en SpikeArrest, la política está diseñada para fallar abierta (*fail-open*): no uses `.failed` para saber si se aplicó el límite, porque bajo carga puede quedar en `true` sin rechazo.

## Errores

### En runtime

| Código de fallo | HTTP | Causa |
|---|---|---|
| `policies.prompttokenlimit.PromptTokenLimitViolation` | 429 | Se superó la tasa de tokens. |
| `policies.prompttokenlimit.FailedToExtractUserPrompt` | 400 | No se pudo extraer el prompt de la petición. |
| `policies.prompttokenlimit.FailedToCalculateUserPromptTokens` | 500 | No se pudieron calcular los tokens. |

La página advierte que también pueden aparecer errores de [SpikeArrest](spike-arrest.md#errores) (p. ej. por una `<Rate ref>` que no resuelve).

### Al desplegar

| Error | Causa |
|---|---|
| `policies.prompttokenlimit.MessageWeightNotSupported` | Se usó `<MessageWeight>`. |

### Variables de fallo

| Variable | Ejemplo |
|---|---|
| `fault.name` | `fault.name = "PromptTokenLimitViolation"` |
| `ratelimit.{name}.failed` | `ratelimit.PTL-Por-App.failed = true` |

## Ejemplos

### 1. Escudo de tokens por app, distribuido

```xml
<PromptTokenLimit name="PTL-Por-App">
  <UserPromptSource>{jsonPath('$.contents[-1].parts[-1].text',request.content,true)}</UserPromptSource>
  <Identifier ref="client_id"/>
  <Rate ref="verifyapikey.VAK-Header.apiproduct.tokens_por_minuto">20000pm</Rate>
  <UseEffectiveCount>true</UseEffectiveCount>
</PromptTokenLimit>
```

### 2. Tope de tamaño por petición (ventana de contexto)

Cada petición tiene su propio contador porque el identificador es único (`messageid`); con `8000pm`, ninguna petición puede mandar más de 8000 tokens de historial.

```xml
<PromptTokenLimit name="PTL-Tope-Contexto">
  <UserPromptSource>{jsonPath('$.messages',request.content,true)}</UserPromptSource>
  <Identifier ref="messageid"/>
  <Rate>8000pm</Rate>
  <UseEffectiveCount>true</UseEffectiveCount>
</PromptTokenLimit>
```

> [!NOTE]
> El ejemplo oficial equivalente usa `<UseEffectiveCount>false</UseEffectiveCount>`, que es justo el modo que Google declara no soportado en producción. Aquí se usa `true`; valida en tu organización que el comportamiento por petición se mantiene.

### 3. Respuesta 429 propia

```xml
<FaultRule name="fr-tokens-prompt">
  <Condition>fault.name = "PromptTokenLimitViolation"</Condition>
  <Step>
    <Name>AM-Error-429-Tokens</Name>
  </Step>
</FaultRule>
```

## Diferencias en Apigee Edge

PromptTokenLimit **no existe en Edge**. Alternativa aproximada: calcular una estimación del número de tokens en una política JavaScript, guardarla en una variable y usarla como `<MessageWeight>` de un [SpikeArrest](spike-arrest.md#messageweight).

## Antipatrones

- Dejar `<UseEffectiveCount>` en `false` (default) en X/hybrid.
- No declarar `<UserPromptSource>` y depender de un default que la documentación no fija.
- Usarla para facturar consumo (para eso está LLMTokenQuota con los tokens que informa el proveedor).
- Registrar `resolvedUserPrompt` en logs.
- Tomar la tasa de una cabecera del cliente.

## Fuentes

- PromptTokenLimit policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/prompt-token-limit-policy> (consultada directamente, contenido completo, 2026-10-22).
