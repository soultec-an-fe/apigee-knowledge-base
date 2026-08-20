---
id: ai-gateway-mcp
titulo: Model Context Protocol (MCP) en Apigee
area: ai
tags: [mcp, model-context-protocol, agentes, tools, api-hub, discovery-proxy]
aplica_a: [apigee-x]
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/apigee-mcp/apigee-mcp-overview
revisado: 2026-08-20
---

# Model Context Protocol (MCP) en Apigee

> [!NOTE]
> Contenido verificado directamente contra la documentación oficial de Google (navegador, no búsqueda). No disponible para **Apigee hybrid** — solo Apigee (X).

## Qué es MCP

**Model Context Protocol (MCP)** es un protocolo de código abierto desarrollado por Anthropic que estandariza cómo las aplicaciones de IA se conectan a fuentes de datos, workflows y herramientas.

Términos del protocolo:

| Término | Rol |
|---|---|
| **MCP host** | La aplicación de IA que interactúa con el usuario. Usa un LLM para procesar peticiones que pueden requerir datos o herramientas externas |
| **MCP client** | Componente dentro del host que traduce las peticiones del LLM hacia el MCP server y sus respuestas de vuelta. Descubre y usa los MCP servers disponibles |
| **MCP server** | El servicio externo que aporta contexto, datos o capacidades al LLM, actuando de proxy entre el LLM y el MCP client |

## Qué aporta Apigee

Apigee expone tus APIs existentes **como herramientas MCP** a aplicaciones agénticas, sin que tengas que:

- Modificar tus APIs existentes.
- Escribir código nuevo.
- Desplegar o gestionar MCP servers locales o remotos.

Los endpoints MCP de Apigee implementan la especificación de MCP server, lo que permite a cualquier cliente MCP compatible con HTTP/S remoto:

- **Descubrir** endpoints disponibles.
- **Listar** las herramientas disponibles en un endpoint (`tools/list`).
- **Autenticarse** contra un endpoint.
- **Invocar** herramientas según las políticas de acceso definidas (`tools/call`).

Apigee ofrece soporte JSON-RPC para los métodos `tools/list` y `tools/call`.

## Cómo funciona: el MCP Discovery Proxy

Para exponer tus APIs como herramientas MCP, creas y despliegas un proxy de Apigee usando la **plantilla MCP Discovery Proxy**. Después, empaquetas las operaciones MCP de ese proxy en un **API product**, lo que hace que tus operaciones/herramientas sean descubribles por clientes MCP a través de la integración con **API hub**.

```
Cliente MCP (agente / MCP host)
        │  HTTP/S
        ▼
Endpoint MCP gestionado: ORG_NAME.mcp.apigee.internal
        │
        ▼
MCP Discovery Proxy  ──►  API product  ──►  tus API proxies existentes
        │
        ▼
API hub  (ingesta la spec OpenAPI, mapea operaciones → herramientas MCP,
          habilita Semantic Search en lenguaje natural)
```

### Pasos para crear un MCP Discovery Proxy

1. **Crea una spec OpenAPI 3.0.x** que describa las operaciones que quieres exponer como herramientas. Versiones soportadas: **3.0.0, 3.0.1, 3.0.2, 3.0.3** (no 3.1.x).
2. **Crea el proxy** desde la Google Cloud Console: `Apigee → Proxy development → API proxies → + Create`, seleccionando la plantilla **MCP Discovery Proxy** y subiendo la spec.
3. **(Opcional) Añade una política de seguridad** al proxy (típicamente OAuth 2.1 / OIDC).
4. **Despliega** el proxy.
5. **Crea el API product** que empaqueta las operaciones MCP, con las cuotas y políticas de acceso que necesites.
6. **Lista las herramientas disponibles** para confirmar que quedaron expuestas.

> [!IMPORTANT]
> **El hostname debe coincidir exactamente.** El valor de `servers.url` en la spec OpenAPI debe ser una coincidencia exacta con el hostname del **environment group** del entorno donde despliegas el MCP Discovery Proxy. Si no coincide, el despliegue del proxy falla — es un requisito estricto, no una recomendación.

```yaml
# mcp-quickstart-openapi.yaml
openapi: 3.0.3
info:
  title: API de productos de Cymbal Group
  version: 1.0.0
servers:
  - url: https://cymbal.products.com        # ← debe coincidir con el hostname del environment group
paths:
  /artists:
    get:
      operationId: listArtists
      parameters:
        - name: limit
          in: query
          schema: { type: integer }
      responses:
        "200":
          description: Lista de artistas
    post:
      operationId: createArtist
      requestBody:
        required: true
        content:
          application/json:
            schema: { $ref: "#/components/schemas/Artist" }
      responses:
        "201":
          description: Artista creado
components:
  securitySchemes:
    oauth2:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: /oauth/authorize
          tokenUrl: /oauth/token
          scopes:
            artists.read: Acceso de lectura
            artists.write: Acceso de escritura
```

Cada `operationId` de la spec se mapea a una herramienta MCP individual.

## Descubrimiento con API hub

Cuando se despliega un MCP Discovery Proxy, **API hub ingiere automáticamente su spec OpenAPI**, le asigna el estilo de API "MCP" y mapea cada operación a una herramienta MCP individual. Esto permite a los desarrolladores:

- Filtrar por APIs habilitadas para MCP en API hub.
- Usar **Semantic Search** con consultas en lenguaje natural para encontrar herramientas relevantes.

## Seguridad

Varias capas, todas gestionadas por Apigee:

| Capa | Mecanismo |
|---|---|
| **Autenticación** | Los endpoints MCP alojados en Apigee soportan **OAuth 2.1** y **OpenID Connect (OIDC)**. Protected Resource Metadata permite a los clientes descubrir los servidores de autorización |
| **Autorización granular** | Puedes restringir el acceso a herramientas MCP según la identidad del cliente OAuth — por ejemplo, que solo agentes con `client_id` conocidos accedan a una herramienta de pagos |
| **Red** | Los endpoints se configuran por hostname o por environment group |
| **Contenido** | Combínalo con [Model Armor](../02-politicas/05-politicas-ai.md) para filtrar prompts y respuestas si el MCP server media tráfico de LLM |

## Observabilidad

Con Apigee Analytics puedes:

- Segmentar el tráfico específico de MCP frente al tráfico estándar de API.
- Ver métricas **por herramienta individual**: volumen de `tools/list` (descubrimiento) frente a `tools/call` (ejecución).
- Distinguir overhead del proxy de tiempo de respuesta del target, igual que en cualquier otro proxy.

## Configurar varios MCP servers

Los endpoints MCP se pueden configurar a nivel de **hostname** o de **environment group**. Ejemplo con una organización que tiene varios hostnames:

| Hostname | MCP server target | Proxy | Environment / grupo |
|---|---|---|---|
| `api.cymbal.com/mcp` | `cymbal.mcp.apigee.internal` | `mcp-api-proxy1` | `prod` / `prod-env-group` |
| `api-internal.cymbal.com/mcp` | `cymbal.mcp.apigee.internal` | `mcp-api-proxy2` | `internal` / `internal-env-group` |
| `api-service.cymbal.com/mcp` | `cymbal.mcp.apigee.internal` | `mcp-api-proxy3` | `dev` / `dev-env-group` |

## Limitaciones

| Limitación | Detalle |
|---|---|
| **Herramientas MCP por organización** | **1.000** (coincide con el límite general documentado en [límites de la plataforma](../10-referencia/01-limites.md)) |
| **No disponible en Apigee hybrid** | Solo Apigee (X) |
| **Versiones de OpenAPI soportadas** | 3.0.0, 3.0.1, 3.0.2, 3.0.3 — **no** 3.1.x |
| **No se puede cambiar el estilo de API a MCP** para un recurso de API hub que ya tiene operaciones existentes | — |
| **Sin soporte de Server-Sent Events (SSE)** | Las peticiones `GET` sobre respuestas de error MCP devuelven `405` |
| **Capacidad regional limitada** | Riesgo de fallo de aprovisionamiento en `europe-central2`, `europe-southwest1`, `europe-west9`, `me-central2`. Si el estado nunca pasa a "Deployed", prueba a desplegar en otra región |
| **API insights no disponible con VPC-SC** | Si la org de Apigee tiene VPC Service Controls activado, API hub no muestra insights de APIs/tráfico MCP |

## Cuándo usar esto frente a un AI Gateway "clásico"

| Necesitas | Documento |
|---|---|
| Que tus APIs REST existentes sean **descubribles e invocables por agentes** como herramientas | Este documento |
| Fronterar y gobernar el **tráfico saliente hacia un LLM** (Gemini, OpenAI, Anthropic) con cuotas de tokens, caché semántica y Model Armor | [Apigee como AI Gateway](01-apigee-como-ai-gateway.md) |
| Ambos a la vez | Combínalos: un agente llama a tus herramientas MCP, y esas herramientas —o el propio agente— hablan con el LLM a través de un proxy con las [políticas de IA](../02-politicas/05-politicas-ai.md) |

## Fuentes

- <https://docs.cloud.google.com/apigee/docs/api-platform/apigee-mcp/apigee-mcp-overview> (consultada directamente, contenido completo)
- <https://docs.cloud.google.com/apigee/docs/api-platform/apigee-mcp/apigee-mcp-quickstart> (consultada directamente, contenido completo)
- <https://docs.cloud.google.com/apigee/docs/api-platform/get-started/ai-capabilities>
- <https://docs.cloud.google.com/apigee/docs/apihub/manage-mcp-tools>
