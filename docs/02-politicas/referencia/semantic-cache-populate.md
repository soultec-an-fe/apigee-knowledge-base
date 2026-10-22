---
id: politica-semantic-cache-populate
titulo: SemanticCachePopulate — referencia completa
area: politicas
tags: [semanticcachepopulate, cache-semantica, llm, vector-search, upsert, ttl, ia, extensible]
aplica_a: [apigee-x, apigee-hybrid]
elemento_xml: SemanticCachePopulate
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/semantic-cache-populate-policy
revisado: 2026-10-22
---

# SemanticCachePopulate — referencia completa

> [!NOTE]
> **Tipo:** Extensible. **Elemento raíz:** `<SemanticCachePopulate>`.
> **Aplica a:** Apigee X y Apigee hybrid **1.15.1 o superior** (solo en Google Cloud), en entornos Intermediate o Comprehensive. **No existe en Apigee Edge.**

SemanticCachePopulate es la mitad de escritura de la caché semántica. Se adjunta en el **flujo de respuesta** y, cuando [SemanticCacheLookup](semantic-cache-lookup.md) no encontró nada, guarda la respuesta del LLM en la caché de Apigee e inserta el embedding del prompt en el índice de Vector Search (operación `upsertDatapoints`), para que preguntas parecidas posteriores acierten.

El funcionamiento completo, los requisitos (índice con actualizaciones en streaming, cuenta de servicio con `roles/aiplatform.user`) y las limitaciones están en [SemanticCacheLookup](semantic-cache-lookup.md#cómo-funciona).

## Sintaxis completa

```xml
<SemanticCachePopulate name="SCP-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
  <SimilaritySearch>
    <VertexAI>
      <URL>https://REGION-aiplatform.googleapis.com/v1/projects/PROYECTO/locations/REGION/indexes/INDICE:upsertDatapoints</URL>
    </VertexAI>
  </SimilaritySearch>
  <TTLInSeconds>60</TTLInSeconds>
</SemanticCachePopulate>
```

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno. |
| `continueOnError` | No | `false` | Con `true`, un fallo al indexar no afecta a la respuesta ya obtenida del LLM. **Recomendado.** |
| `enabled` | No | `true` | Con `false` no se ejecuta. |
| `async` | No | `false` | **Obsoleto.** |

## Elementos hijos

| Elemento | Obligatorio | Default | Resumen |
|---|---|---|---|
| `<DisplayName>` | No | `name` | Etiqueta en la UI. |
| `<IgnoreUnresolvedVariables>` | No | `false` (la plantilla de la UI lo pone en `true`) | Con `true`, las variables sin resolver se ignoran. |
| `<SimilaritySearch>/<VertexAI>/<URL>` | **Sí** | — | Endpoint `:upsertDatapoints` **del índice** (no del endpoint del índice). |
| `<TTLInSeconds>` | No | `60` | Vida de la entrada, en segundos. |

### `<SimilaritySearch>`

Solo admite `<VertexAI>` con `<URL>`. Fíjate en que la URL es la del **índice** (`/indexes/{INDEX_ID}:upsertDatapoints`), mientras que SemanticCacheLookup usa la del **endpoint del índice** (`/indexEndpoints/{ID}:findNeighbors`). `<PrivateServiceConnect>` **no** está soportado aquí: la escritura va siempre por la API pública de Vertex AI, aunque la lectura use PSC. La URL admite plantillas: `<URL>https://{variable.url}</URL>`.

### `<TTLInSeconds>`

Segundos que dura la entrada. Los datapoints del índice vencen a ese mismo tiempo desde su inserción.

> [!WARNING]
> **Discrepancias sobre `<TTLInSeconds>`.** El texto dice que el default es `60`, pero la tabla del elemento indica "N/A". El error de despliegue se titula "must be >= 0", pero su descripción dice que **cero o negativo** hacen fallar el despliegue. Declara siempre un valor positivo.

Apigee **ignora** las cabeceras `Cache-Control` del LLM: este elemento es la única forma de controlar la vida de la entrada. Estrategias que propone Google:

| Tipo de respuesta | TTL sugerido |
|---|---|
| Genérica, no depende del usuario | Largo (p. ej. 1 hora) |
| Específica del usuario | No cachear, o corto (p. ej. 5 minutos) |
| Sensible al tiempo | Corto (p. ej. 5 minutos) |

Para invalidar antes de tiempo hay que borrar datapoints del índice con las herramientas de Vertex AI ("Update and rebuild an active index"); no hay una política de invalidación semántica.

## Variables de flujo

| Variable | Contenido |
|---|---|
| `SemanticCachePopulate.{name}.upsert_index_request` | Petición enviada a Vector Search para insertar el embedding y sus metadatos. |
| `SemanticCachePopulate.{name}.upsert_index_response` | Respuesta de Vector Search (éxito o fallo de la inserción). |

## Errores

### En runtime

| Código de fallo | HTTP | Causa |
|---|---|---|
| `steps.semanticcachepopulate.VectorSearchUpsertServiceUnavailable` | 400 | La API `upsertDatapoints` no está disponible. |
| `steps.semanticcache.populate.VectorSearchUpsertAPIFailed` | 500 | Falló la API `upsertDatapoints`. |
| `steps.semanticcache.populate.AuthenticationFailure` | 500 | La cuenta de servicio no tiene permisos. |
| `steps.semanticcache.populate.CalloutError` | 500 | Falló la llamada a Vertex AI. |
| `steps.semanticcache.populate.InternalError` | 500 | Error inesperado de la política. |

> [!NOTE]
> La tabla oficial mezcla prefijos (`steps.semanticcachepopulate.` en el primero, `steps.semanticcache.populate.` en el resto), y la respuesta de ejemplo de la página dice `SemanticCacheLookup[SC-populate]`, copiada de la otra política. Captura por `fault.name`.

Sin `continueOnError="true"`, un fallo de Vertex AI al **indexar** convierte una respuesta correcta del LLM en un error para el cliente.

### Al desplegar

| Situación | Resultado |
|---|---|
| `<PrivateServiceConnect>` en `<SimilaritySearch>` | No soportado en esta política. |
| `<URL>` vacía, inválida o con esquema distinto de `http`/`https` | Falla el despliegue. |
| `<TTLInSeconds>` cero o negativo | Falla el despliegue. |

### Variables de fallo

| Variable | Ejemplo |
|---|---|
| `fault.name` | `fault.name = "VectorSearchUpsertAPIFailed"` |
| `semanticcachepopulate.{name}.failed` | `semanticcachepopulate.SCP-Gemini.failed = true` |

## Ejemplos

### 1. Pareja con SemanticCacheLookup, solo respuestas correctas

Se indexa solo si no hubo acierto (no tiene sentido reescribir lo que ya estaba) y si el LLM respondió 200.

```xml
<SemanticCachePopulate name="SCP-Gemini" continueOnError="true">
  <SimilaritySearch>
    <VertexAI>
      <URL>https://us-central1-aiplatform.googleapis.com/v1/projects/mi-proyecto/locations/us-central1/indexes/{propertyset.vertex.index_id}:upsertDatapoints</URL>
    </VertexAI>
  </SimilaritySearch>
  <TTLInSeconds>3600</TTLInSeconds>
</SemanticCachePopulate>
```

```xml
<!-- ProxyEndpoint o TargetEndpoint, flujo de respuesta -->
<Step>
  <Name>SCP-Gemini</Name>
  <Condition>response.status.code = 200 and SemanticCacheLookup.SCL-Gemini.cache_hit != true</Condition>
</Step>
```

### 2. TTL corto para respuestas sensibles al tiempo

```xml
<SemanticCachePopulate name="SCP-Noticias" continueOnError="true">
  <SimilaritySearch>
    <VertexAI>
      <URL>https://us-central1-aiplatform.googleapis.com/v1/projects/mi-proyecto/locations/us-central1/indexes/1234567890:upsertDatapoints</URL>
    </VertexAI>
  </SimilaritySearch>
  <TTLInSeconds>300</TTLInSeconds>
</SemanticCachePopulate>
```

## Diferencias en Apigee Edge

No existe en Edge. Alternativa de caché exacta: [PopulateCache](populate-cache.md) con un hash del prompt como clave.

## Antipatrones

- Indexar respuestas de error del LLM, o respuestas que ya salieron de la caché.
- Usar la URL del endpoint del índice (`indexEndpoints`) en lugar de la del índice (`indexes`).
- TTL largo para respuestas que dependen del usuario o de datos que cambian.
- Dejar `continueOnError` en `false`.

## Fuentes

- SemanticCachePopulate policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/semantic-cache-populate-policy> (consultada directamente, contenido completo, 2026-10-22).
- Get started with semantic caching policies: <https://docs.cloud.google.com/apigee/docs/api-platform/tutorials/using-semantic-caching-policies> (consultada directamente, 2026-10-22).
