---
id: politica-llm-token-quota
titulo: LLMTokenQuota — referencia completa
area: politicas
tags: [llmtokenquota, llm, tokens, cuota, ia, sse, countonly, enforceonly, extensible]
aplica_a: [apigee-x, apigee-hybrid]
elemento_xml: LLMTokenQuota
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/llm-token-quota-policy
revisado: 2026-10-22
---

# LLMTokenQuota — referencia completa

> [!NOTE]
> **Tipo:** Extensible. **Elemento raíz:** `<LLMTokenQuota>`.
> **Aplica a:** Apigee X y Apigee hybrid **1.16.1 o superior**. **No existe en Apigee Edge.**

LLMTokenQuota es una [Quota](quota.md) que cuenta **tokens de un LLM** en lugar de peticiones. Lee del cuerpo de la respuesta cuántos tokens se consumieron (y de qué modelo), los suma a un contador por intervalo (minuto, hora, día, semana, mes) y rechaza con `429` cuando se agota el cupo. Sirve para controlar costos y aplicar planes comerciales de consumo de IA.

## Cuándo usarla (y cuándo no)

| Necesidad | Política correcta |
|---|---|
| Cupo de tokens por app o plan en horas, días o meses | **LLMTokenQuota** |
| Frenar ráfagas de tokens por segundo o por minuto | [PromptTokenLimit](prompt-token-limit.md) |
| Cupo de **peticiones** a un LLM | [Quota](quota.md) |
| Edge o hybrid < 1.16.1 | [Quota con `<MessageWeight>`](quota.md#5-cupo-de-tokens-de-un-llm-con-contador-compartido) |

## Modelo de funcionamiento: contar y aplicar

El consumo real de tokens solo se conoce **en la respuesta**, pero el rechazo tiene que ocurrir **antes** de llamar al modelo. Por eso la política se usa en pareja, con un contador compartido:

| Instancia | Dónde | Elemento clave | Qué hace |
|---|---|---|---|
| Aplicación (*enforcement*) | Flujo de **petición** | `<EnforceOnly>true</EnforceOnly>` | Comprueba si queda cupo; si no, `429`. No suma. |
| Conteo (*counting*) | Flujo de **respuesta** | `<CountOnly>true</CountOnly>` | Lee el consumo de la respuesta y lo suma. Nunca rechaza. |

Las dos llevan el mismo `<SharedName>`. **Es obligatorio** que cada instancia tenga exactamente uno de los dos (`<CountOnly>` o `<EnforceOnly>`) en `true`; si no, el despliegue falla con `InvalidConfiguration`.

Consecuencia: la petición que agota el cupo **se completa**; es la siguiente la que recibe `429`. Una sola petición puede dejar el contador muy por encima del límite si consume muchos tokens.

### Con API products

1. `VerifyAPIKey` o `OAuthV2/VerifyAccessToken` en la petición identifica la app y el API product, y expone las variables de cuota LLM de todas las operaciones LLM que coinciden.
2. La instancia de aplicación extrae el nombre del modelo (con `<LLMModelSource>`) y toma la configuración de cuota correspondiente a ese modelo.
3. La instancia de conteo, en la respuesta, suma los tokens.

Proxy o target, da igual dónde se adjunten, siempre que la de aplicación vaya en la petición y la de conteo en la respuesta.

### Con SSE (respuestas en streaming)

Para respuestas `text/event-stream`, la instancia de conteo va en un `<EventFlow>`. Se ejecuta en cada evento, pero solo cuenta cuando el evento trae los metadatos de uso de tokens; en los demás eventos no hace nada.

```xml
<EventFlow content-type="text/event-stream">
  <Response>
    <Step>
      <Name>LTQ-Contar</Name>
    </Step>
  </Response>
</EventFlow>
```

Si la respuesta no trae el conteo de tokens, se omite el conteo (queda registrado en Debug).

## Tipos (atributo `type`)

Igual que en [Quota — Tipos de cuota](quota.md#tipos-de-cuota-atributo-type):

| `type` | Reinicio del contador |
|---|---|
| Sin valor (default) | Al inicio del siguiente minuto / hora; medianoche GMT para día; medianoche GMT del domingo para semana; medianoche GMT del último día del mes para mes. |
| `calendar` | Desde `<StartTime>`, cada `<Interval>` × `<TimeUnit>`. Mes = 28 días. |
| `flexi` | Desde la primera petición de cada app, cada `<Interval>` × `<TimeUnit>`. Mes = 28 días. |
| `rollingwindow` | Nunca se reinicia: en cada petición se recalcula el consumo de la ventana anterior (p. ej. las últimas 2 horas). |

Todas las horas se interpretan en **UTC**, con notación ISO 8601 (`YYYY-MM-DD HH:mm:ss`).

## Modelo de contadores

Mismas reglas que [Quota — Modelo de contadores](quota.md#modelo-de-contadores):

- Con API product: un contador por operación del producto; la configuración de la operación gana a la del producto, y esta a la de la política. Con `quotaCounterScope=PROXY` en el producto, las operaciones sin cuota propia comparten un contador por proxy.
- Sin API product: un contador por **nombre de política**, compartido por todos los sitios donde esté adjunta. Adjuntar la misma política en varios flujos agota el cupo más rápido (antipatrón).
- Con `<Identifier>` o `<Class>`: un contador por valor. **No se pueden usar los dos en la misma política.**
- Los contadores son por proxy: dos proxies con políticas del mismo nombre tienen contadores separados.

## Sintaxis completa

```xml
<LLMTokenQuota name="LTQ-Nombre" type="calendar" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <LLMTokenUsageSource>{jsonPath('$.usageMetadata.candidatesTokenCount',response.content,true)}</LLMTokenUsageSource>
  <LLMModelSource>{jsonPath('$.model',request.content,true)}</LLMModelSource>
  <Allow count="2000" countRef="verifyapikey.VAK.apiproduct.developer.llmQuota.limit"/>
  <Interval ref="verifyapikey.VAK.apiproduct.developer.llmQuota.interval">1</Interval>
  <TimeUnit ref="verifyapikey.VAK.apiproduct.developer.llmQuota.timeunit">month</TimeUnit>
  <StartTime>2026-01-01 00:00:00</StartTime>
  <Distributed>true</Distributed>
  <Synchronous>false</Synchronous>
  <AsynchronousConfiguration>
    <SyncIntervalInSeconds>20</SyncIntervalInSeconds>
    <SyncMessageCount>5</SyncMessageCount>
  </AsynchronousConfiguration>
  <Identifier ref="client_id"/>
  <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>
  <SharedName>contador-tokens</SharedName>
  <EnforceOnly>true</EnforceOnly>
</LLMTokenQuota>
```

Alternativas que no pueden ir juntas en la misma instancia: `<Allow count>` o `<Allow><Class>`; `<Class>` o `<Identifier>`; `<CountOnly>` o `<EnforceOnly>`. `<UseQuotaConfigInAPIProduct>` reemplaza a `<Allow>`, `<Interval>` y `<TimeUnit>`.

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno; nombra el contador y las variables `ratelimit.{name}.*`. |
| `type` | No | — | `calendar`, `flexi`, `rollingwindow`; sin valor = reinicio al inicio de cada unidad. Otro valor → `InvalidQuotaType` al desplegar. |
| `continueOnError` | No | `false` | Con `true`, el flujo sigue aunque falle. |
| `enabled` | No | `true` | Con `false` no se ejecuta. |
| `async` | No | `false` | **Obsoleto.** |

## Elementos hijos

| Elemento | Obligatorio | Tipo | Default | Resumen |
|---|---|---|---|---|
| `<DisplayName>` | No | String | `name` | Etiqueta en la UI. |
| `<LLMTokenUsageSource>` | No | Plantilla | `{jsonPath('$.usageMetadata.candidatesTokenCount',response.content,true)}` | De dónde sale el número de tokens consumidos. |
| `<LLMModelSource>` | No | Plantilla | `{jsonPath('$.model',request.content,true)}` | De dónde sale el nombre del modelo. |
| `<Allow>` | No | Integer o complejo | `count` = 2000 | Tokens permitidos por intervalo. |
| `<Allow>/<Class>` | No | Complejo | — | Límites distintos según el valor de una variable. |
| `<Interval>` | **Sí** | Integer | — | Número de unidades del periodo. |
| `<TimeUnit>` | **Sí** | String | — | `minute`, `hour`, `day`, `week`, `month` (ver nota sobre `second` y `year`). |
| `<StartTime>` | Solo con `calendar` | `yyyy-MM-dd HH:mm:ss` | — | Inicio del primer periodo. |
| `<Distributed>` | No | Boolean | `false` | Contador central sincronizado entre nodos. |
| `<Synchronous>` | No | Boolean | `false` | Actualización síncrona del contador distribuido. |
| `<AsynchronousConfiguration>` | No | Complejo | cada 10 s | Frecuencia de sincronización asíncrona. |
| `<Identifier ref>` | No | String | — | Un contador por valor de la variable. |
| `<IgnoreUnresolvedVariables>` | No | Boolean | `false` | Qué hacer si un `ref` no resuelve. |
| `<UseQuotaConfigInAPIProduct>` | No | Complejo | — | Tomar la cuota del API product. |
| `<SharedName>` | Con `<CountOnly>`/`<EnforceOnly>` | String | — | Contador compartido entre instancias del mismo proxy. |
| `<CountOnly>` | Uno de los dos | Boolean | `false` | Solo cuenta (respuesta). |
| `<EnforceOnly>` | Uno de los dos | Boolean | `false` | Solo aplica el límite (petición). |

`<MessageWeight>` **no está soportado**: el peso es el número de tokens. Usarlo hace fallar el despliegue con `MessageWeightNotSupported`.

### `<LLMTokenUsageSource>`

[Plantilla de mensaje](../../01-proxies/04-variables-de-flujo.md) que debe resolver a **un único número**. El default lee `usageMetadata.candidatesTokenCount` del cuerpo de la respuesta, que es el formato de la API de Gemini y cuenta **solo los tokens de salida**.

> [!IMPORTANT]
> Ajusta la ruta al proveedor y a lo que quieras cobrar. Ejemplos de rutas según el formato de respuesta (verifícalas contra tu proveedor real):
>
> | Formato | Solo salida | Total (entrada + salida) |
> |---|---|---|
> | Gemini (`generateContent`) | `$.usageMetadata.candidatesTokenCount` | `$.usageMetadata.totalTokenCount` |
> | Estilo OpenAI (`chat/completions`) | `$.usage.completion_tokens` | `$.usage.total_tokens` |
>
> Si el cupo debe reflejar el costo real, normalmente se cuenta el **total**: los tokens de entrada también se facturan.

Si la política no está en un event flow y no puede extraer el número, falla con `FailedToResolveTokenUsageCount` (`500`).

En SSE se lee del evento actual, `response.event.current.data`, y el tercer argumento de `jsonPath` (*want-array*) debe ser `false` para obtener un valor y no una lista:

```xml
<LLMTokenUsageSource>{jsonPath('$.usageMetadata.candidatesTokenCount',response.event.current.data,false)}</LLMTokenUsageSource>
```

### `<LLMModelSource>`

Plantilla que resuelve al nombre del modelo, desde la petición o desde la respuesta. Si se omite, se lee el campo `model` del cuerpo de la petición; si tampoco existe, el modelo se toma de la operación LLM configurada en el API product. Si no se puede resolver, la política falla con `FailedToResolveModelName` (`400`). En SSE, igual que arriba, con `response.event.current.data` y `false` (p. ej. `$.modelVersion`).

El modelo extraído queda en `llmtokenquota.{name}.model` y es lo que permite tener cuotas distintas por modelo en el API product.

### `<Allow>` y `<Class>`

| Forma | Ejemplo |
|---|---|
| Literal | `<Allow count="2000"/>` |
| Variable | `<Allow countRef="verifyapikey.VAK.apiproduct.developer.llmQuota.limit"/>` |
| Ambas | Si `countRef` resuelve, gana; si no, se usa `count`. |
| Por clase | `<Allow><Class ref="variable"><Allow class="oro" count="100000"/>…</Class></Allow>` |

Con `<Class>`, cada `<Allow class>` es un contador independiente. Si la variable de `<Class ref>` trae un valor que no coincide con ninguna clase, la política responde **violación de cuota**, no un error de configuración.

### `<Interval>` y `<TimeUnit>`

Ambos obligatorios, con literal y/o `ref` (gana `ref` si resuelve). `<Interval>` debe ser entero (`InvalidQuotaInterval` si no lo es). Si falta, en runtime aparece `FailedToResolveQuotaIntervalReference`; si falta `<TimeUnit>`, `FailedToResolveQuotaIntervalTimeUnitReference`.

> [!WARNING]
> **Discrepancias en `<TimeUnit>`.** El texto de la página lista `minute`, `hour`, `day`, `week`, `month` **o `year`**, y añade que también se acepta `second` solo con `<Distributed>false</Distributed>` (Google recomienda PromptTokenLimit para límites por segundo). Pero el error de despliegue `InvalidQuotaTimeUnit` dice que las unidades soportadas son solo `minute`, `hour`, `day`, `week` y `month`. Es la misma contradicción que en [Quota](quota.md#interval-y-timeunit). Usa solo esas cinco.

### `<StartTime>`

Solo con `type="calendar"`; en otro tipo, el despliegue falla con `StartTimeNotSupported`. Formato `yyyy-MM-dd HH:mm:ss`, en GMT/UTC; otro formato da `InvalidStartTime`.

> [!WARNING]
> **Discrepancia sobre su ausencia.** Una sección dice que si se omite con `calendar`, Apigee da error; otra dice que el periodo empieza el primer día del mes en curso. Igual que en [Quota](quota.md#starttime). Decláralo siempre con `calendar`.
>
> Los propios ejemplos de la página usan `2025-7-16 12:00:00`, sin cero a la izquierda en el mes, cuando el formato declarado es `yyyy-MM-dd`. Usa siempre dos dígitos.

### `<Distributed>`, `<Synchronous>` y `<AsynchronousConfiguration>`

Mismo comportamiento que en [Quota](quota.md#distributed-synchronous-y-asynchronousconfiguration):

- `<Distributed>false</Distributed>` (default): cada nodo cuenta por su cuenta y el cupo real puede superarse. En X/hybrid con varios message processors, usa `true`.
- `<Synchronous>true</Synchronous>`: actualización en cada petición; más exacta, pero con impacto en rendimiento e incluso fallos de transacciones bajo carga.
- `<AsynchronousConfiguration>` (solo con `<Synchronous>false</Synchronous>`): `<SyncIntervalInSeconds>` (≥ 10 s según los límites; default 10) y/o `<SyncMessageCount>`; se sincroniza con lo que ocurra primero. Combinarla con `<Synchronous>true</Synchronous>` hace fallar el despliegue (`InvalidAsynchronizeConfigurationForSynchronousQuota`).

### `<Identifier>`

Un contador por valor de la variable (`client_id`, cuenta de cliente, cabecera, etc.).

> [!WARNING]
> La página de LLMTokenQuota propone `developer.id` como ejemplo, pero advierte en el mismo apartado que `developer.id` y `developer.app.id` pueden cambiar durante un mantenimiento y que, si cambian, la cuota no se aplica con rigor en esa ventana. Usa `client_id` o un atributo propio estable. Ver [VerifyAPIKey — Variables de flujo](verify-api-key.md#variables-de-flujo).

### `<UseQuotaConfigInAPIProduct>` y `<DefaultConfig>`

Igual que en [Quota](quota.md#usequotaconfiginapiproduct-y-defaultconfig): con este elemento se ignoran `<Allow>`, `<Interval>` y `<TimeUnit>` del cuerpo de la política. `stepName` (obligatorio) apunta a la `VerifyAPIKey` o a la `OAuthV2` (operación `VerifyAccessToken`) del flujo. `<DefaultConfig>` (con sus tres hijos obligatorios) se usa cuando el producto no define cuota; si el producto la define, gana el producto.

### `<IgnoreUnresolvedVariables>`

Con `false` (default), un `ref` que no resuelve produce error. Con `true`, se ignora el `ref` y se usa el literal del elemento, o el default si no hay literal.

## Variables de flujo

| Variable | Tipo | Contenido |
|---|---|---|
| `ratelimit.{name}.allowed.count` | Long | Tokens permitidos. |
| `ratelimit.{name}.used.count` | Long | Tokens consumidos en el intervalo. |
| `ratelimit.{name}.available.count` | Long | Tokens restantes. |
| `ratelimit.{name}.exceed.count` | Long | `1` tras superar la cuota. |
| `ratelimit.{name}.total.exceed.count` | Long | `1` tras superar la cuota. |
| `ratelimit.{name}.expiry.time` | Long | Milisegundos UTC del próximo reinicio. **No válido con `rollingwindow`.** |
| `ratelimit.{name}.identifier` | String | Identificador usado. |
| `ratelimit.{name}.class` | String | Clase aplicada. |
| `ratelimit.{name}.class.allowed.count` / `.used.count` / `.available.count` | Long | Lo mismo, por clase. |
| `ratelimit.{name}.class.exceed.count` | Long | Tokens que exceden el límite de la clase en el intervalo actual. |
| `ratelimit.{name}.class.total.exceed.count` | Long | Suma de `class.exceed.count` de todos los intervalos. |
| `ratelimit.{name}.failed` | Boolean | Si la política falló. |
| `llmtokenquota.{name}.model` | String | Modelo extraído. |

Todas son de solo lectura. Con contador compartido, lee las variables de la instancia de conteo para saber el consumo actualizado.

## Errores

### En runtime

| Código de fallo | HTTP | Causa |
|---|---|---|
| `policies.llmtokenquota.LLMTokenQuotaViolation` | 429 | Se agotó el cupo de tokens. |
| `policies.llmtokenquota.FailedToResolveModelName` | 400 | No se pudo resolver el nombre del modelo. |
| `policies.llmtokenquota.MessageTemplateExtractionFailed` | 400 | Falló la extracción de una plantilla de mensaje. |
| `policies.llmtokenquota.FailedToResolveTokenUsageCount` | 500 | No se pudo extraer el número de tokens de la respuesta. |
| `policies.ratelimit.FailedToResolveQuotaIntervalReference` | 500 | Falta `<Interval>` o no resolvió. |
| `policies.ratelimit.FailedToResolveQuotaIntervalTimeUnitReference` | 500 | Falta `<TimeUnit>` o no resolvió. |

> [!NOTE]
> La descripción de la variable `<LLMTokenUsageSource>` menciona el código `policies.ratelimit.FailedToResolveTokenUsageCount`, mientras que la tabla de errores usa el prefijo `policies.llmtokenquota.`. Captura por `fault.name = "FailedToResolveTokenUsageCount"`, que es igual en ambos casos.

### Al desplegar

| Error | Causa |
|---|---|
| `policies.llmtokenquota.MessageWeightNotSupported` | Se usó `<MessageWeight>`. |
| `policies.llmtokenquota.InvalidConfiguration` | No hay exactamente uno de `<CountOnly>` / `<EnforceOnly>` en `true`. |
| `InvalidQuotaInterval` | `<Interval>` no es entero. |
| `InvalidQuotaTimeUnit` | `<TimeUnit>` no soportado. |
| `InvalidQuotaType` | `type` inválido. |
| `InvalidStartTime` | `<StartTime>` con formato distinto de `yyyy-MM-dd HH:mm:ss`. |
| `StartTimeNotSupported` | `<StartTime>` con un `type` que no es `calendar`. |
| `InvalidSynchronizeIntervalForAsyncConfiguration` | `<SyncIntervalInSeconds>` negativo. |
| `InvalidAsynchronizeConfigurationForSynchronousQuota` | `<AsynchronousConfiguration>` junto con `<Synchronous>true</Synchronous>`. |

### Variables de fallo

| Variable | Ejemplo |
|---|---|
| `fault.name` | `fault.name = "LLMTokenQuotaViolation"` |
| `ratelimit.{name}.failed` | `ratelimit.LTQ-Aplicar.failed = true` |

Captura por `errorcode` o `fault.name`, nunca por el texto de `faultstring`.

## Ejemplos

### 1. Pareja contar / aplicar con cupo del API product

El API product define la cuota LLM por operación y modelo. `VAK-Header` verifica la key en la petición.

```xml
<LLMTokenQuota name="LTQ-Aplicar" type="rollingwindow">
  <SharedName>tokens-por-app</SharedName>
  <EnforceOnly>true</EnforceOnly>
  <Identifier ref="client_id"/>
  <Allow count="100000" countRef="verifyapikey.VAK-Header.apiproduct.developer.llmQuota.limit"/>
  <Interval ref="verifyapikey.VAK-Header.apiproduct.developer.llmQuota.interval">1</Interval>
  <TimeUnit ref="verifyapikey.VAK-Header.apiproduct.developer.llmQuota.timeunit">day</TimeUnit>
  <Distributed>true</Distributed>
</LLMTokenQuota>
```

```xml
<LLMTokenQuota name="LTQ-Contar" type="rollingwindow">
  <SharedName>tokens-por-app</SharedName>
  <CountOnly>true</CountOnly>
  <Identifier ref="client_id"/>
  <Allow count="100000" countRef="verifyapikey.VAK-Header.apiproduct.developer.llmQuota.limit"/>
  <Interval ref="verifyapikey.VAK-Header.apiproduct.developer.llmQuota.interval">1</Interval>
  <TimeUnit ref="verifyapikey.VAK-Header.apiproduct.developer.llmQuota.timeunit">day</TimeUnit>
  <Distributed>true</Distributed>
  <LLMTokenUsageSource>{jsonPath('$.usageMetadata.totalTokenCount',response.content,true)}</LLMTokenUsageSource>
  <LLMModelSource>{jsonPath('$.modelVersion',response.content,true)}</LLMModelSource>
</LLMTokenQuota>
```

```xml
<!-- ProxyEndpoint -->
<PreFlow name="PreFlow">
  <Request>
    <Step><Name>VAK-Header</Name></Step>
    <Step><Name>LTQ-Aplicar</Name></Step>
  </Request>
  <Response>
    <Step><Name>LTQ-Contar</Name></Step>
  </Response>
</PreFlow>
```

### 2. Proveedor con formato OpenAI y respuestas en streaming

Para la parte no streaming se cuenta `usage.total_tokens`; para SSE, la misma ruta sobre el evento actual. Con muchos proveedores el uso solo llega en el último evento del stream y a veces hay que pedirlo explícitamente en la petición; comprueba el comportamiento de tu proveedor.

```xml
<LLMTokenQuota name="LTQ-Contar-SSE" type="calendar">
  <SharedName>tokens-mensuales</SharedName>
  <CountOnly>true</CountOnly>
  <Identifier ref="client_id"/>
  <Allow count="5000000"/>
  <Interval>1</Interval>
  <TimeUnit>month</TimeUnit>
  <StartTime>2026-01-01 00:00:00</StartTime>
  <Distributed>true</Distributed>
  <LLMTokenUsageSource>{jsonPath('$.usage.total_tokens',response.event.current.data,false)}</LLMTokenUsageSource>
  <LLMModelSource>{jsonPath('$.model',response.event.current.data,false)}</LLMModelSource>
</LLMTokenQuota>
```

### 3. Planes con `<Class>` y cabeceras de consumo

El plan (`oro`, `plata`) viene de un atributo personalizado de la app, nunca de una cabecera del cliente.

```xml
<LLMTokenQuota name="LTQ-Aplicar-Plan">
  <SharedName>tokens-plan</SharedName>
  <EnforceOnly>true</EnforceOnly>
  <Allow>
    <Class ref="verifyapikey.VAK-Header.app.plan_ia">
      <Allow class="oro" count="1000000"/>
      <Allow class="plata" count="100000"/>
    </Class>
  </Allow>
  <Interval>1</Interval>
  <TimeUnit>day</TimeUnit>
  <Distributed>true</Distributed>
</LLMTokenQuota>
```

> [!NOTE]
> Con `<Class>` no se puede usar `<Identifier>`, así que este contador es **por clase**, no por app: todas las apps `oro` comparten el mismo millón. Para un cupo por app y por plan, usa `<Identifier ref="client_id"/>` y toma el límite con `countRef` de un atributo de la app o del producto.

```xml
<AssignMessage name="AM-Cabeceras-Tokens">
  <Set>
    <Headers>
      <Header name="X-Tokens-Limite">{ratelimit.LTQ-Contar.allowed.count}</Header>
      <Header name="X-Tokens-Usados">{ratelimit.LTQ-Contar.used.count}</Header>
      <Header name="X-Tokens-Disponibles">{ratelimit.LTQ-Contar.available.count}</Header>
    </Headers>
  </Set>
  <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
  <AssignTo createNew="false" transport="http" type="response"/>
</AssignMessage>
```

## Diferencias en Apigee Edge

LLMTokenQuota **no existe en Edge**. Alternativa: [Quota](quota.md) con `<MessageWeight>` alimentado por el conteo de tokens leído de la respuesta, en el patrón de dos políticas con contador compartido (ver [Quota — ejemplo 5](quota.md#5-cupo-de-tokens-de-un-llm-con-contador-compartido)). En Edge, `<SharedName>`/`<CountOnly>`/`<EnforceOnly>` no existen en Quota, así que el control solo puede ser posterior a la llamada.

## Antipatrones

- Dejar el `<LLMTokenUsageSource>` por defecto con un proveedor que no es Gemini, o contar solo los tokens de salida cuando el contrato cobra el total.
- Una sola instancia sin `<CountOnly>`/`<EnforceOnly>` (no despliega) o las dos instancias con `<SharedName>` distinto (nunca se rechaza nada).
- `<Distributed>false</Distributed>` en X/hybrid con varios message processors.
- `developer.id` como `<Identifier>`.
- Tomar la clase o el límite de una cabecera que manda el cliente.
- Confiar en LLMTokenQuota para frenar ráfagas: para eso está [PromptTokenLimit](prompt-token-limit.md).

## Fuentes

- LLMTokenQuota policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/llm-token-quota-policy> (consultada directamente, contenido completo, 2026-10-22).
- Las rutas de uso de tokens del estilo OpenAI son una referencia orientativa y no salen de la documentación de Apigee; verifícalas con la documentación del proveedor.
