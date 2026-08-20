---
id: politicas-ai
titulo: Políticas de IA
area: politicas
tags: [llm, semantic-cache, model-armor, token-quota, vertex-ai, gemini]
aplica_a: [apigee-x]
fuente: https://cloud.google.com/apigee/docs/api-platform/get-started/ai-capabilities
revisado: 2026-08-20
---

# Políticas de IA

Apigee incorpora políticas específicas para gobernar tráfico hacia modelos de lenguaje. Convierten el proxy en un **AI gateway**: control de coste por tokens, caché por significado y filtrado de seguridad.

> [!NOTE]
> Todos los ejemplos XML de este documento están tomados de los **samples oficiales de Google** en
> [`GoogleCloudPlatform/apigee-samples`](https://github.com/GoogleCloudPlatform/apigee-samples) (Apache 2.0),
> adaptados con marcadores de posición en MAYÚSCULAS.

## Las seis políticas

| Política | Elemento XML | Función |
|---|---|---|
| SemanticCacheLookup | `<SemanticCacheLookup>` | Busca respuestas cacheadas **semánticamente similares** vía embeddings |
| SemanticCachePopulate | `<SemanticCachePopulate>` | Inserta la respuesta del modelo en el índice vectorial |
| LLMTokenQuota | `<LLMTokenQuota>` | Cuota sobre **tokens consumidos**, no sobre número de llamadas |
| PromptTokenLimit | `<PromptTokenLimit>` | Limita el tamaño en tokens del prompt de entrada |
| SanitizeUserPrompt | `<SanitizeUserPrompt>` | Filtra el prompt vía **Model Armor** |
| SanitizeModelResponse | `<SanitizeModelResponse>` | Filtra la respuesta del modelo vía Model Armor |

---

## LLMTokenQuota

El problema que resuelve: con un LLM, **el coste no es proporcional al número de llamadas** sino a los tokens. Una `Quota` normal de "1.000 llamadas/hora" no protege nada si cada llamada consume 100.000 tokens.

### Patrón de dos políticas: contar y aplicar

El sample oficial usa **dos** instancias de `LLMTokenQuota` compartiendo contador mediante `<SharedName>`:

- **`EnforceOnly`** → se ejecuta en el **request**, antes de llamar al modelo. Comprueba si queda cuota y bloquea si no.
- **`CountOnly`** → se ejecuta en el **response**, cuando ya se conoce el consumo real. Incrementa el contador.

Es necesario porque el número de tokens consumidos **solo se conoce después** de la respuesta del modelo.

**Política de aplicación** (request flow):

```xml
<LLMTokenQuota continueOnError="false" enabled="true" name="LTQ-TokenEnforce" type="calendar">
  <DisplayName>LTQ-TokenEnforce</DisplayName>
  <Allow count="1000" countRef="verifyapikey.VA-VerifyAPIKey.apiproduct.developer.llmQuota.limit"/>
  <Interval ref="verifyapikey.VA-VerifyAPIKey.apiproduct.developer.llmQuota.interval">1</Interval>
  <TimeUnit ref="verifyapikey.VA-VerifyAPIKey.apiproduct.developer.llmQuota.timeunit">minute</TimeUnit>
  <Distributed>true</Distributed>
  <Synchronous>true</Synchronous>
  <StartTime>2026-01-01 00:00:00</StartTime>
  <LLMModelSource>{model}</LLMModelSource>
  <EnforceOnly>true</EnforceOnly>
  <SharedName>common-counter</SharedName>
</LLMTokenQuota>
```

**Política de conteo** (response flow):

```xml
<LLMTokenQuota continueOnError="false" enabled="true" name="LTQ-TokenCount" type="calendar">
  <DisplayName>LTQ-TokenCount</DisplayName>
  <Allow count="1000" countRef="verifyapikey.VA-VerifyAPIKey.apiproduct.developer.llmQuota.limit"/>
  <Interval ref="verifyapikey.VA-VerifyAPIKey.apiproduct.developer.llmQuota.interval">1</Interval>
  <TimeUnit ref="verifyapikey.VA-VerifyAPIKey.apiproduct.developer.llmQuota.timeunit">minute</TimeUnit>
  <Distributed>true</Distributed>
  <Synchronous>true</Synchronous>
  <StartTime>2026-01-01 00:00:00</StartTime>
  <LLMTokenUsageSource>{jsonPath('$.usageMetadata.candidatesTokenCount',response.content,true)}</LLMTokenUsageSource>
  <LLMModelSource>{model}</LLMModelSource>
  <CountOnly>true</CountOnly>
  <SharedName>common-counter</SharedName>
</LLMTokenQuota>
```

### Elementos específicos

| Elemento | Función |
|---|---|
| `<LLMTokenUsageSource>` | Expresión que extrae el nº de tokens de la respuesta del modelo. Usa la función `jsonPath()` de message templating |
| `<LLMModelSource>` | Variable con el identificador del modelo, para contar por modelo |
| `<CountOnly>` | `true` → solo incrementa el contador, no bloquea |
| `<EnforceOnly>` | `true` → solo comprueba y bloquea, no incrementa |
| `<SharedName>` | Nombre del contador compartido entre ambas políticas |

> [!IMPORTANT]
> `<LLMTokenUsageSource>` es **específico del proveedor**. El ejemplo usa el formato de Vertex AI / Gemini (`$.usageMetadata.candidatesTokenCount`). Para OpenAI sería `$.usage.completion_tokens`, para Anthropic `$.usage.output_tokens`. Ajústalo al modelo que estés fronteando.

### La cuota vive en el API product

Nótese `verifyapikey.VA-VerifyAPIKey.apiproduct.developer.llmQuota.limit`: es un **atributo personalizado** llamado `llmQuota` definido en el API product. El patrón es el mismo que en la [Quota normal](01-traffic-management.md): el producto define el plan, la política solo lo lee.

---

## PromptTokenLimit

Rechaza prompts demasiado largos **antes** de enviarlos al modelo. Protege del coste de un prompt de 500.000 tokens y de ataques de agotamiento de contexto.

Complementa a `LLMTokenQuota`: `PromptTokenLimit` es un límite **por petición**, `LLMTokenQuota` es un límite **acumulado por intervalo**.

---

## Caché semántica

La caché HTTP normal no sirve con LLMs: `"¿cuál es vuestra política de devoluciones?"` y `"cómo devuelvo un producto"` son claves distintas pero merecen la misma respuesta.

La caché semántica:

1. Calcula el **embedding** del prompt del usuario (Vertex AI Embeddings).
2. Busca el vecino más cercano en un **índice vectorial** (Vertex AI Vector Search).
3. Si la distancia está por debajo del umbral → devuelve la respuesta cacheada **sin llamar al modelo**.

### SemanticCacheLookup

```xml
<SemanticCacheLookup async="false" continueOnError="false" enabled="true" name="SCL-Semantic-Cache-Lookup">
    <DisplayName>SCL-Semantic-Cache-Lookup</DisplayName>
    <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>
    <UserPromptSource>{jsonPath('$.contents[-1].parts[-1].text',request.content,true)}</UserPromptSource>
    <Embeddings>
      <VertexAI>
        <URL>https://REGION-aiplatform.googleapis.com/v1/projects/PROJECT_ID/locations/REGION/publishers/google/models/EMBEDDINGS_MODEL_ID:predict</URL>
      </VertexAI>
    </Embeddings>
    <SimilaritySearch>
      <VertexAI>
        <URL>https://PUBLIC_ENDPOINT_SUBDOMAIN.REGION-PROJECT_NUMBER.vdb.vertexai.goog/v1/projects/PROJECT_NUMBER/locations/REGION/indexEndpoints/INDEX_ENDPOINT_ID:findNeighbors</URL>
        <DeployedIndexID>INDEX_ID_NAME</DeployedIndexID>
        <Threshold>NEAREST_NEIGHBOR_DISTANCE</Threshold>
      </VertexAI>
    </SimilaritySearch>
</SemanticCacheLookup>
```

### SemanticCachePopulate

```xml
<SemanticCachePopulate async="false" continueOnError="false" enabled="true" name="SCP-Semantic-Cache-Populate">
    <DisplayName>SCP-Semantic-Cache-Populate</DisplayName>
    <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
    <SimilaritySearch>
        <VertexAI>
            <URL>https://REGION-aiplatform.googleapis.com/v1/projects/PROJECT_NUMBER/locations/REGION/indexes/INDEX_ID:upsertDatapoints</URL>
        </VertexAI>
    </SimilaritySearch>
    <TTLInSeconds>CACHE_ENTRY_TTL_SEC</TTLInSeconds>
</SemanticCachePopulate>
```

### Elementos

| Elemento | Función |
|---|---|
| `<UserPromptSource>` | Expresión que extrae el prompt del payload. Depende del formato del proveedor |
| `<Embeddings><VertexAI><URL>` | Endpoint `:predict` del modelo de embeddings |
| `<SimilaritySearch><VertexAI><URL>` | `:findNeighbors` en lookup, `:upsertDatapoints` en populate |
| `<DeployedIndexID>` | ID del índice desplegado en Vector Search |
| `<Threshold>` | Distancia máxima al vecino más cercano para considerar acierto |
| `<TTLInSeconds>` | Vida de la entrada cacheada |

> [!IMPORTANT]
> El `<Threshold>` es el parámetro que decide si esto funciona o rompe tu producto.
> - **Demasiado permisivo** → sirves la respuesta de una pregunta parecida pero distinta. Peor que un miss.
> - **Demasiado estricto** → hit rate cercano a cero y pagas embeddings + búsqueda vectorial sin ahorrar nada.
>
> Calíbralo con tráfico real y mide el ratio de aciertos frente a la tasa de respuestas incorrectas.

> [!WARNING]
> **No caches respuestas personalizadas.** Si el prompt incluye datos del usuario (su historial, su pedido, su nombre), la caché semántica servirá la respuesta de un usuario a otro. Aplica caché semántica solo a consultas genéricas, o incorpora el identificador de tenant a la separación de índices.

> [!NOTE]
> Las políticas de caché semántica soportan **plantillas de URL**, lo que permite usar variables para los valores de endpoint del modelo.

### Prerrequisitos de infraestructura

La caché semántica **no es autónoma**. Necesitas provisionar antes:

1. Un modelo de **embeddings** en Vertex AI.
2. Un **índice de Vertex AI Vector Search** con endpoint público desplegado.
3. Una **service account** con permisos sobre ambos, asociada al entorno de Apigee.

---

## Model Armor: SanitizeUserPrompt y SanitizeModelResponse

**Model Armor** es el servicio de Google Cloud que inspecciona prompts y respuestas. Apigee lo invoca mediante estas dos políticas.

Detecta:

| Filtro | Qué detecta |
|---|---|
| `piAndJailbreakFilterResult` | Prompt injection y jailbreak |
| `raiFilterResult` | Responsible AI: contenido dañino, odio, acoso, sexual |
| `sdpFilterResult` | Sensitive Data Protection: PII, secretos, datos regulados |
| `maliciousUriFilterResult` | URLs maliciosas |
| `csamFilterFilterResult` | Material de abuso sexual infantil |

### SanitizeUserPrompt (request flow)

```xml
<SanitizeUserPrompt async="false" continueOnError="true" enabled="true" name="SUP-Sanitize-User-Prompt">
  <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
  <DisplayName>SUP-Sanitize-User-Prompt</DisplayName>
  <ModelArmor>
    <TemplateName>{modelArmorTemplate}</TemplateName>
  </ModelArmor>
  <UserPromptSource>{request_prompt_value}</UserPromptSource>
</SanitizeUserPrompt>
```

### SanitizeModelResponse (response flow)

```xml
<SanitizeModelResponse async="false" continueOnError="true" enabled="true" name="SMR-Sanitize-Model-Response">
  <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
  <DisplayName>SMR-Sanitize-Model-Response</DisplayName>
  <ModelArmor>
    <TemplateName>{modelArmorTemplate}</TemplateName>
  </ModelArmor>
  <UserPromptSource>{request_prompt_value}</UserPromptSource>
  <LLMResponseSource>{response_prompt_value}</LLMResponseSource>
</SanitizeModelResponse>
```

> [!IMPORTANT]
> Ambas usan **`continueOnError="true"`**. Es deliberado: la política **no bloquea por sí sola**. Escribe el resultado del análisis en variables y **tú decides** qué hacer con condiciones posteriores. Esto permite políticas de respuesta distintas por tipo de amenaza.

### Variables de resultado

Cada filtro deja una variable con este patrón:

```
SanitizeUserPrompt.<NOMBRE_POLITICA>.<filtro>.matchState
SanitizeModelResponse.<NOMBRE_POLITICA>.<filtro>.matchState
```

Con valor `MATCH_FOUND` cuando el filtro dispara.

### Actuar sobre las detecciones

Patrón oficial del sample: un shared flow que evalúa cada filtro y lanza un `RaiseFault` específico.

```xml
<SharedFlow name="default">
  <Step><Name>KVM-GetModelArmorConfig</Name></Step>

  <Step>
    <Name>SUP-Sanitize-User-Prompt</Name>
    <Condition>type = "user-prompt"</Condition>
  </Step>
  <Step>
    <Name>SMR-Sanitize-Model-Response</Name>
    <Condition>type = "response-prompt"</Condition>
  </Step>

  <Step>
    <Name>RF-CSAM-Detected</Name>
    <Condition>SanitizeUserPrompt.SUP-Sanitize-User-Prompt.csamFilterFilterResult.matchState = "MATCH_FOUND" or SanitizeModelResponse.SMR-Sanitize-Model-Response.csamFilterFilterResult.matchState = "MATCH_FOUND"</Condition>
  </Step>
  <Step>
    <Name>RF-MaliciousURL-Detected</Name>
    <Condition>SanitizeUserPrompt.SUP-Sanitize-User-Prompt.maliciousUriFilterResult.matchState = "MATCH_FOUND" or SanitizeModelResponse.SMR-Sanitize-Model-Response.maliciousUriFilterResult.matchState = "MATCH_FOUND"</Condition>
  </Step>
  <Step>
    <Name>RF-RAI-Detected</Name>
    <Condition>SanitizeUserPrompt.SUP-Sanitize-User-Prompt.raiFilterResult.matchState = "MATCH_FOUND" or SanitizeModelResponse.SMR-Sanitize-Model-Response.raiFilterResult.matchState = "MATCH_FOUND"</Condition>
  </Step>
  <Step>
    <Name>RF-PIAndJailbreak-Detected</Name>
    <Condition>SanitizeUserPrompt.SUP-Sanitize-User-Prompt.piAndJailbreakFilterResult.matchState = "MATCH_FOUND" or SanitizeModelResponse.SMR-Sanitize-Model-Response.piAndJailbreakFilterResult.matchState = "MATCH_FOUND"</Condition>
  </Step>
  <Step>
    <Name>RF-SDP-Detected</Name>
    <Condition>SanitizeUserPrompt.SUP-Sanitize-User-Prompt.sdpFilterResult.inspectResult.matchState = "MATCH_FOUND" or SanitizeModelResponse.SMR-Sanitize-Model-Response.sdpFilterResult.inspectResult.matchState = "MATCH_FOUND"</Condition>
  </Step>
</SharedFlow>
```

Nótese el detalle de `sdpFilterResult`: lleva un nivel extra (`.inspectResult.matchState`).

### Respuesta ante detección

El sample oficial devuelve **200 OK con un payload con forma de respuesta del modelo**, no un error HTTP:

```xml
<RaiseFault continueOnError="false" enabled="true" name="RF-PIAndJailbreak-Detected">
  <DisplayName>RF-PIAndJailbreak-Detected</DisplayName>
  <FaultResponse>
    <Set>
      <Payload contentType="application/json">
      {
        "candidates": [
            {
                "content": {
                    "role": "model",
                    "parts": [
                        { "text": "Tu prompt ha sido marcado como abusivo. Se ha registrado una revisión administrativa." }
                    ]
                },
                "finishReason": "STOP"
            }
        ],
        "modelVersion": "{model}"
      }
      </Payload>
      <StatusCode>200</StatusCode>
      <ReasonPhrase>OK</ReasonPhrase>
    </Set>
  </FaultResponse>
  <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
</RaiseFault>
```

> [!TIP]
> Devolver 200 con forma de respuesta del modelo mantiene la **compatibilidad con los SDKs de cliente**, que esperan el esquema del proveedor y romperían con un 403. La contrapartida es que el rechazo no es distinguible de una respuesta normal en las métricas HTTP — compénsalo con `DataCapture` o `MessageLogging`.

### Configuración vía KVM

El sample carga el nombre de la plantilla de Model Armor desde un KVM (`KVM-GetModelArmorConfig`), no lo hardcodea. Así se cambia la política de filtrado sin redesplegar.

---

## Composición recomendada de un proxy de LLM

```
ProxyEndpoint · PreFlow · Request
  1. CORS
  2. VerifyAPIKey                  → resuelve producto y cuota de tokens
  3. OASValidation                 → valida el esquema de la petición
  4. PromptTokenLimit              → rechaza prompts desmesurados
  5. FlowCallout → ModelArmor      → SanitizeUserPrompt + RaiseFault por filtro
  6. LLMTokenQuota (EnforceOnly)   → ¿queda cuota de tokens?
  7. SemanticCacheLookup           → si acierta, cortocircuita

TargetEndpoint · Request
  8. AssignMessage                 → selección de modelo / routing
  9. → Vertex AI, OpenAI, Anthropic…

TargetEndpoint · Response
 10. FlowCallout → ModelArmor      → SanitizeModelResponse + RaiseFault por filtro
 11. LLMTokenQuota (CountOnly)     → incrementa el contador real
 12. SemanticCachePopulate         → indexa la respuesta

PostClientFlow
 13. MessageLogging / DataCapture  → tokens, modelo, coste, detecciones
```

## Fuentes

- <https://cloud.google.com/apigee/docs/api-platform/get-started/ai-capabilities>
- <https://cloud.google.com/solutions/apigee-ai>
- <https://github.com/GoogleCloudPlatform/apigee-samples> (Apache 2.0)
- <https://cloud.google.com/security-command-center/docs/model-armor-overview>
