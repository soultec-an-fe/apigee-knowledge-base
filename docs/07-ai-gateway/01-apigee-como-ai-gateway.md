---
id: ai-gateway
titulo: Apigee como AI Gateway
area: ai
tags: [ai-gateway, llm, vertex-ai, gemini, openai, model-routing, fanout, tokens]
aplica_a: [apigee-x]
fuente: https://cloud.google.com/solutions/apigee-ai
revisado: 2026-08-20
---

# Apigee como AI Gateway

> [!NOTE]
> Este documento cubre el gobierno del **tráfico saliente hacia un LLM** (cuotas de tokens, caché semántica, Model Armor). Para exponer tus propias APIs **como herramientas invocables por agentes** vía Model Context Protocol, ver [MCP en Apigee](02-mcp-en-apigee.md) — es una capacidad distinta y complementaria.

## El problema

Una organización que empieza a usar LLMs se encuentra, en pocos meses, con esto:

- Cada equipo llama directamente a la API del proveedor con **su propia clave**.
- Nadie sabe cuánto se está gastando, ni **quién** lo gasta.
- No hay límite: un bucle mal escrito puede consumir el presupuesto del trimestre en una noche.
- Los prompts de usuario llegan al modelo **sin filtrar**: prompt injection, jailbreak, PII.
- Cambiar de modelo o de proveedor obliga a tocar el código de cada aplicación.
- No hay registro de qué se preguntó ni qué respondió el modelo.

Es exactamente el conjunto de problemas que la gestión de APIs resolvió hace quince años. Apigee aplica el mismo patrón a los LLMs: **un gateway delante**.

## Lo que aporta el gateway

| Capacidad | Cómo |
|---|---|
| **Una sola credencial por equipo** | API key o token OAuth de Apigee; las claves de proveedor viven en un KVM |
| **Control de coste por tokens** | [`LLMTokenQuota`](../02-politicas/05-politicas-ai.md) con cuota tomada del API product |
| **Límite por petición** | `PromptTokenLimit` |
| **Seguridad del prompt y la respuesta** | `SanitizeUserPrompt` / `SanitizeModelResponse` vía **Model Armor** |
| **Ahorro por reutilización semántica** | `SemanticCacheLookup` / `SemanticCachePopulate` |
| **Cambiar de modelo sin tocar clientes** | Enrutado dinámico en el TargetEndpoint |
| **Observabilidad** | `DataCapture` y `MessageLogging` con tokens, modelo y coste |
| **Failover entre proveedores** | RouteRules y load balancing |

## Arquitectura de referencia

```
Aplicaciones ──► Apigee (proxy LLM) ──┬──► Vertex AI (Gemini)
                       │              ├──► OpenAI
                       │              └──► Anthropic
                       │
                       ├──► Model Armor        (filtrado de prompts/respuestas)
                       ├──► Vertex Embeddings  (caché semántica)
                       ├──► Vector Search      (caché semántica)
                       └──► Cloud Logging      (auditoría)
```

## Composición del proxy

```
ProxyEndpoint · PreFlow · Request
  1. CORS
  2. VerifyAPIKey                  → resuelve producto, equipo y cuota de tokens
  3. OASValidation                 → valida el esquema de la petición
  4. AssignMessage                 → extrae el prompt a una variable
  5. PromptTokenLimit              → rechaza prompts desmesurados
  6. FlowCallout → ModelArmor      → SanitizeUserPrompt + RaiseFault por filtro
  7. LLMTokenQuota (EnforceOnly)   → ¿queda presupuesto de tokens?
  8. SemanticCacheLookup           → si acierta, cortocircuita sin llamar al modelo

TargetEndpoint · Request
  9. AssignMessage                 → selección de modelo y credencial del proveedor

 →  MODELO

TargetEndpoint · Response
 10. FlowCallout → ModelArmor      → SanitizeModelResponse + RaiseFault por filtro
 11. LLMTokenQuota (CountOnly)     → incrementa el contador con el consumo real
 12. SemanticCachePopulate         → indexa la respuesta para futuras consultas

PostClientFlow
 13. MessageLogging / DataCapture  → tokens, modelo, coste, detecciones
```

El XML completo de cada política, con ejemplos oficiales verificados, está en [políticas de IA](../02-politicas/05-politicas-ai.md).

## Enrutado dinámico de modelo

El cliente pide un modelo lógico; Apigee lo traduce a un endpoint concreto:

```json
{ "model": "rapido", "prompt": "..." }
```

`policies/EV-Modelo.xml`:

```xml
<ExtractVariables continueOnError="false" enabled="true" name="EV-Modelo">
    <Source>request</Source>
    <JSONPayload>
        <Variable name="solicitado" type="string"><JSONPath>$.model</JSONPath></Variable>
    </JSONPayload>
    <VariablePrefix>modelo</VariablePrefix>
    <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
</ExtractVariables>
```

`policies/KVM-MapeoModelos.xml`:

```xml
<KeyValueMapOperations continueOnError="false" enabled="true"
                       name="KVM-MapeoModelos" mapIdentifier="modelos">
    <Scope>environment</Scope>
    <ExpiryTimeInSecs>300</ExpiryTimeInSecs>
    <Get assignTo="modelo.endpoint" index="1">
        <Key>
            <Parameter ref="modelo.solicitado"/>
            <Parameter>endpoint</Parameter>
        </Key>
    </Get>
</KeyValueMapOperations>
```

Cambiar de `gemini-2.0-flash` a la siguiente versión = editar una entrada del KVM. **Ningún cliente se entera y no hay despliegue.**

## Failover entre proveedores

```xml
<RouteRule name="fallback-openai">
    <Condition>modelo.primario.fallido = "true"</Condition>
    <TargetEndpoint>openai</TargetEndpoint>
</RouteRule>
<RouteRule name="default">
    <TargetEndpoint>vertex</TargetEndpoint>
</RouteRule>
```

> [!WARNING]
> El failover entre proveedores es **más difícil de lo que parece**: los formatos de petición y respuesta difieren, y también el comportamiento del modelo. Si haces failover, necesitas capas de traducción en ambos sentidos y aceptar que la respuesta puede tener otra calidad o estilo. Prueba el camino de failover con la misma seriedad que el principal.

## Gobierno del coste

El patrón que hace que esto sea gobernable:

```
API Product "equipo-marketing"
  ├── atributo llmQuota.limit    = 1000000
  ├── atributo llmQuota.interval = 1
  └── atributo llmQuota.timeunit = day
```

Y la política lo lee:

```xml
<Allow count="1000" countRef="verifyapikey.VA-VerifyAPIKey.apiproduct.developer.llmQuota.limit"/>
<Interval ref="verifyapikey.VA-VerifyAPIKey.apiproduct.developer.llmQuota.interval">1</Interval>
<TimeUnit ref="verifyapikey.VA-VerifyAPIKey.apiproduct.developer.llmQuota.timeunit">minute</TimeUnit>
```

Subirle el presupuesto a un equipo = editar un atributo del producto. Cero despliegues.

## Métricas que hay que capturar

```xml
<DataCapture continueOnError="true" enabled="true" name="DC-MetricasLlm">
    <Capture>
        <DataCollector>modelo</DataCollector>
        <Source>modelo.solicitado</Source>
    </Capture>
    <Capture>
        <DataCollector>tokens_prompt</DataCollector>
        <Source>llm.tokens.prompt</Source>
    </Capture>
    <Capture>
        <DataCollector>tokens_respuesta</DataCollector>
        <Source>llm.tokens.respuesta</Source>
    </Capture>
    <Capture>
        <DataCollector>cache_semantica_hit</DataCollector>
        <Source>cache.semantica.acierto</Source>
    </Capture>
</DataCapture>
```

| Métrica | Por qué importa |
|---|---|
| Tokens de prompt y de respuesta, por equipo | Es el coste real, por centro de imputación |
| Tasa de acierto de la caché semántica | Mide el ahorro. Si es baja, revisa el `<Threshold>` |
| Detecciones de Model Armor, por filtro | Detecta abuso y calibra los filtros |
| Latencia por modelo | Decide qué modelo usar para cada caso |
| Cuotas de tokens agotadas | Indica equipos mal dimensionados |

## Streaming

Muchos clientes de LLM usan **streaming** (SSE) para mostrar la respuesta token a token.

> [!CAUTION]
> **El streaming rompe casi todas las políticas de respuesta.**
> Con `response.streaming.enabled=true`, Apigee no bufferiza el mensaje: `SanitizeModelResponse`, `SemanticCachePopulate` y el conteo de tokens de la respuesta **no pueden acceder al contenido**.
>
> Opciones:
> - **No usar streaming** en las rutas que requieran filtrado de salida. Es la opción segura.
> - Ofrecer **dos rutas distintas**: `/chat` (con filtrado, sin streaming) y `/chat/stream` (con streaming, sin filtrado de salida) — y documentar la diferencia.
> - Aplicar el filtrado de salida en el cliente, asumiendo que es una capa menos fiable.
>
> No hay una solución que dé streaming y filtrado completo de la respuesta a la vez en el gateway. Decide conscientemente.

## Prerrequisitos

| Capacidad | Necesita |
|---|---|
| Políticas de token | Apigee X con soporte de políticas de IA |
| Caché semántica | Modelo de embeddings en Vertex AI + índice de Vertex AI Vector Search con endpoint público desplegado |
| Model Armor | Model Armor habilitado + plantilla configurada |
| Todo lo anterior | Service account con permisos sobre esos servicios, asociada al entorno de Apigee |

## Errores frecuentes

| Error | Consecuencia | Solución |
|---|---|---|
| Cachear semánticamente respuestas personalizadas | Se sirve la respuesta de un usuario a otro | Cachear solo consultas genéricas, o separar índices por tenant |
| `<Threshold>` demasiado permisivo | Respuestas incorrectas pero plausibles | Calibrar con tráfico real y medir la tasa de error |
| Contar tokens solo en el request | El coste real queda sin medir | Patrón `EnforceOnly` + `CountOnly` con `SharedName` |
| Filtrar el prompt pero no la respuesta | El modelo puede emitir PII o contenido dañino | Aplicar también `SanitizeModelResponse` |
| Clave del proveedor en el bundle | Credencial en Git | KVM cifrado + variable `private.` |
| Registrar prompts completos sin control | Fuga masiva de datos personales al sistema de logs | Registrar metadatos y hashes, no el contenido |
| Streaming con expectativa de filtrado | Falsa sensación de seguridad | Ver la advertencia de streaming arriba |

## Fuentes

- <https://cloud.google.com/solutions/apigee-ai>
- <https://cloud.google.com/apigee/docs/api-platform/get-started/ai-capabilities>
- <https://github.com/GoogleCloudPlatform/apigee-samples>
- <https://cloud.google.com/security-command-center/docs/model-armor-overview>
