---
id: adaptadores-extension-processor
titulo: Apigee Extension Processor
area: adaptadores
tags: [extension-processor, service-extensions, traffic-extension, load-balancer, agent-gateway, mcp, psc, ai-gateway]
aplica_a: [apigee-x]
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/service-extensions/extension-processor-overview
revisado: 2026-10-23
---

# Apigee Extension Processor

> **Fecha de corte: 23 de octubre de 2026.**

El **Apigee Extension Processor** es una *traffic extension* (un tipo de Service Extension de Cloud Load Balancing). Permite que un **Application Load Balancer** haga un *callout* a Apigee en el camino de cada petición y de cada respuesta. Apigee ejecuta las políticas de un proxy especial y devuelve el mensaje, modificado o no, al balanceador, que lo sigue procesando hacia el backend.

Resultado: aplicas VerifyAPIKey, OAuthV2, Quota, políticas de IA o inyección de tokens de Google a **cualquier servicio detrás del balanceador**, sin que el cliente cambie de URL y sin que Apigee reenvíe el tráfico.

## Casos de uso documentados

- Proteger cargas de Google Cloud con políticas de Apigee (VerifyAPIKey, OAuthV2, VerifyJWS…).
- Cuotas sobre el tráfico de red.
- **Inyectar tokens de Google** (access token o ID token) con AssignMessage, para backends que exigen autenticación de Google.
- Protocolos nativos que un proxy convencional no cubre igual: **gRPC bidireccional, server-sent events (SSE) y HTTP/3**.
- Además: Advanced API Security, monetización, trazado distribuido y Analytics sobre ese tráfico.

## Componentes

| Componente | Función |
|---|---|
| Application Load Balancer | Recibe el tráfico; su backend service apunta a un **NEG** con los backends de la aplicación. |
| Traffic extension | Se conecta al runtime de Apigee mediante un endpoint de **Private Service Connect**. |
| Entorno de Apigee dedicado | Con la propiedad **`apigee-service-extension-enabled` = `true`**. |
| Proxy del Extension Processor | **Sin target** (o con SSE habilitado); las políticas viven aquí. |

**Flujo:**

1. El cliente llama al balanceador.
2. El balanceador invoca la extensión.
3. El Message Processor de Apigee ejecuta las políticas y devuelve la petición.
4. El balanceador la entrega al backend.

En la respuesta ocurre lo mismo en sentido inverso.

## Limitaciones

| Límite | Valor |
|---|---|
| Distinción por base path o URL | **Ninguna**: todo el tráfico del balanceador pasa por el mismo proxy |
| Traffic extensions por balanceador | 1 |
| Traffic extensions por proyecto | 100 |
| Cadenas de extensiones por proyecto | 5 |
| Extensiones por recurso | 3 |
| Entornos en el environment group del Extension Processor | 1 |
| Proxies en el entorno dedicado | 50 |
| Tipo de proxy en el entorno | **Todos Standard o todos Extensible**, sin mezclar |

Además, el tráfico queda sujeto a las cuotas de Cloud Load Balancing.

**Políticas no soportadas:**

- PublishMessage, ExternalCallout, IntegrationCallout, ServiceCallout, SetIntegrationRequest, MessageLogging y GenerateJWT.
- Con proxies SSE, tampoco PublishMessage ni MessageLogging dentro de `EventFlows`.

> [!WARNING]
> **Contradicción entre páginas oficiales.** La página del Extension Processor excluye **GenerateJWT** y **ServiceCallout**. Sin embargo, la guía del [Operator for Kubernetes](03-apim-operator-kubernetes.md), que usa el Extension Processor por debajo, los incluye entre las políticas que se pueden añadir al Gateway. Antes de diseñar sobre cualquiera de las dos, pruébala en tu organización.

## Configuración (resumen del quickstart)

1. **Balanceador:**
   - Application Load Balancer externo global.
   - NEG con los backends, backend service, URL map, target proxy y forwarding rule.
2. **Apigee:**
   - Entorno y environment group nuevos, con `apigee-service-extension-enabled` en `true`.
   - Despliega el proxy del Extension Processor: sin target, o SSE.
3. **Traffic extension:**
   - Se crea con la **API de aprovisionamiento del Extension Processor**.
   - Campos principales: `matchCondition` (expresión CEL), `failOpen`, `hostname` y `supportedEvents`.
   - Se puede actualizar después (`networkConfigs`, `extensions`, `extensionProcessor`).
4. **Políticas en el proxy:** por ejemplo VerifyAPIKey (con su API product y su app), o AssignMessage con `<Authentication>` para inyectar un token de Google hacia el backend.

> [!CAUTION]
> **`failOpen`** decide qué pasa si Apigee no responde. Con `true`, el balanceador deja pasar la petición **sin aplicar las políticas**: API keys, cuotas y Model Armor quedan desactivados mientras dure el fallo. Para APIs protegidas, `false`. Esta advertencia es de este repositorio; la página solo describe el campo.

## Políticas de IA y Agent Gateway

El Extension Processor también aplica capacidades de **AI Gateway** a tráfico que no pasa por un proxy: un servicio en GKE, una API detrás de otro gateway, o un **servidor MCP** que usa un agente.

| Dónde se conecta | Tipo de extensión | Qué gobierna |
|---|---|---|
| Application Load Balancer | Traffic extension | El tráfico hacia los backends del balanceador |
| **Agent Gateway** | **Authorization extension** | Las llamadas **salientes** de un agente de IA: a su modelo, a sus herramientas y a servidores MCP, **sin modificar el agente** |

**Con Agent Gateway** (`governedAccessPath: AGENT_TO_ANYWHERE`):

1. El gateway retiene la petición del agente y pide un **veredicto** a la extensión.
2. El *callout* sale por un *network attachment* desde tu VPC.
3. Una zona DNS privada resuelve el nombre al endpoint de PSC.
4. El endpoint de PSC llega a la instancia de Apigee.
5. El environment group enruta por hostname al proxy sin target.
6. Si el veredicto lo permite, el gateway envía la petición original. **Apigee nunca reenvía el tráfico del agente.**

Roles necesarios: `roles/apigee.admin`, `roles/networkservices.serviceExtensionsAdmin`, `roles/networksecurity.admin` y `roles/compute.networkAdmin`.

**Recomendaciones oficiales para estas políticas:**

- **Filtra primero en la extensión:**
  - En una traffic extension, con `matchCondition.celExpression`, por ejemplo `request.host == "example.com"`.
  - En una authorization extension, con `httpRules.to.operations`.
  - Lo que no te interesa gobernar no debería llegar a Apigee.
- **Después, acota cada política con condiciones.** Por ejemplo, `(request.uri Like "*generateContent*")` para limitar al modelo las políticas de tokens y Model Armor, porque las llamadas al modelo, de sesión y de telemetría pueden compartir host.
- **Proxy sin target y Extensible**, y todos los proxies del entorno del mismo tipo.
- **El cuerpo es el del mensaje real.** Para Gemini, el prompt está en `$.contents[-1].parts[-1].text`. Para otros proveedores, ajusta `UserPromptSource`, `LLMTokenUsageSource` y `LLMModelSource`.
- **Cuenta de servicio en el despliegue** para las políticas que llaman a servicios de Google (Model Armor, embeddings de la caché semántica).
- **Quota distribuida y síncrona** cuando necesitas un límite exacto. SpikeArrest se aplica por Message Processor y no garantiza una tasa global.
- Para LLMTokenQuota: una instancia `EnforceOnly` en la petición y otra `CountOnly` en la respuesta.

Referencias de las políticas: [SanitizeUserPrompt](../02-politicas/referencia/sanitize-user-prompt.md), [SanitizeModelResponse](../02-politicas/referencia/sanitize-llm-response.md), [SemanticCacheLookup](../02-politicas/referencia/semantic-cache-lookup.md), [PromptTokenLimit](../02-politicas/referencia/prompt-token-limit.md), [LLMTokenQuota](../02-politicas/referencia/llm-token-quota.md).

## Costes

Además de Apigee, se pagan Service Extensions, el backend service y Private Service Connect.

## Fuentes

- Apigee Extension Processor overview: <https://docs.cloud.google.com/apigee/docs/api-platform/service-extensions/extension-processor-overview> (consultada directamente, contenido completo, 2026-10-23).
- Get started with the Apigee Extension Processor: <https://docs.cloud.google.com/apigee/docs/api-platform/service-extensions/extension-processor-quickstart> (consultada directamente, estructura y campos, 2026-10-23).
- Policies for the Apigee extension processor: <https://docs.cloud.google.com/apigee/docs/api-platform/service-extensions/extension-processor-policies> (consultada directamente, contenido completo, 2026-10-23).
- Connect the Apigee extension processor to an Agent Gateway: <https://docs.cloud.google.com/apigee/docs/api-platform/service-extensions/extension-processor-agent-gateway> (consultada directamente, 2026-10-23).
