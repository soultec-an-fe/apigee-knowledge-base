---
id: politica-semantic-cache-lookup
titulo: SemanticCacheLookup — referencia completa
area: politicas
tags: [semanticcachelookup, cache-semantica, llm, embeddings, vector-search, vertex-ai, ia, extensible]
aplica_a: [apigee-x, apigee-hybrid]
elemento_xml: SemanticCacheLookup
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/semantic-cache-lookup-policy
revisado: 2026-10-22
---

# SemanticCacheLookup — referencia completa

> [!NOTE]
> **Tipo:** Extensible. **Elemento raíz:** `<SemanticCacheLookup>`.
> **Aplica a:** Apigee X y Apigee hybrid **1.15.1 o superior**, solo instalaciones de hybrid **en Google Cloud**. Requiere un entorno **Intermediate o Comprehensive**. **No existe en Apigee Edge.**

SemanticCacheLookup busca en caché una respuesta de LLM para un prompt **parecido en significado**, no idéntico. "¿Por qué el cielo es azul?" y "¿Qué hace que el cielo sea azul?" pueden devolver la misma respuesta cacheada. Si encuentra una, la devuelve sin llamar al modelo. Trabaja en pareja con [SemanticCachePopulate](semantic-cache-populate.md).

## Cómo funciona

```text
Petición ─► SemanticCacheLookup
              1. Extrae el prompt (UserPromptSource)
              2. Pide su embedding a Vertex AI (Embeddings/URL)
              3. Busca el vecino más cercano en Vector Search (SimilaritySearch)
              4. ¿Supera el umbral? ── sí ─► busca la respuesta en la caché de Apigee
                                                 └─ acierto ─► responde al cliente (cabecera Cached-Content: true)
                  └─ no ─► sigue al LLM ─► respuesta ─► SemanticCachePopulate
                                                         5. Guarda la respuesta en la caché de Apigee (TTL)
                                                         6. Inserta el embedding en el índice (upsertDatapoints)
```

- El **índice vectorial** (Vertex AI Vector Search) guarda los embeddings de los prompts.
- La **respuesta** del LLM se guarda en la caché de Apigee. Aplica el límite de **256 KB** por valor.
- La pareja reduce latencia y costo solo si el ahorro supera el costo de dos llamadas a Vertex AI por petición (embedding + búsqueda), que añaden **cientos de milisegundos**.

## Requisitos previos

| Requisito | Detalle |
|---|---|
| Proyecto con Vertex AI | APIs de Compute Engine, Vertex AI y Cloud Storage habilitadas. |
| Índice de Vector Search | Con **actualizaciones en streaming** (`indexUpdateMethod: STREAM_UPDATE`), dimensiones iguales a las del modelo de embeddings y la medida de distancia que luego declararás en `<DistanceMeasureType>`. |
| Endpoint del índice | Público (REST) o privado vía Private Service Connect (gRPC); el índice desplegado en él. El primer despliegue tarda 20-30 minutos. |
| Cuenta de servicio | Con `roles/aiplatform.user`; el proxy se **despliega con esa cuenta de servicio**. |
| Región | Idealmente la misma que la instancia de Apigee. Vector Search no está en todas las regiones. |
| Plantilla | La consola ofrece la plantilla de proxy "Proxy with Semantic Cache", que ya adjunta las dos políticas. |

Si el entorno tiene configurado un **forward proxy**, las llamadas de la política a Vertex AI pasan por él sin configuración adicional (Apigee y hybrid 1.16.10+ o 1.17.0+). Excepción: la búsqueda por Private Service Connect va directa por gRPC y **no** pasa por el forward proxy.

## Sintaxis completa

```xml
<SemanticCacheLookup name="SCL-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>
  <UserPromptSource>{jsonPath('$.contents[-1].parts[-1].text',request.content,true)}</UserPromptSource>
  <Embeddings>
    <VertexAI>
      <URL>https://REGION-aiplatform.googleapis.com/v1/projects/PROYECTO/locations/REGION/publishers/google/models/MODELO:predict</URL>
    </VertexAI>
  </Embeddings>
  <SimilaritySearch>
    <VertexAI>
      <URL>https://DOMINIO_PUBLICO/v1/projects/PROYECTO/locations/REGION/indexEndpoints/ENDPOINT:findNeighbors</URL>
      <DeployedIndexID>ID_DEL_INDICE_DESPLEGADO</DeployedIndexID>
      <Threshold>0.95</Threshold>
      <DistanceMeasureType>DOT_PRODUCT_DISTANCE</DistanceMeasureType>
    </VertexAI>
  </SimilaritySearch>
</SemanticCacheLookup>
```

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno. |
| `continueOnError` | No | `false` | Con `true`, un fallo de Vertex AI no corta la petición: sigue al LLM sin caché. **Recomendado**, ver [Errores](#errores). |
| `enabled` | No | `true` | Con `false` no se ejecuta. |
| `async` | No | `false` | **Obsoleto.** |

## Elementos hijos

| Elemento | Obligatorio | Default | Resumen |
|---|---|---|---|
| `<DisplayName>` | No | `name` | Etiqueta en la UI. |
| `<IgnoreUnresolvedVariables>` | No | `false` | Con `true`, las variables sin resolver se ignoran. |
| `<UserPromptSource>` | No | `{jsonPath('$.contents[-1].parts[-1].text',request.content,true)}` | Plantilla que extrae el texto del prompt. Solo admite valores de texto. |
| `<Embeddings>/<VertexAI>/<URL>` | **Sí** | — | Endpoint `:predict` del modelo de embeddings. |
| `<SimilaritySearch>/<VertexAI>` | **Sí** | — | Dónde y cómo buscar el vecino más cercano. |
| `.../<URL>` | Uno de los dos | — | Endpoint público `:findNeighbors` (REST). |
| `.../<PrivateServiceConnect>/<GrpcEndpoint>` | Uno de los dos | — | Endpoint privado (gRPC). |
| `.../<DeployedIndexID>` | **Sí** | — | ID del índice desplegado en el endpoint. Sin espacios. |
| `.../<Threshold>` | No | `0.9` | Umbral de similitud. |
| `.../<DistanceMeasureType>` | No | `DOT_PRODUCT_DISTANCE` | Medida con la que se construyó el índice. |

### `<UserPromptSource>`

[Plantilla de mensaje](../../01-proxies/04-variables-de-flujo.md); el default es la ruta del **último** texto de una petición de Gemini (`generateContent`). Para otro formato de petición, ajusta la ruta. Si no se puede extraer, falla con `FailedToExtractUserPrompt`.

> [!WARNING]
> Con el default solo se compara **el último mensaje**. En una conversación de varios turnos, dos preguntas iguales con historiales distintos se considerarían la misma y recibirían la misma respuesta. Para chats con contexto, o no uses caché semántica, o incluye en el texto extraído lo que distinga el contexto.

### `<Embeddings>`

Solo admite `<VertexAI>` con `<URL>` (endpoint `:predict` de un modelo de embeddings de texto soportado; el tutorial oficial usa `text-embedding-004`). **No** admite Private Service Connect: usarlo hace fallar el despliegue. La URL admite plantillas: `<URL>https://{variable.url}</URL>`.

### `<SimilaritySearch>`

Exactamente **uno** de los dos transportes dentro de `<VertexAI>`:

| Transporte | Elemento | Protocolo | Notas |
|---|---|---|---|
| Endpoint público | `<URL>…:findNeighbors</URL>` | REST | Admite plantillas en la URL. |
| Endpoint privado (PSC) | `<PrivateServiceConnect><GrpcEndpoint>grpc://HOST:10000</GrpcEndpoint></PrivateServiceConnect>` | gRPC | Apigee y hybrid ≥ 1.17.0. Esquema `grpc://` obligatorio; `grpcs://` (TLS) **no** está soportado; puerto 10000; `HOST` es la IP del endpoint attachment o un registro de DNS privado en una zona peered. |

> [!IMPORTANT]
> El salto gRPC al endpoint privado va **en texto plano y sin autenticación**: su seguridad depende por completo del aislamiento de red. Si tu política de seguridad exige cifrado en tránsito también dentro de la VPC, el endpoint público sobre HTTPS es la opción que lo cumple.

Solo se usa **el vecino más cercano** que supera el umbral.

### `<Threshold>` y `<DistanceMeasureType>`

La medida decide la **dirección** de la comparación:

| `<DistanceMeasureType>` | Hay acierto si | Tipo |
|---|---|---|
| `DOT_PRODUCT_DISTANCE` (default) | `valor >= umbral` | Similitud: más alto = más parecido |
| `COSINE_DISTANCE` | `valor <= umbral` | Distancia: más bajo = más parecido |
| `SQUARED_L2_DISTANCE` | `valor <= umbral` | Distancia |
| `L1_DISTANCE` | `valor <= umbral` | Distancia |

- `<DistanceMeasureType>` **debe coincidir** con la medida del índice. Compruébala con `gcloud ai indexes describe INDEX_ID --region=REGION` (campo `distanceMeasureType`). Un valor fuera de los cuatro hace fallar el despliegue; la comparación es exacta, en mayúsculas.
- Disponible en Apigee `1-18-0-apigee-4` o posterior y en hybrid ≥ 1.17.0. **En versiones anteriores se acepta pero se ignora en silencio** y se compara como `DOT_PRODUCT_DISTANCE`: con un índice de distancia coseno, eso invierte la lógica del umbral.
- `<Threshold>` default `0.9`, pensado para producto escalar; el tutorial recomienda `0.95`. Un umbral demasiado permisivo devuelve respuestas a preguntas que solo se parecen. `NaN` no se admite; `Infinity` y `-Infinity`, sí.
- Google recomienda **vectores normalizados**. Desaconseja `L1_DISTANCE` con normalización L2, porque la distancia escala con la raíz de la dimensión.

Para confirmar qué medida aplicó la política y qué valor devolvió el índice, envía la misma petición dos veces y mira en Debug `semanticcache.lookup.{name}.measure_type` y `.nearest_neighbor_measure`.

> [!NOTE]
> El tutorial oficial escribe el elemento como `<DeployedIndexId>`, con *d* minúscula; la referencia y todos los ejemplos XML usan `<DeployedIndexID>`. Usa el de la referencia.

## Variables de flujo

Todas de solo lectura; se pueden usar con [DataCapture](../04-extension.md) para analítica propia.

| Variable | Contenido |
|---|---|
| `SemanticCacheLookup.{name}.user_prompt` | Texto extraído del prompt. |
| `SemanticCacheLookup.{name}.embeddings_request` | Petición enviada a la API de embeddings. |
| `SemanticCacheLookup.{name}.embeddings_response` | Respuesta de la API de embeddings. |
| `SemanticCacheLookup.{name}.dense_embeddings` | Vector numérico. |
| `SemanticCacheLookup.{name}.is_nearest_neighbor_hit` | Si hubo vecino que supera el umbral. |
| `SemanticCacheLookup.{name}.cache_hit` | Si la respuesta se encontró en la caché. |
| `SemanticCacheLookup.{name}.cached_llm_response` | Respuesta cacheada, si hubo acierto. |
| `semanticcache.lookup.{name}.nearest_neighbor_measure` | Valor crudo del vecino más cercano (en aciertos y fallos). |
| `semanticcache.lookup.{name}.measure_type` | Medida aplicada, incluido el default. |

> [!NOTE]
> Fíjate en el prefijo: las siete primeras usan `SemanticCacheLookup.` (con mayúsculas) y las dos últimas `semanticcache.lookup.`. Así aparecen en la página oficial.

`user_prompt` y `cached_llm_response` contienen texto de usuarios y del modelo: no las registres sin filtrar datos personales.

## Errores

### En runtime

| Código de fallo | HTTP | Causa |
|---|---|---|
| `steps.semanticcache.lookup.MessageTemplateExtractionFailed` | 400 | Falló el JSONPath sobre la petición. |
| `steps.semanticcache.lookup.FailedToExtractUserPrompt` | 500 | No se pudo extraer el prompt. |
| `steps.semanticcache.lookup.EmbeddingsServiceUnavailable` | 400 | Servicio de embeddings no disponible. |
| `steps.semanticcache.lookup.EmbeddingsAPIFailed` | 400 | Falló la API de embeddings. |
| `steps.semanticcache.lookup.VectorSearchServiceUnavailable` | 400 | Vector Search no disponible. |
| `steps.semanticcache.lookup.VectorSearchAPIFailed` | 400 | Falló Vector Search. |
| `steps.semanticcache.lookup.AuthenticationFailure` | 500 | La cuenta de servicio no tiene permisos. |
| `steps.semanticcache.lookup.InternalError` | 500 | Error inesperado de la política. |
| `steps.semanticcache.lookup.CalloutError` | 500 | Falló la llamada a Vertex AI. |

> [!IMPORTANT]
> Que Vertex AI no esté disponible devuelve un **400 al cliente**, como si la petición fuera inválida, y corta el flujo. Una caché no debería tumbar el servicio: declara `continueOnError="true"` para que, si falla, la petición siga al LLM.

La respuesta de ejemplo de la página usa el prefijo `steps.semanticcachelookup.` (sin punto intermedio) y el código `UnresolvedVariable`, que no aparece en la tabla. Captura por `fault.name`, que es la última parte del código y es igual con cualquiera de los dos prefijos.

### Al desplegar

Los errores de despliegue son mensajes de texto, no códigos. Los principales:

| Situación | Resultado |
|---|---|
| `<VertexAI>` vacío en `<Embeddings>` o en `<SimilaritySearch>` | Falla el despliegue. |
| `<URL>` y `<PrivateServiceConnect>` a la vez, o ninguno | Falla el despliegue. |
| `<PrivateServiceConnect>` dentro de `<Embeddings>` | No soportado. |
| URL vacía, inválida o con esquema distinto de `http`/`https` | Falla el despliegue. |
| `<GrpcEndpoint>` sin el formato `grpc://HOST:PUERTO` | Falla el despliegue. |
| `<Threshold>` = `NaN` | Falla el despliegue. |
| `<DistanceMeasureType>` desconocido | Falla el despliegue. |
| `<DeployedIndexID>` vacío o con espacios | Falla el despliegue. |

### Variables de fallo

| Variable | Ejemplo |
|---|---|
| `fault.name` | `fault.name = "EmbeddingsServiceUnavailable"` |
| `semanticcachelookup.{name}.failed` | `semanticcachelookup.SCL-Gemini.failed = true` |

## Ejemplos

### 1. Caché semántica para un proxy de Gemini

```xml
<SemanticCacheLookup name="SCL-Gemini" continueOnError="true">
  <UserPromptSource>{jsonPath('$.contents[-1].parts[-1].text',request.content,true)}</UserPromptSource>
  <Embeddings>
    <VertexAI>
      <URL>https://us-central1-aiplatform.googleapis.com/v1/projects/mi-proyecto/locations/us-central1/publishers/google/models/text-embedding-004:predict</URL>
    </VertexAI>
  </Embeddings>
  <SimilaritySearch>
    <VertexAI>
      <URL>https://{propertyset.vertex.dominio_indice}/v1/projects/mi-proyecto/locations/us-central1/indexEndpoints/{propertyset.vertex.endpoint_id}:findNeighbors</URL>
      <DeployedIndexID>semantic_cache</DeployedIndexID>
      <Threshold>0.95</Threshold>
      <DistanceMeasureType>DOT_PRODUCT_DISTANCE</DistanceMeasureType>
    </VertexAI>
  </SimilaritySearch>
</SemanticCacheLookup>
```

### 2. Índice privado por Private Service Connect

```xml
<SemanticCacheLookup name="SCL-Privado" continueOnError="true">
  <Embeddings>
    <VertexAI>
      <URL>https://us-central1-aiplatform.googleapis.com/v1/projects/mi-proyecto/locations/us-central1/publishers/google/models/text-embedding-004:predict</URL>
    </VertexAI>
  </Embeddings>
  <SimilaritySearch>
    <VertexAI>
      <PrivateServiceConnect>
        <GrpcEndpoint>grpc://10.20.0.5:10000</GrpcEndpoint>
      </PrivateServiceConnect>
      <DeployedIndexID>semantic_cache_psc</DeployedIndexID>
      <Threshold>0.1</Threshold>
      <DistanceMeasureType>COSINE_DISTANCE</DistanceMeasureType>
    </VertexAI>
  </SimilaritySearch>
</SemanticCacheLookup>
```

Con `COSINE_DISTANCE`, el umbral es una **distancia máxima**: `0.1` acepta solo vecinos muy cercanos.

### 3. No cachear peticiones con datos personales

Google recomienda usar Model Armor para no cachear datos sensibles. Coloca antes una [SanitizeUserPrompt](../05-politicas-ai.md#model-armor-sanitizeuserprompt-y-sanitizemodelresponse) y, a partir de sus variables de resultado, fija una variable propia (aquí `flujo.no_cachear`, con AssignMessage o JavaScript). Luego condiciona las dos políticas de caché semántica:

```xml
<Step>
  <Name>SCL-Gemini</Name>
  <Condition>flujo.no_cachear != "true"</Condition>
</Step>
```

## Limitaciones

- **No funciona con SSE**: no se admite en proxies que usan `EventFlow` para streaming.
- Apigee **ignora las cabeceras `Cache-Control`** que devuelva el LLM; la vida la marca el `<TTLInSeconds>` de SemanticCachePopulate.
- Si el umbral es permisivo o el modelo de embeddings no distingue bien preguntas con matices, se devolverán **respuestas incorrectas u obsoletas**.
- En hybrid, solo instalaciones en Google Cloud.
- Para mucho QPS puede hacer falta subir cuotas de Vertex AI: peticiones de predicción online por región, por modelo base, y actualizaciones de streaming de Vector Search (Matching Engine).

## Diferencias en Apigee Edge

No existe en Edge, y no hay equivalente directo. La alternativa más cercana es la caché exacta con [LookupCache](lookup-cache.md) usando como clave un hash del prompt normalizado: solo acierta con prompts idénticos.

## Antipatrones

- Cachear respuestas personalizadas o con datos del usuario (el tutorial recomienda no cachear o usar TTL cortos, del orden de 5 minutos).
- `<DistanceMeasureType>` distinto de la medida real del índice, o declararlo en una versión que lo ignora.
- Dejar `continueOnError` en `false`: una caída de Vertex AI tumba el API.
- Usarla en conversaciones multi-turno extrayendo solo el último mensaje.

## Fuentes

- SemanticCacheLookup policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/semantic-cache-lookup-policy> (consultada directamente, contenido completo, 2026-10-22).
- Get started with semantic caching policies: <https://docs.cloud.google.com/apigee/docs/api-platform/tutorials/using-semantic-caching-policies> (consultada directamente, 2026-10-22).
- Semantic caching with a private (PSC) endpoint: <https://docs.cloud.google.com/apigee/docs/api-platform/tutorials/using-semantic-caching-policies-psc>
