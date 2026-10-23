---
id: ejemplos-apigee-samples
titulo: Mapa de ejemplos — GoogleCloudPlatform/apigee-samples
area: ejemplos
tags: [ejemplos, apigee-samples, samples]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://github.com/GoogleCloudPlatform/apigee-samples
revisado: 2026-10-23
---

<!-- Archivo generado por scripts/generar_mapa_ejemplos.py. No editar a mano. -->

# Mapa de ejemplos — GoogleCloudPlatform/apigee-samples

> **Fecha de corte: 2026-10-23.** Ediciones: Apigee X y hybrid. Repositorio: <https://github.com/GoogleCloudPlatform/apigee-samples>.

Repositorio activo y principal de ejemplos de Google (Apache 2.0). Cada carpeta trae su README y, en la mayoría de los casos, un tutorial de Cloud Shell.

La columna **Políticas** se extrae automáticamente de los XML de cada bundle (`scripts/mapa_ejemplos.py`); enlaza con la referencia de cada política. Una celda vacía indica que el ejemplo no trae bundles (scripts, Terraform, notebooks, portales).

## API hub

| Ejemplo | Qué muestra | Políticas | En este repo |
|---|---|---|---|
| [`apihub-plugins`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/apihub-plugins) | Plugins para sincronizar metadatos de Azure APIM y AWS API Gateway con API hub. |  | [02-integraciones-y-funciones](../docs/12-api-hub/02-integraciones-y-funciones.md) |
| [`apihub-portal-publish`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/apihub-portal-publish) | De API no gestionada en API hub a proxy gestionado publicado en el portal. |  | [02-integraciones-y-funciones](../docs/12-api-hub/02-integraciones-y-funciones.md) |

## Adaptadores

| Ejemplo | Qué muestra | Políticas | En este repo |
|---|---|---|---|
| [`extension-processor-grpc`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/extension-processor-grpc) | Extension Processor con tráfico gRPC. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [VerifyAPIKey](../docs/02-politicas/referencia/verify-api-key.md) | [02-extension-processor](../docs/16-adaptadores/02-extension-processor.md) |
| [`extension-processor-http`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/extension-processor-http) | Políticas de Apigee sobre un Application Load Balancer con el Extension Processor (HTTP). | [VerifyAPIKey](../docs/02-politicas/referencia/verify-api-key.md) | [02-extension-processor](../docs/16-adaptadores/02-extension-processor.md) |

## Arquitectura

| Ejemplo | Qué muestra | Políticas | En este repo |
|---|---|---|---|
| [`monolith-to-microservices-based-on-paths`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/monolith-to-microservices-based-on-paths) | Fachada para migrar de monolito a microservicios por rutas. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [CORS](../docs/02-politicas/referencia/cors.md), [Javascript](../docs/02-politicas/referencia/javascript.md), [KeyValueMapOperations](../docs/02-politicas/referencia/key-value-map-operations.md), [RaiseFault](../docs/02-politicas/referencia/raise-fault.md) | [02-flujos-y-pipeline](../docs/01-proxies/02-flujos-y-pipeline.md) |
| [`traffic-mirroring-sharedflow`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/traffic-mirroring-sharedflow) | Tráfico espejo (*shadow*) con un shared flow para probar endpoints nuevos sin afectar la respuesta. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [FlowCallout](../docs/02-politicas/referencia/flow-callout.md), [ServiceCallout](../docs/02-politicas/referencia/service-callout.md) | [06-shared-flows-y-flow-hooks](../docs/01-proxies/06-shared-flows-y-flow-hooks.md) |

## DevOps

| Ejemplo | Qué muestra | Políticas | En este repo |
|---|---|---|---|
| [`deploy-apigee-config`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/deploy-apigee-config) | Despliegue de configuración (KVM, target servers, productos…) con el plugin Maven y Cloud Build. |  | [02-herramientas-cli](../docs/06-devops/02-herramientas-cli.md) |
| [`deploy-apigee-proxy`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/deploy-apigee-proxy) | Despliegue de un proxy con el plugin Maven de Apigee y Cloud Build. |  | [03-cicd-github-actions](../docs/06-devops/03-cicd-github-actions.md), [02-herramientas-cli](../docs/06-devops/02-herramientas-cli.md) |
| [`deploy-apigee-sharedflow`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/deploy-apigee-sharedflow) | Despliegue de un shared flow con el plugin Maven y Cloud Build. | [Quota](../docs/02-politicas/referencia/quota.md), [SpikeArrest](../docs/02-politicas/referencia/spike-arrest.md), [VerifyAPIKey](../docs/02-politicas/referencia/verify-api-key.md) | [06-shared-flows-y-flow-hooks](../docs/01-proxies/06-shared-flows-y-flow-hooks.md), [02-herramientas-cli](../docs/06-devops/02-herramientas-cli.md) |

## Extensión

| Ejemplo | Qué muestra | Políticas | En este repo |
|---|---|---|---|
| [`java-callout`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/java-callout) | Uso de la política JavaCallout. | [JavaCallout](../docs/02-politicas/referencia/java-callout.md) | [java-callout](../docs/02-politicas/referencia/java-callout.md) |

## IA

| Ejemplo | Qué muestra | Políticas | En este repo |
|---|---|---|---|
| [`llm-circuit-breaking`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/llm-circuit-breaking) | *Circuit breaking* entre varios LLM en aplicaciones RAG. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [DataCapture](../docs/02-politicas/referencia/data-capture.md), [ExtractVariables](../docs/02-politicas/referencia/extract-variables.md), [Quota](../docs/02-politicas/referencia/quota.md), [ServiceCallout](../docs/02-politicas/referencia/service-callout.md) | [01-apigee-como-ai-gateway](../docs/07-ai-gateway/01-apigee-como-ai-gateway.md) |
| [`llm-function-calling`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/llm-function-calling) | Proxy configurado como *function call* de un LLM. | [CORS](../docs/02-politicas/referencia/cors.md), [ExtractVariables](../docs/02-politicas/referencia/extract-variables.md), [Javascript](../docs/02-politicas/referencia/javascript.md), [VerifyAPIKey](../docs/02-politicas/referencia/verify-api-key.md) | [01-apigee-como-ai-gateway](../docs/07-ai-gateway/01-apigee-como-ai-gateway.md) |
| [`llm-inference-gateway`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/llm-inference-gateway) | Apigee con GKE Inference Gateway para autorización y límites. | [ExtractVariables](../docs/02-politicas/referencia/extract-variables.md), [Quota](../docs/02-politicas/referencia/quota.md), [VerifyAPIKey](../docs/02-politicas/referencia/verify-api-key.md) | [02-extension-processor](../docs/16-adaptadores/02-extension-processor.md) |
| [`llm-logging`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/llm-logging) | Registro de prompts y respuestas de LLM. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [ExtractVariables](../docs/02-politicas/referencia/extract-variables.md), [FlowCallout](../docs/02-politicas/referencia/flow-callout.md), [MessageLogging](../docs/02-politicas/referencia/message-logging.md) | [message-logging](../docs/02-politicas/referencia/message-logging.md) |
| [`llm-routing`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/llm-routing) | Enrutamiento entre proveedores de LLM. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [CORS](../docs/02-politicas/referencia/cors.md), [ExtractVariables](../docs/02-politicas/referencia/extract-variables.md), [KeyValueMapOperations](../docs/02-politicas/referencia/key-value-map-operations.md), [MessageLogging](../docs/02-politicas/referencia/message-logging.md), [OASValidation](../docs/02-politicas/referencia/oas-validation.md), [VerifyAPIKey](../docs/02-politicas/referencia/verify-api-key.md) | [01-apigee-como-ai-gateway](../docs/07-ai-gateway/01-apigee-como-ai-gateway.md) |
| [`llm-security`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/llm-security) | Model Armor sobre los prompts (versión con código propio). | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [CORS](../docs/02-politicas/referencia/cors.md), [ExtractVariables](../docs/02-politicas/referencia/extract-variables.md), [FlowCallout](../docs/02-politicas/referencia/flow-callout.md), [KeyValueMapOperations](../docs/02-politicas/referencia/key-value-map-operations.md), [OASValidation](../docs/02-politicas/referencia/oas-validation.md), [RaiseFault](../docs/02-politicas/referencia/raise-fault.md), [ServiceCallout](../docs/02-politicas/referencia/service-callout.md), [VerifyAPIKey](../docs/02-politicas/referencia/verify-api-key.md) | [01-apigee-como-ai-gateway](../docs/07-ai-gateway/01-apigee-como-ai-gateway.md) |
| [`llm-security-v2`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/llm-security-v2) | Model Armor con las políticas estándar SanitizeUserPrompt y SanitizeModelResponse. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [CORS](../docs/02-politicas/referencia/cors.md), [ExtractVariables](../docs/02-politicas/referencia/extract-variables.md), [FlowCallout](../docs/02-politicas/referencia/flow-callout.md), [KeyValueMapOperations](../docs/02-politicas/referencia/key-value-map-operations.md), [OASValidation](../docs/02-politicas/referencia/oas-validation.md), [RaiseFault](../docs/02-politicas/referencia/raise-fault.md), [SanitizeModelResponse](../docs/02-politicas/referencia/sanitize-llm-response.md), [SanitizeUserPrompt](../docs/02-politicas/referencia/sanitize-user-prompt.md), [VerifyAPIKey](../docs/02-politicas/referencia/verify-api-key.md) | [sanitize-user-prompt](../docs/02-politicas/referencia/sanitize-user-prompt.md), [sanitize-llm-response](../docs/02-politicas/referencia/sanitize-llm-response.md) |
| [`llm-semantic-cache`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/llm-semantic-cache) | Caché semántica con la capa de caché de Apigee y Vector Search (versión con código propio). | [AssertCondition](../docs/02-politicas/referencia/assert-condition.md), [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [ExtractVariables](../docs/02-politicas/referencia/extract-variables.md), [FlowCallout](../docs/02-politicas/referencia/flow-callout.md), [Javascript](../docs/02-politicas/referencia/javascript.md), [LookupCache](../docs/02-politicas/referencia/lookup-cache.md), [PopulateCache](../docs/02-politicas/referencia/populate-cache.md), [ServiceCallout](../docs/02-politicas/referencia/service-callout.md) | [01-apigee-como-ai-gateway](../docs/07-ai-gateway/01-apigee-como-ai-gateway.md) |
| [`llm-semantic-cache-v2`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/llm-semantic-cache-v2) | Caché semántica con las políticas estándar SemanticCacheLookup y SemanticCachePopulate. | [SemanticCacheLookup](../docs/02-politicas/referencia/semantic-cache-lookup.md), [SemanticCachePopulate](../docs/02-politicas/referencia/semantic-cache-populate.md) | [semantic-cache-lookup](../docs/02-politicas/referencia/semantic-cache-lookup.md), [semantic-cache-populate](../docs/02-politicas/referencia/semantic-cache-populate.md) |
| [`llm-sse-logging`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/llm-sse-logging) | Streaming SSE con registro de la respuesta en Cloud Logging. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [ExtractVariables](../docs/02-politicas/referencia/extract-variables.md), [Javascript](../docs/02-politicas/referencia/javascript.md), [MessageLogging](../docs/02-politicas/referencia/message-logging.md) | [message-logging](../docs/02-politicas/referencia/message-logging.md) |
| [`llm-sse-security`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/llm-sse-security) | Streaming SSE con Model Armor sobre la respuesta. | [ExtractVariables](../docs/02-politicas/referencia/extract-variables.md), [Javascript](../docs/02-politicas/referencia/javascript.md), [KeyValueMapOperations](../docs/02-politicas/referencia/key-value-map-operations.md), [SanitizeModelResponse](../docs/02-politicas/referencia/sanitize-llm-response.md), [VerifyAPIKey](../docs/02-politicas/referencia/verify-api-key.md) | [sanitize-llm-response](../docs/02-politicas/referencia/sanitize-llm-response.md) |
| [`llm-token-limits`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/llm-token-limits) | Límites de consumo de tokens de LLM por API product. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [DataCapture](../docs/02-politicas/referencia/data-capture.md), [ExtractVariables](../docs/02-politicas/referencia/extract-variables.md), [Quota](../docs/02-politicas/referencia/quota.md), [VerifyAPIKey](../docs/02-politicas/referencia/verify-api-key.md) | [llm-token-quota](../docs/02-politicas/referencia/llm-token-quota.md), [01-apigee-como-ai-gateway](../docs/07-ai-gateway/01-apigee-como-ai-gateway.md) |
| [`llm-token-limits-per-user`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/llm-token-limits-per-user) | Límites de tokens por usuario final. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [DataCapture](../docs/02-politicas/referencia/data-capture.md), [ExtractVariables](../docs/02-politicas/referencia/extract-variables.md), [Quota](../docs/02-politicas/referencia/quota.md), [VerifyAPIKey](../docs/02-politicas/referencia/verify-api-key.md) | [llm-token-quota](../docs/02-politicas/referencia/llm-token-quota.md) |
| [`llm-token-limits-v2`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/llm-token-limits-v2) | Límites de tokens con las políticas estándar (LLMTokenQuota, PromptTokenLimit). | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [DataCapture](../docs/02-politicas/referencia/data-capture.md), [ExtractVariables](../docs/02-politicas/referencia/extract-variables.md), [LLMTokenQuota](../docs/02-politicas/referencia/llm-token-quota.md), [VerifyAPIKey](../docs/02-politicas/referencia/verify-api-key.md) | [llm-token-quota](../docs/02-politicas/referencia/llm-token-quota.md), [prompt-token-limit](../docs/02-politicas/referencia/prompt-token-limit.md) |
| [`llm-vertexai-agent`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/llm-vertexai-agent) | Agente de Vertex Agent Builder detrás de un proxy de Apigee. | [CORS](../docs/02-politicas/referencia/cors.md), [ExtractVariables](../docs/02-politicas/referencia/extract-variables.md), [Javascript](../docs/02-politicas/referencia/javascript.md), [VerifyAPIKey](../docs/02-politicas/referencia/verify-api-key.md) | [01-apigee-como-ai-gateway](../docs/07-ai-gateway/01-apigee-como-ai-gateway.md) |

## Integración GCP

| Ejemplo | Qué muestra | Políticas | En este repo |
|---|---|---|---|
| [`cloud-functions`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/cloud-functions) | Proxy hacia una app en Cloud Functions. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [Javascript](../docs/02-politicas/referencia/javascript.md), [RaiseFault](../docs/02-politicas/referencia/raise-fault.md) | [05-target-endpoints-y-servidores](../docs/01-proxies/05-target-endpoints-y-servidores.md) |
| [`cloud-run`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/cloud-run) | Invocar un servicio de Cloud Run desde Apigee con autenticación de Google. |  | [05-target-endpoints-y-servidores](../docs/01-proxies/05-target-endpoints-y-servidores.md) |

## MCP y agentes

| Ejemplo | Qué muestra | Políticas | En este repo |
|---|---|---|---|
| [`adk-auto-insurance-agent`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/adk-auto-insurance-agent) | Agente ADK de seguros que usa APIs de API hub como herramientas. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [CORS](../docs/02-politicas/referencia/cors.md), [ExtractVariables](../docs/02-politicas/referencia/extract-variables.md), [Javascript](../docs/02-politicas/referencia/javascript.md), [VerifyAPIKey](../docs/02-politicas/referencia/verify-api-key.md) | [02-integraciones-y-funciones](../docs/12-api-hub/02-integraciones-y-funciones.md) |
| [`apigee-mcp`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/apigee-mcp) | Servidor MCP que descubre especificaciones en API hub y las expone como *tools* a través de Apigee. | [AccessEntity](../docs/02-politicas/referencia/access-entity.md), [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [ExtractVariables](../docs/02-politicas/referencia/extract-variables.md), [OAuthV2](../docs/02-politicas/referencia/oauthv2.md), [RaiseFault](../docs/02-politicas/referencia/raise-fault.md), [VerifyAPIKey](../docs/02-politicas/referencia/verify-api-key.md), [XMLToJSON](../docs/02-politicas/referencia/xml-json.md) | [02-mcp-en-apigee](../docs/07-ai-gateway/02-mcp-en-apigee.md) |

## Mediación

| Ejemplo | Qué muestra | Políticas | En este repo |
|---|---|---|---|
| [`composite-api`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/composite-api) | API compuesta que combina varias llamadas a backends. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [ExtractVariables](../docs/02-politicas/referencia/extract-variables.md), [ServiceCallout](../docs/02-politicas/referencia/service-callout.md) | [service-callout](../docs/02-politicas/referencia/service-callout.md) |
| [`cors`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/cors) | CORS para llamadas desde navegadores. | [CORS](../docs/02-politicas/referencia/cors.md) | [cors](../docs/02-politicas/referencia/cors.md) |
| [`extract-variables`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/extract-variables) | Extraer variables y fijar cabeceras con ExtractVariables y AssignMessage. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [ExtractVariables](../docs/02-politicas/referencia/extract-variables.md), [XMLToJSON](../docs/02-politicas/referencia/xml-json.md) | [extract-variables](../docs/02-politicas/referencia/extract-variables.md), [assign-message](../docs/02-politicas/referencia/assign-message.md) |
| [`property-set`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/property-set) | Leer un PropertySet desde AssignMessage. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [Javascript](../docs/02-politicas/referencia/javascript.md) | [read-property-set](../docs/02-politicas/referencia/read-property-set.md) |

## Operación

| Ejemplo | Qué muestra | Políticas | En este repo |
|---|---|---|---|
| [`cloud-logging`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/cloud-logging) | Logs personalizados a Cloud Logging con MessageLogging. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [MessageLogging](../docs/02-politicas/referencia/message-logging.md) | [message-logging](../docs/02-politicas/referencia/message-logging.md) |

## Portales

| Ejemplo | Qué muestra | Políticas | En este repo |
|---|---|---|---|
| [`drupal-developer-portal`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/drupal-developer-portal) | Portal Drupal desde GCP Marketplace con el catálogo de productos. | [CORS](../docs/02-politicas/referencia/cors.md), [VerifyAPIKey](../docs/02-politicas/referencia/verify-api-key.md) | [02-developers-apps](../docs/04-publicacion/02-developers-apps.md) |
| [`integrated-developer-portal`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/integrated-developer-portal) | Portal integrado de Apigee y publicación de API products en su catálogo. | [CORS](../docs/02-politicas/referencia/cors.md), [VerifyAPIKey](../docs/02-politicas/referencia/verify-api-key.md) | [02-developers-apps](../docs/04-publicacion/02-developers-apps.md) |
| [`publish-to-apigee-portal`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/publish-to-apigee-portal) | Publicar una especificación OpenAPI en el portal integrado con Maven y Cloud Build. |  | [02-herramientas-cli](../docs/06-devops/02-herramientas-cli.md) |

## Protocolos

| Ejemplo | Qué muestra | Políticas | En este repo |
|---|---|---|---|
| [`grpc`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/grpc) | Exponer un servicio gRPC en Cloud Run de forma segura. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [VerifyAPIKey](../docs/02-politicas/referencia/verify-api-key.md) | [05-target-endpoints-y-servidores](../docs/01-proxies/05-target-endpoints-y-servidores.md) |
| [`grpc-web`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/grpc-web) | Proxy hacia un servicio gRPC-Web en Cloud Run. | [JavaCallout](../docs/02-politicas/referencia/java-callout.md), [RaiseFault](../docs/02-politicas/referencia/raise-fault.md), [RegularExpressionProtection](../docs/02-politicas/referencia/regular-expression-protection.md) | [05-target-endpoints-y-servidores](../docs/01-proxies/05-target-endpoints-y-servidores.md) |
| [`websockets`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/websockets) | Exponer un servidor de WebSockets en Cloud Run de forma segura. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [VerifyAPIKey](../docs/02-politicas/referencia/verify-api-key.md) | [05-target-endpoints-y-servidores](../docs/01-proxies/05-target-endpoints-y-servidores.md) |

## Publicación

| Ejemplo | Qué muestra | Políticas | En este repo |
|---|---|---|---|
| [`apiproduct-operations`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/apiproduct-operations) | Comportamiento de las *operations* de un API product. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [Javascript](../docs/02-politicas/referencia/javascript.md), [OAuthV2](../docs/02-politicas/referencia/oauthv2.md), [RaiseFault](../docs/02-politicas/referencia/raise-fault.md), [VerifyAPIKey](../docs/02-politicas/referencia/verify-api-key.md) | [01-api-products](../docs/04-publicacion/01-api-products.md) |

## Redes

| Ejemplo | Qué muestra | Políticas | En este repo |
|---|---|---|---|
| [`exposing-to-internet`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/exposing-to-internet) | Exponer una instancia a internet con un balanceador HTTP(S) externo. |  | [03-redes-y-acceso](../docs/15-administracion/03-redes-y-acceso.md) |

## Seguridad

| Ejemplo | Qué muestra | Políticas | En este repo |
|---|---|---|---|
| [`authorize-idp-access-tokens`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/authorize-idp-access-tokens) | Autoriza access tokens JWT emitidos por un proveedor de identidad externo. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [FlowCallout](../docs/02-politicas/referencia/flow-callout.md), [GenerateJWT](../docs/02-politicas/referencia/generate-jwt.md), [GetOAuthV2Info](../docs/02-politicas/referencia/get-oauth-v2-info.md), [OAuthV2](../docs/02-politicas/referencia/oauthv2.md), [VerifyAPIKey](../docs/02-politicas/referencia/verify-api-key.md), [VerifyJWT](../docs/02-politicas/referencia/verify-jwt.md) | [verify-jwt](../docs/02-politicas/referencia/verify-jwt.md), [03-jwt-jws](../docs/03-seguridad/03-jwt-jws.md) |
| [`data-deidentification`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/data-deidentification) | Enmascarar datos de payloads JSON y XML con la API de DLP. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [Javascript](../docs/02-politicas/referencia/javascript.md), [RaiseFault](../docs/02-politicas/referencia/raise-fault.md), [ServiceCallout](../docs/02-politicas/referencia/service-callout.md), [XSL](../docs/02-politicas/referencia/xsl-transform.md) | [service-callout](../docs/02-politicas/referencia/service-callout.md) |
| [`json-web-tokens`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/json-web-tokens) | Generar y verificar JWT con las políticas estándar. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [DecodeJWT](../docs/02-politicas/referencia/decode-jwt.md), [GenerateJWT](../docs/02-politicas/referencia/generate-jwt.md), [KeyValueMapOperations](../docs/02-politicas/referencia/key-value-map-operations.md), [RaiseFault](../docs/02-politicas/referencia/raise-fault.md), [VerifyJWT](../docs/02-politicas/referencia/verify-jwt.md) | [generate-jwt](../docs/02-politicas/referencia/generate-jwt.md), [verify-jwt](../docs/02-politicas/referencia/verify-jwt.md) |
| [`mtls-northbound`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/mtls-northbound) | mTLS de entrada en el balanceador con una CA privada de GCP. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [RaiseFault](../docs/02-politicas/referencia/raise-fault.md) | [04-tls-mtls](../docs/03-seguridad/04-tls-mtls.md) |
| [`mtls-southbound`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/mtls-southbound) | mTLS hacia el backend con keystore y truststore. |  | [04-tls-referencias-y-data-collectors](../docs/15-administracion/04-tls-referencias-y-data-collectors.md) |
| [`oauth-client-credentials`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/oauth-client-credentials) | OAuth 2.0 con el grant *client credentials*. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [OAuthV2](../docs/02-politicas/referencia/oauthv2.md) | [oauthv2](../docs/02-politicas/referencia/oauthv2.md), [02-oauth2](../docs/03-seguridad/02-oauth2.md) |
| [`oauth-client-credentials-with-scope`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/oauth-client-credentials-with-scope) | *Client credentials* con control de acceso por scopes. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [OAuthV2](../docs/02-politicas/referencia/oauthv2.md) | [oauthv2](../docs/02-politicas/referencia/oauthv2.md) |
| [`threat-protection`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/threat-protection) | Protección frente a amenazas en JSON, XML y expresiones regulares. | [JSONThreatProtection](../docs/02-politicas/referencia/json-threat-protection.md), [RegularExpressionProtection](../docs/02-politicas/referencia/regular-expression-protection.md) | [05-threat-protection](../docs/03-seguridad/05-threat-protection.md) |

## Tráfico

| Ejemplo | Qué muestra | Políticas | En este repo |
|---|---|---|---|
| [`basic-caching`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/basic-caching) | Caché de respuestas y de datos con las políticas de caché. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [LookupCache](../docs/02-politicas/referencia/lookup-cache.md), [PopulateCache](../docs/02-politicas/referencia/populate-cache.md), [ResponseCache](../docs/02-politicas/referencia/response-cache.md) | [response-cache](../docs/02-politicas/referencia/response-cache.md), [claves-de-cache](../docs/02-politicas/referencia/claves-de-cache.md) |
| [`basic-quota`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/basic-quota) | Cuota básica de consumo por app. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [Quota](../docs/02-politicas/referencia/quota.md), [RaiseFault](../docs/02-politicas/referencia/raise-fault.md), [VerifyAPIKey](../docs/02-politicas/referencia/verify-api-key.md) | [quota](../docs/02-politicas/referencia/quota.md) |
| [`spike-arrest`](https://github.com/GoogleCloudPlatform/apigee-samples/tree/main/spike-arrest) | Suavizado de picos con SpikeArrest. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [RaiseFault](../docs/02-politicas/referencia/raise-fault.md), [SpikeArrest](../docs/02-politicas/referencia/spike-arrest.md) | [spike-arrest](../docs/02-politicas/referencia/spike-arrest.md) |

## Fuentes

- GoogleCloudPlatform/apigee-samples: <https://github.com/GoogleCloudPlatform/apigee-samples> (clonado y analizado el 2026-10-23).
