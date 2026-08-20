---
id: publicacion-api-products
titulo: API products
area: publicacion
tags: [api-product, quota, scopes, operations, acceso, monetizacion]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://cloud.google.com/apigee/docs/api-platform/publish/what-api-product
revisado: 2026-08-20
---

# API products

> [!IMPORTANT]
> **El API product es el concepto más importante y peor entendido de Apigee.**
>
> - El **API proxy** es *técnico*: cómo se procesa una petición HTTP.
> - El **API product** es *de acceso y negocio*: qué operaciones puede llamar una app, con qué cuota y con qué scopes.
>
> Una API key **no da acceso a un proxy**. Da acceso a **los products que la contienen**.

## El modelo completo

```
API Proxy(s)  ──agrupados en──►  API Product  ◄──suscrita──  Developer App  ◄──posee──  Developer
                                      │                            │
                                      ├─ Cuota                     └─ consumer key + secret
                                      ├─ Scopes OAuth
                                      ├─ Operaciones (verbo + ruta)
                                      ├─ Entornos permitidos
                                      ├─ Nivel de acceso
                                      └─ Atributos personalizados
```

## Qué define un API product

| Atributo | Función |
|---|---|
| **API proxies / Operations** | Qué proxies y qué operaciones concretas (verbo + ruta) están incluidos |
| **Environments** | En qué entornos es válido |
| **Quota** | Límite de llamadas por intervalo, leído por la política `Quota` |
| **OAuth scopes** | Scopes que se conceden a los tokens emitidos para este producto, como lista separada por comas |
| **Access level** | `Public`, `Private` o `Internal only`: controla la visibilidad en el portal |
| **Custom attributes** | Pares clave/valor arbitrarios. **La clave de la flexibilidad** |

> [!IMPORTANT]
> **Requisito en Pay-as-you-go, confirmado en la documentación oficial:** un API product en un proyecto Pay-as-you-go debe incluir **o bien** proxies extensibles con flow hooks, **o bien** al menos una política extensible como `VerifyAPIKey` u `OAuthV2`. Un producto que envuelva únicamente un proxy Standard sin ninguna política extensible no cumple este requisito. Ver [Standard vs. Extensible](../02-politicas/00-catalogo-de-politicas.md#standard-vs-extensible-no-es-solo-una-etiqueta-de-calidad).

## Operations — control granular

En lugar de incluir un proxy entero, se declaran **operaciones**: grupos de atributos que restringen el acceso a uno o más proxies según ruta, método HTTP y cuota.

| Atributo de la operación | ¿Obligatorio? | Descripción |
|---|---|---|
| API proxy | Sí | Cada grupo de operaciones especifica un proxy. Solo uno por grupo |
| Remote Service | Solo si usas Apigee Adapter for Envoy | — |
| Resource path | Sí | Uno o más resource paths: la parte de la URL que va después del basepath |
| HTTP method | No | Si no se especifica, se permiten todos los métodos |
| Quota | No | La cuota de la operación **tiene precedencia** sobre la cuota a nivel de producto, si ambas están definidas |
| Custom attributes | No | Además de los atributos a nivel de producto. Se acceden en runtime con el prefijo `apiproduct.operation.attributes.*` |

En JSON:

```json
{
  "name": "producto-basico",
  "displayName": "Plan Básico",
  "approvalType": "auto",
  "environments": ["prod"],
  "quota": "1000",
  "quotaInterval": "1",
  "quotaTimeUnit": "hour",
  "scopes": ["pedidos.read"],
  "operationGroup": {
    "operationConfigType": "proxy",
    "operationConfigs": [
      {
        "apiSource": "pedidos-v1",
        "operations": [
          { "resource": "/pedidos",   "methods": ["GET"] },
          { "resource": "/pedidos/*", "methods": ["GET"] }
        ],
        "quota": { "limit": "1000", "interval": "1", "timeUnit": "hour" }
      }
    ]
  },
  "attributes": [
    { "name": "nivel",      "value": "basico" },
    { "name": "feature_v2", "value": "false" }
  ]
}
```

El plan premium sería el mismo proxy con más métodos y más cuota:

```json
{
  "name": "producto-premium",
  "quota": "100000",
  "quotaInterval": "1",
  "quotaTimeUnit": "hour",
  "scopes": ["pedidos.read", "pedidos.write"],
  "operationGroup": {
    "operationConfigType": "proxy",
    "operationConfigs": [
      {
        "apiSource": "pedidos-v1",
        "operations": [
          { "resource": "/**", "methods": ["GET", "POST", "PUT", "DELETE"] }
        ]
      }
    ]
  },
  "attributes": [
    { "name": "nivel",      "value": "premium" },
    { "name": "feature_v2", "value": "true" }
  ]
}
```

**El mismo proxy, sin un solo cambio de código, sirve dos planes distintos.**

## Cómo se aplica en runtime

Apigee no valida las API keys automáticamente: **tú** debes incluir `VerifyAPIKey` u `OAuthV2 VerifyAccessToken` en el flujo. Sin una política de este tipo, cualquiera puede invocar tu proxy sin credenciales.

Los pasos exactos que ejecuta Apigee al verificar una credencial, según la documentación oficial:

1. Obtiene las credenciales que vienen en la petición. Con verificación por token OAuth, primero comprueba que el token no ha expirado y luego recupera la consumer key que lo generó.
2. Recupera la lista de API products asociados a esa consumer key.
3. Confirma que el proxy actual está incluido en el producto, que la ruta actual está habilitada en él y, si el producto lo restringe, que se usa el verbo HTTP permitido.
4. Verifica que la cuota, si está definida, no se ha superado.
5. Verifica que la consumer key no está expirada ni revocada, que la app no está revocada y que el developer está activo.

Si todos los checks pasan, la verificación tiene éxito y se pueblan las variables `apiproduct.*`. Si falla el paso 3, Apigee lanza `InvalidApiKeyForGivenResource`.

Luego la política `Quota` **lee** los valores del producto:

```xml
<Quota name="Q-DesdeProducto">
    <Identifier ref="client_id"/>
    <Allow countRef="apiproduct.developer.quota.limit" count="100"/>
    <Interval ref="apiproduct.developer.quota.interval">1</Interval>
    <TimeUnit ref="apiproduct.developer.quota.timeunit">hour</TimeUnit>
    <Distributed>true</Distributed>
    <Synchronous>false</Synchronous>
</Quota>
```

> [!TIP]
> **Este es el patrón que debes interiorizar:** el proxy no sabe nada de planes. Solo lee lo que dice el producto. Cambiar el plan de un cliente = cambiar el producto de su app. Cero despliegues, cero código.

## Atributos personalizados: feature flags sin despliegue

Los custom attributes del producto son accesibles en el flujo:

```xml
<Condition>verifyapikey.VAK-VerificarApiKey.apiproduct.feature_v2 = "true"</Condition>
```

Usos habituales:

| Atributo | Uso |
|---|---|
| `nivel` | Enrutar a backends distintos por tier |
| `feature_*` | Activar comportamiento nuevo por cliente |
| `tenant_id` | Multi-tenancy: filtrar datos por inquilino |
| `llmQuota` | Cuota de tokens para [proxies de LLM](../02-politicas/05-politicas-ai.md) |
| `backend_url` | Backend dedicado por cliente enterprise |

## approvalType

| Valor | Comportamiento |
|---|---|
| `auto` | La app queda aprobada inmediatamente al suscribirse |
| `manual` | Requiere aprobación explícita de un administrador |

Usa `manual` para productos de pago o con datos sensibles.

## Diseño de productos: patrones

### Por nivel de servicio (el más común)
```
producto-free       → 100 req/día,     solo GET
producto-basico     → 10.000 req/día,  GET + POST
producto-premium    → 1M req/día,      todos los métodos
```

### Por dominio funcional
```
producto-pedidos    → proxies de pedidos
producto-clientes   → proxies de clientes
producto-pagos      → proxies de pagos (approvalType: manual)
```

### Por audiencia
```
producto-publico    → subconjunto de solo lectura, access level public
producto-partners   → operaciones ampliadas, approvalType manual
producto-interno    → todo, access level internal
```

> [!NOTE]
> **Matiz importante, no una regla cerrada.** La documentación oficial recomienda mantener una relación **uno a uno entre spec OpenAPI, API proxy y API product** como punto de partida para gobernar el catálogo con claridad. Eso no prohíbe el patrón de planes: puedes tener varios products que envuelven el **mismo proxy** con cuotas y operaciones distintas (`producto-free`, `producto-basico`, `producto-premium`), que es exactamente el mecanismo de `operationConfigs` que se muestra arriba. Lo que sí es un error real es duplicar el **catálogo técnico** — un producto por proxy sin ninguna diferenciación de plan, cuota o audiencia — porque entonces el producto no aporta nada sobre el proxy y solo añade una capa de gestión redundante. La recomendación de Google es sobre claridad de gobierno del catálogo; la del "producto = plan" de aquí es criterio propio derivado de esa idea, no una cita textual de Google.

## Niveles de acceso

| Nivel | Descripción |
|---|---|
| `Public` | Visible para todos los desarrolladores; se puede añadir a portales integrados o basados en Drupal |
| `Private` | Diseñado para uso privado |
| `Internal only` | Diseñado para uso interno |

> [!NOTE]
> Confirmado en la documentación oficial: **no hay diferencia funcional entre `Private` e `Internal only`**. Son dos etiquetas para que elijas la que mejor describa la audiencia prevista del producto; el comportamiento de acceso es idéntico. Para hacerlos visibles a una app concreta hay que añadirlos manualmente desde la UI o la API de Apigee.

## Límites

| Límite | Valor |
|---|---|
| API products por organización | **5.000** |
| API products por API key | 50 |
| API products por app | 100 |
| Atributos personalizados | 18 |

## Gestión con CLI

```bash
# Crear producto desde un JSON
apigeecli products create -f ./producto-basico.json \
  --org "$ORG" --token "$(gcloud auth print-access-token)"

# Listar
apigeecli products list --org "$ORG" --token "$(gcloud auth print-access-token)"

# Exportar todos (para versionar en Git)
apigeecli products export --org "$ORG" --token "$(gcloud auth print-access-token)"
```

> [!TIP]
> **Versiona los API products en Git** igual que los proxies. Son configuración de negocio con impacto directo en facturación y acceso: merecen revisión por PR y trazabilidad, no clics en la consola.

## Fuentes

- <https://cloud.google.com/apigee/docs/api-platform/publish/what-api-product> (consultada directamente, contenido completo)
- <https://cloud.google.com/apigee/docs/api-platform/publish/create-api-products>
- <https://cloud.google.com/apigee/docs/api-platform/reference/limits>
